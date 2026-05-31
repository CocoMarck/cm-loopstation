from .base_repository import BaseRepository
from .format_text import format_tag_name

class TagRepository(BaseRepository):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, column_id="tag_id", column_value="name", format_text=True, **kwargs)

    def format_text(self, text:str):
        if text:
            return format_tag_name(text)
        return None

    def update_name(self, tag_id:int, name:str):
        return self.update_value( tag_id, name )

    def insert_name(self, name:str):
        return self.insert_value( name )

    def name_exists(self, tag_id:int, name: str) -> bool:
        return self.value_exists( tag_id, name )

    def get_name_id(self, name:str) -> int | None:
        return self.get_value_id( name )

    def save_name(self, name:str):
        return self.save_value( name )

    def toggle_name_state(self, name:str):
        return self.toggle_value_state( name )

    def get_name_state(self, name:str):
        return self.get_value_state( name )
