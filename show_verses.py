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
    "Rev": "Revelation"
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
        Psalms 119:105
        2 Sam 5:3
    """

    match = re.match(r"^(.*?)\s+(\d+):(\d+)$", user_input.strip())

    if not match:
        raise ValueError(
            "Input must be in the format 'Book Chapter:Verse'"
        )

    raw_book = match.group(1).strip()
    chapter = match.group(2)
    verse = match.group(3)

    book_name = normalize_book_name(raw_book)

    return book_name, chapter, verse


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


def show_verses(user_input):

    book_name, chapter, verse = parse_reference(user_input)

    reference = f"{chapter}:{verse}"

    ult_file = os.path.join(
        DATA_DIR,
        f"master_ULT_{book_name}.tsv"
    )

    ust_file = os.path.join(
        DATA_DIR,
        f"master_UST_{book_name}.tsv"
    )

    ult_text = find_verse_in_file(ult_file, reference)
    ust_text = find_verse_in_file(ust_file, reference)

    output = []

    if ult_text:
        output.append(
            f"{book_name} {reference} (ULT): {ult_text}"
        )
    else:
        output.append(
            f"{book_name} {reference} (ULT): Verse not found."
        )

    if ust_text:
        output.append(
            f"{book_name} {reference} (UST): {ust_text}"
        )
    else:
        output.append(
            f"{book_name} {reference} (UST): Verse not found."
        )

    result = "\n\n".join(line.lstrip() for line in output)
    return result