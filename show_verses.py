import csv
import os
import re

DATA_DIR = "Data/Texts"


def parse_reference(user_input):
    """
    Splits input like:
        '1 Thessalonians 4:12'
        'Psalms 115:133'

    into:
        book_name, chapter, verse
    """

    match = re.match(r"^(.*?)\s+(\d+):(\d+)$", user_input.strip())

    if not match:
        raise ValueError(
            "Input must be in the format 'Book Chapter:Verse'"
        )

    book_name = match.group(1).strip()
    chapter = match.group(2)
    verse = match.group(3)

    return book_name, chapter, verse


def find_verse_in_file(file_path, reference):
    """
    Searches TSV file for a verse reference like '4:12'
    """

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
    """
    Returns formatted ULT and UST verse output.
    """

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

    return "\n\n".join(output)


if __name__ == "__main__":
    while True:
        user_input = input(
            "Enter reference (example: 1 Thessalonians 4:12): "
        ).strip()

        if user_input.lower() == "quit":
            break

        try:
            result = show_verses(user_input)
            print()
            print(result)
            print()

        except Exception as e:
            print(f"Error: {e}")