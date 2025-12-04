BPM_IN_SECONDS = int(60)

class FPSLoopstation():
    def __init__(self):
        '''
        Este programa necesitara si o si que los fps sean fijos.

        **BPM y cantidad de latidos**
        - `bpm`: beats por minuto
        - `beats_per_compas`: cantidad de latidos que equivalen a un compass. Se cuenta desde cero.
        - `current_beat`: tempo actual

        **En segundos reales**
        - `beat_in_seconds`: bpm a segundos.
        - `compas_in_seconds`: equivalencia en segundos del compass.

        **FPS**
        - `beat_in_fps`: equivalencie de latido en fps
        - `compas_in_fps`: equivalencia del compass en fps
        - `count_fps`: contador de fps

        **Boleanos para determinar posición tempo actual**
        - `change_beat`: Cambiar de tempo.
        - `reset_compas`: Empezar de nuevo.
        - `is_first_beat`: Esta en el primer frame del beat.
        - `is_last_beat`: Esta en el ultimo frame del seundo beat.
        - `is_another_beat`: Esta en el primer frame de cualquire beat que no sea ni el ultimo ni el primero.
        '''
        self.fps = 20

        # BPM y cantidad de latisdos
        self.bpm = 120
        self.beats_per_compas = 3
        self.current_beat = 0

        # En segundos reales
        self.beat_in_seconds = 0
        self.compas_in_seconds = 0

        # FPS
        self.count_fps_of_beat = 0
        self.count_fps = 0
        self.beat_in_fps = 0
        self.compas_in_fps = 0

        # Boleanos para determinar posición tempo actual
        self.change_beat = False
        self.reset_compas = False
        self.is_first_beat = True
        self.is_last_beat = False
        self.is_another_beat = False

        # Actualizar valores para el metronomo
        self.update_metronome_settings()


    def update_beat_duration(self):
        '''
        Depende de `bpm`, y `fps`
        '''
        self.beat_in_seconds = BPM_IN_SECONDS / self.bpm
        self.beat_in_fps = self.fps * (self.beat_in_seconds)

    def update_compas_duration(self):
        '''
        Depende de `beat_in_fps`
        '''
        self.compas_in_fps = self.beat_in_fps * self.beats_per_compas

    def update_metronome_settings(self):
        '''
        '''
        self.update_beat_duration()
        self.update_compas_duration()

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
        self.reset_compas = self.current_beat == self.beats_per_compas+1
        if self.reset_compas:
            self.current_beat = 0
            self.count_fps_of_beat = 0

        # En que tempo va
        self.is_first_beat, self.is_last_beat, self.is_another_beat = False, False, False
        if self.first_frame_of_beat:
            self.is_first_beat = self.current_beat == 0
            self.is_last_beat = self.current_beat == self.beats_per_compas
            self.is_another_beat = (not self.is_first_beat) and (not self.is_last_beat)


    def debug_metronome(self):
        if self.is_first_beat:
            print( f"first-beat     {self.current_beat}" )
        elif self.is_last_beat:
            print( f"last-beat      {self.current_beat}" )
        elif self.is_another_beat:
            print( f"another-beat   {self.current_beat}" )



    def looping(self):
        '''
        La chamba principal
        '''
        # Determinar tempo actual
        self.determine_current_beat()

        # Contar fotogramas por segundo.
        self.count_fps_of_beat += 1
        self.count_fps += 1

        # Debug
        self.debug_metronome()
