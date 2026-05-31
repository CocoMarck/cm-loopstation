from entities.isound_manager import ISoundManager
from core.ffplay_sound import FFPlaySound
import atexit

class SoundManagerFFPlay(ISoundManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_sound(self, path: str):
        '''
        Debe aguantar path, y url directa.
        '''
        sound = FFPlaySound(path, self._DEFAULT_VOLUME)
        atexit.register(sound.stop)
        return sound

    def play_sound(self, sound):
        sound.play()

    def stop_sound(self, sound):
        sound.stop()

    def is_sound_playing(self, sound):
        return sound.is_playing()

    def set_sound_volume(self, sound, volume):
        sound.set_volume(self.validate_volume(volume))

    def set_sound_default_volume(self, sound):
        return self.set_sound_volume( sound, self._DEFAULT_VOLUME )

    def mute_sound(self, sound):
        return self.set_sound_volume( sound, 0.0 )

    def get_sound_length(self, sound) -> float:
        return sound.get_length()
