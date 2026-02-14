from functools import partial
from core.text_util import ignore_text_filter, PREFIX_NUMBER

from core.fps_sound_loopstation_engine import FPSSoundLoopstationEngine
from config.paths import SAMPLE_FILES, TEMP_DIR, ICON

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


# Estilo molon
from kivy.lang import Builder
from views.kvstring import kv
Builder.load_string(kv)


# Constantes | Colores
RGB_OFF_TEMPO = [1,1,1]
RGB_FIRST_TEMPO = [0,1,0]
RGB_ANOTHER_TEMPO = [1,0,0]


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
class FPSSoundLoopstationWindow(Widget):
    '''
    El tempo de preferencia que sea un entero.
    '''
    def __init__(
        self, engine: FPSSoundLoopstationEngine, **kwargs
    ):
        super().__init__(**kwargs)

        # Recordatorio de widgets inyectados | Objetos del `archivo.kv`
        '''
        self.record_button

        self.label_timer
        self.label_tracks
        self.label_tracks_number
        self.label_record_bars
        self.label_bpm
        self.label_center

        self.grid_tracks

        self.button_play
        self.button_stop
        self.button_restart

        self.togglebutton_limit_record
        self.togglebutton_play_beat

        self.textinput_record_bars
        self.slider_timer
        self.slider_bpm
        self.slider_beats

        self.metronome_container
        '''
        #print( self.ids.keys() )

        # LoopstationEngine
        self.circles = []

        self.engine = engine
        self.loopstation = self.engine.sound_loopstation
        self.metronome = self.engine.metronome
        self.recorder_controller = self.engine.recorder_controller
        self.microphone_recorder = self.recorder_controller.recorder
        self.timer = self.engine.timer

        self.last_microphone_recorder_state = self.microphone_recorder.state
        self.current_count_temp_sound = self.loopstation.count_temp_sound

        # Update widget
        self.update_tracks = False
        self.update_interval_tracks = 0.5 # Medio segundo.
        self.accum_update_tracks = 0 # Contador de delta time


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
        self.label_bpm.text = str(self.metronome.bpm)

    def set_slider_beats(self):
        self.slider_beats.value = self.metronome.beats_per_bar

    def set_slider_timer(self):
        self.slider_timer.value = self.timer.seconds

    def set_textinput_record_bars(self):
        self.textinput_record_bars.text = str(self.recorder_controller.record_bars)

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

    def on_timer(self, obj, value):
        self.timer.set_seconds( seconds=value )

    def on_beats_per_bar(self, obj, value):
        self.metronome.beats_per_bar = round(value)
        self.metronome.reset_settings()
        self.loopstation.update_all_track_bars()
        self.update_metronome_circles()
        self.set_widget_track_options()


    def on_bpm(self, obj, value):
        self.metronome.bpm = round(value)
        self.metronome.reset_settings()
        self.loopstation.update_all_track_bars()
        self.label_bpm.text = str(self.metronome.bpm)
        self.set_widget_track_options()





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

    def on_record_bars(self, obj, text):
        number = self.filter_text_to_number(text)
        if number > 0:
            self.recorder_controller.record_bars = number
            self.set_textinput_record_bars()
        else:
            obj.text = ""





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

    def build(self):
        # Loop
        self.engine.start()
        self.icon = ICON

        # widgets
        self.update_metronome_circles()

        self.slider_beats.min = 1
        self.slider_beats.max = self.metronome.beats_limit_per_bar
        self.slider_beats.step = 1

        self.slider_bpm.min = 30
        self.slider_bpm.max = self.metronome.bpm_limit
        self.slider_bpm.step = 10

        self.slider_timer.max = 20
        self.slider_timer.step = 1

        # Samples
        #self.loopstation.save_track( path=SAMPLE_FILES[0], sample=True )
        #self.loopstation.save_track( path=SAMPLE_FILES[1], sample=True )

        # Establecer primer estado de los widgets
        self.set_slider_bpm()
        self.set_slider_beats()
        self.set_slider_timer()
        self.set_textinput_record_bars()
        self.set_togglebutton_play_beat()
        self.set_togglebutton_limit_record()
        self.set_label_tracks_number()
        self.set_widget_track_options()

        # Bind
        self.slider_beats.bind( value=self.on_beats_per_bar )
        self.slider_timer.bind( value=self.on_timer )
        self.slider_bpm.bind( value=self.on_bpm )
        self.textinput_record_bars.bind( text=self.on_record_bars )
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
        signals = self.engine.get_last_signals()
        if not signals:
            return

        loopstation_signals = signals['loopstation']
        metronome_signals = signals['metronome']
        recorder_controller_signals = signals['recorder_controller']
        timer_signals = signals['timer']

        # Señal | Cuando se para la grabación
        if recorder_controller_signals["stop_record"]:
            ## Parar con señal, pero aveces no jala.
            self.current_count_temp_sound = self.loopstation.count_temp_sound
            self.record_button.state = "normal"
            self.set_widget_track_options()

        # Actualizar ultimo estado de grabación. Determinar parar no.
        if self.last_microphone_recorder_state != self.microphone_recorder.state:
            ## Forzar parar, por que aveces no llega la señal de parar. (Es por el loop del kivy
            self.last_microphone_recorder_state = self.microphone_recorder.state

            ## Se supone que ya debe jalar mejor sin limit bars. Testear grabar sin limit bars.
            ## El Engine jala bien, el problema son las señales, pero pos ya deberian jalar.
            if self.microphone_recorder.state == "stop":
                self.record_button.state = "normal"
                self.update_tracks = True # Pedir actualización

        # Obtener tracks | Insertar track
        if self.current_count_temp_sound != self.loopstation.count_temp_sound:
            self.update_tracks = False
            self.current_count_temp_sound = self.loopstation.count_temp_sound
            self.set_widget_track_options()
            self.set_label_tracks_number()

        # Obtener tracks | Actualización de track
        if self.update_tracks == False:
            # Asegurarse de reiniciar conteo de actualización de tracks
            self.accum_update_tracks = 0.0

        if self.update_tracks:
            if self.accum_update_tracks >= self.update_interval_tracks:
                self.update_tracks = False
                self.set_widget_track_options()
                self.set_label_tracks_number()
            else:
                self.accum_update_tracks += dt

        # Timer | Record
        timer_current_fps = 0
        if self.record_button.state == "down":
            self.timer.activate = True
            if self.timer.activate and (not self.recorder_controller.record):
                timer_current_fps = timer_signals['current_fps']
                if timer_signals['timer_finished']:
                    self.recorder_controller.record = True
            else:
                self.recorder_controller.record = True
        else:
            self.recorder_controller.record = False
            self.timer.activate = False
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
                round( (self.timer.seconds_in_fps-timer_current_fps) / self.timer.fps)
            )
        else:
            self.label_center.text = ""
