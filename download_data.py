from note_lookup import download_notes_files
from search import download_text_files
from texts import main
import os


def download_data():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    download_notes_files()
    print('Downloaded notes files')
    download_text_files()
    print('Downloaded text files')
    main()
    print('Processed text files')


if __name__ == '__main__':
    download_data()