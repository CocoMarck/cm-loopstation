from entities.isound_manager import ISoundManager
from config.paths import TEMPO_FILES

class BeatController:
    def __init__(self, sound_manager: ISoundManager ):
        self.sound_manager = sound_manager
        self.sound = self.sound_manager.get_sound(TEMPO_FILES[0])

    def update(self, metronome_signals):
        if metronome_signals["first_step_of_beat"]:
            self.sound_manager.play_sound( self.sound )
