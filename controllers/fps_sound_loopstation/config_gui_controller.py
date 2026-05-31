from entities.fps_sound_loopstation.config_gui import ConfigGUI
from repositories.fps_sound_loopstation.config_gui_repository import load, save
from repositories.fps_sound_loopstation.themes_repository import load as load_themes
from utils.colors import (
    get_rgba, invert_rgb, invert_rgba, rgba_to_normalized, scale_rgba, random_rgba,
    is_the_rgba_color_bright
)

RANDOM_TEXT = "random"

class ConfigGUIController():
    def __init__(self, config, path, themes_path):
        self.path = path
        self.themes_path = themes_path
        self.config = config
        self.load()

    def load(self):
        load( self.config, self.path )

    def update_numerical_view(self, value: bool):
        self.config.numerical_view = bool(value)
        return save(self.config, self.path)

    def load_themes(self):
        themes_with_random = load_themes( self.themes_path )
        themes_with_random.update( {RANDOM_TEXT: None} )
        return themes_with_random

    def get_theme_names(self):
        return list( self.load_themes().keys() )

    def get_rgba_theme(self, name: str):
        if name != RANDOM_TEXT:
            themes = self.load_themes()
            return themes[name]
        return random_rgba()

    def exists_theme(self, name: str):
        return name in self.get_theme_names()

    def update_theme(self, name: str):
        if self.exists_theme( name ):
            self.config.theme = str(name)
            return save(self.config, self.path)
        return False

    def get_current_rgba_theme(self):
        return self.get_rgba_theme( self.config.theme )
