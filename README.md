
# Notion Page creator from Kindle Book notes and highlights

  

This python script creates a notion page in a notion data base from the csv file exported from kindle which contains notes and highlights of a book.

  

Provide execute permissions and run the initial-setup.sh file for python virtual environment setup: 

    chmod u=rwx ./initial-setup.sh
    . ./initial-setup.sh

  

Save notion db secret and database id to environment variables

    export NOTION_KEY="secret_key"
    export NOTION_BOOK_NOTES_DB_ID="database_id"

Run the script:

    python3 -B create-page.py <path/to/the/csv/file>

For Debug prints-
        
    export DEBUG=True