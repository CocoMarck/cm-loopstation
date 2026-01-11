from config.paths import TEMP_DIR
from controller.logging_controller import LoggingController
from core.fps_sound_loopstation import FPSSoundLoopstation


class FPSSoundLoopstationRecorderController():
    def __init__(
        self, fps_sound_loopstation, recorder, recorder_path=TEMP_DIR, fileformat="wav",
        verbose=True, log_level="info", save_log=False
    ):
        '''
        Controlador de Recorder, de prefrencia un `MicrophoneRecorder()`, para adaptarlo a `FPSSoundLoopstation()`.
        Recomendado configurar el recorder y el loopstation antes de ponerlos como parametros.

        RecorderController no hace calculos referentes al loop y sus frames, nada de eso. Solo cosas referentes al recording.

        Ejemplo de uso:
        ```bash
        loopstation = FPSSoundLoopstation(
            fps=FPS, volume=0.05, play_beat=True, beat_play_mode='emphasis_on_first'
        )
        recorder_controller = FPSSoundLoopstationRecorderController(
            fps_sound_loopstation=loopstation, recorder=MicrophoneRecorder()
        )
        ```
        '''

        self.recorder = recorder
        self.fps_sound_loopstation = fps_sound_loopstation
        self.fps_metronome = fps_sound_loopstation.fps_metronome
        self.track_name_prefix = "track"
        self.fileformat = fileformat
        self.recorder_path = recorder_path

        # Relacionado con grabar, iniciar y parar
        self.record = False
        self.limit_record = False
        self.record_bars = 0
        self.record_count_fps = 0

        # Debug
        self.logging = LoggingController(
            name="FPSLoopstationRecorderController", filename="fps_loopstation_recorder_controller", verbose=verbose, log_level=log_level, save_log=save_log, only_the_value=True,
        )



    def record_track(self, metronome_signals):
        '''
        Grabar solo en la detección del primer tempo.
        Obtener señales de metronomo, y los enphasis del beat del metronomo.
        Contar FPS de grabación y determinar cantidad de compases a grabar, y parar automaticamente.
        Este método, hace la chamba principal.
        '''
        track_id = None
        some_track_is_in_focus = self.fps_sound_loopstation.some_temp_track_is_in_focus()
        saved_sound_limit_reached = (
            self.fps_sound_loopstation.temp_saved_sound_limit_reached() and
            self.recorder.state == "stop" and (not some_track_is_in_focus)
        )
        number_of_track = self.fps_sound_loopstation.count_temp_sound
        if saved_sound_limit_reached:
            # Limite de grabaciones alcanzado. Y no hay track temp en focus.
            # Obtener numero de pista en focus
            self.record = False
        if some_track_is_in_focus:
            number_of_track = self.fps_sound_loopstation.get_focused_temp_track_id()
            track_id = number_of_track


        limit_record = self.limit_record and (self.record_bars > 0)
        start_record = (
            metronome_signals['frame_before_the_bar'] and self.record and
            self.recorder.state == "stop"
        )
        if start_record:
            # Empezo el primer beat, esta activado el record, y esta no esta parador el recorder.
            self.recorder.output_filename = self.recorder_path.joinpath(
                f'{self.track_name_prefix}-{number_of_track}.{self.fileformat}'
            )
            self.recorder.record()

        count_fps = self.record_count_fps
        is_count_fps, stop_record, save_record_as_track = False, False, False
        if self.recorder.state == "record":
            # Esta grabando
            if limit_record:
                # Determinar limite, y si llego o paso el limite, parar grabación
                if count_fps >= self.fps_metronome.get_bars_to_fps(self.record_bars):
                    self.record = False

            is_count_fps = self.record
            stop_record = (not self.record) and (metronome_signals['frame_before_the_bar'])
            if is_count_fps:
                # Contar fps
                self.record_count_fps += 1
            else:
                self.record_count_fps = 0
            if stop_record:
                # Forzar parar grabación y guardar
                self.recorder.stop()
                self.fps_sound_loopstation.save_track(
                    track_id=track_id,
                    path=self.recorder.output_filename, loop=True, sample=False
                )

        # Señales
        return {
            'start_record': start_record,
            'limit_record': limit_record,
            'count_fps': count_fps,
            'is_count_fps': is_count_fps,
            'stop_record': stop_record,
            'number_of_track': number_of_track,
            'some_track_is_in_focus': some_track_is_in_focus,
            'saved_sound_limit_reached': saved_sound_limit_reached
        }


    def debug_record_track(self, record_track_signals):
        state = None
        if record_track_signals['start_record']:
            state = "starting recording"
        elif record_track_signals['stop_record']:
            if record_track_signals['saved_sound_limit_reached']:
                state = "limit reached"
            else:
                state = "stopping recording"

        if state != None:
            message = (
                f"{state} | number of track {record_track_signals['number_of_track']}"
                f" | limit record {record_track_signals['limit_record']}"
                f" | is_count_fps {record_track_signals['is_count_fps']}"
                f" | count fps {record_track_signals['count_fps']}"
                f" | focus {record_track_signals['some_track_is_in_focus']}"
            )
            self.logging.log( message=message, log_type="info" )




    def update(self, metronome_signals):
        # Chamba, lista.
        signals = self.record_track( metronome_signals=metronome_signals )

        self.debug_record_track( signals )

        return signals
