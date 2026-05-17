from controllers.logging_controller import LoggingController

class ISoundManager():
    def __init__(
        self, volume:float=1.0, verbose:bool=True, log_level:str="debug", save_log:bool=False,
        name:str="SoundManager", filename:str="sound_manager"
    ):
        self._DEFAULT_VOLUME = float(volume)
        self._MAX_VOLUME = float(1)
        self._MIN_VOLUME = float(0)
        self.volume = float(volume)

        # Debug
        self.logging = LoggingController(
            name=name, filename=filename, verbose=verbose,
            log_level=log_level, save_log=save_log, only_the_value=True,
        )

    def validate_volume(self, volume):
        if volume > self._MAX_VOLUME:
            volume = self._MAX_VOLUME
        elif volume < self._MIN_VOLUME:
            volume = self._MIN_VOLUME
        return volume

    def play_sound(self, sound):
        pass

    def stop_sound(self, sound):
        pass

    def get_sound(self, path):
        pass

    def is_sound_playing(self, sound):
        pass

    def set_sound_volume(self, sound, volume):
        pass

    def set_sound_default_volume(self, sound):
        pass

    def mute_sound(self, sound):
        pass
