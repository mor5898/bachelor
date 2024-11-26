import re
import os

def remove_insert_statements(input_file_path):
    """
    Entfernt alle INSERT INTO Statements aus einer .sql Datei und speichert das Ergebnis in einer neuen Datei.

    Parameters:
    - input_file_path (str): Der Pfad zur ursprünglichen .sql Datei.
    - output_file_path (str): Der Pfad zur bereinigten .sql Datei ohne INSERT INTO Statements.

    Returns:
    - None
    """

    # Überprüfe, ob die Eingabedatei existiert
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError(f"Die Eingabedatei wurde nicht gefunden: {input_file_path}")

    # Lese den Inhalt der Eingabedatei
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Definiere das Muster für INSERT INTO Statements
    # Dieses Muster sucht nach 'INSERT INTO', gefolgt von beliebigen Zeichen bis zum nächsten Semikolon
    insert_pattern = re.compile(r'INSERT\s+INTO\s+.*?;', re.IGNORECASE | re.DOTALL)

    # Entferne alle INSERT INTO Statements
    cleaned_content = re.sub(insert_pattern, '', content)

    # Optional: Entferne überschüssige Leerzeilen, die durch das Entfernen entstehen könnten
    cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content)

    return cleaned_content

if __name__ == "__main__":
    remove_insert_statements("./spider/database/singer/schema.sql", "test.sql")