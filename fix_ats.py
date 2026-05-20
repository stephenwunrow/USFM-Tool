import re
import csv
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import os
import io
import unicodedata
import random
import string

def create_tsv_ult(book_name, version):
    def get_file_content(url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return ''

    # Mapping of book names to their respective acronyms
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

    def scrape_and_read_data(acronym, version):
        url = f"https://git.door43.org/unfoldingWord/en_{version}/raw/branch/master/{acronym}.usfm"
        file_content = get_file_content(url)
        soup = BeautifulSoup(file_content, 'html.parser')
        return soup

    def create_ult(soup, book_name):
        chapter = None
        verse = None
        verse_words = []
        verse_data = []
        text = soup.get_text()
        text = re.sub(r' \\v', r'\n\\v', text)
        pattern = re.compile(r'\\w ([^|]*?)\||([“‘{(]+)\\|\*([){}.,:;!?…‘’“”\—\- ]+)')
        for line in text.splitlines():
            if line.startswith('\\c '):
                if verse_words:
                    verse_data.append(f'{chapter}:{verse}\t{" ".join(verse_words)}')
                match = re.search(r'\\c\s+(\d+)', line)
                if match:
                    chapter = int(match.group(1))
                verse_words = []
            elif line.startswith('\\v '):
                if verse_words:
                    verse_data.append(f'{chapter}:{verse}\t{" ".join(verse_words)}')
                match = re.search(r'\\v\s+(\d+)', line)
                if match:
                    verse = int(match.group(1))
                verse_words = []
                remainder = line[match.end():].strip()
                matches = pattern.findall(remainder)
                for match in matches:
                    if match[0]:
                        verse_words.extend(word.strip() for word in match[0].split())
                    if match[1]:
                        verse_words.append(match[1])
                    if match[2]:
                        verse_words.append(match[2])
            else:
                matches = pattern.findall(line)
                for match in matches:
                    if match[0]:
                        verse_words.extend(word.strip() for word in match[0].split())
                    if match[1]:
                        verse_words.append(match[1])
                    if match[2]:
                        verse_words.append(match[2])
        if verse_words:
            verse_data.append(f'{chapter}:{verse}\t{" ".join(verse_words)}')
        return verse_data

    def cleanup_lines(verse_data):
        cleaned_data = []
        for line in verse_data:
            line = re.sub(r'( )([.,;:’”?!\—\-})]+)', r'\2', line)
            line = re.sub(r'([({“‘\—\-]+)( )', r'\1', line)
            line = re.sub(r'(\w[’]) (s)', r'\1\2', line)
            line = re.sub(r'  +', r' ', line)
            line = re.sub(r'(\.),[ .,]*([\n])', r'\1\2', line)
            line = re.sub(r'(\.),[ .,]*([\w])', r'\1 \2', line)
            line = re.sub(r'\.\.+', r'\.', line)
            line = re.sub(r'(\d,) (\d)', r'\1\2', line)
            line = line.strip()
            cleaned_data.append(line)
        return cleaned_data

    def setup_output(book_name, file_name):
        output_path = f'output/{book_name}'
        os.makedirs(output_path, exist_ok=True)
        if '.tsv' not in file_name:
            file_name += '.tsv'
        return f'{output_path}/{file_name}'

    def write_tsv(book_name, file_name, headers, data):
        output_file = setup_output(book_name, file_name)
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            file.write('\t'.join(headers) + '\n')
            for line in data:
                file.write(line + '\n')
        print(f'Data written to {output_file}')

    # === Main Execution ===
    book_list = []


    if book_name in acronym_mapping:
        book_list = [book_name]
    else:
        print("Invalid book name. Please enter a valid book name.")
        exit()

    for book_name in book_list:
        acronym = acronym_mapping[book_name]
        for version in ['ult', 'ust']:
            print(f"Processing {book_name} ({version})...")
            soup = scrape_and_read_data(acronym, version)
            verse_data = create_ult(soup, book_name)
            cleaned_data = cleanup_lines(verse_data)
            headers = ['Reference', 'Verse']
            file_name = f'{version}_book.tsv'
            write_tsv(book_name, file_name, headers, cleaned_data)

# Function to get the content of the file
def get_file_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return ''

def parse_verse_ref(verse_ref):
    # Function to split verse_ref into chapter and verse and return as tuple for sorting
    chapter, verse = verse_ref.split(':')
    return int(chapter), int(verse)

def setup_output(book_name, file_name):
    # Construct the output path
    output_path = f'output/{book_name}'

    # Ensure the directory exists
    os.makedirs(output_path, exist_ok=True)

    if '.tsv' not in file_name:
        file_name += '.tsv'

    # Path to the file you want to write
    return f'{output_path}/{file_name}'

def ensure_headers(tsv_io, headers):
    # Move to start and peek first line
    tsv_io.seek(0)
    first_line = tsv_io.readline()
    # Reset back to start for reading later
    tsv_io.seek(0)

    # Simple heuristic: if first cell starts with digit, assume no headers
    first_cell = first_line.split('\t')[0] if first_line else ''
    if first_cell and first_cell[0].isdigit():
        # No headers: prepend header line + newline + original content
        content = tsv_io.read()
        new_content = '\t'.join(headers) + '\n' + content
        return io.StringIO(new_content)
    else:
        # Already has headers or empty, just return original
        return tsv_io

def duplicate_fifth_column_as_eighth(file_obj):
    updated_rows = []

    file_obj.seek(0)  # ensure we're at the start
    reader = csv.reader(file_obj, delimiter='\t')
    headers = next(reader)
    rows = list(reader)

    # Check the first data row
    if rows and len(rows[0]) > 7:
        # Already has at least 8 columns, skip modification
        return
    # Add 'Snippet' as the new header
    headers.append("Snippet")

    # Process each row
    for row in rows:
        if len(row) >= 5:
            row.append(row[4])  # Copy fifth column to new eighth column
        else:
            row.append('')  # Fill with empty string if fifth column is missing
        updated_rows.append(row)

    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t', lineterminator='\n')
    writer.writerow(headers)
    writer.writerows(updated_rows)

    return output.getvalue()

# Function to read and parse TSV files
def read_ai_notes(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        headers = next(reader)  # Assuming the first row is headers
        for row in reader:
            data.append(row)
    return data, headers

def get_hbo(book_name, acronym):

    # URL of the file to download
    url = f"https://git.door43.org/unfoldingWord/hbo_uhb/raw/branch/master/{acronym}.usfm"

    # Function to get the content of the file
    def __get_file_content(url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return ''

    # Get the file content
    file_content = __get_file_content(url)

    # Process the file content
    soup = BeautifulSoup(file_content, 'html.parser')

    # Combine all lines into a single string
    combined_text = soup.get_text(separator='\n')

    return combined_text

def find_unique_numbers(combined_text):
    # Initialize variables
    chapter = None
    verse = None
    unique_numbers = []
    current_number = 1  # Initialize a counter for consecutive numbering

    # Split the combined text by "\\v" to get verse chunks
    chunks = combined_text.split('\\v ')

    for chunk in chunks:

        # Find verse in the chunk
        verse_match = re.search(r'(\d+)', chunk)
        if verse_match:
            verse = int(verse_match.group(1))

        # Find Hebrew words in the chunk
        hebrew_words = re.findall(r'\\w (.+?)\|', chunk)

        if chapter is not None and verse is not None:
            verse_ref = f'{chapter}:{verse}'

            # Initialize a dictionary to keep track of word occurrences within the same verse
            word_occurrences = defaultdict(int)

            for word in hebrew_words:
                word_occurrences[word] += 1
                occurrence_number = word_occurrences[word]

                unique_numbers.append((verse_ref, word, current_number, occurrence_number))
                current_number += 1  # Increment the counter

                    # Find chapter in the chunk
        chapter_match = re.search(r'\\c (\d+)', chunk)
        if chapter_match:
            chapter = int(chapter_match.group(1))

    return unique_numbers

def combine_entries(ult_dict):
    # Add an index column starting at 1
    indexed_entries = [[i + 1] + list(entry) for i, entry in enumerate(ult_dict)]

    # Dictionary to store combined entries
    combined_entries = []

    # Group entries by (verse_ref, gloss, chunk_number)
    from collections import defaultdict
    grouped_entries = defaultdict(list)

    for entry in indexed_entries:
        index, verse_ref, hebrew_word, number, gloss, chunk_number = entry

        key = (verse_ref, gloss, chunk_number)
        grouped_entries[key].append((index, verse_ref, hebrew_word, number, gloss, chunk_number))

    # Process each group
    for key, entries in grouped_entries.items():
        if len(entries) == 1:
            # If there's only one entry, add it directly
            combined_entries.append(entries[0])
        else:
            # Sort entries by index
            entries.sort(key=lambda x: x[0])

            # Check if hebrew_word is the same for all entries in the group
            same_hebrew_word = all(entry[2] == entries[0][2] for entry in entries)

            if same_hebrew_word:
                # If hebrew_word is the same, add each entry separately
                combined_entries.extend(entries)
            else:
                # If hebrew_word differs, combine hebrew_word and number entries
                combined_entry = list(entries[0])  # Start with the first entry
                combined_hebrew_words = [entries[0][2]]  # List to store combined hebrew_words
                combined_numbers = [str(entries[0][3])]  # List to store combined numbers

                for entry in entries[1:]:
                    combined_hebrew_words.append(entry[2])
                    combined_numbers.append(str(entry[3]))  # Convert number to string

                # Combine hebrew_words and numbers
                combined_entry[2] = ' '.join(combined_hebrew_words)
                combined_entry[3] = ' '.join(combined_numbers)

                combined_entries.append(tuple(combined_entry))  # Add as tuple for immutability

    # Sort combined_entries by the index column
    combined_entries.sort(key=lambda x: x[0])

    # Remove the index column
    final_entries = [entry[1:] for entry in combined_entries]

    return final_entries

def construct_ult_dict(version, acronym, unique_numbers):
    # URL of the file to download
    url = f"https://git.door43.org/unfoldingWord/en_{version}/raw/branch/master/{acronym}.usfm"

    # Get the file content
    file_content = get_file_content(url)

    # Process the file content
    soup = BeautifulSoup(file_content, 'html.parser')

    # Combine all lines into a single string
    combined_text = soup.get_text(separator='\n')

    ult_dict = []
    text_chunks = {}
    chapter = None
    verse = None

    # Split the combined text by "\\v" to get verse chunks
    chunks = combined_text.split('\\v')

    for chunk in chunks:

        # Find verse in the chunk
        verse_match = re.search(r'(\d+)', chunk)
        if verse_match:
            verse = int(verse_match.group(1))

        if chapter is not None and verse is not None:
            verse_ref = f'{chapter}:{verse}'
            text_chunks[verse_ref] = chunk

        # Find chapter in the chunk
        chapter_match = re.search(r'\\c (\d+)', chunk)
        if chapter_match:
            chapter = int(chapter_match.group(1))

    for verse_ref, hebrew_word, number, occurrence_number in unique_numbers:
        if verse_ref in text_chunks:

            chunk = text_chunks[verse_ref]

            lexeme_chunks = chunk.split('-e\\*')

            chunk_number = 0  # Initialize a counter for consecutive numbering

            for lexeme_chunk in lexeme_chunks:

                chunk_number += 1

                escaped_hebrew_word = re.escape(hebrew_word)
                hebrew_pattern = re.compile(rf'zaln-s.+?x-occurrence="{occurrence_number}" x-occurrences="\d" x-content="{escaped_hebrew_word}".+?\\w\*\\zaln', re.DOTALL)
                matches = hebrew_pattern.findall(lexeme_chunk)

                for match in matches:

                    # Find instances of certain English words within the match
                    gloss_pattern = re.compile(r'\\w \b(.+?)\b\|')
                    gloss_matches = gloss_pattern.findall(match)

                    for gloss in gloss_matches:
                        ult_dict.append([verse_ref, hebrew_word, number, gloss, chunk_number])

    ult_dict_combined = combine_entries(ult_dict)

    # Sort ult_dict_combined by chapter, verse, and then by chunk_number
    ult_dict_sorted = sorted(ult_dict_combined, key=lambda x: (parse_verse_ref(x[0]), x[4]))
    return ult_dict_sorted

def combine_possessives(ult_dict):
    ult_dict_combined = []
    temp_dict = {}

    i = 0
    while i < len(ult_dict):
        entry = list(ult_dict[i])  # Convert tuple to list
        reference = entry[0]
        hebrew_word = entry[1]
        unique_number = entry[2]
        gloss = entry[3]
        chunk_number = entry[4]

        if gloss == 's':
            if i > 0:
                previous_entry = list(ult_dict[i - 1])  # Convert tuple to list
                prev_reference = previous_entry[0]
                prev_hebrew_word = previous_entry[1]
                prev_unique_number = previous_entry[2]
                prev_gloss = previous_entry[3]
                prev_chunk_number = previous_entry[4]

                if (reference == prev_reference and
                    chunk_number == prev_chunk_number and
                    unique_number == prev_unique_number and
                    hebrew_word == prev_hebrew_word):

                    # Add '’s' to the gloss of the previous entry
                    previous_entry[3] = prev_gloss + '’s'
                    # Update the previous entry in ult_dict_combined
                    ult_dict_combined[-1] = previous_entry
                    # Skip the current entry
                    i += 1
                    continue

        ult_dict_combined.append(entry)
        i += 1

    return ult_dict_combined

def find_sequence(ult_dict_combined, input_file):
    data, headers = read_ai_notes(input_file)
    snippet_data = []

    # Step 1: Create a dictionary with verse_ref as key and concatenated string of gloss words as value
    gloss_dict = {}
    for entry in ult_dict_combined:
        verse_ref = entry[0]
        gloss_word = entry[3]
        chunk_number = entry[4]

        if verse_ref not in gloss_dict:
            gloss_dict[verse_ref] = []

        # Append a tuple of (gloss_word, chunk_number) to the list
        gloss_dict[verse_ref].append((gloss_word, chunk_number))

    # Convert the list of tuples to a concatenated string for each verse_ref
    final_gloss_dict = {verse_ref: ' '.join([f'{gloss_word} {chunk_number}' for gloss_word, chunk_number in gloss_words]) for verse_ref, gloss_words in gloss_dict.items()}

    # Step 2: Find sequences
    for row in data:
        if len(row) < 8 or not row[7]:
            continue
        verse_ref = row[0]
        phrase = row[7].strip()
        lower_phrase = phrase.lower()
        mod_phrase = re.sub(r'[.,]’', r'', lower_phrase)
        mod_phrase = re.sub('-', ' ', mod_phrase)
        mod_phrase = re.sub(r'(\d),(\d)', r'\1 \2', mod_phrase)
        mod_phrase = re.sub(r'[{}.,:;”‘“!?—*]', r'', mod_phrase)
        mod_phrase = re.sub('s’', 's', mod_phrase)
        mod_phrase = re.escape(mod_phrase)
        mod_phrase = re.sub(r'[\\ ]*…[\\ ]*', ' )(.+?)(', mod_phrase)
        mod_phrase = re.sub(r'\\\&', ')(.+?)(', mod_phrase)
        mod_phrase = re.sub(r'(\w+)', r'\\b\1\\b', mod_phrase)
        search_phrase = re.sub(r' ', r' \\d+ ', mod_phrase)
        search_phrase = search_phrase + ' \\d+'
        search_phrase = '(' + search_phrase + ')'

        chunk_numbers = []
        numbers = []

        if verse_ref in final_gloss_dict:
            gloss_text = final_gloss_dict[verse_ref].lower()
            matches = list(re.finditer(search_phrase, gloss_text))[:1]
            if matches:
                for match in matches:
                    if match.lastindex and match.lastindex == 3:
                        match = match.group(1) + match.group(3)
                    elif match.lastindex and match.lastindex == 5:
                        match = match.group(1) + match.group(3) + match.group(5)
                    elif match.lastindex and match.lastindex >= 7:
                        match = match.group(1) + match.group(3) + match.group(5) + match.group(7)
                    else:
                        match = match.group(0)
                    pairs = re.findall(r'(\w+) (\d+)', match)
                    if pairs:
                        for gloss_word, chunk_number in pairs:
                            for entry in ult_dict_combined:
                                if entry[0] == verse_ref and entry[3].lower() == gloss_word.lower() and entry[4] == int(chunk_number):
                                    entry_2_str = str(entry[2])
                                    if ' ' in entry_2_str:
                                        for num in entry_2_str.split():
                                            numbers.append(int(num))
                                    else:
                                        numbers.append(int(entry[2]))
                                    chunk_numbers.append(int(entry[4]))
            else:
                search_phrase = re.sub(r'(\\d\+) ', r'\1.*?', search_phrase)
                matches = list(re.finditer(search_phrase, gloss_text))[:1]
                for match in matches:
                    if match.lastindex and match.lastindex >= 2:
                        match = match.group(1) + match.group(3)
                    else:
                        match = match.group(0)
                    pairs = re.findall(r'(\w+) (\d+)', match)
                    if pairs:
                        for gloss_word, chunk_number in pairs:
                            for entry in ult_dict_combined:
                                if entry[0] == verse_ref and entry[3].lower() == gloss_word.lower() and entry[4] == int(chunk_number):
                                    entry_2_str = str(entry[2])
                                    if ' ' in entry_2_str:
                                        for num in entry_2_str.split():
                                            numbers.append(int(num))
                                    else:
                                        numbers.append(int(entry[2]))
                                    chunk_numbers.append(int(entry[4]))

            # Sort numbers and chunk_numbers numerically
            numbers.sort()
            chunk_numbers.sort()

            snippet_data.append([verse_ref, phrase, numbers, chunk_numbers])
    return snippet_data

def remove_split_snippets(snippet_data, ult_dict_combined):
    # Build dictionaries for quick lookup, keyed by verse
    number_to_chunks_by_verse = {}
    chunk_to_numbers_by_verse = {}

    for ult_row in ult_dict_combined:
        verse = ult_row[0]
        # Split numbers like "8203 8204" into separate ints
        num_parts = [int(p) for p in str(ult_row[2]).split() if p.isdigit()]
        chunk_num = int(ult_row[4])

        number_to_chunks_by_verse.setdefault(verse, {})
        chunk_to_numbers_by_verse.setdefault(verse, {})

        for num in num_parts:
            number_to_chunks_by_verse[verse].setdefault(num, set()).add(chunk_num)
        chunk_to_numbers_by_verse[verse].setdefault(chunk_num, set()).update(num_parts)

    processed_snippet_data = []

    for row in snippet_data:
        verse_ref = row[0]
        phrase = row[1]

        # Handle split numbers in snippet_data
        numbers = []
        for n in row[2]:
            for part in str(n).split():
                if part.isdigit():
                    numbers.append(int(part))
        numbers = sorted(set(numbers))

        chunk_numbers = sorted(set(int(cn) for cn in row[3]))

        verse_num_to_chunks = number_to_chunks_by_verse.get(verse_ref, {})
        verse_chunk_to_numbers = chunk_to_numbers_by_verse.get(verse_ref, {})

        # Step 2: expand numbers and chunk_numbers
        added_new = False  # track if step 2 adds anything
        for number in list(numbers):  # copy so we can modify numbers
            if number in verse_num_to_chunks:
                for cn in verse_num_to_chunks[number]:
                    if cn not in chunk_numbers:
                        chunk_numbers.append(cn)
                        numbers.extend(verse_chunk_to_numbers.get(cn, []))
                        added_new = True  # mark that we added new chunks/numbers

        # Step 3: fill gaps only if step 2 added something
        if added_new:
            chunk_numbers = sorted(set(chunk_numbers))
            filled_chunk_numbers = []
            for i in range(len(chunk_numbers) - 1):
                filled_chunk_numbers.append(chunk_numbers[i])
                next_num = chunk_numbers[i + 1]
                if next_num != chunk_numbers[i] + 1:
                    for gap in range(chunk_numbers[i] + 1, next_num):
                        filled_chunk_numbers.append(gap)
                        numbers.extend(verse_chunk_to_numbers.get(gap, []))
            if chunk_numbers:
                filled_chunk_numbers.append(chunk_numbers[-1])

            chunk_numbers = sorted(set(filled_chunk_numbers))

        numbers = sorted(set(numbers))

        processed_snippet_data.append([verse_ref, phrase, numbers, chunk_numbers])

    return processed_snippet_data


def write_origl_and_snippet(snippet_data, ult_dict_combined, unique_numbers):
    processed_data = []

    # Step 1: Include each unique number only once within brackets
    for row in snippet_data:
        verse_ref = row[0]
        phrase = row[1]
        numbers = sorted(set(row[2]))  # Remove duplicates
        chunk_numbers = sorted(set(row[3]))  # Remove duplicates

        # Step 2: Replace "number" with the corresponding Hebrew word
        hebrew_words = []
        for num in numbers:
            for entry in unique_numbers:
                if entry[2] == num:
                    hebrew_words.append(entry[1])
                    break

        # Step 3: Replace "chunk_number" with the corresponding English words
        # Group English words by chunk number
        chunk_to_english = {}
        for entry in ult_dict_combined:
            entry_verse, chunk_num, eng_word = entry[0], int(entry[4]), entry[3]
            if entry_verse == verse_ref and chunk_num in chunk_numbers:
                chunk_to_english.setdefault(chunk_num, []).append(eng_word)

        # Join hebrew_words with '&' where numbers are not consecutive
        hebrew_phrase = ''
        for i, word in enumerate(hebrew_words):
            if i > 0 and numbers[i] != numbers[i - 1] + 1:
                hebrew_phrase += f' & {word}'
            else:
                hebrew_phrase += f' {word}'

        hebrew_phrase = hebrew_phrase.strip()

        # Build a lookup set of all (verse_ref, chunk_num) in ult_dict_combined
        ult_chunks = {
            (entry[0], int(entry[4]))
            for entry in ult_dict_combined
        }

        # Join words, adding '…' only if skipped chunk(s) actually exist in ult_dict_combined
        english_phrase = ''
        for i, cn in enumerate(chunk_numbers):
            words = chunk_to_english.get(cn, [])
            group = ' '.join(words)

            if i > 0 and cn != chunk_numbers[i - 1] + 1:
                prev_cn = chunk_numbers[i - 1]
                # Check if any missing chunk between prev_cn and cn exists in ult_dict_combined
                missing_exists = any(
                    (verse_ref, missing_cn) in ult_chunks
                    for missing_cn in range(prev_cn + 1, cn)
                )
                if missing_exists:
                    english_phrase += f' … {group}'
                else:
                    english_phrase += f' {group}'
            else:
                english_phrase += f' {group}'


        english_phrase = english_phrase.strip()

        # Append the processed row to processed_data
        processed_data.append([verse_ref, phrase, hebrew_phrase, english_phrase])

    return processed_data

def write_output(book_name, file, headers, data, fieldnames=None):

    output_file = setup_output(book_name, file)

    # Write results to a TSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        if fieldnames:
            writer = csv.DictWriter(file, delimiter='\t', fieldnames=fieldnames)
            writer.writeheader()
        else:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(headers)  # Column headers
        for line in data:
            writer.writerow(line)

    print(f"Data has been written to {output_file}")

def add_punctuation(book_name, origl_and_snippet):
    book_file = f'output/{book_name}/ult_book.tsv'
    data, headers = read_ai_notes(book_file)
    data_str = ' '.join([' '.join(row) for row in data])

    for row in origl_and_snippet:
        verse_ref = row[0]
        phrase = row[1]
        hebrew_words = row[2]
        english_words = row[3]

        # Create a regex pattern to match the phrase with punctuation
        search_phrase = re.sub(r' ', '[ .,;’”“‘!?:—]+', english_words)

        # Find all matches of the search phrase in the data string
        matches = re.findall(search_phrase, data_str)
        if matches:
            # Update english_words with the first match found
            row[3] = matches[0]

    return origl_and_snippet

def process_ai_notes(input_file, origl_and_snippet):
    ai_notes, headers = read_ai_notes(input_file)

    unique_origl_and_snippet = []
    seen_pairs = set()

    for row in origl_and_snippet:
        reference = row[0]
        snippet = row[1]
        pair = (reference, snippet)
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_origl_and_snippet.append(row)

    # Iterate over origl_and_snippet
    for row in unique_origl_and_snippet:
        reference = row[0]
        snippet = row[1]
        hebrew_words = row[2]
        context = row[3]

        # Find corresponding line in ai_notes using reference and snippet
        for ai_row in ai_notes:
            if not re.match(r'\d', ai_row[0]):
                ai_notes.remove(ai_row)
            if ai_row[0] == reference and ai_row[7].strip() == snippet.strip():
                # Replace "Quote" (row 5 in ai_notes) with english_words (row 3 in origl_and_snippet)
                if hebrew_words.strip() != '':
                    ai_row[4] = hebrew_words
                if re.search(r'Alternate translation: \[[^…]*…[^…]*\]', ai_row[6]):
                    escaped_snippet = snippet
                    mod_snippet = re.sub('…', '(.+?)', escaped_snippet)
                    matches = list(re.finditer(mod_snippet, context))
                    if matches:
                        match = matches[0]

                        if match.lastindex and match.lastindex >= 1:
                            mod_match = match.group(1).strip('[] ')
                            ai_row[6] = re.sub(
                                r'(\[[^]]*)…([^]]*\])',
                                rf'\1{mod_match}\2',
                                ai_row[6]
                            )
                            snippet = re.sub('…', mod_match, snippet)

                # Locate snippet in context and get pre-words and post-words
                snippet = re.sub(r'[\{\}]', '', snippet)
                snippet = re.sub('-', ' ', snippet)
                snippet_index = context.lower().find(snippet.lower())
                if snippet_index != -1:
                    pre_words = context[:snippet_index].strip('] [\'')
                    post_words = context[snippet_index + len(snippet):].strip('] [\'')


                    quote_texts = re.findall(r'Alternate translation: ((?:\[[^\[\]]+\](?: or )?)+)', ai_row[6])

                    if quote_texts:
                        alternates = re.findall(r'\[([^\[\]]+)\]', quote_texts[0])
                    else:
                        alternates = []

                    # ✅ Wrap each new alternate in brackets and strip surrounding whitespace properly
                    new_alternates = [f"[{(pre_words + ' ' + alt + ' ' + post_words).strip()}]" for alt in alternates]
                    new_AT = ' or '.join(new_alternates)

                    # Typographic apostrophe replacement
                    new_AT = re.sub(r'\'s', r'’s', new_AT)
                    new_AT = re.sub(r'(\ba\b)( \b[aeiou])', r'\1n\2', new_AT)


                    # ✅ Replace the whole alternate translation block
                    ai_row[6] = re.sub(r'(Alternate translation: )((?:\[[^\[\]]+\](?: or )?)+)', rf'\1{new_AT}', ai_row[6])
                    ai_row[6] = re.sub(r'(\[[^\]\[]*?)(\b\w+\b)\s+\2\b([^\]\[]*?)(\])', r'\1\2\3\4', ai_row[6], flags=re.IGNORECASE)


                if snippet_index == -1:
                    if re.search(r'Alternate translation: \[[^…]*\]', ai_row[6]):
                        search_snippet = re.sub(r' ', '(.*?)', snippet)
                        combined = []
                        matches = list(re.finditer(search_snippet, context))
                        if matches:
                            match = matches[0]
                            groups = match.groups()
                            combined = ' '.join(groups)
                            combined = combined.strip()
                            if combined:
                                ai_row[6] = ai_row[6] + f' MISSING: {combined}'
                        else:
                            if 'Alternate translation' in ai_row[6] and not ai_row[4].startswith('QUOTE_NOT_FOUND: '):
                                ai_row[4] = 'QUOTE_NOT_FOUND: ' + ai_row[4]
                    else:
                        if 'Alternate translation' in ai_row[6] and not ai_row[4].startswith('QUOTE_NOT_FOUND: '):
                            ai_row[4] = 'QUOTE_NOT_FOUND: ' + ai_row[4]

    return ai_notes

def generate_unique_id(existing_ids):
    """Generate a unique 4-character ID starting with a lowercase letter."""
    while True:
        new_id = random.choice(string.ascii_lowercase) + ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=3)
        )
        if new_id not in existing_ids:
            return new_id

def scrape_and_update_ids(book_name, tsv_url, ai_notes):
    # Step 1: Scrape TSV from website
    response = requests.get(tsv_url)
    response.raise_for_status()
    scraped_lines = response.text.strip().splitlines()
    scraped_reader = csv.reader(scraped_lines, delimiter="\t")

    scraped_ids = set()
    for row in scraped_reader:
        if len(row) >= 2:
            scraped_ids.add(row[1])  # second column

    # Step 2: Check ai_notes for duplicates
    seen_ids = set(scraped_ids)  # start with scraped IDs
    updated_ai_notes = []

    for row in ai_notes:
        if len(row) >= 2:
            current_id = row[1]
            if current_id in seen_ids:
                # Duplicate found, make a new one
                new_id = generate_unique_id(seen_ids)
                row[1] = new_id
                seen_ids.add(new_id)
            else:
                seen_ids.add(current_id)
        updated_ai_notes.append(row)

    return updated_ai_notes


def format_tsv_output(data):
    # data is a list of lists, e.g. your ai_notes list
    lines = []
    for row in data:
        # join each cell with a tab
        line = '\t'.join(str(cell) for cell in row)
        lines.append(line)
    return '\n'.join(lines)

def fix_ats(book_name, tsv_content):

    # Mapping of book names to their respective acronyms
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
        "Song of Solomon": "22-SNG",
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

    if book_name in acronym_mapping:
        acronym = acronym_mapping[book_name]
    version = 'ult'

    headers = ['Reference', 'ID', 'Tags', 'SupportReference', 'Quote', 'Occurrence', 'Note']
    tsv_data = io.StringIO(tsv_content)

    tsv_data = ensure_headers(tsv_data, headers)

    create_tsv_ult(book_name, version)

    ai_notes_str = duplicate_fifth_column_as_eighth(tsv_data)
    reader = csv.reader(io.StringIO(ai_notes_str), delimiter='\t')
    data = list(reader)
    old_headers = data[0]
    rows = data[1:]
    headers = ['Reference', 'ID', 'Tags', 'SupportReference', 'Quote', 'Occurrence', 'Note', 'Snippet']
    file = 'ai_notes.tsv'
    write_output(book_name, file, headers, rows)

    input_file = f'output/{book_name}/ai_notes.tsv'

    combined_text = get_hbo(book_name, acronym)
    unique_numbers = find_unique_numbers(combined_text)

    data = unique_numbers
    headers = ['Reference', 'Hebrew word', 'Unique number', 'Occurrence number']
    file = '1_unique_numbers.tsv'
    write_output(book_name, file, headers, data)

    ult_dict = construct_ult_dict(version, acronym, unique_numbers)
    ult_dict_combined = combine_possessives(ult_dict)

    data = ult_dict_combined
    headers = ['Reference', 'Hebrew word', 'Unique number', 'Gloss', 'Chunk number']
    file = '2_ult_dict.tsv'
    write_output(book_name, file, headers, data)

    snippet_data = find_sequence(ult_dict_combined, input_file)
    processed_snippet_data = remove_split_snippets(snippet_data, ult_dict_combined)

    data = processed_snippet_data
    headers = ['Reference', 'Phrase', 'Unique numbers', 'Chunk numbers']
    file = '3_snippet_data.tsv'
    write_output(book_name, file, headers, data)

    origl_and_snippet = write_origl_and_snippet(processed_snippet_data, ult_dict_combined, unique_numbers)

    origl_and_snippet = add_punctuation(book_name, origl_and_snippet)

    data = origl_and_snippet
    headers = ['Reference', 'Snippet', 'Hebrew phrase', 'English phrase']
    file = '4_origl_and_snippet.tsv'
    write_output(book_name, file, headers, data)

    ai_notes = process_ai_notes(input_file, origl_and_snippet)
    number, tn_acronym = acronym.split('-')
    tsv_url = f'https://git.door43.org/unfoldingWord/en_tn/raw/branch/master/tn_{tn_acronym}.tsv'
    updated_ai_notes = scrape_and_update_ids(book_name, tsv_url, ai_notes)

    data = updated_ai_notes
    for row in data:
        if len(row) >= 8:
            del row[7]
        if len(row) == 7:
            row[6] = row[6].strip()

    headers = ['Reference', 'ID', 'Tags', 'SupportReference', 'Quote', 'Occurrence', 'Note']
    file = 'final_notes.tsv'
    write_output(book_name, file, headers, data)

    formatted_data = format_tsv_output(data)

    return formatted_data


if __name__ == "__main__":
    fix_ats()