from .standard_database import StandardDatabase
import sqlite3

class StandardTable():
    def __init__(self, database: StandardDatabase, name:str ):
        self.database = database
        self.name = name

    def get_cursor(self) -> sqlite3.Cursor:
        cursor = self.database.execute( statement=f"SELECT * FROM '{self.name}';", commit=False )
        return cursor

    def get_columns(self) -> list:
        cursor = self.get_cursor()
        columns = []
        for cols in cursor.description:
            columns.append( cols[0] )
        return columns

    def get_rows(self) -> list:
        cursor = self.get_cursor()
        return list( cursor.fetchall() )

    def clear(self) -> bool:
        try:
            self.database.execute( f"DELETE FROM '{self.name}';", commit=True )
            self.database.execute(
                f"DELETE FROM sqlite_sequence WHERE name='{self.name}';", commit=True
            )
            return True
        except:
            return False

    def delete_row(self, column: str, value) -> bool:
        try:
            self.database.execute(
                statement=f"DELETE FROM '{self.name}' WHERE {column}=?;",
                commit=True, params=(value,)
            )
            return True
        except:
            return False
