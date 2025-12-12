from controller.logging_controller import LoggingController

# Uso de para loopstation
from .microphone_recorder import MicrophoneRecorder
from .fps_metronome import (FPSMetronome, BPM_IN_SECONDS)
from .sound_manager import SoundManager

# Rutas en donde guardar los samples y temp audios
from config.paths import TEMP_DIR, TEMPO_FILES

# Constantes necesarias
AUDIO_NAME_PREFIX = "track-"


class FPSSoundLoopstation():
    def __init__(
        self, fps=20, bpm=120, beats_per_bar=3, beats_limit_per_bar=0, bpm_limit=0,
        volume=1, play_beat=False, beat_play_mode='neutral', save_log=False, log_level="debug", verbose=True, temp_saved_sound_limit=3, sample_saved_sound_limit=3,
    ):
        '''
        Para reproducir sonidos en bucle, sonidos sincronizados con el metronomo.
        '''
        self.fps_metronome = FPSMetronome(
            fps=fps, bpm=bpm, beats_per_bar=beats_per_bar, bpm_limit=bpm_limit,
            beats_limit_per_bar=beats_limit_per_bar, volume=volume, play_beat=play_beat, beat_play_mode=beat_play_mode, save_log=save_log, log_level=log_level, verbose=verbose
        )
        self.sound_manager = self.fps_metronome.sound_manager
        self.volume = volume



        # Pistas
        self.dict_tracks = {}

        self.count_saved_track = 0
        self.count_temp_sound = 0
        self.count_sample_sound = 0

        self.temp_saved_sound_limit = temp_saved_sound_limit
        self.sample_saved_sound_limit = sample_saved_sound_limit


        # Debug
        self.logging = LoggingController(
            name="FPSSoundLoopstation", filename="fps_sound_loopstation", verbose=True,
            log_level="debug", save_log=False, only_the_value=True,
        )


    def sample_saved_sound_limit_reached(self):
        '''
        Detectar si se alcanzo el limite de sonidos sample.
        '''
        return self.count_sample_sound >= self.sample_sound_limit+1


    def temp_saved_sound_limit_reached(self):
        '''
        Detectar si se alcanzo el limite de sonidos sample.
        '''
        return self.count_temp_sound >= self.temp_sound_limit+1


    def get_focused_track_id(self):
        '''
        Obtener track con focus actual.
        Solo se obtiene el primero que detecte. Se supono que solo debe haber focus en un track, no en varios.
        '''
        track_id = None
        for i in self.dict_track.keys():
            if self.dict_track[i]['focus']:
                track_id = i
                break
        return track_id


    def some_sample_track_is_in_focus(self):
        '''
        Algun sample track esta en focus
        '''
        track_id = self.get_focused_track_id()
        if isinstance(track_id, int ):
            return self.dict_track[track_id]['sample']
        else:
            return False


    def some_temp_track_is_in_focus(self):
        '''
        Algun temp track esta en focus
        '''
        track_id = self.get_focused_track_id()
        if isinstance(track_id, int ):
            return self.dict_track[track_id]['sample'] == False
        else:
            return False


    def save_track(self, track_id=None, path=str, loop=True, sample=True):
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
            limit_reached = not( self.temp_saved_sound_limit_reached() )

        # Guardando
        if limit_reached or update_track:
            sound = self.sound_manager.get_sound( path )
            self.sound_manager.set_sound_volume( sound, self.volume )
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
                        "bars": self.fps_metronome.get_seconds_to_bars( sound.length ),
                        "length_in_fps": self.fps_metronome.get_seconds_to_fps( sound.length ),
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


    def debug_save_track(self, save_track_signals):
        log_type = "debug"
        if save_track_signals["update_track"]:
            message = "update-track"
        elif save_track_signals["limit_reached"]:
            message = "insert-track"
        if not(
            save_track_signals["limit_reached"] and save_track_signals["update_track"]
        ):
            log_type = "warning"
            message = "limit-reached"

        message += (
         f" | track_id {save_track_signals['track_id']} | sample {save_track_signals['sample']}"
        )
        self.logging.log( message=message, log_type=log_type )


    def playback_track(self, metronome_signals):
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
                    self.sound_manager.mute_sound( track['sound'] )
                else:
                    self.sound_manager.set_sound_volume( track['sound'], track['volume'] )

                # Reproducir o parar | Contar fps
                playing = self.sound_manager.is_sound_playing( track['sound'] )
                starting = metronome_signals['is_first_beat'] and not playing
                if starting:
                    self.sound_manager.play_sound( track['sound'] )

                real_count_fps = track['count_fps']
                stopping = real_count_fps >= track['length_in_fps']-1
                if stopping:
                    self.sound_manager.stop_sound( track['sound'] )

                playing = self.sound_manager.is_sound_playing( track['sound'] )
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
            'track_starting': ids_track_starting,
            'track_stopping': ids_track_stopping
        }

    def debug_playback_track(self, playback_track_signals={}):
        for signal in playback_track_signals.keys():
            for track_id, count_fps in playback_track_signals[signal]:
                track = self.dict_track[track_id]
                text = (
                 f"{signal}: {track_id} | sample {track['sample']} | `{track['source']}` | "
                 f"length_in_fps: {count_fps}/{track['length_in_fps']}`"
                )
                self.logging.log( message=text, log_type="debug" )



    def get_tracks(self):
        # Obtener pistas
        return self.dict_track.values()

    def get_track_ids(self):
        # Obtenmer id de pistas
        return self.dict_track.keys()


    def play_track_loop(self, track_id):
        # Iniciar el loop de las pista
        self.dict_track[track_id]["loop"] = True

    def stop_track_loop(self, track_id):
        # Parar loop de pista
        self.dict_track[track_id]["loop"] = False


    def play_track_sound(self, track_id):
        # Reproducir pista
        self.sound_manager.play_sound( self.dict_track[track_id]['sound'] )

    def stop_track_sound(self, track_id):
        # Parar sonido de pista
        self.sound_manager.stop_sound( self.dict_track[track_id]['sound'] )
        self.dict_track[track_id]["count_fps"] = 0


    def break_track_loop(self, track_id):
        '''
        Quitar loop y parar sonido de pista
        '''
        self.stop_track_loop( track_id=track_id )
        self.stop_track_sound( track_id )

    def reset_track_loop(self, track_id):
        # Parar sonido y iniciar loop de pista
        self.break_track_loop( track_id )
        self.play_track_loop( track_id )


    def play_loop_of_all_tracks(self):
        # Reprodcir loop de todas las pistas
        for track_id in self.get_track_ids():
            self.play_track_loop( track_id )

    def stop_loop_of_all_tracks(self):
        # Parar loop detodas las pistas
        for track_id in self.get_track_ids():
            self.stop_track_loop( track_id )

    def break_loop_of_all_tracks(self):
        # Parar loop y sonido en todas las pistas
        for track_id in self.get_track_ids():
            self.break_track_loop( track_id )

    def reset_loop_of_all_tracks(self):
        # Parar sonido, y iniciar loop en todas las pistas
        for track_id in self.get_track_ids():
            self.reset_track_loop( track_id )


    def update_track_bars(self, track_id):
        '''
        Actualizar barras de pista
        '''
        track = self.dict_track[track_id]
        track["bars"] = self.fps_metronome.get_seconds_to_bars( track["length"] )
        track["length_in_fps"] = self.fps_metronome.get_seconds_to_fps( track["length"] )


    def set_track_volume(self, track_id, volume):
        # Establecer vulumen de pista
        self.dict_track[track_id]['volume'] = volume


    def update_tracks(self):
        '''
        Parar sonido y actualizar barras de pistas
        '''
        for track_id in self.get_track_ids():
            self.stop_track_sound( track_id )
            self.update_track_bars( track_id=track_id )

    def reset_tracks(self):
        '''
        Resetear loop, y establecer volumen de pistas
        '''
        for track_id in self.get_track_ids():
            self.reset_track_loop( track_id )
            self.set_track_volume( track_id=track_id, volume=self.volume)
            self.update_track_bars( track_id=track_id )




    def update(self):
        # Bucle
        metronome_signals = self.fps_metronome.update()

        # Pistas
        playback_track_signals = self.playback_track( metronome_signals )

        # Debug
        debug_playback_track(
            playback_track_signals
        )

