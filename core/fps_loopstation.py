from kivy.core.audio import SoundLoader # Para sound
from core.microphone_recorder import MicrophoneRecorder

from config.paths import TEMP_DIR

BPM_IN_SECONDS = int(60)
AUDIO_NAME_PREFIX = "track-"

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
        self.bpm = 120
        self.beats_per_bar = 3
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
        self.recording = False
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
        if self.is_first_beat:
            print( f"first-beat     {self.current_beat}" )
        elif self.is_last_beat:
            print( f"last-beat      {self.current_beat}" )
        elif self.is_another_beat:
            print( f"another-beat   {self.current_beat}" )




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
        return self.count_sample_sound >= self.sample_sound_limit

    def temp_sound_limit_reached(self):
        return self.count_temp_sound >= self.temp_sound_limit

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

        count = self.count_temp_sound
        limit = self.temp_sound_limit
        if sample:
            count = self.count_sample_sound
            limit = self.sample_sound_limit
        insert_track = not( count > limit )

        # Guardando
        if insert_track or update_track:
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
            self.count_saved_track += 1
            if sample:
                self.count_sample_sound += 1
            else:
                self.count_temp_sound += 1

        # Retornar estados de interes.
        return {
            "update_track": update_track,
            "insert_track": insert_track,
            "track_id": track_id,
            "count": count,
            "limit": limit
        }



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
                print(
                 f"--{signal}: {track_id} | sample {track['sample']} | `{track['source']}`--\n"
                 f"--length_in_fps: {count_fps}/{track['length_in_fps']}`--"
                )




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
        if not self.some_track_is_in_focus() and self.temp_sound_limit_reached():
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
            self.is_the_recorder_limit_activated() and
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
                str( TEMP_DIR.joinpath( sound_name ) )
            )
            self.microphone_recorder.stop()
            dict_save_track = self.save_track(
                track_id=number_of_track, path=self.microphone_recorder.WAVE_OUTPUT_FILENAME,
                sample=False, loop=True
            )
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
            print( f"++{text} | {info}++" )




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
            text = "**starting-timer: "
        elif dict_timer_signal['completed'] and dict_timer_signal["count_fps"] > 0:
            text = "**stopping-timer: "
        if text != None:
            text += (
             f"count {dict_timer_signal['count_fps']} | limit {self.timer_in_fps}**"
            )
            print(text)




    def update_all_data(self):
        '''
        Actualizar todos los datos necesarios para el looping
        '''
        self.update_metronome_settings()
        self.update_timer_duration()
        self.update_recorder_limit()





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

