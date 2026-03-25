from core.sqlite.standard_table import StandardTable
from .language_repository import LanguageRepository

class SettingRepository():
    def __init__(self, table: StandardTable ):

        self.table = table
        self.database = self.table.database
        self._COLUMN_ID = 'setting_id'
        self._COLUMN_PARAMETER = 'parameter_name'
        self._COLUMN_LANGUAGE_ID = "language_id"
        self._PARAMETER_DEFAULT_LANGUAGE = "default_language"
        self._PARAMETER_SYSTEM_LANGUAGE = "system_language"
        self._PARAMETER_CURRENT_LANGUAGE = "current_language"

    def update_parameter_language_id(self, parameter_name:str, language_id:int):
        try:
            cursor = self.database.execute(
                statement=(
                    f"UPDATE {self.table.name} SET {self._COLUMN_LANGUAGE_ID}=? WHERE {self._COLUMN_PARAMETER}=?;"
                ),  commit=True, params=( language_id, parameter_name )
            )
            return True
        except:
            return False

    def insert_parameter_language_id(self, parameter_name:str, language_id:int):
        try:
            cursor = self.database.execute(
                statement=(
                    f"INSERT INTO {self.table.name} ({self._COLUMN_PARAMETER}, {self._COLUMN_LANGUAGE_ID}) VALUES(?, ?);"
                ),
                commit=True, params=( parameter_name, language_id )
            )
            return True
        except:
            return False

    def update_parameter_language_code(self, parameter_name, language_code):
        try:
            cursor = self.database.execute(
                statement=(
                    f"UPDATE {self.table.name} SET {self._COLUMN_LANGUAGE_ID} = "
                    f"(SELECT l.language_id FROM languages l "
                    f"WHERE l.code=? AND l.deleted_at IS NULL) "
                    f"WHERE {self._COLUMN_PARAMETER}=?;"
                ), commit=True, params=(language_code, parameter_name)
            )
            return True
        except:
            return False

    def update_current_language_id(self, language_id:int ):
        return self.update_parameter_language_id( self._PARAMETER_CURRENT_LANGUAGE, language_id )

    def update_default_language_id(self, language_id:int ):
        return self.update_parameter_language_id( self._PARAMETER_DEFAULT_LANGUAGE, language_id )

    def update_system_language_id(self, language_id:int ):
        return self.update_parameter_language_id( self._PARAMETER_SYSTEM_LANGUAGE, language_id )

    def update_current_language_code(self, language_code:str ):
        if language_code == self._PARAMETER_DEFAULT_LANGUAGE:
            return self.update_current_language_id( self.select_default_language_id() )
        elif language_code == self._PARAMETER_SYSTEM_LANGUAGE:
            return self.update_current_language_id( self.select_system_language_id() )
        else:
            return self.update_parameter_language_code( self._PARAMETER_CURRENT_LANGUAGE, language_code )

    def update_default_language_code(self, language_code:str ):
        return self.update_parameter_language_code( self._PARAMETER_DEFAULT_LANGUAGE, language_code )

    def update_system_language_code(self, language_code:str ):
        return self.update_parameter_language_code( self._PARAMETER_SYSTEM_LANGUAGE, language_code )

    def select_parameter_id(self, parameter_name:str) -> int | None:
        try:
            cursor = self.database.execute(
                statement=(
                    f"SELECT {self._COLUMN_ID} FROM {self.table.name} WHERE " f"{self._COLUMN_PARAMETER}=?"
                ), commit=False, params=(parameter_name,),
            )
            value = cursor.fetchone()
            return value[0]
        except:
            return None

    def select_parameter_language_id(self, parameter_name:str) -> int | None:
        try:
            cursor = self.database.execute(
                statement=(
                    f"SELECT {self._COLUMN_LANGUAGE_ID} FROM {self.table.name} WHERE " f"{self._COLUMN_PARAMETER}=?"
                ), commit=False, params=(parameter_name,),
            )
            value = cursor.fetchone()
            return value[0]
        except:
            return None

    def select_parameter_language_code(self, parameter_name) -> str | None:
        try:
            cursor = self.database.execute(
                statement=(
                    f"SELECT l.code FROM {self.table.name} s JOIN languages l "
                    f"ON s.{self._COLUMN_LANGUAGE_ID}=l.language_id "
                    f"WHERE s.{self._COLUMN_PARAMETER}=? AND l.deleted_at IS NULL"
                ), commit=False, params=(parameter_name,)
            )
            value = cursor.fetchone()
            return value[0]
        except:
            return None

    def select_current_language_id(self):
        return self.select_parameter_language_id( self._PARAMETER_CURRENT_LANGUAGE )

    def select_default_language_id(self):
        return self.select_parameter_language_id( self._PARAMETER_DEFAULT_LANGUAGE )

    def select_system_language_id(self):
        return self.select_parameter_language_id( self._PARAMETER_SYSTEM_LANGUAGE )

    def select_current_language_code(self):
        return self.select_parameter_language_code( self._PARAMETER_CURRENT_LANGUAGE )

    def select_default_language_code(self):
        return self.select_parameter_language_code( self._PARAMETER_DEFAULT_LANGUAGE )

    def is_current_language_system(self) -> bool:
        current_id = self.select_current_language_id()
        system_id = self.select_system_language_id()
        return current_id == system_id

    def is_current_language_default(self) -> bool:
        current_id = self.select_current_language_id()
        default_id = self.select_default_language_id()
        return current_id == default_id

    def get_language_codes(self) -> list:
        parameters = [
            self._PARAMETER_SYSTEM_LANGUAGE#, self._PARAMETER_DEFAULT_LANGUAGE,
        ]
        try:
            cursor = self.database.execute(
                statement="SELECT code FROM languages;", commit=False
            )
            codes = parameters
            for x in list( cursor.fetchall() ):
                codes.append( x[0] )
            return codes
        except:
            return []

    def get_language_ids(self):
        parameters = [
            self.select_system_language_id()#, self.select_default_language_id()
        ]
        try:
            cursor = self.database.execute(
                statement="SELECT language_id FROM languages;", commit=False
            )
            codes = parameters
            for x in list( cursor.fetchall() ):
                codes.append( x[0] )
            return codes
        except:
            return []
