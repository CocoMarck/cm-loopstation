# Grabador de microfonillo
from core.microphone_recorder import MicrophoneRecorder

# Constantes necesarias
VOLUME = float(0.2)
FPS = float(20)
BPM_TO_SECONDS = int(60)


## Sonido
from kivy.core.audio import SoundLoader
SOUNDS = []
TEMPO_SOUNDS = [
    SoundLoader.load('./resources/audio/tempo/tempo-1.ogg'),
    SoundLoader.load('./resources/audio/tempo/tempo-2.ogg'),
    SoundLoader.load('./resources/audio/tempo/tempo-3.ogg')
]
SOUNDS.extend(TEMPO_SOUNDS)
SAMPLE_SOUNDS = [
    SoundLoader.load('./resources/audio/sample/loop-01-party.ogg'),
    SoundLoader.load('./resources/audio/sample/loop-02-macaco.ogg'),
    SoundLoader.load('./resources/audio/sample/loop-03-do-scale.ogg'),
    SoundLoader.load('./resources/audio/sample/loop-04-metro.ogg')
]
SOUNDS.extend(SAMPLE_SOUNDS)

for sound in SOUNDS:
    sound.volume = VOLUME

TEMP_DIR = "./tmp"


# Primer forzar FPS
from kivy.config import Config
Config.set('graphics', 'vsync', '0')
Config.set('graphics', 'maxfps', str(FPS))

# App
from kivy.app import App

# Kivy
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.properties import (
    ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock




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
    vbox_tracks = ObjectProperty(None)
    button_play = ObjectProperty(None)
    button_stop = ObjectProperty(None)
    button_restart = ObjectProperty(None)

    # Variables para el metrnomo
    bpm = 120
    tempos = 4 # Cantidad de tiempos
    count_tempos = 0 # Contador de tiempos
    tempo = FPS * (BPM_TO_SECONDS / bpm) # Tiempo individual.
    count = 0
    compass_in_fps = 0

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
    sounds = {}
    sound_count_repeated_times = {}

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
    timer_in_fps = 0
    timer_count = 0

    # Diccionario | Contenedor de tracks
    dict_track_options = {}
    dict_track_values = {}

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
        for x in range(0, self.tempos):
            circle = LoopstationCircle()
            self.circles.append( circle )
            self.add_widget(circle)

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


    def set_dict_track_options(self):
        self.dict_track_options.clear()
        for key in self.sounds.keys():
            self.dict_track_options.update( {key: []} )


    def set_widget_tracks(self):
        '''
        Agragar widgets al scroll

        Se llama al inicio del probrama, y cada stop de grabación.
        '''
        self.set_dict_track_options()
        self.vbox_tracks.clear_widgets()
        for key in self.sounds.keys():
            sound_values = self.sounds[key]

            hbox = BoxLayout(orientation="horizontal")

            label_name = Label( text=str(key) )
            hbox.add_widget(label_name)

            label_compass = Label( text=f"compass: {round(sound_values['repeated-times'])}" )
            hbox.add_widget( label_compass )


            if sound_values['loop']:
                state, text = "down", "play"
            else:
                state, text= "normal", "stop"
            togglebutton_play = ToggleButton( text=text, state=state )
            hbox.add_widget( togglebutton_play )

            if sound_values['mute']:
                state = "down"
            else:
                state = "normal"
            togglebutton_mute = ToggleButton( text="mute", state=state )
            hbox.add_widget( togglebutton_mute )

            slider_volume = Slider(
                min=0, max=100, value=int(sound_values['volume']*100), orientation='horizontal'
            )
            hbox.add_widget( slider_volume )

            checkbox = CheckBox()
            hbox.add_widget(checkbox)

            self.vbox_tracks.add_widget( hbox )
            self.dict_track_options[key] = [
                togglebutton_play, togglebutton_mute, slider_volume, checkbox
            ]


    def set_dict_track_values(self):
        '''
        Establecer el reproducir o no
        name:str, play:bool, mute:bool, volume:float, active:bool
        '''
        self.dict_track_values.clear()
        for key in self.dict_track_options.keys():
            togglebutton_play, togglebutton_mute, slider_volume, checkbox = (
                self.dict_track_options[key]
            )
            nested_dict = {
                'play': togglebutton_play.state == 'down',
                'mute': togglebutton_mute.state == 'down',
                'volume': slider_volume.value_normalized,
                'active': checkbox.state == 'down'
            }
            self.dict_track_values.update( {key: nested_dict} )



    def update_compass(self):
        self.compass_in_fps = self.tempo * self.tempos

    def update_timer(self):
        self.timer_in_fps = self.timer_in_seconds*FPS

    def init_sound_count_repeated_times(self):
        for key in self.sounds.keys():
            self.sound_count_repeated_times.update( {key: 0} )

    def get_sound_repetition_limit(self, name):
        return self.sounds[name]['repeated-times']*self.compass_in_fps

    def get_sound_reached_repetition_limit(self, name):
        limit = self.get_sound_repetition_limit(name)
        count = self.sound_count_repeated_times[name]
        return count >= limit


    def save_sound(
            self, name:str, sound:SoundLoader, loop=False
        ):
        good_name = isinstance(name, str)
        good_sound = True #isinstance(sound, SoundLoader)
        good_loop = isinstance(loop, bool)

        save = good_name and good_sound and good_loop
        if save:
            repeated_times = ( sound.length / (self.compass_in_fps/FPS) )
            self.sounds.update(
                {name:
                  {
                   'sound': sound,
                   'loop': loop,
                   'volume': VOLUME,
                   'mute': False,
                   'repeated-times': repeated_times
                  }
                }
            )

        self.init_sound_count_repeated_times()

        return save



    def init_the_essential(self):
        self.init_metronome()

        # Obtener datos adecuados
        self.update_compass()
        self.update_timer()

        # Agregar samples
        self.save_sound( "party", SAMPLE_SOUNDS[0], False )
        self.save_sound( "macaco", SAMPLE_SOUNDS[1], False )
        self.save_sound( "do-scale", SAMPLE_SOUNDS[2], False )
        self.save_sound( "metro", SAMPLE_SOUNDS[3], False )

        # Establecer contador de repetición
        self.init_sound_count_repeated_times()

        # Reproductor de pistas
        self.set_widget_tracks()

        # Pruebas
        #self.sound_name = "party"
        #self.play_sound()




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
        self.change_compass = self.count_tempos == self.tempos
        if self.change_compass:
            self.count = 0
            self.count_tempos = 0


        # Inicio de tempo | Tipo de inicio de tempo
        self.first_tempo, self.last_tempo, self.other_tempo = False, False, False
        if self.init_tempo:
            self.first_tempo = self.count_tempos == 0
            self.last_tempo = self.count_tempos == self.tempos-1
            self.other_tempo = not(self.first_tempo and self.last_tempo)


        # Grabar | Sonidos grabados
        self.record = self.record_button.state == "down"

        self.first_frame_of_recording = (
         self.record and self.timer_completed and self.record_count == 0 and self.first_tempo
        )

        ## Limite de record
        self.record_limit = self.record_files_count >= self.record_files_limit

        # Timer
        self.timer_completed = self.timer_count >= self.timer_in_fps
        if self.record:
            if not self.timer_completed:
                self.timer_count += 1
        else:
            self.timer_count = 0


        # Grabar o guardar grabación
        if self.first_frame_of_recording and not self.record_limit:
            # Grabando
            self.microphone_recorder.record()
            self.record_files_count += 1
        if (
            self.record == False and self.microphone_recorder.state == "record"
            and self.first_tempo
        ):
            ## Guardar archivo
            self.microphone_recorder.WAVE_OUTPUT_FILENAME = (
                f"{TEMP_DIR}/audio-test-{self.record_files_count}.wav"
            )

            self.microphone_recorder.stop()
            sound_microphone = SoundLoader.load(self.microphone_recorder.WAVE_OUTPUT_FILENAME)
            sound_microphone.volume = VOLUME
            self.save_sound( str(self.record_files_count), sound_microphone, True )

            ## Actualizar lista de pistas
            self.set_widget_tracks()


        # Grabar | Cuenta los frames que sucedan al grabar
        if self.microphone_recorder.state == "record":
            self.record_count += 1
        else:
            self.record_count = 0


        # Reproducir o no sonido
        debug_play_sounds = []
        for key in self.sounds.keys():
            # Variables necesarias
            sound = self.sounds[key]['sound']
            loop = self.sounds[key]['loop']
            repeated_times = self.sounds[key]['repeated-times']

            # Reproducción Modo contador de repeticione
            ## Determinar el contar o no
            count_play = repeated_times > 0

            if count_play and loop:
                ## Repeticiones | Sonido se reproduce, contador de reprodución
                #if add_seconds:
                debug_add_sounds = False
                if sound.state == "stop" and self.first_tempo:
                    sound.play()
                    debug_add_sounds = True

                if sound.state == "play":
                    self.sound_count_repeated_times[key] += 1
                count = self.sound_count_repeated_times[key]

                ## Alcanzo el limite
                if (
                    (self.get_sound_reached_repetition_limit(key) and self.first_tempo) or
                    self.first_frame_of_recording
                ):
                    debug_add_sounds = True
                    self.sound_count_repeated_times[key] = 0
                    sound.stop()
                    sound.play()

                ## Debug | Determinar agregar soniditos
                if debug_add_sounds:
                    debug_play_sounds.append(
                     [
                      sound.source, count, self.get_sound_repetition_limit(key)
                     ]
                    )

            # Reproducción por unicamente detección de tempo
            if loop and not count_play:
                if self.first_frame_of_recording:
                    sound.stop()
                    sound.play()
                elif sound.state == "stop" and self.first_tempo:
                    # Reproducir
                    debug_play_sounds.append( [sound.source, 0, 0] )
                    sound.play()






        # Sonido | Metrónomo
        # Detección frame 1, del; Primer tempo, ultimo tempo, y otro tempo
        if self.first_tempo:
            TEMPO_SOUNDS[0].play()
        elif self.last_tempo or self.other_tempo:
            TEMPO_SOUNDS[2].play()



        # Tracks | Opciones de reproducción
        self.set_dict_track_values()
        for key in self.dict_track_options.keys():
            # Valores necesarios
            sound_values = self.sounds[key]
            values = self.dict_track_values[key]

            update_track_options = False

            # Volumen
            ## Mute o no
            sound_values['mute'] = values['mute']
            if values["mute"]:
                sound_values['sound'].volume = 0
            else:
                sound_values['sound'].volume = values['volume']

            # Reproducir o no
            if values['play'] and not sound_values['loop']:
                update_track_options = True
                sound_values['loop'] = True
            elif not values['play'] and sound_values['loop']:
                update_track_options = True
                sound_values['loop'] = False

                sound_values['sound'].stop()
                self.sound_count_repeated_times[key] = 0

            # Actualizar track widget options o no
            if update_track_options:
                self.set_widget_tracks()






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
            self.debug(f"--Fin de compas de {self.tempos} tempos--")

        ## Debug | Reproducir sonidos
        for source, count, limit in debug_play_sounds:
            self.debug(
             (
              f"++Reproducir: '{source}'++\n"
              f"++Contador: {count}++\n"
              f"++Limite: {limit}++"
             )
            )

        ## Debug | Cambio de tempos
        if self.first_tempo:
            self.debug("Primer tempo")
        elif self.last_tempo:
            self.debug("Ultimo tempo")
        elif self.other_tempo:
            self.debug(f"Tempo: {self.count_tempos}")

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
        loopstation.init_the_essential()

        Clock.schedule_interval(loopstation.update, 1.0/FPS)

        return loopstation

if __name__ == '__main__':
    LoopstationApp().run()
