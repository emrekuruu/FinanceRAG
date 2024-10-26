import re
import pandas as pd
import sqlite3

def extract_table_from_text(text: str) -> pd.DataFrame:
    # Regex pattern to split on '|' and keep spaces and empty cells
    row_pattern = re.compile(r"\s*\|\s*")
    table_data = []

    for line in text.splitlines():
        # Skip lines that are purely dashes (table separators)
        if re.match(r"^\s*-+\s*$", line):
            continue
        
        if '|' in line:
            # Split by '|' and retain empty cells or cells with spaces
            row_data = row_pattern.split(line)
            # Strip leading and trailing whitespace in each cell, keep spaces within
            row_data = [cell if cell != "" else "" for cell in row_data]
            table_data.append(row_data)

    # Find the maximum column count for consistent row length
    max_cols = max(len(row) for row in table_data)

    # Pad rows to ensure uniform column lengths
    padded_rows = [row + [""] * (max_cols - len(row)) for row in table_data]

    # Generate dynamic column names
    columns = [f"Column_{i+1}" for i in range(max_cols)]

    # Convert to DataFrame
    df = pd.DataFrame(padded_rows, columns=columns)
    df.drop(index=1, inplace=True)
    df.columns = df.iloc[0].values
    df.drop(index=0, inplace=True)

    table = df
    temp = df

    try:

        for column in table.columns:
            if wrong_header(column):
                table = table.T
                table.reset_index(inplace=True)
                table.drop("index", axis=1, inplace=True)
                table = table.T
                table.columns = table.iloc[0].values
                table.drop(index=2, axis=0, inplace=True)
    except:
        table = temp

    
    columns = table.columns
    next_columns = table.T.iloc[0].values
    columns = [ column for column in columns if column != "" or wrong_header(column)]
    table = table.T.loc[columns]
    table.columns = next_columns

    for index in table.index:
        if "(in" in index.split() or "in" in index.split():
            table.drop(index=index, axis=0, inplace=True)
    
    return table


def wrong_header(column: str) -> bool:
        try:
            words = column.split()
            for word in words:
                if word == "Years" or word == "in" or word == "As" or "Year" or "30" or "31" or "32" or "YearEnded" or "Fiscal" or "At" or "30," or "31,":
                    return True
        except:
            return False


class TableDatabase:
    def __init__(self, documents: dict, db_name="tables.db"):
        """
        Initialize the class with a dictionary of documents and create the database.
        Each document will have its table extracted and stored with the document ID as the table ID.
        
        :param documents: A dictionary where keys are document IDs and values are document metadata.
        :param db_name: The name of the SQLite database file.
        """
        self.documents = documents
        self.conn = sqlite3.connect(db_name)
        self.create_database()
        
        # Process each document and extract/store tables
        for doc_id, metadata in documents.items():
            text = metadata["text"]
            self.insert_table(doc_id, text)

    def create_database(self):
        """
        Creates the necessary tables in the SQLite database.
        """
        cursor = self.conn.cursor()

        # Create a Cells table where each cell is linked to a document's table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cells (
            table_id TEXT,
            row_name TEXT,
            column_name TEXT,
            value TEXT,
            PRIMARY KEY (table_id, row_name, column_name)
        )
        """)

        self.conn.commit()



    def insert_table(self, doc_id: str, text: str):
        """
        Extracts the table from the document text and inserts it into the database with the document ID as the table ID.
        
        :param doc_id: The document ID (used as the table ID).
        :param text: The document text containing the table.
        """
        cursor = self.conn.cursor()

        # Extract the table from the document text
        df = extract_table_from_text(text)

        # Insert each row and column value into the Cells table
        for row_name, row_data in df.iterrows():
            for column_name, cell_value in row_data.items():
                row_name = row_name.strip()
                column_name = column_name.strip()
                cursor.execute("""
                    INSERT OR REPLACE INTO Cells (table_id, row_name, column_name, value)
                    VALUES (?, ?, ?, ?)
                """, (doc_id, row_name, column_name, str(cell_value)))

        self.conn.commit()

    def query_table(self, table_id):
        """
        Queries the entire table for a given table ID.
        
        :param table_id: The ID of the table (same as the document ID).
        :return: A pandas DataFrame representing the table.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT row_name, column_name, value
        FROM Cells
        WHERE table_id = ?
        """, (table_id,))
        results = cursor.fetchall()

        df = pd.DataFrame(results, columns=["row_name", "column_name", "value"])
        return df.pivot(index="row_name", columns="column_name", values="value")

    def query_cell(self, table_id, row_name=None, column_name=None):
        """
        Queries a specific cell, row, or column in the table by table ID.
        
        :param table_id: The ID of the table (same as the document ID).
        :param row_name: The name of the row to query (optional).
        :param column_name: The name of the column to query (optional).
        :return: The cell value if both row and column are specified, or the entire row/column if one is omitted.
        """
        cursor = self.conn.cursor()

        if row_name and column_name:
            # Query a specific cell
            cursor.execute("""
            SELECT value
            FROM Cells
            WHERE table_id = ? AND row_name = ? AND column_name = ?
            """, (table_id, row_name, column_name))
            return cursor.fetchone()
        
        elif row_name:
            # Query an entire row
            cursor.execute("""
            SELECT column_name, value
            FROM Cells
            WHERE table_id = ? AND row_name = ?
            """, (table_id, row_name))
            return cursor.fetchall()

        elif column_name:
            # Query an entire column
            cursor.execute("""
            SELECT row_name, value
            FROM Cells
            WHERE table_id = ? AND column_name = ?
            """, (table_id, column_name))
            return cursor.fetchall()

        else:
            return None
