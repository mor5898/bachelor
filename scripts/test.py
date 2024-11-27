import sqlite3
import os

def get_sqlite_schema(db_file_path):
    if not os.path.isfile(db_file_path):
        raise FileNotFoundError(f"Die SQLite-Datei wurde nicht gefunden: {db_file_path}")

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type IN ('table', 'index', 'trigger', 'view') AND sql NOT NULL;")
    schema_items = cursor.fetchall()

    conn.close()

    schema = "\n\n".join(item[0] for item in schema_items)
    return schema

def remove_insert_statements(schema):
    import re

    insert_pattern = re.compile(r'INSERT\s+INTO\s+.*?;', re.IGNORECASE | re.DOTALL)

    cleaned_content = re.sub(insert_pattern, '', schema)

    cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content)

    return cleaned_content

if __name__ == "__main__":
    sqlite_file = 'spider/database/voter_1/voter_1.sqlite'

    try:
        schema = get_sqlite_schema(sqlite_file)
        print("Originales Schema:")
        print(schema)

        cleaned_schema = remove_insert_statements(schema)
        print("\nBereinigtes Schema (ohne INSERT INTO Statements):")
        print(cleaned_schema)

    except FileNotFoundError as e:
        print(e)
    except sqlite3.Error as e:
        print(f"SQLite-Fehler: {e}")
