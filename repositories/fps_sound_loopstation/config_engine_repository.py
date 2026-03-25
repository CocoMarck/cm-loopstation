import tomllib, tomli_w
from entities.fps_sound_loopstation.config_engine import ConfigEngine

def load(config, path) -> ConfigEngine:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    config.beats = data["beats"]
    config.beats_limit = data["beats_limit"]
    config.bpm = data["bpm"]
    config.bpm_limit = data["bpm_limit"]
    config.volume = data["volume"]
    config.play_beat = data["play_beat"]
    config.fps = data["fps"]

    config.limit_record = data["limit_record"]
    config.record_bars = data["record_bars"]

    config.seconds = data["seconds"]

def save(config, path):
    data = {
        "beats":config.beats,
        "beats_limit":config.beats_limit,
        "bpm":config.bpm,
        "bpm_limit":config.bpm_limit,
        "volume":config.volume,
        "play_beat":config.play_beat,
        "fps":config.fps,

        "limit_record":config.limit_record,
        "record_bars":config.record_bars,

        "seconds":config.seconds,
    }
    with open(path, "wb") as f:
        tomli_w.dump(data, f)
    return True
