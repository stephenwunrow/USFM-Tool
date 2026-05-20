import csv
import string
import random

def is_valid_id(id_):
    return (
        len(id_) == 4 and
        id_[0] in string.ascii_lowercase and
        all(c in string.ascii_lowercase + string.digits for c in id_)
    )

def generate_unique_id(existing_ids):
    while True:
        new_id = random.choice(string.ascii_lowercase)
        new_id += ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        if new_id not in existing_ids:
            return new_id

def check_tsv_ids(file_path):
    seen_ids = set()
    duplicates = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

    for row in rows:
        if len(row) < 2:
            continue  # skip rows that don't have a second column
        current_id = row[1]
        if not is_valid_id(current_id):
            print(f"Invalid ID format: {current_id}")
            replacement = generate_unique_id(seen_ids)
            print(f"Suggested replacement: {replacement}")
            seen_ids.add(replacement)
        elif current_id in seen_ids:
            replacement = generate_unique_id(seen_ids)
            print(f"Duplicate ID found: {current_id}")
            print(f"Suggested replacement: {replacement}")
            seen_ids.add(replacement)
        else:
            seen_ids.add(current_id)

# Example usage:
check_tsv_ids("test_tn_NUM.tsv")
