from .base_repository import BaseRepository

class LanguageRepository(BaseRepository):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, column_id="language_id", column_value="code", kebab_case=True, **kwargs)

    def update_code(self, language_id:int, code:str):
        return self.update_value( language_id, code )

    def insert_code(self, code:str):
        return self.insert_value( code )

    def code_exists(self, language_id:int, code: str) -> bool:
        return self.value_exists( language_id, code )

    def get_code_id(self, code:str) -> int | None:
        return self.get_value_id( code )

    def save_code(self, code:str):
        return self.save_value( code )

    def toggle_code_state(self, code:str):
        return self.toggle_value_state( code )

    def get_code_state(self, code:str):
        return self.get_value_state( code )
