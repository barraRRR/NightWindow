import json
import sys


def load_texts(language: str) -> dict:
    filename = f'{language}_texts.json'
    try:
        with open(filename, 'r', encoding='utf-8') as data:
            return json.load(data)

    except Exception:
        sys.exit('❌ Error: text file not found')


def load_logo() -> str:
    try:
        with open('title.txt', 'r', encoding='utf-8') as file:
            return file.read()

    except FileNotFoundError:
        sys.exit('Error: title.txt not found')
    
    return logo


TEXTS: dict = load_texts('en')
LOGO: str = load_logo()