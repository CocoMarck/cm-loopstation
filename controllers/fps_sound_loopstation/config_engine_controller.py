from entities.fps_sound_loopstation.config_engine import ConfigEngine
from repositories.fps_sound_loopstation.config_engine_repository import load, save


class ConfigEngineController():
    def __init__(self, config, path):
        self.path = path
        self.config = config
        load( config, self.path )

    def positive_or_zero_number(self, number):
        if number < 0:
            raise "Numero menor a cero"
        return number

    def positive_number(self, number):
        if number <= 0:
            raise "Numero menor o igual a cero"
        return number

    def number_one_or_more(self, number):
        if number < 1:
            raise "Numero menor a uno"
        return number

    def update_beats(self, beats: int):
        self.config.beats = self.positive_or_zero_number( beats )
        return save( self.config, self.path )

    def update_beats_limit(self, beats_limit: int):
        self.config.beats_limit = self.positive_or_zero_number( beats_limit )
        return save( self.config, self.path )

    def update_bpm(self, bpm: int):
        self.config.bpm = self.number_one_or_more(bpm)
        return save( self.config, self.path )

    def update_bpm_limit(self, bpm_limit: int):
        self.config.bpm_limit = self.number_one_or_more(bpm_limit)
        return save( self.config, self.path )

    def update_play_beat(self, play_beat: bool):
        self.config.play_beat = play_beat
        return save( self.config, self.path )

    def update_fps(self, fps: int):
        self.config.fps = self.number_one_or_more(fps)
        return save( self.config, self.path )

    def update_volume(self, volume: float):
        self.config.volume = self.positive_number( volume )
        return save( self.config, self.path )


    def update_limit_record(self, limit_record: bool):
        self.config.limit_record = limit_record
        return save( self.config, self.path )

    def update_record_bars(self, bars):
        self.config.record_bars = self.positive_or_zero_number( bars )
        return save( self.config, self.path )


    def update_seconds(self, seconds):
        self.config.seconds = self.positive_or_zero_number( seconds )
        return save( self.config, self.path )
