import re
import html
import os

DATA_DIR = "Data/Texts"


def normalize_query(query: str):
    """
    - Converts smart quotes to straight quotes
    - Detects quoted phrase vs single word search
    """
    query = query.replace("“", '"').replace("”", '"').strip()

    # Phrase search: "something like this"
    if query.startswith('"') and query.endswith('"'):
        return query[1:-1], True

    return query, False

def highlight_text(text, query, is_phrase):
    """
    Wrap matches in HTML span for styling
    """

    if is_phrase:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
    else:
        pattern = re.compile(rf"\b{re.escape(query)}\b", re.IGNORECASE)

    def replacer(match):
        return f"<span class='highlight'>{html.escape(match.group(0))}</span>"

    return pattern.sub(replacer, html.escape(text))

def search_verses(query, version="ULT"):
    """
    Searches ULT_for_accordance.txt or UST_for_accordance.txt
    """

    query, is_phrase = normalize_query(query)

    file_path = os.path.join(
        DATA_DIR,
        f"{version}_for_accordance.txt"
    )

    results = []

    if not os.path.exists(file_path):
        return ["File not found."]

    with open(file_path, "r", encoding="mac_roman") as f:
        for line in f:
            original_line = line.rstrip("\n")

            # Split: "Book Chapter:Verse text..."
            parts = original_line.split(" ", 2)
            if len(parts) < 3:
                continue

            book_ref = f"{parts[0]} {parts[1]}"
            verse_text = parts[2]

            match_found = False

            if is_phrase:
                if query.lower() in verse_text.lower():
                    match_found = True
            else:
                # word match (whole word)
                if re.search(rf"\b{re.escape(query)}\b", verse_text, re.IGNORECASE):
                    match_found = True

            if match_found:
                highlighted_text = highlight_text(verse_text, query, is_phrase)

                results.append(
                    f"<span class='ref'>{book_ref}</span> {highlighted_text}"
                )

    return results