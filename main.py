from core.text_util import ignore_text_filter, PREFIX_NUMBER

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
    label_compass_to_record = ObjectProperty(None)
    label_bpm = ObjectProperty(None)


    grid_tracks = ObjectProperty(None)

    button_play = ObjectProperty(None)
    button_stop = ObjectProperty(None)
    button_restart = ObjectProperty(None)

    togglebutton_automatic_stop = ObjectProperty(None)
    togglebutton_play_beat = ObjectProperty(None)

    textinput_compass_to_stop = ObjectProperty(None)
    textinput_timer = ObjectProperty(None)
    textinput_bpm = ObjectProperty(None)
    textinput_beats = ObjectProperty(None)

    metronome_container = ObjectProperty(None)

    # Variables para el metrnomo
    bpm = 120
    beats = 4 # Cantidad de tiempos
    count_beats = 0 # Contador de tiempos
    beat_in_fps = 0 # Tiempo individual.
    count = 0
    compass_in_fps = 0
    play_beat = False

    # Para dibujar el tempo
    circles = []

    # Cambio de tempo y sonidotos
    change_tempo = False
    change_compass = False
    first_beat = False
    last_beat = False
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
    timer_in_seconds = 0
    timer_in_fps = 0
    timer_count = 0

    # Detener segun x cantidad de compases
    record_compass_to_stop = 4
    record_force_stop = False
    record_automatic_stop = False

    current_save_sound_key = None

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
    def update_metronome_circles(self):
        # Establecer circulos
        self.circles.clear()
        self.metronome_container.clear_widgets()
        for x in range(0, self.beats):
            circle = LoopstationCircle()
            self.circles.append( circle )
            self.metronome_container.add_widget(circle)

    def set_circle_position(self, dt):
        pass
        '''
        # Posicionar
        first_position = [self.width * 0.4, self.height * 0.75]
        multipler = 0
        for circle in self.circles:
            circle.x = first_position[0] + circle.width * multipler
            circle.y = first_position[1]
            multipler += 1
        '''



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
        self.grid_tracks.clear_widgets()
        for key in self.sounds.keys():
            sound_values = self.sounds[key]

            label_name = Label( text=str(key) )
            self.grid_tracks.add_widget(label_name)

            label_compass = Label( text=f"compass: {round(sound_values['repeated-times'])}" )
            self.grid_tracks.add_widget( label_compass )


            if sound_values['loop']:
                state, text = "down", "play"
            else:
                state, text= "normal", "stop"
            togglebutton_play = ToggleButton( text=text, state=state )
            self.grid_tracks.add_widget( togglebutton_play )

            if sound_values['mute']:
                state = "down"
            else:
                state = "normal"
            togglebutton_mute = ToggleButton( text="mute", state=state )
            self.grid_tracks.add_widget( togglebutton_mute )

            slider_volume = Slider(
                min=0, max=100, value=int(sound_values['volume']*100), orientation='horizontal'
            )
            self.grid_tracks.add_widget( slider_volume )

            checkbox = CheckBox( group="focus" )
            checkbox.active = sound_values['focus']
            self.grid_tracks.add_widget(checkbox)

            self.dict_track_options[key] = [
                togglebutton_play, togglebutton_mute, slider_volume, checkbox
            ]


    def set_dict_track_values(self):
        '''
        Establecer el reproducir o no
        name:str, play:bool, mute:bool, volume:float, focus:bool
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
                'focus': checkbox.state == 'down'
            }
            self.dict_track_values.update( {key: nested_dict} )



    def update_compass(self):
        '''
        Establecer compass basado en fps
        '''
        self.compass_in_fps = self.beat_in_fps * self.beats

    def update_timer(self):
        '''
        Establecer timer basado en fps
        '''
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


    def get_times_in_loop(self, seconds):
        return ( seconds / (self.compass_in_fps/FPS) )


    def save_sound(
            self, name:str, sound:SoundLoader, loop=False, sample=False
        ):
        good_name = isinstance(name, str)
        good_sound = True #isinstance(sound, SoundLoader)
        good_loop = isinstance(loop, bool)

        save = good_name and good_sound and good_loop
        if save:
            length = sound.length
            self.sounds.update(
                {name:
                  {
                   'sound': sound,
                   'length': length,
                   'source': sound.source,
                   'loop': loop,
                   'volume': VOLUME,
                   'mute': False,
                   'sample': sample,
                   'repeated-times': self.get_times_in_loop( length ),
                   'focus': False
                  }
                }
            )

        self.init_sound_count_repeated_times()

        return save

    def update_tracks(self):
        for key in self.sounds.keys():
            values = self.sounds[key]
            values['sound'].stop()
            values['repeated-times'] = self.get_times_in_loop( values['length'] )
            values['volume'] = VOLUME
            values['mute'] = False


    def set_bpm(self):
        '''
        Establecer bpm, y inicializar todo.
        '''
        if self.bpm <= 0:
            self.bpm = 1
        self.beat_in_fps = FPS * (BPM_TO_SECONDS / self.bpm)
        self.update_compass()
        self.count = 0
        self.count_beats = 0
        self.update_tracks()
        self.init_sound_count_repeated_times()
        self.set_widget_tracks()


    def update_beats(self):
        '''
        Actualizar beats, inicializar y actualizar todo lo relacionado
        '''
        self.count = 0
        self.count_beats = 0
        self.update_compass()
        self.update_metronome_circles()
        self.update_tracks()
        self.init_sound_count_repeated_times()
        self.set_widget_tracks()



    def init_the_essential(self):
        self.update_metronome_circles()

        # Obtener datos adecuados
        self.set_bpm()
        self.update_timer()

        # Establecer contador de repetición
        self.init_sound_count_repeated_times()

        # Agregar samples
        #self.save_sound( "party", SAMPLE_SOUNDS[0], False, sample=True )
        #self.save_sound( "macaco", SAMPLE_SOUNDS[1], False, sample=True )
        #self.save_sound( "do-scale", SAMPLE_SOUNDS[2], False, sample=True )
        #self.save_sound( "metro", SAMPLE_SOUNDS[3], False, sample=True )

        # Reproductor de pistas
        self.set_widget_tracks()

        # Widgets
        self.on_play_beat(
            self.togglebutton_play_beat, self.togglebutton_play_beat.state
        )


        self.textinput_compass_to_stop.text = str(self.record_compass_to_stop)
        self.textinput_bpm.text = str(self.bpm)
        self.textinput_beats.text = str(self.beats)

        self.on_bpm(self.textinput_bpm, self.textinput_bpm.text)
        self.set_record(self.record_button, self.record_button.state)
        self.on__record_compsss_to_stop(
            self.textinput_compass_to_stop, self.textinput_compass_to_stop.text
        )
        self.on_timer( self.textinput_timer, self.textinput_timer.text)

        # Bind widgets
        self.record_button.bind(state=self.set_record)
        self.togglebutton_automatic_stop.bind(state=self.on_record_automatic_stop)
        self.togglebutton_play_beat.bind(state=self.on_play_beat)

        self.textinput_compass_to_stop.bind(text=self.on__record_compsss_to_stop)
        self.textinput_bpm.bind(text=self.on_bpm)
        self.textinput_timer.bind(text=self.on_timer)
        self.textinput_beats.bind(text=self.on_beats)



    def set_record(self, obj, value):
        '''
        Variable que indica el estado de la grabación
        '''
        self.record = value == "down"
        if self.record:
            obj.text = "stop record"
        else:
            obj.text = "record"

    def on_play_beat(self, obj, value):
        self.play_beat = value == "down"


    def on_record_automatic_stop(self, obj, value):
        '''Establecer parar grabación de forma automatica'''
        self.record_automatic_stop = value == "down"

    def filter_text_to_number(self, textinput:str):
        '''
        Filtrar texto del numero de compases a grabar
        '''
        text = ignore_text_filter( textinput, PREFIX_NUMBER )
        if text == None:
            text = ""
            number = 0
        else:
            number = int(text)
        return number

    def on__record_compsss_to_stop(self, obj, text):
        '''
        Establecer la cantidad de compases a grabar
        '''
        self.record_compass_to_stop = self.filter_text_to_number( text )
        if self.record_compass_to_stop == 0:
            obj.text = ""
        else:
            obj.text = str(self.record_compass_to_stop)

    def on_bpm(self, obj, text):
        self.bpm = self.filter_text_to_number( text )
        if self.bpm == 0 or self.bpm > 200:
            self.bpm == 1
            obj.text = ""
        else:
            obj.text = str(self.bpm)
        self.set_bpm()

    def on_timer(self, obj, text):
        self.timer_in_seconds = self.filter_text_to_number( text )
        if self.timer_in_seconds > 30:
            self.timer_in_seconds = 0

        if self.timer_in_seconds == 0:
            obj.text = ""
        else:
            obj.text = str(self.timer_in_seconds)
        self.update_timer()

    def on_beats(self, obj, text):
        self.beats = self.filter_text_to_number( text )
        if self.beats <= 1 or self.beats >= 10:
            self.beats = 2
            obj.text = ""
        else:
            obj.text = str(self.beats)
        self.update_beats()




    # Actualizar todo
    def update(self, dt):
        '''
        Para la sincronización
        '''

        # Relacionado con el metronomo.
        self.change_tempo = self.count >= self.beat_in_fps

        ## Cambio de tempo
        if self.change_tempo:
            self.count = 0
            self.count_beats += 1

        ## Inicio de tempo
        self.init_tempo = self.count == 0

        ## Fin de compas
        self.change_compass = self.count_beats == self.beats
        if self.change_compass:
            self.count = 0
            self.count_beats = 0


        # Inicio de tempo | Tipo de inicio de tempo
        self.first_beat, self.last_beat, self.other_beat = False, False, False
        if self.init_tempo:
            self.first_beat = self.count_beats == 0
            self.last_beat = self.count_beats == self.beats-1
            self.other_beat = not(self.first_beat and self.last_beat)


        # Grabar | Sonidos grabados
        # Esta en bind -> `self.record = self.record_button.state == "down"`

        self.first_frame_of_recording = (
         self.record and self.timer_completed and self.record_count == 0 and self.first_beat
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
        if self.first_frame_of_recording:
            ## Solo guardar cuando esta en focus, o no esta en alcanzado limite de tracks
            ## Se establece nombre de archivo.
            sound_source = None
            for key in self.sounds.keys():
                sound = self.sounds[key]
                if sound['focus'] == True and not sound['sample']:
                    sound_source = sound['source']
                    self.current_save_sound_key = key
                    break
            new_sound = sound_source == None and not self.record_limit
            if new_sound:
                self.current_save_sound_key = f"track-{self.record_files_count}"
                sound_source = f"{TEMP_DIR}/{self.current_save_sound_key}.wav"

            self.microphone_recorder.WAVE_OUTPUT_FILENAME = sound_source

            if sound_source != None:
                self.microphone_recorder.record()
                if new_sound:
                    self.record_files_count += 1

        if (
            self.record == False and self.microphone_recorder.state == "record"
            and self.first_beat
        ):
            self.microphone_recorder.stop()
            sound_microphone = SoundLoader.load(self.microphone_recorder.WAVE_OUTPUT_FILENAME)
            sound_microphone.volume = VOLUME
            self.save_sound( self.current_save_sound_key, sound_microphone, True, sample=False )

            ## Actualizar lista de pistas
            self.set_widget_tracks()


        # Grabar | Cuenta los frames que sucedan al grabar
        if self.microphone_recorder.state == "record":
            self.record_count += 1
        else:
            self.record_count = 0


        # Grabar | Forzar detencción
        self.record_force_stop = (
            (self.record_count >= self.record_compass_to_stop*self.compass_in_fps) and
            (self.record_compass_to_stop >= 1) and self.record_automatic_stop
        )
        if self.record_force_stop:
            self.record_button.state = "normal"


        # Sonido | Reproducir o no pista/sample
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
                if sound.state == "stop" and self.first_beat:
                    sound.play()
                    debug_add_sounds = True

                if sound.state == "play":
                    self.sound_count_repeated_times[key] += 1
                count = self.sound_count_repeated_times[key]

                ## Alcanzo el limite
                if (
                    (self.get_sound_reached_repetition_limit(key) and self.first_beat) or
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
                elif sound.state == "stop" and self.first_beat:
                    # Reproducir
                    debug_play_sounds.append( [sound.source, 0, 0] )
                    sound.play()






        # Sonido | Metrónomo
        # Detección frame 1, del; Primer tempo, ultimo tempo, y otro tempo
        if self.play_beat:
            if self.first_beat:
                TEMPO_SOUNDS[0].play()
            elif self.last_beat or self.other_beat:
                TEMPO_SOUNDS[2].play()



        # Tracks | Opciones de reproducción
        self.set_dict_track_values()
        for key in self.dict_track_options.keys():
            # Valores necesarios
            sound_values = self.sounds[key]
            values = self.dict_track_values[key]

            update_track_options = False

            # Focus
            sound_values['focus'] = values['focus']

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
        if self.count_beats == 0:
            # Aun en primer tempo | Mostrar en verde
            rgb = RGB_FIRST_TEMPO
        else:
            # Otro tipo de tempo
            rgb = RGB_TEMPO
        self.circles[self.count_beats].color.rgb = rgb

        for index in range( 0, len(self.circles) ):
            if self.count_beats != index:
                # Circulos no perteneciente al tempo | Apagado
                self.circles[index].color.rgb = RGB_OFF_TEMPO


        ## Visual record y timer
        timer_count_in_seconds = (self.timer_in_fps -self.timer_count)/FPS
        if timer_count_in_seconds > 0 and self.record and self.microphone_recorder.state == "stop":
            self.record_button.text = f"record...{round(timer_count_in_seconds)}"

        ## Cantidad de pistas
        self.label_tracks.text = f"tracks {self.record_files_count}"


        # Contador de tempo
        self.count += 1




        # Debug
        ## Debug | Cambio de compas
        if self.change_compass:
            self.debug(f"--Fin de compas de {self.beats} beats--")

        ## Debug | Reproducir sonidos
        for source, count, limit in debug_play_sounds:
            self.debug(
             (
              f"++Reproducir: '{source}'++\n"
              f"++Contador: {count}++\n"
              f"++Limite: {limit}++"
             )
            )

        ## Debug | Cambio de beats
        if self.first_beat:
            self.debug("Primer pulso")
        elif self.last_beat:
            self.debug("Ultimo pulso")
        elif self.other_beat:
            self.debug(f"Pulso: {self.count_beats}")

        ## Debug | Boton grabador
        if self.first_frame_of_recording:
            self.debug(f"@@Grabando | Frame {self.record_count}@@")
        if self.record_force_stop:
            self.debug(f"Forzando parar en compas {self.record_compass_to_stop}")



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
