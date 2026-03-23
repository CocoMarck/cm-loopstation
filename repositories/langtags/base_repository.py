from core.sqlite.standard_table import StandardTable
from core.sqlite.standard_database import StandardDatabase
from utils.datetime_util import get_datetime_now, set_datetime_formatted
from utils.text_util import in_kebab_format

class BaseRepository:
    def __init__(
        self, table: StandardTable, column_id: str, column_value: str, kebab_case=False
    ):
        self.table = table
        self.database = self.table.database
        self._COLUMN_ID = column_id
        self._COLUMN_VALUE = column_value
        self._KEBAB_CASE = kebab_case

    def update_value(self, value_id:int, value: str, is_deleted:bool):
        value = in_kebab_format( value ) if self._KEBAB_CASE else value
        try:
            cursor = self.database.execute(
                statement=(
                    f"UPDATE {self.table.name} SET {self._COLUMN_VALUE}=?, updated_at=?, deleted_at=? WHERE {self._COLUMN_ID}=?;"
                ),  commit=True, params=(
                    value, get_datetime_now(), (get_datetime_now() if is_deleted else None), value_id
                )
            )
            return True
        except:
            return False

    def insert_value(self, value:str, is_deleted:bool):
        value = in_kebab_format( value ) if self._KEBAB_CASE else value
        try:
            cursor = self.database.execute(
                statement=(
                    f"INSERT INTO {self.table.name} ({self._COLUMN_VALUE},created_at,updated_at,deleted_at) VALUES(?, ?, NULL, ?);"
                ),
                commit=True, params=(
                    value, get_datetime_now(), (get_datetime_now() if is_deleted else None)
                )
            )
            return True
        except:
            return False

    def exists(self, value_id:int) -> bool:
        try:
            cursor = self.database.execute(
                statement=(
                    f'SELECT 1 FROM {self.table.name} WHERE {self._COLUMN_ID}=? LIMIT 1;'
                ),
                commit=False, params=(value_id,)
            )
            return cursor.fetchone() is not None
        except:
            return False

    def value_exists(self, value_id:int, value: str) -> bool:
        try:
            cursor = self.database.execute(
                statement=(
                    f'SELECT 1 FROM {self.table.name} WHERE {self._COLUMN_ID}=? AND {self._COLUMN_VALUE}=? LIMIT 1;'
                ),
                commit=False, params=(value_id,value)
            )
            return cursor.fetchone() is not None
        except:
            return False

    def get_row(self, row_id: int) -> list:
        try:
            cursor = self.database.execute(
                statement=f"SELECT * FROM {self.table.name} WHERE {self._COLUMN_ID}=? LIMIT 1;",
                commit=False, params=(row_id,)
            )
            row = cursor.fetchone()
            return row if row else []
        except:
            return []

    def get_value_id(self, value:str) -> int | None:
        value = in_kebab_format( value ) if self._KEBAB_CASE else value
        try:
            cursor = self.database.execute(
                statement=f"SELECT {self._COLUMN_ID} FROM {self.table.name} WHERE {self._COLUMN_VALUE}=? LIMIT 1;",
                commit=False, params=(value,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except:
            return None

    def get_value_with_id(self, value_id):
        try:
            cursor = self.database.execute(
                statement=f"SELECT {self._COLUMN_VALUE} FROM {self.table.name} WHERE {self._COLUMN_ID}=? LIMIT 1;",
                commit=False, params=(value_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except:
            return None

    def save(self, value_id:int=None, value:str=None, is_deleted:bool=False):
        inserted = False
        updated = False
        if value_id is not None:
            updated = self.update_value( value_id, value, is_deleted )
        if updated == False:
            inserted = self.insert_value( value, is_deleted )
        return updated or inserted

    def save_value(self, value:str, is_deleted:bool):
        value = in_kebab_format( value ) if self._KEBAB_CASE else value
        value_id = self.get_value_id(value)
        return self.save( value_id, value, is_deleted )


    def deactivate(self, value_id: int):
        try:
            cursor = self.database.execute(
                statement=f"UPDATE {self.table.name} SET deleted_at=? WHERE {self._COLUMN_ID}=?;",
                commit=True, params=(get_datetime_now(), value_id)
            )
            return True
        except:
            return False

    def activate(self, value_id: int):
        try:
            cursor = self.database.execute(
                statement=f"UPDATE {self.table.name} SET deleted_at=NULL WHERE {self._COLUMN_ID}=?;",
                commit=True, params=(value_id,)
            )
            return True
        except:
            return False

    def is_deleted(self, value_id:str) -> bool:
        try:
            cursor = self.database.execute(
                statement=f"SELECT deleted_at FROM {self.table.name} WHERE {self._COLUMN_ID}=? LIMIT 1;",
                commit=False, params=(value_id,)
            )
            row = cursor.fetchone()
            return row[0] is not None
        except:
            return False


    def toggle_row_state(self, value_id: int):
        deleted = self.is_deleted( value_id )
        if isinstance(value_id, int):
            if deleted:
                return self.activate( value_id )
            else:
                return self.deactivate( value_id )
        return False

    def toggle_value_state(self, value: str):
        value = in_kebab_format( value ) if self._KEBAB_CASE else value
        value_id = self.get_value_id(value)
        return self.toggle_row_state( value_id )

    def get_value_state(self, value: str) -> bool:
        value = in_kebab_format( value ) if self._KEBAB_CASE else value
        value_id = self.get_value_id(value)
        return not self.is_deleted( value_id )
