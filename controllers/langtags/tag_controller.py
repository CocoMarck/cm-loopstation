from repositories.langtags.tag_repository import TagRepository
from .base_controller import BaseController
from models.langtags.tag import Tag

class TagController(BaseController):
    def __init__( self, *args, **kwargs ):
        super().__init__(*args, attributes={ "id": "tag_id", "value": "name" }, **kwargs)
