import vlc
from entities.isound_manager import ISoundManager

class SoundManagerVLC(ISoundManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, name="SoundManagerVLC", filename="sound_manager_vlc", **kwargs)

        self._instance = vlc.Instance("--no-video")
        self._player = self._instance.media_player_new()
        self._player.audio_get_volume()
    
    def play_sound(self, sound):
        self._player.set_media(sound)
        self._player.play()
     
    def stop_sound(self, sound=None):
        self._player.stop()
    
    def is_sound_playing(self, sound=None):
        state = self._player.get_state()

        return state in [
            vlc.State.Opening,
            vlc.State.Buffering,
            vlc.State.Playing
        ]
     
    def set_sound_volume(self, sound=None, volume=1.0):
        self._player.audio_set_volume( int(self.validate_volume(volume)*100) )
        
    def set_sound_default_volume(self, sound=None):
        self._player.audio_set_volume( int(self._DEFAULT_VOLUME*100) )
    
    def mute_sound(self, sound=None):
        self._player.audio_set_volume( 0 )
    
    def get_sound(self, url):
        sound = self._instance.media_new(url)
        self.set_sound_volume( sound, self.volume )
        return sound

    def get_sound_length(self, sound) -> float:
        return sound.get_duration() / 1000.0
