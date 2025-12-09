from kivy.core.audio import SoundLoader # Para sound
from core.microphone_recorder import MicrophoneRecorder
from controller.logging_controller import LoggingController

from config.paths import TEMP_DIR, TEMPO_FILES

BPM_IN_SECONDS = int(60)
AUDIO_NAME_PREFIX = "track-"

# Sonidos
TEMPO_SOUNDS = []
for path in TEMPO_FILES:
    TEMPO_SOUNDS.append( SoundLoader.load( str(path) ) )



class FPSLoopstation():
    def __init__(self):
        '''
        Este programa necesitara si o si que los fps sean fijos.

        **BPM y cantidad de latidos**
        - `bpm`: beats por minuto
        - `beats_per_bar`: cantidad de latidos que equivalen a un bars. Se cuenta desde cero.
        - `current_beat`: tempo actual

        **En segundos reales**
        - `beat_in_seconds`: bpm a segundos.
        - `bar_in_seconds`: equivalencia en segundos del bars.

        **FPS**
        - `beat_in_fps`: equivalencie de latido en fps
        - `bar_in_fps`: equivalencia del bars en fps
        - `count_fps`: contador de fps

        **Boleanos para determinar posición tempo actual**
        - `change_beat`: Cambiar de tempo.
        - `reset_bar`: Empezar de nuevo.
        - `is_first_beat`: Esta en el primer frame del beat.
        - `is_last_beat`: Esta en el ultimo frame del seundo beat.
        - `is_another_beat`: Esta en el primer frame de cualquire beat que no sea ni el ultimo ni el primero.
        '''
        self.fps = 20

        # BPM y cantidad de latisdos
        self.__DEFAULT_BPM = 120
        self.bpm = self.__DEFAULT_BPM
        self.bpm_limit = 0
        self.beats_per_bar = 3
        self.beats_limit_per_bar = 0
        self.current_beat = 0

        # En segundos reales
        self.beat_in_seconds = 0
        self.bar_in_seconds = 0

        # FPS
        self.count_fps_of_beat = 0
        self.count_fps = 0
        self.beat_in_fps = 0
        self.bar_in_fps = 0

        # Boleanos para determinar posición tempo actual
        self.change_beat = False
        self.reset_bar = False
        self.first_frame_of_beat = False
        self.is_first_beat = True
        self.is_last_beat = False
        self.is_another_beat = False

        # Actualizar valores para el metronomo
        self.update_metronome_settings()

        # Pistas
        self.__DEFAULT_VOLUME = float(1)
        self.volume = self.__DEFAULT_VOLUME
        self.dict_track = {}
        self.count_saved_track = 0
        self.count_temp_sound = 0
        self.temp_sound_limit = 3
        self.count_sample_sound = 0
        self.sample_sound_limit = 3

        # Grabador
        self.microphone_recorder = MicrophoneRecorder()
        self.microphone_recorder.logging.verbose = True
        self.microphone_recorder.logging.log_level = "info"
        self.microphone_recorder.logging.save_log = False
        self.microphone_recorder.logging.set_config()
        self.recording = False
        self.limit_recording = False
        self.recorder_limit_in_bars = 0
        self.recorder_limit_in_seconds = 0
        self.recorder_limit_in_fps = 0
        self.recorder_count_fps = 0

        # Timer
        self.timer_in_seconds = 0
        self.timer_limit_in_seconds = 180
        self.timer_in_fps = 0
        self.timer_count_fps = 0
        self.update_timer_duration()

        # Debug
        self.logging = LoggingController(
            name="FPSLoopstation", filename="fps_loopstation", verbose=True,
            log_level="debug", save_log=False, only_the_value=True,
        )

        # Sonido, reproducir metronomo
        self.play_beat = False
        self.__DICT_BEAT_PLAY_MODE = {
            "neutral": 0,
            "emphasis_on_first": 1,
            "emphasis_on_last": 2,
            "emphasis_on_first_and_last": 3,
        }
        self.beat_play_mode = 0
        self.set_play_mode_beat( 'neutral' )
        self.beat_sounds = []
        self.update_beat_sounds()



    def update_bpm(self):
        '''
        Actualiza bpm a unos aceptables, no crash.
        '''
        if self.bpm_limit > 0:
            if self.bpm > self.bpm_limit:
                self.bpm = self.bpm_limit
        if self.bpm <= 0:
            self.bpm = self.__DEFAULT_BPM

    def update_beats_per_bar(self):
        '''
        Actualiza beats a unos aceptables, no crash.
        '''
        if self.beats_limit_per_bar > 0:
            if self.beats_per_bar > self.beats_limit_per_bar:
                self.beats_per_bar = self.beats_limit_per_bar
        if self.beats_per_bar < 0:
            self.beats_per_bar = 0


    def update_beat_duration(self):
        '''
        Depende de `bpm`, y `fps`
        '''
        self.beat_in_seconds = BPM_IN_SECONDS / self.bpm
        self.beat_in_fps = self.fps * (self.beat_in_seconds)

    def update_bar_duration(self):
        '''
        Depende de `beat_in_fps`. El mas uno es porque empieza de cero, el contar de la beats
        '''
        self.bar_in_seconds = self.beat_in_seconds * (self.beats_per_bar+1)
        self.bar_in_fps = self.fps * self.bar_in_seconds

    def update_metronome_settings(self):
        '''
        '''
        self.update_bpm()
        self.update_beats_per_bar()
        self.update_beat_duration()
        self.update_bar_duration()

    def determine_current_beat(self):
        '''
        Determinar beat actual
        '''

        # Beat
        self.change_beat = self.count_fps_of_beat >= self.beat_in_fps

        if self.change_beat:
            self.count_fps_of_beat = 0
            self.current_beat += 1
        self.first_frame_of_beat = self.count_fps_of_beat == 0

        # Compas
        self.reset_bar = self.current_beat == self.beats_per_bar+1
        if self.reset_bar:
            self.current_beat = 0
            self.count_fps_of_beat = 0

        # En que tempo va
        self.is_first_beat, self.is_last_beat, self.is_another_beat = False, False, False
        if self.first_frame_of_beat:
            self.is_first_beat = self.current_beat == 0
            self.is_last_beat = self.current_beat == self.beats_per_bar
            self.is_another_beat = (not self.is_first_beat) and (not self.is_last_beat)


    def debug_metronome(self):
        text = None
        if self.is_first_beat:
            text = f"first-beat     {self.current_beat}"
        elif self.is_last_beat:
            text = f"last-beat      {self.current_beat}"
        elif self.is_another_beat:
            text = f"another-beat   {self.current_beat}"
        if text != None:
            self.logging.log( message=text, log_type="info" )


    def reset_metronome(self):
        '''
        Actualiza detos de metronomo y se reinicia.
        '''
        self.update_metronome_settings()
        self.count_fps_of_beat = 0
        self.current_beat = 0





    def get_sound(self, path):
        '''
        Obtener sound por path
        '''
        # SondLoader, pide un string como ruta.
        return SoundLoader.load( str(path) )


    def play_sound(self, sound):
        sound.play()

    def stop_sound(self, sound):
        sound.stop()

    def set_sound_volume(self, sound, volume=float(1) ):
        if volume > 1:
            volume = 1
        elif volume < 0:
            volume = 0
        sound.volume = volume

    def mute_sound(self, sound):
        self.set_sound_volume( sound, volume=float(0) )

    def is_sound_playing(self, sound):
        return sound.state == "play"


    def get_seconds_to_bars( self, seconds=int ):
        return seconds/self.bar_in_seconds


    def sample_sound_limit_reached(self):
        return self.count_sample_sound >= self.sample_sound_limit+1

    def temp_sound_limit_reached(self):
        return self.count_temp_sound >= self.temp_sound_limit+1

    def get_focused_track_id(self):
        track_id = None
        for i in self.dict_track.keys():
            if self.dict_track[i]['focus']:
                track_id = i
                break
        return track_id

    def some_track_is_in_focus(self):
        return isinstance( self.get_focused_track_id(), int )

    def save_track(self, track_id=None, path=str, loop=True, sample=False):
        '''
        Guardar pista, cada pista tendra valores, indicados en un dict.
        Las pistas no se borran, por lo que sera necesario establecer un limite en la cantidad de pistas.

        - `sound`, objeto tipo sonido.
        - `source`, path.
        - `length`, tamaño en segundos del sound.
        - `sample`, indicar si es sample o no.
        - `loop`, si se reproduce o no en loop.
        - `volume`, volumen de track.
        - `mute`, establecer el volumen ne cero.
        - `focus`, pista seleccionada o no. Sirve para remplazar, borrar, o etc.
        '''
        # Actualizar o insertar. Determinar si se alcanzo el limite.
        update_track = track_id in self.dict_track.keys()
        if update_track:
            # Determinar si es un sample. Y si lo es ignorar remplazo de path
            sample = self.dict_track[track_id]["sample"]
            if not sample:
                path = self.dict_track[track_id]["source"]

        if track_id == None:
            track_id = self.count_saved_track

        if sample:
            limit_reached = not( self.sample_sound_limit_reached() )
        else:
            limit_reached = not( self.temp_sound_limit_reached() )

        # Guardando
        if limit_reached or update_track:
            sound = self.get_sound( path )
            self.set_sound_volume( sound, self.volume )
            self.dict_track.update(
                {
                    track_id: {
                        "sound": sound,
                        "source": path,
                        "length": sound.length,
                        "volume": self.volume,
                        "mute": 0,

                        "loop": loop,
                        "sample": sample,
                        "focus": False,
                        "bars": self.get_seconds_to_bars( sound.length ),
                        "length_in_fps": sound.length*self.fps,
                        "count_fps": 0
                    }
                }
            )

            # Contar cantidad de tracks, cantidad de samples y no samples
            if update_track == False:
                self.count_saved_track += 1
                if sample:
                    self.count_sample_sound += 1
                else:
                    self.count_temp_sound += 1

        # Retornar estados de interes.
        return {
            "track_id": track_id,
            "update_track": update_track,
            "limit_reached": limit_reached,
            "sample": sample
        }

    def debug_save_track(self, signals):
        log_type = "debug"
        if signals["update_track"]:
            message = "update-track"
        elif signals["limit_reached"]:
            message = "insert-track"
        if not( signals["limit_reached"] and signals["update_track"] ):
            log_type = "warning"
            message = "limit-reached"

        message += f" | track_id {signals['track_id']} | sample {signals['sample']}"
        self.logging.log( message=message, log_type=log_type )





    def playback_track(self):
        '''
        Reproduce las pistas, de manera sincronizada, y con comases determinados, por la duración en segundos del sonido.
        Depende de `determine_current_beat`

        Se enviara una señalillas de las pistas iniciado o parando. Se enviara su id.
        '''
        ids_track_starting = []
        ids_track_stopping = []
        for track_id in self.dict_track.keys():
            track = self.dict_track[track_id]
            if track['loop']:
                # Configurar adecuadamente track
                if track['mute']:
                    self.mute_sound( track['sound'] )
                else:
                    self.set_sound_volume( track['sound'], track['volume'] )

                # Reproducir o parar | Contar fps
                playing = self.is_sound_playing( track['sound'] )
                starting = self.is_first_beat and not playing
                if starting:
                    self.play_sound( track['sound'] )

                real_count_fps = track['count_fps']
                stopping = real_count_fps >= track['length_in_fps']-1
                if stopping:
                    self.stop_sound( track['sound'] )

                playing = self.is_sound_playing( track['sound'] )
                if playing:
                    track['count_fps'] += 1
                else:
                    track['count_fps'] = 0

                # Agregar ids de track iniciando o parando
                if starting:
                    ids_track_starting.append( [track_id, real_count_fps] )
                if stopping:
                    ids_track_stopping.append( [track_id, real_count_fps] )

        return {
            'starting': ids_track_starting,
            'stopping': ids_track_stopping
        }


    def debug_playback_track(self, dict_track_id_playing_signal={}):
        for signal in dict_track_id_playing_signal.keys():
            for track_id, count_fps in dict_track_id_playing_signal[signal]:
                track = self.dict_track[track_id]
                text = (
                 f"{signal}: {track_id} | sample {track['sample']} | `{track['source']}` | "
                 f"length_in_fps: {count_fps}/{track['length_in_fps']}`"
                )
                self.logging.log( message=text, log_type="debug" )


    def play_track_loop(self, track_id):
        self.dict_track[track_id]["loop"] = True

    def stop_track_loop(self, track_id):
        self.dict_track[track_id]["loop"] = False

    def break_track_loop(self, track_id):
        self.stop_track_loop( track_id=track_id )
        self.stop_sound( self.dict_track[track_id]["sound"] )

    def reset_track_loop(self, track_id):
        self.break_track_loop( track_id )
        self.play_track_loop( track_id )


    def play_loop_of_all_tracks(self):
        for track_id in self.dict_track.keys():
            self.play_track_loop( track_id )

    def stop_loop_of_all_tracks(self):
        for track_id in self.dict_track.keys():
            self.stop_track_loop( track_id )

    def break_loop_of_all_tracks(self):
        for track_id in self.dict_track.keys():
            self.break_track_loop( track_id )

    def reset_loop_of_all_tracks(self):
        for track_id in self.dict_track.keys():
            self.reset_track_loop( track_id )


    def update_track_bars(self, track_id):
        track = self.dict_track[track_id]
        track["bars"] = self.get_seconds_to_bars( track["length"] )
        track["length_in_fps"] = track["length"]*self.fps


    def update_tracks(self):
        for track_id in self.dict_track.keys():
            track = self.dict_track[track_id]
            self.stop_sound( track["sound"] )
            track["count_fps"] = 0
            self.update_track_bars( track_id=track_id )


    def reset_tracks(self):
        for track_id in self.dict_track.keys():
            track = self.dict_track[track_id]
            self.stop_sound( track["sound"] )
            track["loop"] = True
            track["volume"] = self.volume
            track["count_fps"] = 0
            self.update_track_bars( track_id=track_id )

    def get_tracks(self):
        return self.dict_track.values()





    def update_recorder_limit(self):
        self.recorder_limit_in_seconds = self.bar_in_seconds*self.recorder_limit_in_bars
        self.recorder_limit_in_fps = self.recorder_limit_in_seconds*self.fps

    def is_the_recorder_limit_activated(self):
        return self.recorder_limit_in_bars > 0

    def track_recording(self, dict_timer_signal):
        dict_recorder_signal = {
            "start_recording": False,
            "stop_recording": False,
            "sound_name": None,
            "count_fps": 0
        }
        if ( not self.some_track_is_in_focus() ) and ( self.temp_sound_limit_reached() ):
            # No se grabara, porque se alcanzo limite de audios. Y no hay focus en alguna pista.
            self.recording = False

        if (
            self.recording and self.is_first_beat and self.microphone_recorder.state == "stop" and
            dict_timer_signal['completed']
        ):
            # Empezar a grabar al inicio del compas
            # Indicar el limite actual.
            self.microphone_recorder.record()
            self.update_recorder_limit()
            dict_recorder_signal['start_recording'] = True
            dict_recorder_signal['count_fps'] = self.recorder_count_fps

        if (
            self.microphone_recorder.state == "record" and
            self.is_the_recorder_limit_activated() and self.limit_recording and
            self.recorder_count_fps >= self.recorder_limit_in_fps
        ):
            # Mandar señal para detener la grabación, en limite establecido.
            self.recording = False

        if self.recording == False and self.microphone_recorder.state == "record":
            # Detener, solo si se esta grabando.
            # Establecer nombre de archivo. Guardar pista.
            # Remplazar el sonido de la pista que tenga focus.
            if self.some_track_is_in_focus():
                number_of_track = self.get_focused_track_id()
            else:
                number_of_track = self.count_saved_track
            sound_name = f"{AUDIO_NAME_PREFIX}{number_of_track}.wav"
            self.microphone_recorder.WAVE_OUTPUT_FILENAME = (
                TEMP_DIR.joinpath( sound_name )
            )
            self.microphone_recorder.stop()
            dict_save_track_signals = self.save_track(
                track_id=number_of_track, path=self.microphone_recorder.WAVE_OUTPUT_FILENAME,
                sample=False, loop=True
            )
            self.debug_save_track( signals=dict_save_track_signals )
            dict_recorder_signal['stop_recording'] = True
            dict_recorder_signal['sound_name'] = sound_name
            dict_recorder_signal['count_fps'] = self.recorder_count_fps


        if self.microphone_recorder.state == "record":
            # Contar fps de grabación
            self.recorder_count_fps += 1
        else:
            # Establecer en cero la grabación.
            self.recorder_count_fps = 0

        return dict_recorder_signal


    def debug_track_recording(self, dict_recorder_signal ):
        text = None
        if dict_recorder_signal['start_recording']:
            text = 'start-recording'
        elif dict_recorder_signal['stop_recording']:
            text = 'stop-recording'
        if text != None:
            text_frames = f"frames {dict_recorder_signal['count_fps']}"
            if dict_recorder_signal['sound_name'] != None:
                info = f"{text_frames} | {dict_recorder_signal['sound_name']}"
            else:
                info = text_frames
            self.logging.log( message=f"{text} | {info}" , log_type="info" )





    def update_timer_duration(self):
        if self.timer_in_seconds > self.timer_limit_in_seconds:
            self.timer_in_seconds = self.timer_limit_in_seconds
        elif self.timer_in_seconds < 0:
            self.timer_in_seconds = 0
        self.timer_in_fps = self.timer_in_seconds*self.fps

    def timer(self):
        dict_timer_signal = {
            "completed": True,
            "count_fps": self.timer_count_fps
        }
        if self.recording:
            dict_timer_signal['completed'] = self.timer_count_fps >= self.timer_in_fps
            if not dict_timer_signal['completed']:
                self.timer_count_fps += 1
        else:
            self.timer_count_fps = 0
        return dict_timer_signal

    def debug_timer(self, dict_timer_signal):
        text = None
        if not dict_timer_signal['completed'] and dict_timer_signal["count_fps"] == 0:
            text = "starting-timer | "
        elif (
            dict_timer_signal['completed'] and (dict_timer_signal["count_fps"] > 0) and
            self.recorder_count_fps == 1
        ):
            text = "stopping-timer | "
        if text != None:
            text += (
             f"frames {dict_timer_signal['count_fps']}/{self.timer_in_fps}"
            )
            self.logging.log( message=text, log_type="info" )




    def get_beat_sounds(self):
        self.beat_sounds.clear()
        for path in TEMPO_FILES:
            self.beat_sounds.append( self.get_sound( path=path ) )

    def update_beat_sounds(self):
        self.get_beat_sounds()
        for sound in self.beat_sounds:
            self.set_sound_volume( sound, volume=self.volume )


    def play_beat_sound(self, number_of_beat=0):
        self.play_sound( self.beat_sounds[number_of_beat] )


    def set_play_mode_beat(self, mode="neutral"):
        if mode in self.__DICT_BEAT_PLAY_MODE:
            self.beat_play_mode = self.__DICT_BEAT_PLAY_MODE[mode]
        else:
            self.beat_play_mode = self.__DICT_BEAT_PLAY_MODE["neutral"]


    def beat_playback(self):
        emphasis = False
        if self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['neutral']:
            emphasis = False
        if self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['emphasis_on_first']:
            emphasis = self.is_first_beat
        elif self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['emphasis_on_last']:
            emphasis = self.is_last_beat
        elif self.beat_play_mode == self.__DICT_BEAT_PLAY_MODE['emphasis_on_first_and_last']:
            emphasis = self.is_first_beat or self.is_last_beat

        if emphasis:
            self.play_beat_sound(0)
        elif self.first_frame_of_beat:
            self.play_beat_sound(2)




    def update_all_data(self):
        '''
        Actualizar todos los datos necesarios para el looping
        '''
        self.update_metronome_settings()
        self.update_timer_duration()
        self.update_recorder_limit()
        self.update_tracks()
        self.update_beat_sounds()




    def reset_looping(self):
        self.reset_metronome()
        self.reset_tracks()


    def update_looping(self):
        self.reset_metronome()
        self.update_tracks()


    def looping(self):
        '''
        La chamba principal
        '''
        # Determinar tempo actual
        self.determine_current_beat()


        # Grabación
        # timer y recorder
        dict_timer_signal = self.timer()
        dict_recorder_signal = self.track_recording( dict_timer_signal=dict_timer_signal )


        # Reproduccion de Tracks
        dict_track_id_playing_signal = self.playback_track()


        # Sonido de metronomo
        if self.play_beat:
            self.beat_playback()


        # Contar fotogramas por segundo.
        self.count_fps_of_beat += 1
        #self.count_fps += 1 # Aun no se necesita.


        # Debug
        self.debug_timer( dict_timer_signal=dict_timer_signal )
        self.debug_track_recording( dict_recorder_signal=dict_recorder_signal )
        self.debug_playback_track( dict_track_id_playing_signal=dict_track_id_playing_signal )
        self.debug_metronome()

        return {
            "timer_signal": dict_timer_signal,
            "recorder_signal": dict_recorder_signal,
            "track_id_playing_signal": dict_track_id_playing_signal
        }

