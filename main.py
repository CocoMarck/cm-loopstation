# Kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import (
    ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

# Grabador de microfonillo
from core.microphone_recorder import MicrophoneRecorder

# Constantes necesarias
VOLUME = float(0.2)
FPS = float(60)
BPM_TO_SECONDS = int(60)

## Sonido
SOUNDS = []
TEMPO_SOUNDS = [
    SoundLoader.load('./resources/audio/tempo/tempo-1.ogg'),
    SoundLoader.load('./resources/audio/tempo/tempo-2.ogg'),
    SoundLoader.load('./resources/audio/tempo/tempo-3.ogg')
]
SOUNDS.extend(TEMPO_SOUNDS)
SAMPLE_SOUNDS = [
    SoundLoader.load('./resources/audio/sample/loop-01-party.ogg'),
    SoundLoader.load('./resources/audio/sample/loop-02-macaco.ogg')
]
SOUNDS.extend(SAMPLE_SOUNDS)

for sound in SOUNDS:
    sound.volume = VOLUME

TEMP_DIR = "./tmp"




# Objeto criculos del metronomo
class LoopstationCircle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (32,32)

        with self.canvas:
            self.color = Color(1,1,1,1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

        # Cuando cambie la posición o tamaño del widget → mover el círculo
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        '''
        Necesario para actualizar graficos, se usa en automatico.
        '''
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size


# Ventana, el loop del porgrama
class LoopstationWindow(Widget):
    '''
    El tempo de preferencia que sea un entero.
    '''
    # Objetos del `archivo.kv`
    record_button = ObjectProperty(None)
    label_timer = ObjectProperty(None)
    label_tracks = ObjectProperty(None)

    # Variables para el metrnomo
    bpm = 120
    tempos = 3 # Cantidad de tiempos
    count_tempos = 0 # Contador de tiempos
    tempo = FPS * (BPM_TO_SECONDS / bpm) # Tiempo individual.
    count = 0

    # Para dibujar el tempo
    circles = []

    # Cambio de tempo y sonidotos
    change_tempo = False
    change_compass = False
    first_tempo = False
    last_tempo = False
    init_tempo = False

    # Diccionario para sonidos a reproducir
    sound_name = str
    sounds = {
        "party": [SAMPLE_SOUNDS[0], False],
        "macaco": [SAMPLE_SOUNDS[1], False]
    }

    # Grabar
    microphone_recorder = MicrophoneRecorder( output_filename=f"{TEMP_DIR}/audio-test-1.wav" )
    record_files_count = 0
    record_files_limit = 4
    record_limit = False
    record_count = 0
    record = False

    # Temporizador
    timer_completed = False
    timer_in_seconds = 10
    timer_in_fps = timer_in_seconds*FPS
    timer_count = 0

    # Debug
    verbose = True


    def on_size(self, *args):
        '''
        Se llama automáticamente cada vez que cambia el tamaño del widget
        '''
        self.set_circle_position(0)

    def debug(self, text):
        if self.verbose:
            print(text)

    # Posicionar metronomo
    def init_metronome(self):
        # Establecer circulos
        self.circles.clear()
        for x in range(0, self.tempos+1):
            circle = LoopstationCircle()
            self.circles.append( circle )
            self.add_widget(circle)

        # Pruebas
        #self.sound_name = "party"
        #self.play_sound()

    def set_circle_position(self, dt):
        # Posicionar
        first_position = [self.width * 0.4, self.height * 0.75]
        multipler = 0
        for circle in self.circles:
            circle.x = first_position[0] + circle.width * multipler
            circle.y = first_position[1]
            multipler += 1



    def play_sound(self):
        if self.sound_name in self.sounds.keys():
            self.sounds[self.sound_name][1] = True

    def stop_sound(self):
        if self.sound_name in self.sounds.keys:
            self.sounds[self.sound_name][1] = False




    # Actualizar todo
    def update(self, dt):
        '''
        Para la sincronización
        '''

        # Relacionado con el metronomo.
        self.change_tempo = self.count >= self.tempo

        ## Cambio de tempo
        if self.change_tempo:
            self.count = 0
            self.count_tempos += 1

        ## Inicio de tempo
        self.init_tempo = self.count == 0

        ## Fin de compas
        self.change_compass = self.count_tempos == self.tempos+1
        if self.change_compass:
            self.count = 0
            self.count_tempos = 0


        # Grabar | Sonidos grabados
        self.record = self.record_button.state == "down"

        self.first_frame_of_recording = (
         self.record and self.timer_completed and self.record_count == 0
        )

        #if self.first_frame_of_recording:
            ## Forzar el metronomo al inicio, grabar de una
            #self.count = 0
            #self.count_tempos = 0

        ## Cuenta los frames que sucedan al grabar
        if self.record and self.timer_completed:
            self.record_count += 1
        else:
            self.record_count = 0

        ## Limite de record
        self.record_limit = self.record_files_count >= self.record_files_limit

        # Timer
        self.timer_completed = self.timer_count >= self.timer_in_fps
        if self.record:
            if not self.timer_completed:
                self.timer_count += 1
        else:
            self.timer_count = 0


        # Inicio de tempo | Tipo de inicio de tempo
        self.first_tempo, self.last_tempo, self.other_tempo = False, False, False
        if self.init_tempo:
            self.first_tempo = self.count_tempos == 0
            self.last_tempo = self.count_tempos == self.tempos
            self.other_tempo = not(self.first_tempo and self.last_tempo)


        # Grabar
        if self.first_frame_of_recording and not self.record_limit:
            self.microphone_recorder.record()
            self.record_files_count += 1
        if self.record == False and self.microphone_recorder.state == "record":
            ## Guardar archivo
            self.microphone_recorder.WAVE_OUTPUT_FILENAME = (
                f"{TEMP_DIR}/audio-test-{self.record_files_count}.wav"
            )

            self.microphone_recorder.stop()
            sound_microphone = SoundLoader.load(self.microphone_recorder.WAVE_OUTPUT_FILENAME)
            sound_microphone.volume = VOLUME
            self.sounds.update(
             {
              self.record_files_count: [ sound_microphone, True ]
             }
            )


        # Reproducir o no sonido
        debug_play_sounds = []
        for sound, loop in self.sounds.values():
            if loop:
                if self.first_frame_of_recording:
                    sound.stop()
                    sound.play()
                elif sound.state == "stop" and self.first_tempo:
                    # Reproducir
                    debug_play_sounds.append(sound.source)
                    sound.play()


        # Sonido | Metrónomo
        # Detección frame 1, del; Primer tempo, ultimo tempo, y otro tempo
        if self.first_tempo:
            TEMPO_SOUNDS[0].play()
        elif self.last_tempo or self.other_tempo:
            TEMPO_SOUNDS[2].play()




        # Visual | Métrononmo | Cambiar de color
        RGB_OFF_TEMPO = [1,1,1]
        RGB_FIRST_TEMPO = [0,1,0]
        RGB_TEMPO = [1,0,0]
        if self.count_tempos == 0:
            # Aun en primer tempo | Mostrar en verde
            rgb = RGB_FIRST_TEMPO
        else:
            # Otro tipo de tempo
            rgb = RGB_TEMPO
        self.circles[self.count_tempos].color.rgb = rgb

        for index in range( 0, len(self.circles) ):
            if self.count_tempos != index:
                # Circulos no perteneciente al tempo | Apagado
                self.circles[index].color.rgb = RGB_OFF_TEMPO


        ## Visual timer
        self.label_timer.text = f"Timer { round((self.timer_in_fps-self.timer_count)/FPS) }"

        ## Visual pistas
        self.label_tracks.text = f"Tracks {self.record_files_count}"


        # Contador de tempo
        self.count += 1




        # Debug
        ## Debug | Cambio de compas
        if self.change_compass:
            self.debug(f"--Fin de compas de {self.tempos+1} tempos--")

        ## Debug | Reproducir sonidos
        for name in debug_play_sounds:
            self.debug(f"++Reproducir: '{name}'++")

        ## Debug | Cambio de tempos
        if self.first_tempo:
            self.debug("Primer tempo")
        elif self.last_tempo:
            self.debug("Ultimo tempo")
        elif self.other_tempo:
            self.debug(f"Tempo: {self.count_tempos+1}")

        ## Debug | Boton grabador
        if self.first_frame_of_recording:
            self.debug(f"@@Grabando | Frame {self.record_count}@@")



'''
Constructor de aplicación
'''
Window.size = (960, 540)
Window.resizable = True
class LoopstationApp(App):
    def build(self):
        loopstation = LoopstationWindow()
        loopstation.init_metronome()
        Clock.schedule_interval(loopstation.update, 1.0/FPS)
        return loopstation

if __name__ == '__main__':
    LoopstationApp().run()
