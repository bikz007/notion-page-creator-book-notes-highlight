import json
import requests
import os
import csv
from pprint import pp, pprint
import sys
DEBUG = True if os.environ.get('DEBUG', "") == "True" else False
N_TOKEN = os.environ.get('NOTION_KEY', "")
N_DB_ID = os.environ.get('NOTION_BOOK_NOTES_DB_ID', "")
REQUEST_HEADER = {
    "Authorization": "Bearer " + N_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Notion-Version": "2022-06-28",
}
BASE_URL = 'https://api.notion.com/v1/pages'
AUTHOR_NAMES = []
BOOK_NAME = ""
CSV_FILE_NAME = sys.argv[1]
NOTION_CONTENT_LENGTH_LIMIT = 2000


def validate_essentials():
    if N_TOKEN == "" or N_DB_ID == "":
        print(
            "notion token='{n_token}' or database id='{n_db_id} cannot be empty".format(
                n_token=N_TOKEN,
                n_db_id=N_DB_ID))


def create_page(page_data):
    validate_essentials()
    new_page_data = {
        "parent": {
            "type": "database_id",
            "database_id": N_DB_ID
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": page_data["book_name"]
                        }
                    }
                ]
            },
            "Author": {
                "multi_select": page_data["author_names"]
            },
        },
        "children": page_data["book_notes_highlights"]
    }

    write_data = json.dumps(new_page_data)

    resp = requests.request(
        "POST",
        BASE_URL,
        headers=REQUEST_HEADER,
        data=write_data)
    if DEBUG is True:
        pp(page_data)
        pp(write_data)
        print(resp.status_code)
        print(resp.text)


def get_page_childrens(notes_data):
    childrens = []
    for note_highlight in notes_data:
        callout_text = note_highlight[0] + ":" + note_highlight[1]
        # to manage notions 2000 characters content limit
        if len(callout_text) == NOTION_CONTENT_LENGTH_LIMIT:
            childrens.append(get_callout(callout_text))
            continue
        num_of_parts = (len(callout_text)//NOTION_CONTENT_LENGTH_LIMIT)+1
        chunk_start_idx = 0
        chunk_end_idx = 0
        i = 0
        while( i < num_of_parts):
            chunk_start_idx = NOTION_CONTENT_LENGTH_LIMIT * i
            if i == (num_of_parts-1): # last chunk
                childrens.append(get_callout(callout_text[chunk_end_idx:]))
            else:
                chunk_end_idx = chunk_start_idx + NOTION_CONTENT_LENGTH_LIMIT
                childrens.append(get_callout(callout_text[chunk_start_idx:chunk_end_idx]))
            i += 1
    if DEBUG is True:
        pp(childrens)
    return childrens


def get_callout(callout_text):
    result_callout = {
        "object": "block",
        "callout": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": callout_text,
                },
            }],
            "icon": {
                "emoji": "💡"
            },
            "color": "default"
        }
    }
    if DEBUG is True:
        pp(result_callout)
    return result_callout


def get_notes_and_highlights(csv_file_name):
    rows = []
    with open(csv_file_name, 'r') as file:
        csvreader = csv.reader(file)
        initial_row_cntr = 0
        for row in csvreader:
            if initial_row_cntr < 9:
                initial_row_cntr += 1
                if initial_row_cntr == 2:
                    global BOOK_NAME
                    BOOK_NAME = row[0]
                elif initial_row_cntr == 3:
                    global AUTHOR_NAMES
                    AUTHOR_NAMES = [{ "name": row[0][3:] , "color": "default" } ] # fix for multiple authors required
            else:
                rows.append(row[1:2]+row[3:]) # to remove column 0 and 2
    if DEBUG is True:
        pp(rows)
    return rows

if AUTHOR_NAMES or len(BOOK_NAME) < 0:
    print(
        "book name='{book_n}' cannot be empty or authors='{authors} cannot be empty".format(
            book_n=BOOK_NAME,
            authors=AUTHOR_NAMES))
else:
    notes_data = get_notes_and_highlights(CSV_FILE_NAME)
    page_data = {
        "book_name": BOOK_NAME,
        "author_names": AUTHOR_NAMES,
        "book_notes_highlights": get_page_childrens(notes_data)}
    create_page(page_data)
