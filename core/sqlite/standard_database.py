import sqlite3
import pathlib

# Local
from utils.text_util import read_text

class StandardDatabase():
    def __init__(self, directory: pathlib.Path, name: str  ):
        self.directory = directory
        self.name = name

    def get_path(self):
        path = self.directory.joinpath( self.name )
        return path

    def exists(self):
        return self.get_path().exists()

    def _connect(self):
        return sqlite3.connect( self.get_path() )

    def execute( self, statement:str, commit: bool, params: tuple=() ) -> sqlite3.Cursor:
        '''
        Devuelve un cursor
        '''
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION") # Iniciar transacción Para que jale el rollback
            cursor.execute(statement, params)

            if commit:
                conn.commit()
            else:
                conn.rollback()

            return cursor

    def init_schema(self, schema_file):
        sql_script = read_text( schema_file, 'ModeText', "utf-8" )
        print(sql_script)
        conn = self._connect()
        conn.executescript( sql_script )
        conn.commit()

    def create_file(self):
        if self.get_path().exists():
            return False
        conn = self._connect()
        conn.close()
        return True

    def delete(self):
        path = self.get_path()
        if not path.exists():
            return False
        return pathlib.Path.unlink( path )

    def get_tables(self):
        cursor = self.execute(
            statement=(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ), commit=False
        )
        return cursor.fetchall()

    def get_table_names(self):
        tables = []
        for cols in self.get_tables():
            tables.append( cols[0] )
        return tables

    def table_exists(self, table: str) -> bool:
        return table in self.get_table_names()

    def drop_table(self, table: str) -> bool:
        exists = self.table_exists(table)
        if exists:
            cursor = self.execute(
                statement=f"DROP TABLE {table};",
                commit=True
            )

        return not exists

    def drop_all_tables(self):
        tables = self.get_table_names()
        for name in tables:
            self.delete_table(name)
        return len(tables) > 0
