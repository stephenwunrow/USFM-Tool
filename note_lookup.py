import os
import re
import requests
import shlex
import html

# Mapping of book names to their respective acronyms
acronym_mapping = {
    "Genesis": "01-GEN", "Exodus": "02-EXO", "Leviticus": "03-LEV", "Numbers": "04-NUM",
    "Deuteronomy": "05-DEU", "Joshua": "06-JOS", "Judges": "07-JDG", "Ruth": "08-RUT",
    "1 Samuel": "09-1SA", "2 Samuel": "10-2SA", "1 Kings": "11-1KI", "2 Kings": "12-2KI",
    "1 Chronicles": "13-1CH", "2 Chronicles": "14-2CH", "Ezra": "15-EZR", "Nehemiah": "16-NEH",
    "Esther": "17-EST", "Job": "18-JOB", "Psalms": "19-PSA", "Proverbs": "20-PRO",
    "Ecclesiastes": "21-ECC", "Song": "22-SNG", "Isaiah": "23-ISA", "Jeremiah": "24-JER",
    "Lamentations": "25-LAM", "Ezekiel": "26-EZK", "Daniel": "27-DAN", "Hosea": "28-HOS",
    "Joel": "29-JOL", "Amos": "30-AMO", "Obadiah": "31-OBA", "Jonah": "32-JON",
    "Micah": "33-MIC", "Nahum": "34-NAM", "Habakkuk": "35-HAB", "Zephaniah": "36-ZEP",
    "Haggai": "37-HAG", "Zechariah": "38-ZEC", "Malachi": "39-MAL", "Matthew": "41-MAT",
    "Mark": "42-MRK", "Luke": "43-LUK", "John": "44-JHN", "Acts": "45-ACT", "Romans": "46-ROM",
    "1 Corinthians": "47-1CO", "2 Corinthians": "48-2CO", "Galatians": "49-GAL",
    "Ephesians": "50-EPH", "Philippians": "51-PHP", "Colossians": "52-COL",
    "1 Thessalonians": "53-1TH", "2 Thessalonians": "54-2TH", "1 Timothy": "55-1TI",
    "2 Timothy": "56-2TI", "Titus": "57-TIT", "Philemon": "58-PHM", "Hebrews": "59-HEB",
    "James": "60-JAS", "1 Peter": "61-1PE", "2 Peter": "62-2PE", "1 John": "63-1JN",
    "2 John": "64-2JN", "3 John": "65-3JN", "Jude": "66-JUD", "Revelation": "67-REV"
}

code_to_name = {v.split("-")[1]: k for k, v in acronym_mapping.items()}

def download_notes_files(logger=print):
    os.makedirs("Master_Notes", exist_ok=True)
    for book_code in acronym_mapping.values():
        code = book_code.split("-")[1]
        link = f'https://git.door43.org/unfoldingWord/en_tn/raw/branch/master/tn_{code}.tsv'
        try:
            response = requests.get(link)
            response.raise_for_status()
            with open(f"Master_Notes/tn_{code}.tsv", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger(f"Downloaded tn_{code}.tsv")
        except requests.RequestException as e:
            logger(f"Failed to download tn_{code}.tsv: {e}")


def normalize_quotes(s):
    replacements = {
        "“": '"',
        "”": '"',
        "‘": '"',
        "’": '"'
    }
    for smart, straight in replacements.items():
        s = s.replace(smart, straight)
    return s

def search_notes(user_input, use_regex=False):

    user_input = normalize_quotes(user_input)

    parts = shlex.split(user_input.strip())
    result_lines = []

    if len(parts) == 3:
        note_type, keyword, book_name = parts

        book_code = acronym_mapping.get(book_name)
        if not book_code:
            return f"Book '{book_name}' not recognized."

        code = book_code.split("-")[1]
        path = f"Master_Notes/tn_{code}.tsv"
        if not os.path.exists(path):
            return f"File {path} not found."

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                matched = False
                if note_type.lower() == "none":
                    if re.fullmatch(r"\d+:\d+", keyword):
                        matched = re.search(rf'^{re.escape(keyword)}\t', line, re.IGNORECASE)
                    else:
                        if use_regex:
                            matched = re.search(keyword, line, re.IGNORECASE)
                        else:
                            matched = re.search(re.escape(keyword), line, re.IGNORECASE)
                else:
                    if use_regex:
                        matched = re.search(rf'\t[^\t]*-{note_type}\t[^\t]*\t[^\t]*\t[^\t\n]*{keyword}[^\t\n]*', line, re.IGNORECASE)
                    else:
                        matched = re.search(rf'\t[^\t]*-{note_type}\t[^\t]*\t[^\t]*\t[^\t\n]*{re.escape(keyword)}[^\t\n]*', line, re.IGNORECASE)

                if matched:
                    parts = line.rstrip().rsplit("\t", 1)
                    if len(parts) == 2:
                        prefix, note = parts
                        if '\\n' in note and keyword.strip().lower() != 'intro':
                            new_chunks = []
                            note = re.sub(r'(###.+?)\\n\\n', r'\1~', note)
                            chunks = note.split('\\n')
                            for chunk in chunks:
                                if use_regex:
                                    match = re.search(keyword, chunk, re.IGNORECASE)
                                    if match:
                                        new_chunks.append(chunk)
                                    else:
                                        new_chunks.append('…')
                                else:
                                    match = re.search(re.escape(keyword), chunk, re.IGNORECASE)
                                    if match:
                                        new_chunks.append(chunk)
                                    else:
                                        new_chunks.append('…')
                            note = '\n'.join(new_chunks)
                            note = re.sub(r'~', r'\n\n', note)
                            note = re.sub(r'(…\n)+', r'\n…\n', note)
                        if use_regex:
                            highlighted = re.sub(rf'({keyword})', r'<mark>\1</mark>', note, flags=re.IGNORECASE)
                        else:
                            highlighted = re.sub(rf'({re.escape(keyword)})', r'<mark>\1</mark>', note, flags=re.IGNORECASE)
                        result_lines.append(f"<b>{prefix}</b><br>{highlighted}<br><br>")
                    else:
                        result_lines.append(f"{line.strip()}<br>")

    elif len(parts) == 2:
        note_type, keyword = parts

        for book_name, book_code in acronym_mapping.items():
            code = book_code.split("-")[1]
            path = f"Master_Notes/tn_{code}.tsv"
            if not os.path.exists(path):
                continue

            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    matched = False
                    if note_type.lower() == "none":
                        if re.fullmatch(r"\d+:\d+", keyword):
                            matched = re.search(rf'^{re.escape(keyword)}\t', line, re.IGNORECASE)
                        else:
                            if use_regex:
                                matched = re.search(keyword, line, re.IGNORECASE)
                            else:
                                matched = re.search(re.escape(keyword), line, re.IGNORECASE)
                    else:
                        if use_regex:
                            matched = re.search(rf'\t[^\t]*-{note_type}\t[^\t]*\t[^\t]*\t[^\t\n]*{keyword}[^\t\n]*', line, re.IGNORECASE)
                        else:
                            matched = re.search(rf'\t[^\t]*-{note_type}\t[^\t]*\t[^\t]*\t[^\t\n]*{re.escape(keyword)}[^\t\n]*', line, re.IGNORECASE)

                    if matched:
                        parts = line.rstrip().rsplit("\t", 1)
                        if len(parts) == 2:
                            prefix, note = parts
                            if '\\n' in note and keyword.strip().lower() != 'intro':
                                new_chunks = []
                                note = re.sub(r'(###.+?)\\n\\n', r'\1~', note)
                                chunks = note.split('\\n')
                                for chunk in chunks:
                                    if use_regex:
                                        match = re.search(keyword, chunk, re.IGNORECASE)
                                        if match:
                                            new_chunks.append(chunk)
                                        else:
                                            new_chunks.append('…')
                                    else:
                                        match = re.search(re.escape(keyword), chunk, re.IGNORECASE)
                                        if match:
                                            new_chunks.append(chunk)
                                        else:
                                            new_chunks.append('…')
                                note = '\n'.join(new_chunks)
                                note = re.sub(r'~', r'\n\n', note)
                                note = re.sub(r'(…\n)+', r'\n…\n', note)
                            if use_regex:
                                highlighted = re.sub(rf'({keyword})', r'<mark>\1</mark>', note, flags=re.IGNORECASE)
                            else:
                                highlighted = re.sub(rf'({re.escape(keyword)})', r'<mark>\1</mark>', note, flags=re.IGNORECASE)
                            result_lines.append(f"<b>{book_name} {prefix}</b><br>{highlighted}<br><br>")
                        else:
                            result_lines.append(f"{line.strip()}<br>")
    else:
        return "Invalid input format. Use: <note_type> <keyword> [book]"

    return "\n".join(result_lines) if result_lines else "No results found."


def main():
    user_input = input('Do you want to refresh the notes directory? (yes/no): ').strip().lower()
    if user_input == 'yes':
        download_notes_files()
    while True:
        user_input = input("Enter input (note_type [or 'none'] keyword [book]) or type 'quit' to exit: ").strip()
        if user_input.lower() == "quit":
            break
        try:
            search_notes(user_input)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
