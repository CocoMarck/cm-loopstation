# translation_util.py
# Inicializa DB, repos y controladores de langtags.
# Expone funciones convenientes como get_text().

# DB
from core.sqlite.standard_database import StandardDatabase
from core.sqlite.standard_table import StandardTable

# Models
from models.langtags.language import Language
from models.langtags.tag import Tag
from models.langtags.translation import Translation
from models.langtags.setting import Setting

# Repostories
from repositories.langtags.language_repository import LanguageRepository
from repositories.langtags.tag_repository import TagRepository
from repositories.langtags.translation_repository import TranslationRepository
from repositories.langtags.setting_repository import SettingRepository

# Controllers
from controllers.langtags.language_controller import LanguageController
from controllers.langtags.tag_controller import TagController
from controllers.langtags.translation_controller import TranslationController
from controllers.langtags.setting_controller import SettingController

# Paths
from config.langtags.paths import SCHEMAS_LANGTAGS_FILES, DATA_DIR, LANGTAGS_FILENAME

# Creación de db si no exite.
db = StandardDatabase( directory=DATA_DIR, name=LANGTAGS_FILENAME )
if not db.exists():
    print('Creando base de datos y aplicando schemas...')
    db.execute( 'PRAGMA foreign_keys = ON;', commit=True )
    for f in SCHEMAS_LANGTAGS_FILES:
        db.init_schema( f )

# Establecer controladores
table_language = StandardTable( database=db, name="languages" )
language_repository = LanguageRepository( table=table_language )
language_model = Language()
language_controller = LanguageController(language_repository, language_model)

tag_table = StandardTable( database=db, name="tags" )
tag_repository = TagRepository( table=tag_table )
tag_model = Tag()
tag_controller = TagController(tag_repository, tag_model)

setting_table = StandardTable( database=db, name="settings" )
setting_repository = SettingRepository( setting_table )
setting_model = Setting()
setting_controller = SettingController( setting_repository, setting_model )
setting_controller.get_current_language_model()

translation_table = StandardTable( database=db, name="translations" )
translation_repository = TranslationRepository(
    table=translation_table, language_repository=language_repository, tag_repository=tag_repository,
    setting_repository=setting_repository
)
translation_model = Translation()
translation_controller = TranslationController( translation_repository, translation_model )

# Funcion para obtener textitos
get_text = translation_controller.get_text

# Exportar solo lo que quieres usar fuera
__all__ = [
    "language_controller",
    "tag_controller",
    "translation_controller",
    "setting_controller",
    "get_text",
]
