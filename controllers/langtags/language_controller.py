from repositories.langtags.tag_repository import TagRepository
from .base_controller import BaseController
from models.langtags.language import Language

class LanguageController(BaseController):
    def __init__( self, *args, **kwargs ):
        super().__init__(*args, attributes={ "id": "language_id", "value": "code" }, **kwargs)
