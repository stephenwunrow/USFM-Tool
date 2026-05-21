from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file, abort
from search import run_web_search, download_text_files
from texts import main as build_texts
from show_verses import show_verses
from search_texts import search_verses
from note_lookup import search_notes
from note_lookup import download_notes_files
from fix_ats import fix_ats
from threading import Thread, Lock
import os
import io
import zipfile
import unicodedata

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # necessary for sessions

download_in_progress = False
logs = []
logs_lock = Lock()

# You can either import this from search.py or define here
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
    "Malachi": "39-MAL"
}

def logger(message):
    with logs_lock:
        logs.append(message)

def run_note_search(user_input, use_regex=False):
    try:
        return search_notes(user_input, use_regex=use_regex)
    except Exception as e:
        return f"Error: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    note_result = ""
    selected_book = session.get("selected_book", None)
    selected_books = session.get("selected_books", [])

    refresh_message = session.pop('refresh_message', None)
    refresh_logs = session.pop('refresh_logs', [])
    note_refresh_message = session.pop('note_refresh_message', None)
    note_refresh_logs = session.pop('note_refresh_logs', [])

    if request.method == "POST":

        session['use_regex'] = bool(request.form.get("use_regex"))

        # Handle book dropdown for main search
        book = request.form.get("book_select")
        if book in acronym_mapping:
            session["selected_book"] = book
            selected_book = book

        if request.method == "POST":
            selected_books = request.form.getlist("book_buttons")
            if "All" in selected_books:
                selected_books = None
            session["selected_books"] = selected_books

        input_str = request.form.get("input_str", "").strip()
        note_input_str = request.form.get("note_query", "").strip()  # ← matches the input name in your HTML

        # Run primary text search
        if input_str:
            if selected_book:
                file_code = acronym_mapping[selected_book]
                file_path = f"Data/en_ult/{file_code}.usfm"
                result = run_web_search(input_str, file_path, selected_books=selected_books)
            else:
                result = "Please select a valid book."

        # Run note search
        if note_input_str:
            use_regex = session.get("use_regex", False)
            note_result = run_note_search(note_input_str, use_regex)

    return render_template("index.html",
                           result=result,
                           note_result=note_result,
                           books=acronym_mapping.keys(),
                           selected_book=selected_book,
                           selected_books=selected_books,
                           message=refresh_message,
                           logs=refresh_logs,
                           note_message=note_refresh_message,
                           note_logs=note_refresh_logs)

@app.route('/refresh', methods=['POST'])
def refresh():
    logs = []

    def collect_logs(message):
        logs.append(message)

    try:
        download_text_files(logger=collect_logs)
        session['refresh_logs'] = logs  # store logs in session temporarily
        session['refresh_message'] = "Data files refreshed successfully."
        build_texts()
        session['refresh_message'] += " Texts built successfully."
    except Exception as e:
        session['refresh_logs'] = []
        session['refresh_message'] = f"Error during refresh: {e}"

    return redirect(url_for('index'))

@app.route('/refresh_notes', methods=['POST'])
def refresh_notes():
    note_logs = []

    def collect_note_logs(message):
        note_logs.append(message)

    try:
        download_notes_files(logger=collect_note_logs)
        session['note_refresh_logs'] = note_logs  # store logs in session temporarily
        session['note_refresh_message'] = "Data files refreshed successfully."
    except Exception as e:
        session['note_refresh_logs'] = []
        session['note_refresh_message'] = f"Error during refresh: {e}"

    return redirect(url_for('index'))

@app.route("/tsv-tool", methods=["GET", "POST"])
def tsv_tool():
    books = [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges",
        "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
        "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song",
        "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
        "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi"
    ]

    update_complete = False
    output_data = None
    book_name = session.get('selected_book', None)

    if request.method == "POST":
        book_name = request.form.get("book_name")
        tsv_content = request.form.get("tsv_content")

        if book_name in books:
            session['selected_book'] = book_name  # Save choice in session

            # Call your processing function
            output_data = fix_ats(book_name, tsv_content)

            output_data = unicodedata.normalize('NFC', output_data)

            update_complete = True
        else:
            # Invalid book; fallback or handle error as you want
            book_name = session.get('selected_book', None)

    return render_template(
        "tsv_tool.html",
        books=books,
        selected_book=book_name,
        update_complete=update_complete,
        output_data=output_data
    )

@app.route("/download-tsv")
def download_tsv():
    book_name = request.args.get('book_name')
    if not book_name:
        abort(400, "Missing book_name")

    # Construct path to the single TSV file to download
    file_path = f"output/{book_name}/final_notes.tsv"

    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        abort(404, "File not found")

@app.route("/download-all")
def download_all():
    book_name = request.args.get('book_name')
    if not book_name:
        abort(400, "Missing book_name")

    folder_path = f"output/{book_name}/"
    if not os.path.isdir(folder_path):
        abort(404, "Folder not found")

    # Create an in-memory bytes buffer
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Loop through all files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                # Add file to the zip archive
                zipf.write(file_path, arcname=filename)

    memory_file.seek(0)  # Reset pointer to the start of the BytesIO buffer

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{book_name}_all_files.zip"
    )

# =========================
# Translations Routes
# =========================
@app.route('/translations', methods=['GET', 'POST'])
def translations():
    output = None
    
    version = request.form.get('version') or request.args.get('version') or "ULT"
    
    if request.method == 'POST':

        verse_input = request.form.get('verse_input', '').strip()
        search_input = request.form.get('search_input', '').strip()

        # Priority: search wins if both filled
        if search_input:
            output = search_verses(search_input, version)

        elif verse_input:
            output = show_verses(verse_input)

    return render_template('translations.html', output=output, version=version)

@app.route('/download_accordance')
def download_accordance():
    output_dir = 'Data/Texts'

    files_to_zip = [
        os.path.join(output_dir, 'ULT_for_accordance.txt'),
        os.path.join(output_dir, 'UST_for_accordance.txt')
    ]

    zip_path = os.path.join(output_dir, 'accordance_bibles.zip')

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=os.path.basename(file_path))

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    download_text_files(logger=logger)
    app.run(host="0.0.0.0", port=8080)
