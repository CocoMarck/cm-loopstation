# Python
from functools import partial

# Texto
from core.text_util import ignore_text_filter, PREFIX_NUMBER

# Engine
from core.dt_sound_loopstation_engine import DTSoundLoopstationEngine
from config.constants import VERSION, DEVELOPER, WEBSITE, NAME, HELP

# Metronome
from controllers.beat_controller import BeatController


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

# PyKivy Estilo molon
from views.kvstring import kv
from kivy.lang import Builder
Builder.load_string( kv )

# Colors
from utils.colors import (
    get_rgba, invert_rgb, invert_rgba, rgba_to_normalized, scale_rgba, random_rgba,
    is_the_rgba_color_bright
)

# Mis views functions. Images for custom widgets
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

# Custom Widgets
from views.pykivy.widgets.sticky_image import StickyImage
from views.pykivy.widgets.popup_information import PopupInformation
from views.pykivy.widgets.popup_grid_layout import PopupGridLayout
from views.pykivy.widgets.screen_android_ready import ScreenAndroidReady
from views.pykivy.widgets.metronome_circle import MetronomeCircle

# Traductor wrapper
from utils.translation_util import get_text

# Ventana, el loop del porgrama
class DTSoundLoopstationScreen(ScreenAndroidReady):
    '''
    El tempo de preferencia que sea un entero.
    '''
    def __init__(
        self, engine: DTSoundLoopstationEngine=None, config_controller=None, beat_controller: BeatController=None, play_metronome_beat=True, *args, **kwargs
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
        self.rgba_off_tempo = [1,1,1,1]
        self.rgba_first_tempo = [0,1,0,1]
        self.rgba_another_tempo = [1,0,0,1]

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

        # Play beat
        self.play_metronome_beat = play_metronome_beat

        # Widget dropdown
        self.dropdown = DropDown()
        self.menu_buttons = {
            "start": None,
            "stop": None,
            "settings": None,
            "help": None,
            "about": None
        }
        for key in self.menu_buttons.keys():
            button = Button( text=get_text(key), size_hint_y=None )
            self.menu_buttons[key] = button
            self.dropdown.add_widget( button )

        # Beat controller
        self.beat_controller = beat_controller

        # Loop
        self.work = True

        # Eventos de ventana
        Window.bind(on_minimize=self._on_minimize)
        Window.bind(on_restore=self._on_restore)

    # Build
    def build_metronome_circles(self):
        self._metronome_circles.clear()
        self.hbox_metronome_circles.clear_widgets()
        for x in range( 0, self.metronome.get_beats_per_bar() ):
            circle = MetronomeCircle( self.rgba_off_tempo )
            self._metronome_circles.append( circle )
            self.hbox_metronome_circles.add_widget(circle)

    # GUI Colorear
    def coloring_metronome_circles(self, metronome_signals):
        '''
        Metronomo | colorear
        '''
        for i in range( 0, len(self._metronome_circles) ):
            if metronome_signals['current_beat'] != i+1:
                self._metronome_circles[i].color.rgb = self.rgba_off_tempo

        if ( metronome_signals['current_beat']-1 in range( 0, len(self._metronome_circles) ) ):
            self._metronome_circles[ metronome_signals['current_beat']-1 ].color.rgb = self.rgba_another_tempo

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

        self.rgba_off_tempo = colors['off_tempo']
        self.rgba_first_tempo = colors['first_tempo']
        self.rgba_another_tempo = colors['another_tempo']

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

    def stop_work(self):
        self.work = False
        self.loopstation.break_loop_of_all_tracks()
        self.metronome.reset_counts()

        # Reset view
        self.build_metronome_circles()
        self.update_track_options_widgets()

    def start_work(self):
        self.work = True

    # Bind
    def _on_size(self, *args):
        self.change_padding_using_resolution(self.main_vbox_layout)
        self.update_size_of_configuration_buttons()

    def _on_minimize(self, *args):
        self.stop_work()

    def _on_restore(self, *args):
        self.start_work()

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

    def on_play_metronome_beat(self, widget):
        self.play_metronome_beat = widget.state == "down"

    def on_configuration(self, state):
        self.update_size_of_configuration_buttons()

    def on_start(self, state):
        self.start_work()

    def on_stop(self, state):
        self.stop_work()

    def on_beats_per_bar(self, widget, value):
        self.metronome.set_beats_per_bar( value )
        self.metronome.reset_counts()
        self.loopstation.update_all_track_bars()

        # Reset view
        self.update_beats_per_bar_widgets()
        self.update_track_options_widgets()
        self.build_metronome_circles()

    def on_bpm(self, widget, value):
        self.metronome.set_bpm( value )
        self.metronome.reset_counts()
        self.loopstation.update_all_track_bars()

        # Reset view
        self.update_bpm_widgets()
        self.update_track_options_widgets()

    def on_bars_to_record(self, widget, value):
        self.recorder_controller.record_bars = value
        self.update_bars_to_record_widgets()

    def on_timer(self, widget, value):
        self.timer.set_seconds( value )
        self.update_timer_widgets()

    def open_popup_information(self, title, text_information):
        popup = PopupInformation(
            title=title, size_hint=(0.8, 0.8),
            text_information=text_information, text_ok=get_text('ok')
        )
        popup.open()

    def on_help(self, button):
        self.open_popup_information(
            title=get_text("help"), text_information=get_text('fps-sound-loopstation-help')
        )

    def on_about(self, button):
        self.open_popup_information(
            title=get_text("about"), text_information=(
                f"[b]{NAME}[/b]: {get_text('version')} {VERSION}\n\n"
                f"- {get_text('developer')}: [b]{DEVELOPER}[/b]\n"
                f"- {get_text('website')}: [b]{WEBSITE}[/b]"
            )
        )

    def on_settings(self, button):
        popup = PopupGridLayout(
            title=get_text("settings"),
            cols=2, rows=2, row_default_height=self.height*0.1,
            size_hint=(0.8, 0.8), text_ok=get_text('ok')
        )
        popup.second_container.add_widget( Label( text=get_text("numerical-view") ) )
        checkbox_metronome_numeircal_view = CheckBox( active=self.config.numerical_view )
        checkbox_metronome_numeircal_view.bind( active=self.on_numeric_metronome )
        popup.second_container.add_widget( checkbox_metronome_numeircal_view )

        popup.second_container.add_widget( Label( text=get_text("theme") ) )
        spinner = Spinner(
            text=self.config.theme,
            values=self.config_controller.get_theme_names(),
        )
        spinner.bind(text=lambda inst, val: self.on_theme_selected(val))
        popup.second_container.add_widget( spinner )

        popup.open()

    def on_numeric_metronome(self, widget, active):
        self.config_controller.update_numerical_view( active )

    def on_theme_selected(self, name):
        if self.config_controller.update_theme(name):
            rgba = self.config_controller.get_rgba_theme( name )
            self.set_colors(rgba)

    # Init widgets
    def init_slider_bpm(self):
        self.slider_bpm.min = 30
        self.slider_bpm.max = self.metronome.get_bpm_limit()
        self.slider_bpm.step = 10

    def init_slider_beats_per_bar(self):
        self.slider_beats_per_bar.min = 2
        self.slider_beats_per_bar.max = self.metronome.get_beats_limit_per_bar()
        self.slider_beats_per_bar.step = 1

    def init_slider_bars_to_record(self):
        self.slider_bars_to_record.min = 1
        self.slider_bars_to_record.max = 30
        self.slider_bars_to_record.step = 1

    def init_slider_timer(self):
        self.slider_timer.min = 0
        self.slider_timer.max = 60
        self.slider_timer.step = 1

    def init_limit_record(self):
        if self.recorder_controller.limit_record:
            state = "down"
        else:
            state = "normal"
        self.togglebutton_limit_record.state = state

    def init_widget_images(self):
        # Images
        self.sticky_images = {
            "record": StickyImage(
                image=record_image, widget=self.togglebutton_record
            ),
            "play": StickyImage(
                image=play_image, widget=self.button_play_all_tracks
            ),
            "stop": StickyImage(
                image=stop_image, widget=self.button_stop_all_tracks
            ),
            "restart": StickyImage(
                image=restart_image, widget=self.button_restart_all_tracks
            ),
            "about": StickyImage(
                image=about_image, widget=self.menu_buttons["about"]
            ),
            "configuration": StickyImage(
                image=menu_image, widget=self.button_configuration
            )
        }
        for sticky_image in self.sticky_images.values():
            sticky_image.widget.text = ""

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
        bars_to_record_value = int(self.recorder_controller.record_bars)
        self.slider_bars_to_record.value = bars_to_record_value
        self.label_bars_to_record_value.text = str( bars_to_record_value )

    def update_track_options_widgets(self):
        self.grid_track_options.clear_widgets()
        for track_id in self.loopstation.get_track_ids():
            track = self.loopstation.get_track( track_id )

            vbox = BoxLayout(orientation="vertical", size_hint=(1.0, 1.0), valign="top")

            hbox_section_1 = BoxLayout(orientation="horizontal", size_hint=(1.0, 1.0))

            label_track_id_value = Label( text=str(track_id), size_hint=(0.02, 1.0) )
            hbox_section_1.add_widget( label_track_id_value )

            hbox_bars = BoxLayout( orientation="horizontal", size_hint=(0.05, 1.0) )
            label_bars = Label( text=get_text("bars"), size_hint=(1.0, 1.0) )
            hbox_bars.add_widget( label_bars )

            label_bars_value = Label( text="{:.1f}".format(track["bars"]), size_hint=(1.0, 1.0) )
            hbox_bars.add_widget( label_bars_value )

            hbox_section_1.add_widget( hbox_bars )

            togglebutton_loop = ToggleButton( text=get_text("loop"), size_hint=(0.05, 1.0) )
            togglebutton_loop.bind( on_press=partial(self.on_track_loop, track_id) )
            if track['loop']:
                togglebutton_loop.state = "down"
            else:
                togglebutton_loop.state = "normal"
            hbox_section_1.add_widget( togglebutton_loop )

            togglebutton_mute = ToggleButton( text=get_text("mute"), size_hint=(0.05, 1.0) )
            togglebutton_mute.bind( on_press=partial(self.on_track_mute, track_id) )
            if track['mute']:
                togglebutton_mute.state = "down"
            else:
                togglebutton_mute.state = "normal"
            hbox_section_1.add_widget( togglebutton_mute )

            checkbox = CheckBox( group="focus", size_hint=(0.02, 1.0) )
            checkbox.active = track['focus']
            hbox_section_1.add_widget( checkbox )

            vbox.add_widget(hbox_section_1)

            #
            hbox = BoxLayout(orientation="horizontal")
            label_volume = Label( text=get_text("volume"), size_hint=(0.15, 1.0) )
            hbox.add_widget(label_volume)
            slider_volume = Slider(
                min=0, max=100, value=int( (track['volume']*100) )
            )
            slider_volume.bind( value_normalized=partial(self.on_track_volume, track_id) )
            hbox.add_widget(slider_volume)

            if track['sample']:
                label = Label( text=get_text("sample"), size_hint=(0.15, 1.0) )
                hbox.add_widget(label)
            else:
                label = Label( text=get_text("temp"), size_hint=(0.15, 1.0) )
                hbox.add_widget(label)

                checkbox.bind( active=partial(self.on_track_focus, track_id) )

            vbox.add_widget( hbox )
            self.grid_track_options.add_widget( vbox )

        self.update_colors_with_config()

    def update_text(self):
        self.label_beats.text = get_text("beats")
        self.label_bars_to_record.text = get_text("bars")
        self.togglebutton_limit_record.text = get_text("limit-record")
        self.togglebutton_play_metronome_beat.text = get_text("play-beat")
        #self.label_timer_text.text = get_text("timer")

    def update_play_metronome_beat(self):
        if self.play_metronome_beat:
            self.togglebutton_play_metronome_beat.state = "down"
        else:
            self.togglebutton_play_metronome_beat.state = "normal"

    def update_limit_record(self):
        if self.recorder_controller.limit_record:
            self.button_limit_record.state = "down"
        else:
            self.button_limit_record.state = "normal"

    def update_size_of_configuration_buttons(self):
        for button in self.menu_buttons.values():
            button.height = self.height*0.05

    def update_timer_widgets(self):
        timer_seconds_value = int( self.timer.get_seconds() )
        self.slider_timer.value = timer_seconds_value
        self.label_timer_value.text = str( timer_seconds_value )


    # Builders
    def build(self):
        self.build_metronome_circles()

        # Colors
        self.update_colors_with_config()

        # Init widgets
        self.init_slider_bpm()
        self.init_slider_beats_per_bar()
        self.init_slider_timer()
        self.init_slider_bars_to_record()
        self.init_widget_images()
        self.init_limit_record()

        # Bind
        self.togglebutton_play_metronome_beat.bind( on_press=self.on_play_metronome_beat )
        self.button_play_all_tracks.bind( state=self.on_play_loop_of_all_tracks )
        self.button_stop_all_tracks.bind( state=self.on_break_loop_of_all_tracks )
        self.button_restart_all_tracks.bind( state=self.on_reset_loop_of_all_tracks )
        self.slider_bars_to_record.bind( value=self.on_bars_to_record )
        self.slider_beats_per_bar.bind( value=self.on_beats_per_bar )
        self.slider_bpm.bind( value=self.on_bpm )
        self.slider_timer.bind( value=self.on_timer )
        self.button_configuration.bind( on_press=self.on_configuration )
        self.button_configuration.bind( on_release=self.dropdown.open )
        self.menu_buttons['start'].bind( on_press=self.on_start )
        self.menu_buttons['stop'].bind( on_press=self.on_stop )
        self.menu_buttons['about'].bind( on_press=self.on_about )
        self.menu_buttons['help'].bind( on_press=self.on_help )
        self.menu_buttons["settings"].bind( on_press=self.on_settings )

        # Update widgets
        self.update_bpm_widgets()
        self.update_beats_per_bar_widgets()
        self.update_bars_to_record_widgets()
        self.update_track_options_widgets()
        self.update_play_metronome_beat()
        self.update_timer_widgets()
        self.update_text()

    # Loopstation loop
    def update(self, dt):
        '''
        Para la sincronización
        '''
        if self.work:
            # Señales
            signals = self.engine.update( dt )

            # Timer activeted
            timer_working = self.timer.activate and (not self.recorder_controller.record)
            timer_current_dt = 0
            if self.togglebutton_record.state == "down":
                # Grabar con timer
                if not timer_working:
                    self.timer.activate = True
                if not timer_working:
                    timer_working = self.timer.activate and (not self.recorder_controller.record)
                if timer_working:
                    timer_current_dt = signals['timer']['current_dt']
                    self.recorder_controller.record = signals['timer']['timer_finished']
                else:
                    self.recorder_controller.record = True
            else:
                # Restablecer timer
                self.recorder_controller.record = False
                self.timer.activate = False
                self.timer.reset()

            # Grabación
            self.recorder_controller.limit_record = self.togglebutton_limit_record.state == "down"
            if signals["recorder_controller"]["stop_record"]:
                self.update_track_options_widgets()
                self.togglebutton_record.state = "normal"
                self.recorder_controller.record = False

            # Play metronome beat
            if self.play_metronome_beat:
                self.beat_controller.update( signals['metronome'] )

            # Colorear metronomo
            self.coloring_metronome_circles( signals["metronome"] )

            # Mostrar
            if timer_working:
                self.label_timer_count_value.text = str(
                    round( self.timer.get_seconds() -signals['timer']['current_dt'] )
                )
            else:
                self.label_timer_count_value.text = ""
        else:
            self.recorder_controller.record = False
