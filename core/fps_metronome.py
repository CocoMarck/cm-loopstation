from controller.logging_controller import LoggingController
from config.paths import TEMPO_FILES
from .sound_manager import SoundManager


BPM_IN_SECONDS = int(60)

class FPSMetronome():
    def __init__(
        self, fps=20, bpm=120, beats_per_bar=3, bpm_limit=0, beats_limit_per_bar=0,
        volume=1, play_beat=False, beat_play_mode='neutral',
        save_log=False, log_level="debug", verbose=True
    ):
        '''
        # Metronomo que jala en base a fps fijos.

        ## Atributos
        - `fps`: Fotogramas por segundo fijos.

        - `bpm`: Cantidad de bpm
        - `bpm_limit`: Limite en bpm
        - `beat_pear_bar`:` Cantidad de tempos por cada compas.
        - `beats_limit_per_bar`: Limite sobre cantidad de tempos por cada compas.
        - `current_beat`: Este contiene el beat actual a ser procesado.

        - `beat_in_seconds`: Equivalencia del tempo en segundos.
        - `beat_in_fps`: Equivalencia del tempo en fps.
        - `bar_in_seconds`: Equivalencia de un compas en segundos.
        - `bar_in_fps`: Equivalencia de un compas en fps.
        - `count_fps_of_beat`: Contar los fps sucedidos del tempo actual.

        ## Métodos
        - `set_default_bpm()`: Establece bpm default
        - `validate_and_set_bpm()`: Establece los datos relacionados al bpm.
        - `validate_and_set_beats_per_bar()`: Establece los datos relacionados con la cantidad de tempos por cada compas.
        - `calculate_beat_duration()`: Establece la duración de un tempo.
        - `calculate_bar_duration()`: Establece datos la duración del compas.
        - `set_settings()`: Establece los valores de los atributos
        - `reset_settings()`: Establece los valores de los atributos, y renicia contadores
        - `determine_current_beat()`: Determina beat actual, y retorna datos relacionados.
        - `debug_current_beat()`: Debugea el beat actual, y datos relacionados.
        - `update()`
        '''
        self.fps = fps

        # BPM y cantidad de latisdos
        self.__DEFAULT_BPM = 120
        self.bpm = bpm
        self.bpm_limit = bpm_limit
        self.beats_per_bar = beats_per_bar
        self.beats_limit_per_bar = beats_limit_per_bar
        self.current_beat = 0

        # En segundos reales
        self.beat_in_seconds = 0
        self.bar_in_seconds = 0

        # FPS
        self.count_fps_of_beat = 0
        self.beat_in_fps = 0
        self.bar_in_fps = 0

        # Actualizar valores para el metronomo
        self.set_settings()


        # Sonido, reproducir beat
        self.sound_manager = SoundManager( volume=volume )

        self.volume = volume
        self.play_beat = play_beat
        self.__DICT_BEAT_PLAY_MODE = {
            "neutral": 0,
            "emphasis_on_first": 1,
            "emphasis_on_last": 2,
            "emphasis_on_first_and_last": 3,
        }
        self.beat_play_mode = 0
        self.set_play_mode_beat( beat_play_mode )
        self.beat_sounds = []
        self.configure_and_get_beat_sounds()

        # Debug
        self.logging = LoggingController(
            name="FPSMetronome", filename="fps_metronome", verbose=verbose,
            log_level=log_level, save_log=save_log, only_the_value=True,
        )

    def set_default_bpm(self):
        self.bpm = self.__DEFAULT_BPM

    def validate_and_set_bpm(self):
        '''
        Establece bpm a unos aceptables, no crash.
        '''
        if self.bpm_limit > 0:
            if self.bpm > self.bpm_limit:
                self.bpm = self.bpm_limit
        if self.bpm <= 0:
            self.set_default_bpm()

    def validate_and_set_beats_per_bar(self):
        '''
        Esatablce beats a unos aceptables, no crash.
        '''
        if self.beats_limit_per_bar > 0:
            if self.beats_per_bar > self.beats_limit_per_bar:
                self.beats_per_bar = self.beats_limit_per_bar
        if self.beats_per_bar < 0:
            self.beats_per_bar = 0

    def calculate_beat_duration(self):
        '''
        Depende de `bpm`, y `fps`
        '''
        self.beat_in_seconds = BPM_IN_SECONDS / self.bpm
        self.beat_in_fps = self.fps * (self.beat_in_seconds)

    def calculate_bar_duration(self):
        '''
        Depende de `beat_in_fps`. El mas uno es porque empieza de cero, el contar de la beats
        '''
        self.bar_in_seconds = self.beat_in_seconds * (self.beats_per_bar+1)
        self.bar_in_fps = self.fps * self.bar_in_seconds

    def set_settings(self):
        '''
        Establecer configuración del metronomo
        '''
        self.validate_and_set_bpm()
        self.validate_and_set_beats_per_bar()
        self.calculate_beat_duration()
        self.calculate_bar_duration()




    def determine_current_beat(self):
        '''
        Determinar beat actual
        '''
        count_fps = self.count_fps_of_beat # FPS actual analizado

        # Beat
        change_beat = self.count_fps_of_beat >= self.beat_in_fps

        if change_beat:
            self.count_fps_of_beat = 0
            self.current_beat += 1
        first_frame_of_beat = self.count_fps_of_beat == 0

        # Compas
        reset_bar = self.current_beat == self.beats_per_bar+1
        if reset_bar:
            self.current_beat = 0
            self.count_fps_of_beat = 0

        # En que tempo va
        is_first_beat, is_last_beat, is_another_beat = False, False, False
        if first_frame_of_beat:
            is_first_beat = self.current_beat == 0
            is_last_beat = self.current_beat == self.beats_per_bar
            is_another_beat = (not is_first_beat) and (not is_last_beat)

        return {
            "change_beat": change_beat,
            "first_frame_of_beat": first_frame_of_beat,
            "reset_bar": reset_bar,
            "is_first_beat": is_first_beat,
            "is_last_beat": is_last_beat,
            "is_another_beat": is_another_beat,
            "current_beat": self.current_beat,
            "count_fps": count_fps
        }


    def debug_current_beat(self, signals:dict):
        text_current_beat = None
        if signals['is_first_beat']:
            text_current_beat = f"first-beat     {signals['current_beat']}/{self.beats_per_bar}"
        elif signals['is_last_beat']:
            text_current_beat = f"last-beat      {signals['current_beat']}/{self.beats_per_bar}"
        elif signals['is_another_beat']:
            text_current_beat = f"another-beat   {signals['current_beat']}/{self.beats_per_bar}"

        if signals['reset_bar']:
            self.logging.log(
                message=f"reset-bar | frames {signals['count_fps']}", log_type="debug"
            )
        if text_current_beat != None:
            self.logging.log( message=text_current_beat, log_type="info" )


    def reset_settings(self):
        '''
        Establce datos de metronomo y se reinician datos de conteo.
        '''
        self.set_settings()
        self.count_fps_of_beat = 0
        self.current_beat = 0




    def configure_and_get_beat_sounds(self):
        '''
        Obtener sonidos de beat
        '''
        self.beat_sounds.clear()
        for path in TEMPO_FILES:
            self.sound_manager.volume = self.volume
            self.beat_sounds.append( self.sound_manager.get_sound(path) )

    def set_beat_sound_volume(self):
        '''
        Establecer volumen a los beats
        '''
        for sound in self.beat_sounds:
            self.sound_manager.set_sound_volume( sound, self.volume )

    def set_play_mode_beat(self, mode="neutral"):
        '''
        Establecer modo de reproducción de beats
        '''
        if mode in self.__DICT_BEAT_PLAY_MODE:
            self.beat_play_mode = self.__DICT_BEAT_PLAY_MODE[mode]
        else:
            self.beat_play_mode = self.__DICT_BEAT_PLAY_MODE["neutral"]

    def play_beat_sound(self, number_of_beat=0):
        '''
        Reproducir beat
        '''
        play = number_of_beat in range(0, len(self.beat_sounds) )
        if play:
            self.sound_manager.play_sound( self.beat_sounds[number_of_beat] )
        return play


    def determine_emphasis_of_beat(self, signals):
        emphasis = False
        if self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['neutral']:
            emphasis = False

        if self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['emphasis_on_first']:
            emphasis = signals['is_first_beat']

        elif self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['emphasis_on_last']:
            emphasis = signals['is_last_beat']

        elif self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['emphasis_on_first_and_last']:
            emphasis = signals['is_first_beat'] or signals['is_last_beat']

        return {
            "emphasis": emphasis,
            "neutral": (not emphasis) and signals['first_frame_of_beat']
        }


    def beat_playback(self, emphasis_of_beat_signals):
        '''
        Reprodcción de beats
        '''
        sound_exists = False
        playing = False
        if self.play_beat:
            playing = True
            if emphasis_of_beat_signals['emphasis']:
                sound_exists = self.play_beat_sound(0)
            elif emphasis_of_beat_signals['neutral']:
                sound_exists = self.play_beat_sound(2)
            else:
                playing = False

        return {
            "emphasis": emphasis_of_beat_signals['emphasis'],
            "playing": playing,
            "sound_exists": sound_exists
        }


    def debug_beat_playback(self, signals):
        message = None
        log_type = "debug"
        if signals["playing"]:
            if signals["sound_exists"]:
                message = f"playing beat"
                if signals["emphasis"]:
                    message += " | emphasis"
                else:
                    message += " | neutral"
            else:
                message = f"there is no sound beat"
                log_type = "warning"

        if not message == None:
            self.logging.log(
                message=message, log_type=log_type
            )


    def get_seconds_to_bars( self, seconds=int ):
        '''
        Segundos a barras, a cantidad de compases
        '''
        return seconds/self.bar_in_seconds

    def get_seconds_to_fps(self, seconds:int ):
        '''
        Segundos a fps
        '''
        return seconds*self.fps

    def get_bars_to_fps(self, bars:int ):
        return self.bars_in_fps*bars






    def update(self):
        # Chamba principal
        signals = self.determine_current_beat()


        # Reproducir beat
        emphasis_of_beat_signals = self.determine_emphasis_of_beat( signals )
        beat_playback_signals = self.beat_playback( emphasis_of_beat_signals )


        # Sumar fps
        self.count_fps_of_beat += 1


        # Debug
        self.debug_current_beat( signals )
        self.debug_beat_playback( beat_playback_signals )


        return {
            'metronome': signals,
            'emphasis_of_beat': emphasis_of_beat_signals,
            'beat_playback': beat_playback_signals
        }
