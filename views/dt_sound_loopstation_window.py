# Funciones
from functools import partial
from core.text_util import ignore_text_filter, PREFIX_NUMBER

# Engine
from core.dt_sound_loopstation_engine import DTSoundLoopstationEngine
from config.paths import SAMPLE_FILES, TEMP_DIR, ICON
from config.constants import VERSION, DEVELOPER, WEBSITE, NAME, HELP

# PyKivy
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import (
    ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.metrics import dp

# PyKivy Funciones para estilizar
from kivy.graphics import Color, Rectangle

# Colors
from utils.colors import (
    get_rgba, invert_rgb, invert_rgba, rgba_to_normalized, scale_rgba, random_rgba,
    is_the_rgba_color_bright
)

# Images for custom widgets
from config.paths import (
    ICON, PLAY_IMAGE, STOP_IMAGE, RESTART_IMAGE, RECORD_IMAGE, ABOUT_IMAGE, MENU_IMAGE, TIMER_IMAGE
)
record_image = Image( source=str(RECORD_IMAGE), allow_stretch=True )
play_image = Image( source=str(PLAY_IMAGE), allow_stretch=True )
stop_image = Image( source=str(STOP_IMAGE), allow_stretch=True )
restart_image = Image( source=str(RESTART_IMAGE), allow_stretch=True )
about_image = Image( source=str(ABOUT_IMAGE), allow_stretch=True )
menu_image = Image( source=str(MENU_IMAGE), allow_stretch=True )
timer_image = Image( source=str(TIMER_IMAGE), allow_stretch=True )


# Estilo molon
with open("./views/kvstring_dt.txt", 'r') as file:
    content = file.read()
from kivy.lang import Builder
Builder.load_string( content )

# Custom Widgets
from views.pykivy.widgets.sticky_image import StickyImage
from views.pykivy.widgets.loopstation_circle import LoopstationCircle
from views.pykivy.widgets.popup_information import PopupInformation
from views.pykivy.widgets.popup_grid_layout import PopupGridLayout
from views.pykivy.widgets.screen_android_ready import ScreenAndroidReady
from views.pykivy.widgets.metronome_circle import MetronomeCircle

# Text
from utils.translation_util import get_text

# Ventana, el loop del porgrama
class DTSoundLoopstationWindow(ScreenAndroidReady):
    '''
    El tempo de preferencia que sea un entero.
    '''
    def __init__(
        self, engine: DTSoundLoopstationEngine, config_controller=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Recordatorio de widgets inyectados | Objetos del `archivo.kv`
        # Se inyectarion en el `super().__init__(**kwargs)`
        '''
        '''
        #print( self.ids.keys() )

        # Config controller
        self.config_controller = config_controller
        self.config = self.config_controller.config

        # Colors
        self.rgb_off_tempo = [1,1,1]
        self.rgb_first_tempo = [0,1,0]
        self.rgb_another_tempo = [1,0,0]

        # LoopstationEngine
        self.engine = engine
        self.loopstation = self.engine.sound_loopstation
        self.metronome = self.engine.metronome
        self.recorder_controller = self.engine.recorder_controller
        self.microphone_recorder = self.recorder_controller.recorder
        self.timer = self.engine.timer

        # Circulo data
        self._metronome_circles = []

        # Bind. Padding
        self.bind(size=self._on_size)

    # Build
    def build_metronome_circles(self):
        self._metronome_circles.clear()
        self.hbox_metronome_circles.clear_widgets()
        for x in range( 0, self.metronome.get_beats_per_bar() ):
            circle = MetronomeCircle()
            self._metronome_circles.append( circle )
            self.hbox_metronome_circles.add_widget(circle)

    # GUI Colorear
    def coloring_metronome_circles(self, metronome_signals):
        '''
        Metronomo | colorear
        '''
        for i in range( 0, len(self._metronome_circles) ):
            if metronome_signals['current_beat'] != i+1:
                self._metronome_circles[i].color.rgb = self.rgb_off_tempo

        if ( metronome_signals['current_beat']-1 in range( 0, len(self._metronome_circles) ) ):
            self._metronome_circles[ metronome_signals['current_beat']-1 ].color.rgb = self.rgb_another_tempo

    def get_colors(self, rgba):
        scale_more = 1.25
        scale_less = 0.75
        base_color = rgba
        base_color_less = scale_rgba( base_color, scale_less )
        base_color_more = scale_rgba( base_color, scale_more )
        inverted_base_color = invert_rgba( base_color )
        inverted_base_color_more = scale_rgba( inverted_base_color, scale_more )
        inverted_base_color_less = scale_rgba( inverted_base_color, scale_less )

        colors = {
            "base": base_color,
            "base_less": base_color_less,
            "base_more": base_color_more,
            "inverted_base": inverted_base_color,
            "inverted_base_less": inverted_base_color_less,
            "inverted_base_more": inverted_base_color_more,
            "label": inverted_base_color_more,
            "text_input": base_color_less,
            "off_tempo": base_color_less,
            "first_tempo": inverted_base_color_more,
            "another_tempo": inverted_base_color
        }
        if is_the_rgba_color_bright(base_color):
            colors['label'] = inverted_base_color_less
            colors['text_input'] = base_color_more
            colors['first_tempo'] = inverted_base_color
            colors['another_tempo'] = inverted_base_color_less

        for key in colors.keys():
            colors[key] = rgba_to_normalized( colors[key] )

        return colors

    def set_colors(self, rgba):
        colors = self.get_colors( rgba )

        for widget in self.walk():
            if isinstance(widget, Button):
                continue # Ignorar botones
            if isinstance(widget, Label):
                widget.color = colors['label']
            elif isinstance(widget, TextInput):
                widget.background_color = colors['inverted_base']
                widget.foreground_color = colors['text_input']

        self.rgb_off_tempo = colors['off_tempo']
        self.rgb_first_tempo = colors['first_tempo']
        self.rgb_another_tempo = colors['another_tempo']

        # Fondos
        if not hasattr(self, "rect_window"):
            with self.canvas.before:
                self.color_window = Color( *colors['base'] )
                self.rect_window = Rectangle(pos=self.pos, size=self.size)
            self.bind(
                pos=lambda inst, val: setattr(self.rect_window, 'pos', inst.pos),
                size=lambda inst, val: setattr(self.rect_window, 'size', inst.size)
            )
        else:
            self.color_window.rgba = colors['base']
            self.main_vbox_layout.pos=self.pos
            self.main_vbox_layout.size=self.size

    # Bind
    def _on_size(self, *args):
        return self.change_padding_using_resolution(self.main_vbox_layout)

    ## On widgets
    def on_play_loop_of_all_tracks(self, widget, state):
        self.loopstation.play_loop_of_all_tracks()
        self.update_track_options_widgets()

    def on_break_loop_of_all_tracks(self, widget, state):
        self.loopstation.break_loop_of_all_tracks()
        self.update_track_options_widgets()

    def on_reset_loop_of_all_tracks(self, widget, state):
        self.loopstation.reset_loop_of_all_tracks()
        self.update_track_options_widgets()

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

    # Init widgets
    def init_slider_bpm(self):
        self.slider_bpm.min = 30
        self.slider_bpm.max = self.metronome.get_bpm_limit()
        self.slider_bpm.step = 10

    def init_slider_beats_per_bar(self):
        self.slider_beats_per_bar.min = 1
        self.slider_beats_per_bar.max = self.metronome.get_beats_limit_per_bar()
        self.slider_beats_per_bar.step = 1

    def init_slider_bars_to_record(self):
        self.slider_bars_to_record.min = 0
        self.slider_bars_to_record.max = 30
        self.slider_bars_to_record.step = 1

    # Widgets update
    # Establecer valores de opciones
    def update_colors_with_config(self):
        self.set_colors( self.config_controller.get_current_rgba_theme() )

    def update_bpm_widgets(self):
        bpm_value = self.metronome.get_bpm()
        self.slider_bpm.value = bpm_value
        self.label_bpm_value.text = str( bpm_value )

    def update_beats_per_bar_widgets(self):
        beats_per_bar_value = self.metronome.get_beats_per_bar()
        self.slider_beats_per_bar.value = beats_per_bar_value
        self.label_beats_per_bar_value.text = str(beats_per_bar_value)

    def update_bars_to_record_widgets(self):
        bars_to_record_value = self.recorder_controller.record_bars
        self.slider_bars_to_record.value = bars_to_record_value
        self.label_bars_to_record_value.text = str(bars_to_record_value)

    def update_track_options_widgets(self):
        self.grid_track_options.clear_widgets()
        for track_id in self.loopstation.get_track_ids():
            track = self.loopstation.get_track( track_id )

            label_track_id_value = Label( text=str(track_id), size_hint=(0.02, 1.0) )
            self.grid_track_options.add_widget( label_track_id_value )

            hbox = BoxLayout(orientation="vertical", size_hint=(0.45, 1.0))
            label_bars = Label( text=get_text("bars") )
            hbox.add_widget( label_bars )
            label_bars_value = Label( text="{:.1f}".format(track["bars"]) )
            hbox.add_widget( label_bars_value )
            self.grid_track_options.add_widget( hbox )

            togglebutton_loop = ToggleButton( text=get_text("loop"), size_hint=(0.45, 1.0) )
            togglebutton_loop.bind( on_press=partial(self.on_track_loop, track_id) )
            if track['loop']:
                togglebutton_loop.state = "down"
            else:
                togglebutton_loop.state = "normal"
            self.grid_track_options.add_widget( togglebutton_loop )

            togglebutton_mute = ToggleButton( text=get_text("mute"), size_hint=(0.45, 1.0) )
            togglebutton_mute.bind( on_press=partial(self.on_track_mute, track_id) )
            if track['mute']:
                togglebutton_mute.state = "down"
            else:
                togglebutton_mute.state = "normal"
            self.grid_track_options.add_widget( togglebutton_mute )


            hbox = BoxLayout(orientation="vertical")
            label_volume = Label( text=get_text("volume") )
            hbox.add_widget(label_volume)
            slider_volume = Slider(
                min=0, max=100, value=int( (track['volume']*100) )
            )
            slider_volume.bind( value_normalized=partial(self.on_track_volume, track_id) )
            hbox.add_widget(slider_volume)
            self.grid_track_options.add_widget( hbox )

            if track['sample']:
                label = Label( text=get_text("sample"), size_hint=(0.02, 1.0) )
                self.grid_track_options.add_widget(label)
            else:
                checkbox = CheckBox( group="focus", size_hint=(0.02, 1.0) )
                checkbox.active = track['focus']
                checkbox.bind( active=partial(self.on_track_focus, track_id) )
                self.grid_track_options.add_widget(checkbox)
        self.update_colors_with_config()

    def update_text(self):
        self.label_beats.text = get_text("beats")
        self.label_bars_to_record.text = get_text("bars")
        self.togglebutton_limit_record.text = get_text("limit-record")

    # Builders
    def build(self):
        self.build_metronome_circles()

        # Colors
        self.update_colors_with_config()

        # Init widgets
        self.init_slider_bpm()
        self.init_slider_beats_per_bar()
        self.init_slider_bars_to_record()

        self.button_play_all_tracks.bind( state=self.on_play_loop_of_all_tracks )
        self.button_stop_all_tracks.bind( state=self.on_break_loop_of_all_tracks )
        self.button_restart_all_tracks.bind( state=self.on_reset_loop_of_all_tracks )

        # Update widgets
        self.update_bpm_widgets()
        self.update_beats_per_bar_widgets()
        self.update_bars_to_record_widgets()
        self.update_track_options_widgets()

        self.update_text()

    # Loopstation loop
    def update(self, dt):
        '''
        Para la sincronización
        '''
        # Señales
        signals = self.engine.update( dt )

        self.recorder_controller.record = self.togglebutton_record.state == "down"
        if signals["recorder_controller"]["stop_record"]:
            self.update_track_options_widgets()
            self.togglebutton_record.state = "normal"
            self.recorder_controller.record = False

        self.coloring_metronome_circles( signals["metronome"] )
