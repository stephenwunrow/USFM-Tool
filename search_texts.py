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

def highlight_text(text, query, is_regex_mode):
    """
    Wrap matches in HTML span for styling
    """

    escaped_text = html.escape(text)

    if is_regex_mode:
        try:
            pattern = re.compile(query, re.IGNORECASE)
        except re.error:
            return escaped_text
    else:
        pattern = re.compile(rf"\b{re.escape(query)}\b", re.IGNORECASE)

    def replacer(match):
        return f"<span class='highlight'>{match.group(0)}</span>"

    return pattern.sub(replacer, escaped_text)

def search_verses(query, version="ULT"):
    """
    Searches ULT_for_accordance.txt or UST_for_accordance.txt
    """

    file_path = os.path.join(
        DATA_DIR,
        f"{version}_for_accordance.txt"
    )

    results = ""
    match_count = 0

    if not os.path.exists(file_path):
        return ["File not found."]

    is_regex_mode = False

    # Detect quoted regex input
    if len(query) >= 2 and query[0] == '"' and query[-1] == '"':
        is_regex_mode = True
        query = query[1:-1]  # strip quotes

    results = ""

    with open(file_path, "r", encoding="mac_roman") as f:
        for line in f:
            original_line = line.rstrip("\n")

            parts = original_line.split(" ", 2)
            if len(parts) < 3:
                continue

            book_ref = f"{parts[0]} {parts[1]}"
            verse_text = parts[2]

            match_found = False

            if is_regex_mode:
                # RAW regex mode
                try:
                    matches = re.findall(query, verse_text, re.IGNORECASE)

                    if matches:
                        match_found = True
                        match_count += len(matches)
                except re.error:
                    continue
            else:
                # SAFE word-boundary mode (always \b)
                pattern = rf"\b{re.escape(query)}\b"
                matches = re.findall(pattern, verse_text, re.IGNORECASE)

                if matches:
                    match_found = True
                    match_count += len(matches)

            if match_found:
                highlighted_text = highlight_text(verse_text, query, is_regex_mode)

                results += (
                    f"<div class='result'>"
                    f"<span class='ref'>{book_ref}</span> {highlighted_text}"
                    f"</div>"
                )

    results = (
        f"<div class='result-count'>"
        f"<span class='ref'>Found {match_count} matches.</span>"
        f"</div></div>"
        + results
    )

    return results