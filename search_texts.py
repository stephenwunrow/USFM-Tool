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


def load_translation_lookup(version):
    """
    Build a lookup for verse text by book reference in the given translation.
    """
    file_path = os.path.join(DATA_DIR, f"{version}_for_accordance.txt")
    lookup = {}

    if not os.path.exists(file_path):
        return lookup

    with open(file_path, "r", encoding="mac_roman") as f:
        for line in f:
            original_line = line.rstrip("\n")
            parts = original_line.split(" ", 2)
            if len(parts) < 3:
                continue
            book_ref = f"{parts[0]} {parts[1]}"
            lookup[book_ref] = parts[2]

    return lookup


def sanitize_id(value: str):
    return re.sub(r"[^A-Za-z0-9_-]", "-", value.strip()).lower()


def search_verses(query, version="ULT"):
    """
    Searches ULT_for_accordance.txt or UST_for_accordance.txt
    """

    file_path = os.path.join(
        DATA_DIR,
        f"{version}_for_accordance.txt"
    )

    other_version = "UST" if version == "ULT" else "ULT"
    other_lookup = load_translation_lookup(other_version)

    results = ""
    match_count = 0

    if not os.path.exists(file_path):
        return "<div class='result-count'><span class='ref'>File not found.</span></div>"

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
                escaped_ref = html.escape(book_ref)
                verse_id = sanitize_id(book_ref)
                other_text = other_lookup.get(book_ref)
                other_html = html.escape(other_text) if other_text else "<em>Other translation verse not found.</em>"
                other_div_id = f"other-{verse_id}"

                results += (
                    f"<div class='result'>"
                    f"<div class='result-line'>"
                    f"<div class='verse-text'><span class='ref'>{escaped_ref}</span> {highlighted_text}</div>"
                    f"<button type='button' class='toggle-translation-button' data-target='{other_div_id}' data-translation='{other_version}'>See {other_version}</button>"
                    f"</div>"
                    f"<div class='other-translation' id='{other_div_id}' style='display:none;'>"
                    f"<span class='ref'>{escaped_ref} ({other_version})</span> {other_html}"
                    f"</div>"
                    f"</div>"
                )

    results = (
        f"<div class='result-count'>"
        f"<div class='count-row'>"
        f"<span class='ref'>Found {match_count} matches.</span>"
        f"<button type='button' class='toggle-all-translations-button' data-translation='{other_version}'>See all {other_version}</button>"
        f"</div>"
        f"</div>"
        + results
    )

    return results