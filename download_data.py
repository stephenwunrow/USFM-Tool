from note_lookup import download_notes_files
from search import download_text_files
from texts import main


def download_data():
    download_notes_files()
    print('Downloaded notes files')
    download_text_files()
    print('Downloaded text files')
    main()
    print('Processed text files')


if __name__ == '__main__':
    download_data()