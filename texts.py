import os
import re

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

def read_usfm_file(acronym, version):
    """Read USFM file from the Data folder"""
    file_path = f"Data/en_{version.lower()}/{acronym}.usfm"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File not found at {file_path}")
        return ""

def create_ult(usfm_text, book_name):
    chapter = None
    verse = None
    verse_words = []
    verse_data = []
    text = usfm_text
    text = re.sub(r' \\v', r'\n\\v', text)
    pattern = re.compile(r'w ([^|]*?)\||([“‘{(]+)\\|\*([){}.,:;!?…‘’“”\—\- ]+)')
    for line in text.splitlines():
        if line.startswith('\\c '):
            if verse_words:
                verse_data.append(f'{chapter}:{verse}\t{" ".join(verse_words)}')
            match = re.search(r'\\c\s+(\d+)', line)
            if match:
                chapter = int(match.group(1))
            verse_words = []
            verse = "0"
        elif line.startswith('\\v '):
            if verse_words:
                verse_data.append(f'{chapter}:{verse}\t{" ".join(verse_words)}')
            match = re.search(r'\\v\s+(\d+-*\d*)', line)
            if match:
                verse = match.group(1)
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

def verse_bridges(verse_data):
    bridge_data = []
    for line in verse_data:
        matches = re.search(r'^(\d+):(\d+)-(\d+)', line)
        verse_text = line.split('\t', 1)[1]
        if matches:
            chapter = int(matches.group(1))
            first_verse = int(matches.group(2))
            last_verse = int(matches.group(3))
            verses = list(range(first_verse, last_verse + 1))
            for verse in verses:
                new_line = f'{chapter}:{verse}\t[vbridge {chapter}:{first_verse}-{last_verse}] {verse_text}'
                bridge_data.append(new_line)
        else:
            bridge_data.append(line)
    return bridge_data
            


def setup_output(book_name, file_name):
    output_path = 'Data/Texts'
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

def create_accordance_bibles():
    output_dir = 'Data/Texts'
    
    # Create a reverse lookup for acronym → book name
    reverse_mapping = {v: k for k, v in acronym_mapping.items()}
    
    for version in ['ULT', 'UST']:
        combined_lines = []
        for acronym in acronym_mapping.values():
            book_name = reverse_mapping[acronym]
            file_path = os.path.join(output_dir, f'master_{version}_{book_name}.tsv')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    next(f)  # skip header
                    book_name = re.sub(r' ', r'', book_name)
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split('\t', 1)
                        if len(parts) == 2:
                            ref, verse_text = parts
                            new_line = f"{book_name} {ref} {verse_text}"
                            combined_lines.append(new_line)

        output_file = os.path.join(output_dir, f'{version}_for_accordance.txt')
        with open(output_file, 'w', encoding='mac_roman', errors='ignore') as f:
            for line in combined_lines:
                f.write(line + '\n')
        print(f'Created {output_file}')

def main():
    book_list = list(acronym_mapping.keys())

    for book_name in book_list:
        acronym = acronym_mapping[book_name]
        for version in ['ULT', 'UST']:
            print(f"Processing {book_name} ({version})...")
            usfm_text = read_usfm_file(acronym, version)
            if usfm_text:
                verse_data = create_ult(usfm_text, book_name)
                cleaned_data = cleanup_lines(verse_data)
                bridge_data = verse_bridges(cleaned_data)
                headers = ['Reference', 'Verse']
                file_name = f'master_{version}_{book_name}.tsv'
                write_tsv(book_name, file_name, headers, bridge_data)

    print("Creating Bibles for Accordance...")
    create_accordance_bibles()

if __name__ == "__main__":
    main()