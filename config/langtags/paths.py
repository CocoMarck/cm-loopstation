from config.paths import resource_loader

SCHEMAS_DIR = resource_loader.base_dir.joinpath( 'schemas' )
SCHEMAS_LANGTAGS_DIR = SCHEMAS_DIR.joinpath( 'langtags' )
SCHEMAS_LANGTAGS_DIR_TREE = resource_loader.get_recursive_tree( SCHEMAS_LANGTAGS_DIR )
SCHEMAS_LANGTAGS_FILES = SCHEMAS_LANGTAGS_DIR_TREE['file']
DATA_DIR = resource_loader.data_dir
LANGTAGS_FILENAME = 'langtags.sqlite'


