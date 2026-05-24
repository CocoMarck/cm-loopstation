from controllers.logging_controller import LoggingController

class DTMetronome():
    def __init__(
        self, bpm=120, beats_per_bar=4, bpm_limit=200, beats_limit_per_bar=16,
        save_log=False, log_level="debug", verbose=True
    ):
        # Valores default
        self._INITIAL_BPM = bpm
        self._INITIAL_BEATS_PER_BAR = beats_per_bar
        self._INITIAL_BPM_LIMIT = bpm_limit
        self._INITIAL_BEATS_LIMIT_PER_BAR = beats_limit_per_bar

        # Valores usables
        self._bpm = None
        self._beats_per_bar = None

        self._bpm_limit = self._INITIAL_BPM_LIMIT
        self._beats_limit_per_bar = self._INITIAL_BEATS_LIMIT_PER_BAR

        self._current_beat = 1
        self._count_dt_of_beat = 0

        # Configurar
        self.set_settings(self._INITIAL_BPM, self._INITIAL_BEATS_PER_BAR)

        # Debug
        self.logging = LoggingController(
            name="DTMetronome", filename="dt_metronome", verbose=verbose,
            log_level=log_level, save_log=save_log, only_the_value=True,
        )
    def get_bpm_limit(self):
        return self._bpm_limit

    def get_bpm(self):
        return self._bpm

    def get_beats_limit_per_bar(self):
        return self._beats_limit_per_bar

    def get_beats_per_bar(self):
        return self._beats_per_bar

    def get_beat_interval(self):
        # Obtener duración de cada beat en segundos.
        return (60 / self._bpm)

    def get_beats_per_bar_interval(self):
        # Obtener duración de barra en segundos.
        return (self.get_beat_interval() * self._beats_per_bar)

    def get_seconds_to_bars( self, seconds:float ):
        '''
        Segundos a barras, a cantidad de compases
        '''
        return seconds/self.get_beats_per_bar_interval()

    def get_bars_to_seconds(self, seconds:int):
        return float(self.get_beats_per_bar_interval()*seconds)

    def get_current_beat(self):
        return self._current_beat

    def validate_and_get_bpm(self, bpm):
        '''
        Establece bpm a unos aceptables, no crash.
        '''
        if bpm <= 0:
            bpm = self._INITIAL_BPM
        if self._bpm_limit > 0:
            if bpm > self._bpm_limit:
                bpm = self._bpm_limit
        return bpm

    def validate_and_get_beats_per_bar(self, beats_per_bar):
        '''
        Esatablce beats a unos aceptables, no crash.
        '''
        if beats_per_bar < 1:
            beats_per_bar = 1
        if self._beats_limit_per_bar > 1:
            if beats_per_bar > self._beats_limit_per_bar:
                beats_per_bar = self._beats_limit_per_bar
        return beats_per_bar

    def set_bpm(self, bpm):
        self._bpm = self.validate_and_get_bpm(bpm)

    def set_beats_per_bar(self, beats_per_bar ):
        self._beats_per_bar = self.validate_and_get_beats_per_bar( beats_per_bar )

    def set_settings(self, bpm, beats_per_bar):
        '''
        Establecer configuración del metronomo
        '''
        self.set_bpm(bpm)
        self.set_beats_per_bar(beats_per_bar)

    def reset_counts(self):
        self._current_beat = 1
        self._count_dt_of_beat = 0

    def set_and_reset_settings(self, bpm, beats_per_bar):
        self.set_settings(bpm, beats_per_bar)
        self.reset_counts()

    def set_and_reset_to_default_settings(self):
        self.set_settings( self._INITIAL_BPM, self._INITIAL_BEATS_PER_BAR )
        self._bpm_limit = self._INITIAL_BPM_LIMIT
        self._beats_limit_per_bar = self._INITIAL_BEATS_LIMIT_PER_BAR
        self.reset_counts()


    def determine_current_beat(self, dt):
        change_beat = self._count_dt_of_beat >= self.get_beat_interval()

        if change_beat:
            self._count_dt_of_beat = 0
            self._current_beat += 1
        first_step_of_beat = self._count_dt_of_beat == 0

        # Delta time actual analizado
        real_count_dt_of_beat = self._count_dt_of_beat

        # Compas
        reset_bar = self._current_beat == self._beats_per_bar+1
        if reset_bar:
            self._current_beat = 1
            self._count_dt_of_beat = 0 # Esto no se deberia necesitar. Pero sepa la bola... Doble verificación.

        # En que tempo va
        is_first_beat, is_last_beat, is_another_beat = False, False, False
        if first_step_of_beat:
            is_first_beat = self._current_beat == 1
            is_last_beat = self._current_beat == self._beats_per_bar
            is_another_beat = (not is_another_beat) and (not is_last_beat)

        # Paso antes de la barra
        step_before_the_bar = (
            (self._current_beat == self._beats_per_bar) and
            (real_count_dt_of_beat >= self.get_beat_interval()-dt)
        )

        # Sumar dt
        self._count_dt_of_beat += dt

        return {
            "change_beat": change_beat,
            "first_step_of_beat": first_step_of_beat,
            "reset_bar": reset_bar,
            "is_first_beat": is_first_beat,
            "is_last_beat": is_last_beat,
            "is_another_beat": is_another_beat,
            "step_before_the_bar": step_before_the_bar,
            "current_beat": self._current_beat,
            "count_dt": real_count_dt_of_beat
        }

    def debug_current_beat(self, signals:dict):
        text_current_beat = None
        if signals['is_first_beat']:
            text_current_beat = f"first-beat     {signals['current_beat']}/{self._beats_per_bar}"
        elif signals['is_last_beat']:
            text_current_beat = f"last-beat      {signals['current_beat']}/{self._beats_per_bar}"
        elif signals['is_another_beat']:
            text_current_beat = f"another-beat   {signals['current_beat']}/{self._beats_per_bar}"

        if signals['reset_bar']:
            self.logging.log(
                message=f"reset-bar | seconds {self.get_beats_per_bar_interval()}", log_type="debug"
            )
        if signals['step_before_the_bar']:
            self.logging.log(
                message=f"step before the bar | count dt {signals['count_dt']}", log_type="debug"
            )
        if text_current_beat != None:
            self.logging.log( message=text_current_beat, log_type="info" )


    def update(self, dt):
        '''
        Chamba principal
        '''
        signals = self.determine_current_beat(dt)
        self.debug_current_beat(signals)

        return signals

