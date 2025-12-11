from controller.logging_controller import LoggingController
from kivy.core.audio import SoundLoader # Para sound


class SoundManager():
    def __init__(
            self, volume=float(1), verbose=True, log_level="debug", save_log=False
        ):
        self.__DEFAULT_VOLUME = float(1)
        self.__MAX_VOLUME = float(1)
        self.__MIN_VOLUME = float(0)
        self.volume = volume

        # Debug
        self.logging = LoggingController(
            name="SondLoader", filename="sound_loader", verbose=verbose,
            log_level=log_level, save_log=save_log, only_the_value=True,
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
        if volume > self.__MAX_VOLUME:
            volume = self.__MAX_VOLUME
        elif volume < self.__MIN_VOLUME:
            volume = self.__MIN_VOLUME
        sound.volume = volume

    def set_sound_default_volume(self, sound):
        self.set_sound_volume( sound, self.__DEFAULT_VOLUME)

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


