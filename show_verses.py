import csv
import os
import re

DATA_DIR = "Data/Texts"

# Main book names
BOOK_NAMES = [
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation"
]

# Common abbreviations
BOOK_ABBREVIATIONS = {
    "Gen": "Genesis",
    "Exod": "Exodus",
    "Lev": "Leviticus",
    "Num": "Numbers",
    "Deut": "Deuteronomy",
    "Josh": "Joshua",
    "Judg": "Judges",
    "Ruth": "Ruth",
    "1 Sam": "1 Samuel",
    "2 Sam": "2 Samuel",
    "1 Kgs": "1 Kings",
    "2 Kgs": "2 Kings",
    "1 Chr": "1 Chronicles",
    "2 Chr": "2 Chronicles",
    "1 Chron": "1 Chronicles",
    "2 Chron": "2 Chronicles",
    "Ezra": "Ezra",
    "Neh": "Nehemiah",
    "Est": "Esther",
    "Job": "Job",
    "Ps": "Psalms",
    "Psalm": "Psalms",
    "Prov": "Proverbs",
    "Eccl": "Ecclesiastes",
    "Song": "Song",
    "Isa": "Isaiah",
    "Jer": "Jeremiah",
    "Lam": "Lamentations",
    "Ezek": "Ezekiel",
    "Dan": "Daniel",
    "Hos": "Hosea",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obad": "Obadiah",
    "Jon": "Jonah",
    "Mic": "Micah",
    "Nah": "Nahum",
    "Hab": "Habakkuk",
    "Zeph": "Zephaniah",
    "Hag": "Haggai",
    "Zech": "Zechariah",
    "Mal": "Malachi",
    "Matt": "Matthew",
    "Mark": "Mark",
    "Luke": "Luke",
    "John": "John",
    "Acts": "Acts",
    "Rom": "Romans",
    "1 Cor": "1 Corinthians",
    "2 Cor": "2 Corinthians",
    "Gal": "Galatians",
    "Eph": "Ephesians",
    "Phil": "Philippians",
    "Col": "Colossians",
    "1 Thess": "1 Thessalonians",
    "2 Thess": "2 Thessalonians",
    "1 Tim": "1 Timothy",
    "2 Tim": "2 Timothy",
    "Titus": "Titus",
    "Phlm": "Philemon",
    "Heb": "Hebrews",
    "Jas": "James",
    "1 Pet": "1 Peter",
    "2 Pet": "2 Peter",
    "1 John": "1 John",
    "2 John": "2 John",
    "3 John": "3 John",
    "Jude": "Jude",
    "Rev": "Revelation",
    "GEN": "Genesis",
    "EXO": "Exodus",
    "LEV": "Leviticus",
    "NUM": "Numbers",
    "DEU": "Deuteronomy",
    "JOS": "Joshua",
    "JDG": "Judges",
    "RUT": "Ruth",
    "1SA": "1 Samuel",
    "2SA": "2 Samuel",
    "1KI": "1 Kings",
    "2KI": "2 Kings",
    "1CH": "1 Chronicles",
    "2CH": "2 Chronicles",
    "EZR": "Ezra",
    "NEH": "Nehemiah",
    "EST": "Esther",
    "JOB": "Job",
    "PSA": "Psalms",
    "PRO": "Proverbs",
    "ECC": "Ecclesiastes",
    "SNG": "Song",
    "ISA": "Isaiah",
    "JER": "Jeremiah",
    "LAM": "Lamentations",
    "EZK": "Ezekiel",
    "DAN": "Daniel",
    "HOS": "Hosea",
    "JOL": "Joel",
    "AMO": "Amos",
    "OBA": "Obadiah",
    "JON": "Jonah",
    "MIC": "Micah",
    "NAM": "Nahum",
    "HAB": "Habakkuk",
    "ZEP": "Zephaniah",
    "HAG": "Haggai",
    "ZEC": "Zechariah",
    "MAL": "Malachi",
    "MAT": "Matthew",
    "MRK": "Mark",
    "LUK": "Luke",
    "JHN": "John",
    "ACT": "Acts",
    "ROM": "Romans",
    "1CO": "1 Corinthians",
    "2CO": "2 Corinthians",
    "GAL": "Galatians",
    "EPH": "Ephesians",
    "PHP": "Philippians",
    "COL": "Colossians",
    "1TH": "1 Thessalonians",
    "2TH": "2 Thessalonians",
    "1TI": "1 Timothy",
    "2TI": "2 Timothy",
    "TIT": "Titus",
    "PHM": "Philemon",
    "HEB": "Hebrews",
    "JAS": "James",
    "1PE": "1 Peter",
    "2PE": "2 Peter",
    "1JN": "1 John",
    "2JN": "2 John",
    "3JN": "3 John",
    "JUD": "Jude",
    "REV": "Revelation"
}


def normalize_book_name(book_input):
    """
    Converts abbreviations into full book names.
    """

    book_input = book_input.strip()

    # Exact match first
    if book_input in BOOK_NAMES:
        return book_input

    # Abbreviation match
    if book_input in BOOK_ABBREVIATIONS:
        return BOOK_ABBREVIATIONS[book_input]

    # Case-insensitive abbreviation match
    for abbrev, full_name in BOOK_ABBREVIATIONS.items():
        if book_input.lower() == abbrev.lower():
            return full_name

    # Partial match against full book names
    for book_name in BOOK_NAMES:
        if book_name.lower().startswith(book_input.lower()):
            return book_name

    raise ValueError(f"Unknown book name: {book_input}")


def parse_reference(user_input):
    """
    Parses:
        1 Cor 13:4
        Ps 23:1
        Psalms 119
        2 Sam 5
    """

    user_input = user_input.strip()

    if ';' not in user_input and ',' not in user_input:

        # Chapter + verse
        verse_match = re.match(r"^(.*?)\s+(\d+):(\d+)$", user_input)

        if verse_match:
            raw_book = verse_match.group(1).strip()
            chapter = verse_match.group(2)
            verse = verse_match.group(3)

            book_name = normalize_book_name(raw_book)

            return [(book_name, chapter, verse)]

        # Chapter only
        chapter_match = re.match(r"^(.*?)\s+(\d+)$", user_input)

        if chapter_match:
            raw_book = chapter_match.group(1).strip()
            chapter = chapter_match.group(2)

            book_name = normalize_book_name(raw_book)

            return [(book_name, chapter, None)]

    elif ';' in user_input or ',' in user_input:
        verses = []
        book_name = None
        chapter = None
        verse = None
        blocks = re.split(r"[;,]", user_input)
        for block in blocks:
            block = block.strip()
            verse_match = re.match(r"^(.*?)\s+(\d+):(\d+)$", block)
            if verse_match:
                raw_book = verse_match.group(1).strip()
                chapter = verse_match.group(2)
                verse = verse_match.group(3)

                book_name = normalize_book_name(raw_book)
                verses.append((book_name, chapter, verse))
            else:
                verse_match = re.match(r"^(\d+):(\d+)$", block)
                if verse_match:
                    chapter = verse_match.group(1) 
                    verse = verse_match.group(2)
                    verses.append((book_name, chapter, verse))
                else:
                    verse_match = re.match(r"^(\d+)$", block)
                    if verse_match:
                        verse = verse_match.group(1)
                        verses.append((book_name, chapter, verse))
        if any(book is None or chap is None for book, chap, verse in verses):
            raise ValueError("Enter a valid reference.")
        return verses

    raise ValueError(
        "Enter a valid reference."
    )

def find_verse_in_file(file_path, reference):

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            for row in reader:
                if row["Reference"].strip() == reference:
                    return row["Verse"].strip()

    except FileNotFoundError:
        return None

    return None

def find_chapter_in_file(file_path, chapter):

    verses = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            for row in reader:
                ref = row["Reference"].strip()

                if ref.startswith(f"{chapter}:"):
                    verses.append(
                        f"<div class='verse'>"
                        f"<span class='ref'>{ref}</span> "
                        f"{row['Verse'].strip()}"
                        f"</div>"
                    )

    except FileNotFoundError:
        return None

    return verses

def show_verses(user_input):

    to_print = []

    current_book = None

    for book_name, chapter, verse in parse_reference(user_input):
        if book_name != current_book:
            current_book = book_name
            ult_file = os.path.join(
                DATA_DIR,
                f"master_ULT_{book_name}.tsv"
            )

            ust_file = os.path.join(
                DATA_DIR,
                f"master_UST_{book_name}.tsv"
            )

        output = []

        # SINGLE VERSE LOOKUP
        if verse is not None:

            reference = f"{chapter}:{verse}"

            ult_text = find_verse_in_file(ult_file, reference)
            ust_text = find_verse_in_file(ust_file, reference)

            if ult_text:
                output.append(
                    f"<strong>{book_name} {reference} (ULT)</strong>: {ult_text}"
                )
            else:
                output.append(
                    f"<strong>{book_name} {reference} (ULT)</strong>: Verse not found."
                )

            if ust_text:
                output.append(
                    f"<strong>{book_name} {reference} (UST)</strong>: {ust_text}"
                )
            else:
                output.append(
                    f"<strong>{book_name} {reference} (UST)</strong>: Verse not found."
                )

            result = "\n\n".join(line.lstrip() for line in output)
            to_print.append(result)

        # CHAPTER LOOKUP
        else:

            ult_verses = find_chapter_in_file(ult_file, chapter)
            ust_verses = find_chapter_in_file(ust_file, chapter)

            output.append(f"<h2>{book_name} {chapter} (ULT)</h2>")

            if ult_verses:
                output.extend(ult_verses)
            else:
                output.append("Chapter not found.")

            output.append(f"<h2>{book_name} {chapter} (UST)</h2>")

            if ust_verses:
                output.extend(ust_verses)
            else:
                output.append("Chapter not found.")

            result = "".join(line.lstrip() for line in output)
            to_print.append(result)

    return "\n\n\n".join(to_print)
    