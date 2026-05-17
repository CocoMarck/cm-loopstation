from controllers.logging_controller import LoggingController
from entities.isound_manager import ISoundManager
from kivy.core.audio import SoundLoader # Para sound


class SoundManagerKivy(ISoundManager):
    def __init__( self, *args, **kwargs ):
        super().__init__(
            *args, name="SoundManagerKivy", filename="sound_manager_kivy", **kwargs
        )

    def is_sound_playing(self, sound):
        '''
        Determinar si se esta reproducioendo el sonido
        '''
        return sound.state == "play"

    def play_sound(self, sound):
        '''
        Reproducir sonido
        '''
        sound.play()

    def stop_sound(self, sound):
        '''
        Parar sonido
        '''
        sound.stop()

    def set_sound_volume(self, sound, volume=float(1) ):
        '''
        Establecer volumen a sonido
        '''
        sound.volume = self.validate_volume(volume)

    def set_sound_default_volume(self, sound):
        self.set_sound_volume( sound, self._DEFAULT_VOLUME)

    def mute_sound(self, sound):
        '''
        Establecer volumen a cero a sonido
        '''
        self.set_sound_volume( sound, volume=float(0) )

    def get_sound(self, path, mute=False):
        '''
        Obtener sound por path
        '''
        # SondLoader, pide un string como ruta.
        sound = SoundLoader.load( str(path) )
        if mute:
            self.mute_sound( sound )
        else:
            self.set_sound_volume( sound=sound, volume=self.volume )

        return sound


