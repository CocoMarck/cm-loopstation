import tomllib, tomli_w
from entities.fps_sound_loopstation.config_gui import ConfigGUI

def load(config, path) -> ConfigGUI:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    config.theme = data["theme"]
    config.numerical_view = data["numerical_view"]

def save(config, path):
    data = {
        "theme":config.theme,
        "numerical_view":config.numerical_view,
    }
    with open(path, "wb") as f:
        tomli_w.dump(data, f)
    return True
