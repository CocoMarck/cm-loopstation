from entities.isound_manager import ISoundManager

from jnius import autoclass


MediaPlayer = autoclass("android.media.MediaPlayer")


class SoundManagerAndroid(ISoundManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_sound(self, path: str):
        '''
        Debe aguantar path, y url directa.
        '''
        mp = MediaPlayer()
        mp.setDataSource(path)
        mp.prepare()

        return mp

    def play_sound(self, sound):
        if sound:
            sound.start()
            return True
        return False

    def stop_sound(self, sound):
        if sound:
            sound.pause()
            sound.seekTo(0)
            return True
        return False

    def is_sound_playing(self, sound):
        return sound.isPlaying()

    def set_sound_volume(self, sound, volume):
        if sound:
            volume = self.validate_volume(volume)
            sound.setVolume(float(volume), float(volume))
            return True
        return False

    def set_sound_default_volume(self, sound):
        return self.set_sound_volume( sound, self._DEFAULT_VOLUME )

    def mute_sound(self, sound):
        return self.set_sound_volume( sound, 0.0 )

    def get_sound_length(self, sound):
        if sound:
            return sound.getDuration() / 1000.0  # segundos
        return 0.0

