# Repository
from .base_repository import BaseRepository
from .language_repository import LanguageRepository
from .tag_repository import TagRepository
from .setting_repository import SettingRepository

# Utils
from utils.datetime_util import get_datetime_now
from utils.text_util import in_kebab_format

# Core
from core.locale_util import system_language

class TranslationRepository(BaseRepository):
    def __init__(
        self, *args,
        language_repository:LanguageRepository, tag_repository:TagRepository,
        setting_repository: SettingRepository,
        **kwargs
    ):
        super().__init__(*args, column_id="translation_id", column_value="value", format_text=False, **kwargs)

        self.language_repository = language_repository
        self.tag_repository = tag_repository
        self.setting_repository = setting_repository

    def update_value(
        self, translation_id:int, tag_id:int, language_id:int, value: str, is_deleted:bool=False
    ):
        try:
            cursor = self.database.execute(
                statement=(
                    f"UPDATE {self.table.name} SET tag_id=?, language_id=?, {self._COLUMN_VALUE}=?, updated_at=?, deleted_at=? WHERE {self._COLUMN_ID}=?;"
                ),  commit=True,
                params=(
                    tag_id, language_id, value, get_datetime_now(),
                    (get_datetime_now() if is_deleted else None), translation_id
                )
            )
            return True
        except:
            return False

    def insert_value(self, tag_id:int, language_id:int, value: str, is_deleted:bool=False):
        try:
            cursor = self.database.execute(
                statement=(
                    f"INSERT INTO {self.table.name} (tag_id,language_id,{self._COLUMN_VALUE},created_at,deleted_at) VALUES(?,?,?,?,?);"
                ),
                commit=True, params=(
                    tag_id,language_id,value,get_datetime_now(),
                    (get_datetime_now() if is_deleted else None)
                )
            )
            return True
        except:
            return False


    def translation_exists(self, translation_id:int, language_id:str, tag_id:int ) -> bool:
        try:
            cursor = self.database.execute(
                statement=(
                    f'SELECT 1 FROM {self.table.name} WHERE tag_id=? AND language_id=? AND {self._COLUMN_ID}=? LIMIT 1;'
                ),
                commit=False, params=(tag_id,language_id,translation_id)
            )
            return cursor.fetchone() is not None
        except:
            return False

    def get_translation_id(self, tag_id:int, language_id:int ) -> int | None:
        try:
            cursor = self.database.execute(
                statement=f"SELECT {self._COLUMN_ID} FROM {self.table.name} WHERE tag_id=? AND language_id=? LIMIT 1;",
                commit=False, params=(tag_id,language_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except:
            return None

    def get_translation_id_with_strings(self, tag_name, language_code):
        tag_id = self.tag_repository.get_value_id( tag_name )
        language_id = self.language_repository.get_value_id( language_code )
        return self.get_translation_id( tag_id, language_id )

    def save(
        self, translation_id:int, tag_id:int, language_id:int, value:str, is_deleted:bool=False
    ):
        exists_language_id = self.language_repository.exists(language_id)
        exists_tag_id = self.tag_repository.exists(tag_id)

        updated = False
        inserted = False
        if exists_language_id and exists_tag_id:
            if self.exists( translation_id ):
                updated = self.update_value( translation_id, tag_id, language_id, value, is_deleted )
            if updated == False:
                inserted = self.insert_value( tag_id, language_id, value, is_deleted )
        return updated or inserted

    def save_value(self, tag_name:str, language_code:str, value:str, is_deleted:bool=False):
        language_id = self.language_repository.get_code_id(language_code)
        tag_id = self.tag_repository.get_name_id(tag_name)
        translation_id = self.get_translation_id( tag_id, language_id )

        return self.save( translation_id, tag_id, language_id, value, is_deleted)

    def toggle_translation_state(self, tag_name:str, language_code:str):
        language_id = self.language_repository.get_code_id(language_code)
        tag_id = self.tag_repository.get_name_id(tag_name)
        translation_id = self.get_translation_id( tag_id, language_id )
        if translation_id is not None:
            deleted = self.is_deleted( translation_id )
            if deleted:
                return self.activate( translation_id )
            else:
                return self.deactivate( translation_id )
        return False

    def get_translation_state(self, tag_name:str, language_code:str) -> bool:
        language_id = self.language_repository.get_code_id(language_code)
        tag_id = self.tag_repository.get_name_id(tag_name)
        translation_id = self.get_translation_id( tag_id, language_id )
        return not self.is_deleted( translation_id )

    def get_language_code(self, language_id) -> str:
        return self.language_repository.get_value_with_id( language_id )

    def get_tag_name(self, tag_id):
        return self.tag_repository.get_value_with_id( tag_id )

    def get_value(self, tag_name:str, language_code:str) -> str | None:
        language_id = self.language_repository.get_code_id(language_code)
        tag_id = self.tag_repository.get_name_id(tag_name)
        translation_id = self.get_translation_id( tag_id, language_id )
        try:
            cursor = self.database.execute(
                statement=f"SELECT {self._COLUMN_VALUE} FROM {self.table.name} WHERE {self._COLUMN_ID}=? AND deleted_at IS NULL LIMIT 1;",
                commit=False, params=(translation_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"Error in get_value: {e}")
            return None

    def get_text(self, tag_name:str=None, language_code:str=None):
        '''
        Obtener texto si o si.
        '''
        if not language_code:
            if self.setting_repository.is_current_language_system():
                language_code = system_language()
            else:
                language_code = self.setting_repository.select_current_language_code()

        # Es none
        if self.language_repository.get_code_id(language_code) is None:
            language_code = self.setting_repository.select_default_language_code()

        if language_code == None: # No existe language code
            return in_kebab_format(tag_name)

        # Obtener texto
        value = self.get_value( tag_name, language_code )
        if value == None:
            language_code = self.setting_repository.select_default_language_code()

        if language_code is not None: # No existe default
            value = self.get_value( tag_name, language_code )

        # Retornar
        if value != None:
            return value
        return in_kebab_format(tag_name)

    def get_view_cursor(self):
        statement=(
            f"SELECT\n"
            f"    t.translation_id,\n"
            f"    g.name AS tag_name,\n"
            f"    l.code AS language_code,\n"
            f"    t.value,\n"
            f"    t.created_at,\n"
            f"    t.updated_at,\n"
            f"    t.deleted_at\n"
            f"FROM '{self.table.name}' t\n"
            f"JOIN '{self.tag_repository.table.name}' g ON t.tag_id = g.tag_id\n"
            f"JOIN '{self.language_repository.table.name}' l ON t.language_id = l.language_id;"
        )
        return self.database.execute( statement=statement, commit=False )

    def get_view_rows(self):
        cursor = self.get_view_cursor()
        return list( cursor.fetchall() )

    def get_view_columns(self):
        cursor = self.get_view_cursor()
        columns = []
        for cols in cursor.description:
            columns.append( cols[0] )
        return columns
