from functools import partial

from core.microphone_recorder import MicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from core.fps_timer import FPSTimer
from controller.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController

from config.paths import SAMPLE_FILES


# Constantes necesarias
VOLUME = float(1)
FPS = float(20)


## Colores
RGB_OFF_TEMPO = [1,1,1]
RGB_FIRST_TEMPO = [0,1,0]
RGB_ANOTHER_TEMPO = [1,0,0]


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


# Estilo molon
from kivy.lang import Builder
kv = '''
#:import Window kivy.core.window.Window
#<BoxLayout>
    #size_hint_y: None
    #height: dp( min(Window.width, Window.height)*0.1 )
#<ScrollView>
    #size_hint_y: None
    #height: dp( min(Window.width, Window.height)*0.1 )


<Label>:
    font_size: min(Window.width, Window.height) * 0.05
<TextInput>
    font_size: min(Window.width, Window.height) * 0.05
<ToggleButton>:
    font_size: min(Window.width, Window.height) * 0.05


<LoopstationWindow>:
    record_button: record
    label_timer: timer_text
    label_tracks: tracks_text
    label_tracks_number: tracks_number
    label_record_bars: record_bars_text
    label_center: center_label

    label_bpm: text_bpm
    slider_bpm: bpm_slider


    grid_tracks: track_container

    button_play: play
    button_stop: stop
    button_restart: restart

    togglebutton_limit_record: limit_record
    togglebutton_play_beat: option_play_beat

    slider_record_bars: record_bars
    slider_timer: timer_slider
    slider_beats: beats_slider

    metronome_container: metronome_box

    BoxLayout:
        width: root.width
        height: root.height*0.5
        y: root.height*0.5

        orientation: "vertical"

        # Fila 1
        ## circulos del Metronomo
        BoxLayout:
            id: metronome_box
            orientation: "horizontal"

        # Fila 2
        BoxLayout:
            orientation: "horizontal"

            ## timer
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: timer_text
                    text: "timer"
                Slider:
                    id: timer_slider

            ## Beats
            BoxLayout:
                orientation: "horizontal"
                Label:
                    text: "beats"
                Slider:
                    id: beats_slider

            ## BPM
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: text_bpm
                    text: "bpm"
                Slider:
                    id: bpm_slider

        # Fila 3
        BoxLayout:
            orientation: "horizontal"

            ## compases a grabar
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: record_bars_text
                    text: "bars"

                TextInput:
                    id: record_bars

            ## tracks
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: tracks_text
                    text: "tracks"
                Label:
                    id: tracks_number
                    text: "0"

        # Fila 4
        BoxLayout:
            ## Widgets
            orientation: "horizontal"

            # Col 1
            ToggleButton:
                id: option_play_beat
                text: "play beat"
                state: "down"

            ## Grabar
            ToggleButton:
                id: record
                text: "record"

            ## Opcion Parar grabación por numero de compass
            ToggleButton:
                id: limit_record
                text: "limit bars"

        BoxLayout:
            ## Widgets
            orientation: "horizontal"

            ## Opciones de reproducción de tracks
            Button:
                id: play
                text: 'play'

            Button:
                id: stop
                text: 'stop'

            Button:
                id: restart
                text: 'restart'


    # Segunda mitad de window
    # Scroll | Contenedor de Pistas
    ScrollView:
        width: root.width
        height: root.height*0.5
        y: 0
        do_scroll_x: True
        do_scroll_y: True

        # CheckBox Tracks
        GridLayout:
            id: track_container
            cols: 6

            size_hint_y: None
            height: self.minimum_height

            row_default_height: dp( min(Window.width, Window.height) * 0.1 )
            row_force_default: True

    # Timer
    FloatLayout:
        Label:
            id: center_label
            center_x: root.center_x
            center_y: root.center_y
            opacity: 1

'''
Builder.load_string(kv)




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
        min_size = min(self.size)
        good_size = [ min_size, min_size ]
        self.ellipse.size = good_size

        good_pos = [0, 0]
        good_pos[0] = self.x + (self.width -good_size[0]) / 2
        good_pos[1] = self.y + (self.height -good_size[1]) / 2
        self.ellipse.pos = good_pos


# Ventana, el loop del porgrama
class LoopstationWindow(Widget):
    '''
    El tempo de preferencia que sea un entero.
    '''
    # Objetos del `archivo.kv`
    record_button = ObjectProperty(None)

    label_timer = ObjectProperty(None)
    label_tracks = ObjectProperty(None)
    label_tracks_number = ObjectProperty(None)
    label_record_bars = ObjectProperty(None)
    label_bpm = ObjectProperty(None)
    label_center = ObjectProperty(None)


    grid_tracks = ObjectProperty(None)

    button_play = ObjectProperty(None)
    button_stop = ObjectProperty(None)
    button_restart = ObjectProperty(None)

    togglebutton_limit_record = ObjectProperty(None)
    togglebutton_play_beat = ObjectProperty(None)

    slider_record_bars = ObjectProperty(None)
    slider_timer = ObjectProperty(None)
    slider_bpm = ObjectProperty(None)
    slider_beats = ObjectProperty(None)

    metronome_container = ObjectProperty(None)

    circles = []

    # FPSLoopstation
    loopstation = FPSSoundLoopstation(
        fps=FPS, volume=VOLUME, play_beat=True, beat_play_mode='emphasis_on_first',
        beats_per_bar=3, beats_limit_per_bar=9, bpm_limit=200
    )
    metronome = loopstation.fps_metronome
    recorder_controller = FPSSoundLoopstationRecorderController(
        fps_sound_loopstation=loopstation, recorder=MicrophoneRecorder()
    )
    recorder_controller.limit_record = True
    recorder_controller.record_bars = 1

    # Timer
    timer = FPSTimer( fps=FPS, seconds=10, activate=True )


    # Posicionar metronomo
    def update_metronome_circles(self):
        # Establecer circulos
        self.circles.clear()
        self.metronome_container.clear_widgets()
        for x in range(0, self.metronome.beats_per_bar+1):
            circle = LoopstationCircle()
            self.circles.append( circle )
            self.metronome_container.add_widget(circle)


    def set_slider_bpm(self):
        self.slider_bpm.value = self.metronome.bpm

    def set_slider_beats(self):
        self.slider_beats.value = self.metronome.beats_per_bar

    def set_textinput_record_bars(self):
        self.slider_record_bars.text = str(self.recorder_controller.record_bars)

    def set_togglebutton_play_beat(self):
        state = "up"
        if self.metronome.play_beat:
            state = "down"
        self.togglebutton_play_beat.state = state

    def set_togglebutton_limit_record(self):
        state = "normal"
        if self.recorder_controller.limit_record:
            state = "down"
        self.togglebutton_limit_record.state = state

    def set_label_tracks_number(self):
        self.label_tracks_number.text = str(self.loopstation.count_temp_sound)




    def on_play_beat(self, obj, value):
        self.metronome.play_beat = value == "down"


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


    def on_limit_record(self, obj, state):
        self.recorder_controller.limit_record = state == "down"
        self.set_togglebutton_limit_record()




    def on_track_loop(self, track_id, widget):
        if widget.state == "down":
            self.loopstation.play_track_loop( track_id=track_id )
        else:
            self.loopstation.break_track_loop( track_id=track_id )

    def on_track_mute(self, track_id, widget):
        track = self.loopstation.get_track(track_id)
        track['mute'] = (widget.state == "down")

    def on_track_volume(self, track_id, widget, value):
        track = self.loopstation.get_track(track_id)
        track['volume'] = value

    def on_track_focus(self, track_id, widget, active):
        track = self.loopstation.get_track(track_id)
        track['focus'] = active


    def set_widget_track_options(self):
        '''
        Establecer widgets
        '''
        self.grid_tracks.clear_widgets()
        for track_id in self.loopstation.get_track_ids():
            track = self.loopstation.get_track( track_id )

            label_name = Label( text=str(track_id) )
            self.grid_tracks.add_widget(label_name)

            label_bars = Label( text=f"bars: {round(track['bars'])}" )
            self.grid_tracks.add_widget( label_bars )

            if track['loop']:
                state = "down"
            else:
                state = "normal"
            togglebutton_loop = ToggleButton( text="loop", state=state )
            togglebutton_loop.bind( on_press=partial(self.on_track_loop, track_id) )
            self.grid_tracks.add_widget( togglebutton_loop )

            if track['mute']:
                state = "down"
            else:
                state = "normal"
            togglebutton_mute = ToggleButton( text="mute", state=state )
            togglebutton_mute.bind( on_press=partial(self.on_track_mute, track_id) )
            self.grid_tracks.add_widget( togglebutton_mute )

            slider_volume = Slider(
                min=0, max=100, value=int(track['volume']*100), orientation='horizontal'
            )
            slider_volume.bind( value_normalized=partial(self.on_track_volume, track_id) )
            self.grid_tracks.add_widget( slider_volume )

            if track['sample']:
                label = Label( text=str("sample") )
                self.grid_tracks.add_widget(label)
            else:
                checkbox = CheckBox( group="focus" )
                checkbox.active = track['focus']
                checkbox.bind( active=partial(self.on_track_focus, track_id) )
                self.grid_tracks.add_widget(checkbox)




    def on_play_loop_of_all_tracks(self, widget, state):
        self.loopstation.play_loop_of_all_tracks()
        self.set_widget_track_options()

    def on_break_loop_of_all_tracks(self, widget, state):
        self.loopstation.break_loop_of_all_tracks()
        self.set_widget_track_options()

    def on_reset_loop_of_all_tracks(self, widget, state):
        self.loopstation.reset_loop_of_all_tracks()
        self.set_widget_track_options()




    def init_the_essential(self):
        self.update_metronome_circles()

        self.slider_beats.max = self.metronome.beats_limit_per_bar
        self.slider_bpm.max = self.metronome.bpm_limit

        # Samples
        #self.loopstation.save_track( path=SAMPLE_FILES[0], sample=True )
        #self.loopstation.save_track( path=SAMPLE_FILES[1], sample=True )

        # Establecer primer estado de los widgets
        self.set_slider_bpm()
        self.set_slider_beats()
        self.set_textinput_record_bars()
        self.set_togglebutton_play_beat()
        self.set_togglebutton_limit_record()
        self.set_label_tracks_number()
        self.set_widget_track_options()

        # Bind
        self.togglebutton_play_beat.bind( state=self.on_play_beat )
        self.togglebutton_limit_record.bind( state=self.on_limit_record )
        self.button_play.bind( state=self.on_play_loop_of_all_tracks )
        self.button_stop.bind( state=self.on_break_loop_of_all_tracks )
        self.button_restart.bind( state=self.on_reset_loop_of_all_tracks )




    # Actualizar todo
    def update(self, dt):
        '''
        Para la sincronización
        '''
        loopstation_signals = self.loopstation.update()
        metronome_signals = loopstation_signals['metronome']
        recorder_controller_signals = self.recorder_controller.update(
            metronome_signals=metronome_signals
        )

        # Cuando se para la grabación
        if recorder_controller_signals["stop_record"]:
            self.record_button.state = "normal"
            self.set_widget_track_options()

        # Timer | Record
        timer_current_fps = 0
        if self.record_button.state == "down":
            if self.timer.activate and (not self.recorder_controller.record):
                timer_signals = self.timer.update()
                timer_current_fps = timer_signals['current_fps']
                if timer_signals['timer_finished']:
                    self.recorder_controller.record = True
            else:
                self.recorder_controller.record = True
        else:
            self.timer.reset()

        # Metronomo | Visual
        for i in range( 0, len(self.circles) ):
            if not metronome_signals['current_beat'] == i:
                self.circles[i].color.rgb = RGB_OFF_TEMPO

        if loopstation_signals['emphasis_of_beat']['emphasis']:
            self.circles[ metronome_signals['current_beat'] ].color.rgb = RGB_FIRST_TEMPO
        elif loopstation_signals['emphasis_of_beat']['neutral']:
            self.circles[ metronome_signals['current_beat'] ].color.rgb = RGB_ANOTHER_TEMPO

        # Visual Timer
        if timer_current_fps > 0:
            self.label_center.text = str(
                round( (self.timer.seconds_in_fps-timer_current_fps) / FPS)
            )
        else:
            self.label_center.text = ""




'''
Constructor de aplicación
'''
#Window.size = (960, 540)
#Window.resizable = True
class LoopstationApp(App):
    def build(self):
        window = LoopstationWindow()
        window.init_the_essential()

        Clock.schedule_interval(window.update, 1.0/FPS)

        return window

if __name__ == '__main__':
    LoopstationApp().run()
