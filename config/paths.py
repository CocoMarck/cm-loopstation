from utils import ResourceLoader

resource_loader = ResourceLoader()
TEMP_DIR = resource_loader.base_dir.joinpath('tmp')
AUDIO_DIR = resource_loader.resources_dir.joinpath( 'audio' )
TEMPO_DIR = AUDIO_DIR.joinpath( 'tempo' )
SAMPLE_DIR = AUDIO_DIR.joinpath( 'sample' )

DICT_SAMPLE_DIR = resource_loader.get_recursive_tree( SAMPLE_DIR )
SAMPLE_FILES = DICT_SAMPLE_DIR['file']

DICT_TEMPO_DIR = resource_loader.get_recursive_tree( TEMPO_DIR )
TEMPO_FILES = sorted( DICT_TEMPO_DIR["file"] )

ICON = resource_loader.get_icon('fps-sound-loopstation.png')
