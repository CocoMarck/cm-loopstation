from entities.isound_manager import ISoundManager
from core.android_sound_pool_alone import AndroidSoundPoolAlone
import pathlib

class SoundManagerAndroidPoolAlone(ISoundManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_sound(self, path: pathlib.Path):
        sound = AndroidSoundPoolAlone( path )
        sound.set_volume( self._DEFAULT_VOLUME )
        return sound

    def play_sound(self, sound):
        return sound.play()

    def stop_sound(self, sound):
        return sound.stop()

    def is_sound_playing(self, sound):
        return sound.is_playing()

    def set_sound_volume(self, sound, volume):
        return sound.set_volume( volume )

    def set_sound_default_volume(self, sound):
        return sound.set_volume( self._DEFAULT_VOLUME )

    def mute_sound(self, sound):
        return sound.set_volume( 0.0 )

    def get_sound_length(self, sound):
        return sound.get_length()
