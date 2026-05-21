import re
import os
from collections import Counter, defaultdict, OrderedDict
import requests
import io
import sys
import time
from threading import Thread, Lock
import subprocess
import sys

STEM_CODES = {
    "qal": "q",
    "niphal": "N",
    "piel": "p",
    "pual": "P",
    "hiphil": "h",
    "hophal": "H",
    "hithpael": "t",
    "polel": "o",
    "polal": "O",
    "hithpolel": "r",
    "poel": "m",
    "poal": "M",
    "palel": "k",
    "pulal": "K",
    "qal passive": "Q",
    "pilpel": "l",
    "polpal": "L",
    "hithpalpel": "f",
    "nithpael": "D",
    "pealal": "j",
    "pilel": "i",
    "hothpaal": "u",
    "tiphil": "c",
    "hishtaphel": "v",
    "nithpalel": "w",
    "nithpoel": "y",
    "hithpoel": "z",
}

acronym_mapping = {
    "Genesis": "01-GEN",
    "Exodus": "02-EXO",
    "Leviticus": "03-LEV",
    "Numbers": "04-NUM",
    "Deuteronomy": "05-DEU",
    "Joshua": "06-JOS",
    "Judges": "07-JDG",
    "Ruth": "08-RUT",
    "1 Samuel": "09-1SA",
    "2 Samuel": "10-2SA",
    "1 Kings": "11-1KI",
    "2 Kings": "12-2KI",
    "1 Chronicles": "13-1CH",
    "2 Chronicles": "14-2CH",
    "Ezra": "15-EZR",
    "Nehemiah": "16-NEH",
    "Esther": "17-EST",
    "Job": "18-JOB",
    "Psalms": "19-PSA",
    "Proverbs": "20-PRO",
    "Ecclesiastes": "21-ECC",
    "Song": "22-SNG",
    "Isaiah": "23-ISA",
    "Jeremiah": "24-JER",
    "Lamentations": "25-LAM",
    "Ezekiel": "26-EZK",
    "Daniel": "27-DAN",
    "Hosea": "28-HOS",
    "Joel": "29-JOL",
    "Amos": "30-AMO",
    "Obadiah": "31-OBA",
    "Jonah": "32-JON",
    "Micah": "33-MIC",
    "Nahum": "34-NAM",
    "Habakkuk": "35-HAB",
    "Zephaniah": "36-ZEP",
    "Haggai": "37-HAG",
    "Zechariah": "38-ZEC",
    "Malachi": "39-MAL",
    "Matthew": "41-MAT",
    "Mark": "42-MRK",
    "Luke": "43-LUK",
    "John": "44-JHN",
    "Acts": "45-ACT",
    "Romans": "46-ROM",
    "1 Corinthians": "47-1CO",
    "2 Corinthians": "48-2CO",
    "Galatians": "49-GAL",
    "Ephesians": "50-EPH",
    "Philippians": "51-PHP",
    "Colossians": "52-COL",
    "1 Thessalonians": "53-1TH",
    "2 Thessalonians": "54-2TH",
    "1 Timothy": "55-1TI",
    "2 Timothy": "56-2TI",
    "Titus": "57-TIT",
    "Philemon": "58-PHM",
    "Hebrews": "59-HEB",
    "James": "60-JAS",
    "1 Peter": "61-1PE",
    "2 Peter": "62-2PE",
    "1 John": "63-1JN",
    "2 John": "64-2JN",
    "3 John": "65-3JN",
    "Jude": "66-JUD",
    "Revelation": "67-REV"
}

logs = []
logs_lock = Lock()
download_in_progress = False


def add_log(message):
    with logs_lock:
        logs.append(message)


def clear_logs():
    with logs_lock:
        logs.clear()


def download_text_files(logger=add_log):
    chunk_size = 2
    delay = 1
    logger("Starting download of text files...")
    os.makedirs("Data/en_ult", exist_ok=True)
    os.makedirs("Data/en_ust", exist_ok=True)
    versions = ["ult", "ust"]
    for version in versions:
        book_codes = list(acronym_mapping.values())
        for i in range(0, len(book_codes), chunk_size):
            chunk = book_codes[i:i + chunk_size]
            for book_code in chunk:
                link = f'https://git.door43.org/unfoldingWord/en_{version}/raw/branch/master/{book_code}.usfm'
                try:
                    response = requests.get(link)
                    response.raise_for_status()
                    with open(f"Data/en_{version}/{book_code}.usfm",
                              "w",
                              encoding="utf-8") as f:
                        f.write(response.text)
                    logger(f"Downloaded en_{version}/{book_code}.usfm")
                except requests.RequestException as e:
                    logger(
                        f"Failed to download en_{version}/{book_code}.usfm: {e}"
                    )
            time.sleep(delay)
    logger("Download complete.")


def parse_user_input(input_str):
    # Handle Hebrew root lookup form like 'H:עבד [stem]'
    if input_str.startswith("H:"):
        parts = input_str[2:].strip().split()
        if not parts:
            raise ValueError("Missing word after 'H:'.")
        word = parts[0]
        word = strip_hebrew_vowels(word)
        version = parts[1].lower()
        stem = parts[2] if len(parts) > 2 else None
        if stem:
            stem = stem.lower()
        return "H", None, word, version, stem
        """Extracts chapter, verse, word, version, and optional stem."""
    else:
        parts = input_str.strip().split()
        if len(parts) < 3:
            raise ValueError(
                "Input must include chapter:verse, word, and version.")

        chapter_verse, word, version = parts[:3]
        stem = parts[3] if len(parts) > 3 else None

        chapter, verse = chapter_verse.split(":")
        version = version.lower()
        if stem:
            stem = stem.lower()
        return chapter, verse, word, version, stem


def find_word(chapter, verse, word, version, file_path):
    """Constructs a regex pattern to match the word form."""

    with open(f"{file_path}", "r", encoding="utf-8") as f:
        usfm_text = f.read()

    chapter_end = str(int(chapter) + 1)
    verse_end = str(int(verse) + 1)
    chapter_match = re.search(rf"\\c {chapter}[\n ].*?\\c {chapter_end}[\n ]",
                              usfm_text, re.DOTALL)
    if not chapter_match:
        return None
    chapter_text = chapter_match.group(0)

    verse_match = re.search(rf"\\v {verse}.*?\\v {verse_end}", chapter_text,
                            re.DOTALL)
    if not verse_match:
        last_verse_match = re.search(rf"\\v {verse}.*?\\c {chapter_end}",
                                     chapter_text, re.DOTALL)
        verse_match = last_verse_match
        if not last_verse_match:
            return None
    verse_text = verse_match.group(0)
    """change the below to isolate blocks and then find the correct ones"""
    aligned_blocks = re.findall(r"\\zaln-s.*?\\zaln-e", verse_text, re.DOTALL)
    matches = []
    for block in aligned_blocks:
        if re.search(rf"\\w {re.escape(word)}\|", block):
            matches.append(block)
    for match in matches:
        word_matches = re.findall(r'x-lemma=\"([^"]*?)\"', match)
        word_text = word_matches[-1] if word_matches else None
    print(word_text)
    return word_text


def strip_hebrew_vowels(text):
    """Remove Hebrew vowels (niqqud and cantillation marks) from a string."""
    return re.sub(r'[\u0591-\u05C7]', '', text)


def search_usfm_files(word_lemma, version, stem, strip_lemma=False, selected_books=None):
    """Search through USFM files and find aligned phrases for a lemma, optionally filtered by stem."""
    directory = f'Data/en_{version}'

    stem_code = STEM_CODES.get(stem) if stem else None

    # Normalize selected_books to uppercase for comparison
    if selected_books:
        selected_books = set(acronym_mapping[book].split('-')[1].upper() for book in selected_books)

    # Master list preserving exact discovery order: (phrase, reference, x_content)
    phrase_ref_pairs = []

    for filename in os.listdir(directory):
        if not filename.endswith(".usfm"):
            continue

        # Extract the book code from filename, e.g., "01-GEN.usfm" -> "GEN"
        book_code = filename.split('-')[1].split('.')[0].upper()

        # Skip file if not in selected_books
        if selected_books and book_code not in selected_books:
            continue

        with open(os.path.join(directory, filename), 'r',
                  encoding='utf-8') as f:
            content = f.read()

        # Split by chapter
        chapter_chunks = re.split(r'\\c (\d+)', content)
        # list: [intro_text, chap1, text1, chap2, text2, ...]
        for i in range(1, len(chapter_chunks), 2):
            chapter_num = chapter_chunks[i]
            chapter_text = chapter_chunks[i + 1]

            # Split by verse
            verse_chunks = re.split(r'\\v (\d+)', chapter_text)
            for j in range(1, len(verse_chunks), 2):
                verse_num = verse_chunks[j]
                verse_text = verse_chunks[j + 1]

                # Find aligned blocks in this verse
                aligned_blocks = re.findall(r"\\zaln-s.*?\\zaln-e", verse_text,
                                            re.DOTALL)

                # Track all matching phrases in discovery order here
                for block in aligned_blocks:
                    if strip_lemma:
                        stripped_block = strip_hebrew_vowels(block)
                    else:
                        stripped_block = block
                    # Match lemma and optional stem
                    if re.search(rf'x-lemma="{re.escape(word_lemma)}"', stripped_block) and \
                       (not stem_code or re.search(rf'x-morph="[^"]*V{re.escape(stem_code)}[^"]*"', stripped_block)):
                        x_content_match = re.search(r'x-content="(.*?)"',
                                                    block)
                        if not x_content_match:
                            continue
                        x_content = x_content_match.group(1)
                        words = re.findall(r'\\w (.*?)\|', block)
                        if words:
                            phrase = " ".join(words)
                            ref = f"{book_code} {chapter_num}:{verse_num}"
                            phrase_ref_pairs.append((phrase, ref, x_content))

    # Group by (reference, x_content), preserving order of discovery
    ref_content_to_phrases = defaultdict(list)
    for idx, (phrase, ref, x_content) in enumerate(phrase_ref_pairs):
        key = (ref, x_content)
        ref_content_to_phrases[key].append((idx, phrase))

    # Build merged phrases
    new_translations = []
    new_references = defaultdict(list)
    seen_keys = set()

    for _, ref, x_content in phrase_ref_pairs:
        key = (ref, x_content)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        indexed_phrases = ref_content_to_phrases[key]
        # Sort by discovery order
        phrases = [p for _, p in sorted(indexed_phrases, key=lambda x: x[0])]
        unique_phrases = list(
            dict.fromkeys(phrases))  # preserve order, remove duplicates
        merged_phrase = " ".join(unique_phrases)

        new_translations.append(merged_phrase)
        new_references[merged_phrase].append(ref)

    # Count phrases ignoring case
    counts = Counter()
    original_case_map = {}

    for phrase in new_translations:
        phrase_lower = phrase.lower()
        counts[phrase_lower] += 1
        # Remember first original casing for printing
        if phrase_lower not in original_case_map:
            original_case_map[phrase_lower] = phrase

    # Build book order dict from acronym_mapping
    book_order = {}
    for full_name, code in acronym_mapping.items():
        order_str, abbrev = code.split('-')
        book_order[abbrev] = int(order_str)

    def ref_sort_key(ref):
        # ref like "NEH 8:11"
        book, cv = ref.split()
        chapter_str, verse_str = cv.split(':')
        return (
            book_order.get(book, 999),  # unknown books go last
            int(chapter_str),
            int(verse_str))

    # Print results preserving original casing but sorted by count
    print('\n')
    for phrase_lower, count in counts.most_common():
        phrase_original = original_case_map[phrase_lower]
        print(
            f'<span style="color: #1E90FF;">-- {phrase_original}: {count}</span>'
        )

        # Collect all references of all matching-case variants
        refs = []
        for p, refs_list in new_references.items():
            if p.lower() == phrase_lower:
                refs.extend(refs_list)

        # Sort references by book, chapter, verse
        sorted_refs = sorted(refs, key=ref_sort_key)

        print("     " + ", ".join(sorted_refs))
    print('\n')


def main():
    user_input = input(
        'Do you want to refresh the translation directory? (yes/no): ').strip(
        ).lower()
    if user_input == 'yes':
        download_text_files()
        subprocess.run([sys.executable, "texts.py"])
    selected_books = None
    while True:
        user_input = input(
            "Enter input (chapter:verse word version [stem]) or (H:עבד version [stem]) or type 'quit' to exit: "
        ).strip()
        if user_input.lower() == "quit":
            break

        try:
            chapter, verse, word, version, stem = parse_user_input(user_input)
            if chapter == "H":  # handle H:עבד or H:עבד love
                glosses = search_usfm_files(word,
                                            version,
                                            stem,
                                            strip_lemma=True)
            else:
                word_text = find_word(chapter, verse, word, version)
                glosses = search_usfm_files(word_text, version, stem, selected_books=selected_books)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()


def run_web_search(user_input, file_path, selected_books=None):
    old_stdout = sys.stdout  # Save the current stdout
    sys.stdout = mystdout = io.StringIO()  # Redirect stdout to a string buffer

    try:
        chapter, verse, word, version, stem = parse_user_input(user_input)

        if chapter == "H":  # Hebrew root search
            search_usfm_files(word, version, stem, strip_lemma=True, selected_books=selected_books)
        else:  # Chapter/verse + word search
            word_text = find_word(chapter, verse, word, version, file_path)
            if not word_text:
                print(f"No lemma found for {chapter}:{verse} '{word}'")
            else:
                search_usfm_files(word_text, version, stem, selected_books=selected_books)

    except Exception as e:
        print(f"Error: {e}")

    output = mystdout.getvalue()  # Get the captured output
    sys.stdout = old_stdout  # Restore original stdout
    return output
