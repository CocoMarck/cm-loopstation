from controller.logging_controller import LoggingController

BPM_IN_SECONDS = int(60)

class FPSMetronome():
    def __init__(
        self, fps=20, bpm=120, beats_per_bar=3, bpm_limit=0,
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
        self.beats_limit_per_bar = 0
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


    def update(self):
        # Chamba principal
        metronome_signals = self.determine_current_beat()

        # Sumar fps
        self.count_fps_of_beat += 1

        # Debug
        self.debug_current_beat(metronome_signals)

        return metronome_signals
