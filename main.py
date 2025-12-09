from functools import partial
from core.text_util import ignore_text_filter, PREFIX_NUMBER
from config.paths import (
    TEMP_DIR, AUDIO_DIR, TEMPO_DIR, SAMPLE_DIR, DICT_SAMPLE_DIR, SAMPLE_FILES, DICT_TEMPO_DIR, TEMPO_FILES
)
from core.fps_loopstation import FPSLoopstation


# Grabador de microfonillo
from core.microphone_recorder import MicrophoneRecorder

# Constantes necesarias
VOLUME = float(0.1)
FPS = float(20)
BPM_TO_SECONDS = int(60)


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
        self.ellipse.size = ( min(self.size), min(self.size) )


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
    label_compass_to_record = ObjectProperty(None)
    label_bpm = ObjectProperty(None)
    label_center = ObjectProperty(None)


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

    circles = []

    # FPSLoopstation
    fps_loopstation = FPSLoopstation()


    # Posicionar metronomo
    def update_metronome_circles(self):
        # Establecer circulos
        self.circles.clear()
        self.metronome_container.clear_widgets()
        for x in range(0, self.fps_loopstation.beats_per_bar+1):
            circle = LoopstationCircle()
            self.circles.append( circle )
            self.metronome_container.add_widget(circle)




    def set_textinput_timer(self):
        self.textinput_timer.text = str( self.fps_loopstation.timer_in_seconds )

    def set_textinput_bpm(self):
        self.textinput_bpm.text = str( self.fps_loopstation.bpm )

    def set_textinput_compass_to_stop(self):
        self.textinput_compass_to_stop.text = str( self.fps_loopstation.recorder_limit_in_bars )

    def set_textinput_beats(self):
        self.textinput_beats.text = str( self.fps_loopstation.beats_per_bar+1 )

    def set_togglebutton_play_beat(self):
        state = "up"
        if self.fps_loopstation.play_beat:
            state = "down"
        self.togglebutton_play_beat.state = state

    def set_togglebutton_automatic_stop(self):
        state = "normal"
        if self.fps_loopstation.limit_recording:
            state = "down"
        self.togglebutton_automatic_stop.state = state

    def set_label_tracks_number(self):
        self.label_tracks_number.text = str( self.fps_loopstation.count_saved_track )




    def on_play_beat(self, obj, value):
        self.fps_loopstation.play_beat = value == "down"


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




    def on_bpm(self, obj, text):
        number = self.filter_text_to_number( text )
        if number >= 10:
            self.fps_loopstation.bpm = number
            self.fps_loopstation.reset_looping()
            self.set_textinput_bpm()
        self.set_widget_track_options()


    def on_beats(self, obj, text):
        number = self.filter_text_to_number( text )
        if number >= 2:
            self.fps_loopstation.beats_per_bar = number-1
            self.fps_loopstation.reset_looping()
            self.update_metronome_circles()
            self.set_textinput_beats()
        self.set_widget_track_options()


    def on_timer(self, obj, text):
        number = self.filter_text_to_number(text)
        if number > 0:
            self.fps_loopstation.timer_in_seconds = number
            self.fps_loopstation.update_timer_duration()
            self.set_textinput_timer()

    def on_compass_to_stop(self, obj, text):
        number = self.filter_text_to_number(text)
        if number >= 0:
            if number > 100:
                number = 100
            self.fps_loopstation.recorder_limit_in_bars = number
            self.fps_loopstation.update_recorder_limit()
            if number != 0:
                self.set_textinput_compass_to_stop()
        if not self.fps_loopstation.limit_recording:
            self.fps_loopstation.recorder_limit_in_bars = 0
            self.fps_loopstation.update_recorder_limit()


    def on_automatic_stop(self, obj, state):
        self.fps_loopstation.limit_recording = state == "down"
        self.set_togglebutton_automatic_stop()

    def on_record(self, obj, state):
        self.fps_loopstation.recording = state == "down"




    def on_track_loop(self, track_id, widget):
        if widget.state == "down":
            self.fps_loopstation.play_track_loop( track_id=track_id )
        else:
            self.fps_loopstation.break_track_loop( track_id=track_id )

    def on_track_mute(self, track_id, widget):
        track = self.fps_loopstation.dict_track[track_id]
        track['mute'] = (widget.state == "down")

    def on_track_volume(self, track_id, widget, value):
        track = self.fps_loopstation.dict_track[track_id]
        track['volume'] = value

    def on_track_focus(self, track_id, widget, active):
        track = self.fps_loopstation.dict_track[track_id]
        track['focus'] = active


    def set_widget_track_options(self):
        '''
        Establecer widgets
        '''
        self.grid_tracks.clear_widgets()
        for track_id in self.fps_loopstation.dict_track.keys():
            track = self.fps_loopstation.dict_track[track_id]

            label_name = Label( text=str(track_id) )
            self.grid_tracks.add_widget(label_name)

            label_bars = Label( text=f"compass: {round(track['bars'])}" )
            self.grid_tracks.add_widget( label_bars )

            if track['loop']:
                state = "down"
            else:
                state = "normal"
            togglebutton_loop = ToggleButton( text="loop", state=state )
            togglebutton_loop.bind(
                on_press=partial(self.on_track_loop, track_id)
            )
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

            checkbox = CheckBox( group="focus" )
            checkbox.active = track['focus']
            checkbox.bind( active=partial(self.on_track_focus, track_id) )
            self.grid_tracks.add_widget(checkbox)




    def on_play_loop_of_all_tracks(self, widget, state):
        self.fps_loopstation.play_loop_of_all_tracks()
        self.set_widget_track_options()

    def on_break_loop_of_all_tracks(self, widget, state):
        self.fps_loopstation.break_loop_of_all_tracks()
        self.set_widget_track_options()

    def on_reset_loop_of_all_tracks(self, widget, state):
        self.fps_loopstation.reset_loop_of_all_tracks()
        self.set_widget_track_options()




    def init_the_essential(self):
        self.fps_loopstation.fps = FPS
        self.fps_loopstation.volume = VOLUME
        self.fps_loopstation.set_play_mode_beat( "emphasis_on_first" )
        self.fps_loopstation.play_beat = True
        self.fps_loopstation.recorder_limit_in_bars = 1
        self.fps_loopstation.bpm_limit = 200
        self.fps_loopstation.beats_limit_per_bar = 7
        self.fps_loopstation.timer_limit_in_seconds = 20
        self.fps_loopstation.limit_recording = True
        self.fps_loopstation.sample_sound_limit = 3
        self.fps_loopstation.temp_sound_limit = 3
        self.fps_loopstation.update_all_data()

        self.update_metronome_circles()

        # Establecer primer estado de los widgets
        self.set_textinput_bpm()
        self.set_textinput_timer()
        self.set_textinput_compass_to_stop()
        self.set_textinput_beats()
        self.set_togglebutton_play_beat()
        self.set_togglebutton_automatic_stop()
        self.set_label_tracks_number()

        # Bind
        self.togglebutton_play_beat.bind( state=self.on_play_beat )
        self.textinput_bpm.bind( text=self.on_bpm )
        self.textinput_beats.bind( text=self.on_beats )
        self.textinput_timer.bind( text=self.on_timer )
        self.textinput_compass_to_stop.bind( text=self.on_compass_to_stop )
        self.togglebutton_automatic_stop.bind( state=self.on_automatic_stop )
        self.record_button.bind( state=self.on_record )
        self.button_play.bind( state=self.on_play_loop_of_all_tracks )
        self.button_stop.bind( state=self.on_break_loop_of_all_tracks )
        self.button_restart.bind( state=self.on_reset_loop_of_all_tracks )




    # Actualizar todo
    def update(self, dt):
        '''
        Para la sincronización
        '''
        signals = self.fps_loopstation.looping()

        # Parando grabación | Poner en falso el togglebutton
        if signals['recorder_signal']['stop_recording']:
            self.record_button.state = "normal"
            self.set_widget_track_options()
            self.set_label_tracks_number()

        # Visual timer de grabación
        if (
            (not signals['timer_signal']['completed']) and
            signals['timer_signal']['count_fps'] > 0
        ):
            self.label_center.text = str(
                round(
                    (self.fps_loopstation.timer_in_fps -signals['timer_signal']['count_fps']) /
                    self.fps_loopstation.fps
                )
            )
        else:
            self.label_center.text = ""


        # Metronomo | Visual
        for i in range( 0, len(self.circles) ):
            if not self.fps_loopstation.current_beat == i:
                self.circles[i].color.rgb = RGB_OFF_TEMPO

        if self.fps_loopstation.is_first_beat:
            self.circles[self.fps_loopstation.current_beat].color.rgb = RGB_FIRST_TEMPO
        elif self.fps_loopstation.first_frame_of_beat:
            self.circles[self.fps_loopstation.current_beat].color.rgb = RGB_ANOTHER_TEMPO




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
