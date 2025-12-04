from kivy.core.audio import SoundLoader # Para sound

BPM_IN_SECONDS = int(60)

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
        self.default_volume = 0.1
        self.dict_track = {}
        self.sample_limit = 3
        self.track_limit = 3


    def update_beat_duration(self):
        '''
        Depende de `bpm`, y `fps`
        '''
        self.beat_in_seconds = BPM_IN_SECONDS / self.bpm
        self.beat_in_fps = self.fps * (self.beat_in_seconds)

    def update_bar_duration(self):
        '''
        Depende de `beat_in_fps`
        '''
        self.bar_in_seconds = self.beat_in_seconds * self.beats_per_bar
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
        return SoundLoader.load( path )


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


    def save_track(self, track_id=0, path=str, loop=True, sample=False):
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
        sound = self.get_sound( path )
        self.set_sound_volume( sound, self.default_volume )
        self.dict_track.update(
            {
                track_id: {
                    "sound": sound,
                    "source": path,
                    "length": sound.length,
                    "volume": self.default_volume,
                    "mute": 0,

                    "loop": loop,
                    "sample": sample,
                    "focus": True,
                    "bars": self.get_seconds_to_bars( sound.length ),
                    "length_in_fps": sound.length*self.fps,
                    "count_fps": 0
                }
            }
        )





    def looping(self):
        '''
        La chamba principal
        '''
        # Determinar tempo actual
        self.determine_current_beat()

        # Track
        for track in self.dict_track.values():
            if track['loop']:
                playing = self.is_sound_playing( track['sound'] )
                if self.is_first_beat:
                    if not playing:
                        self.play_sound( track['sound'] )

                if track['count_fps'] >= track['length_in_fps']-1:
                    self.stop_sound( track['sound'] )

                playing = self.is_sound_playing( track['sound'] )
                if playing:
                    track['count_fps'] += 1
                else:
                    track['count_fps'] = 0


        # Contar fotogramas por segundo.
        self.count_fps_of_beat += 1
        self.count_fps += 1

        # Debug
        self.debug_metronome()
