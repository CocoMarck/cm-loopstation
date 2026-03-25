from functools import partial
from core.text_util import ignore_text_filter, PREFIX_NUMBER

from core.fps_sound_loopstation_engine import FPSSoundLoopstationEngine
from config.paths import SAMPLE_FILES, TEMP_DIR, ICON
from config.constants import VERSION, DEVELOPER, WEBSITE, NAME, HELP

# Kivy
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

# Funciones para estilizar
from kivy.graphics import Color, Rectangle

# Colors
from utils.colors import (
    get_rgba, invert_rgb, invert_rgba, rgba_to_normalized, scale_rgba, random_rgba,
    is_the_rgba_color_bright
)

# Images
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
from kivy.lang import Builder
from views.kvstring import kv
Builder.load_string(kv)

# Custom Widgets
from views.pykivy.widgets.sticky_image import StickyImage
from views.pykivy.widgets.loopstation_circle import LoopstationCircle
from views.pykivy.widgets.popup_information import PopupInformation
from views.pykivy.widgets.popup_grid_layout import PopupGridLayout

# Text
from utils.translation_util import get_text

# Ventana, el loop del porgrama
class FPSSoundLoopstationWindow(Screen):
    '''
    El tempo de preferencia que sea un entero.
    '''
    def __init__(
        self, engine: FPSSoundLoopstationEngine,
        vertical_padding_offsets=[0,0,0,0], horizontal_padding_offsets=[0,0,0,0],
        config_controller=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Recordatorio de widgets inyectados | Objetos del `archivo.kv`
        # Se inyectarion en el `super().__init__(**kwargs)`
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

        # Circulo data
        self.circles = []
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

        self.last_microphone_recorder_state = self.microphone_recorder.state
        self.current_count_temp_sound = self.loopstation.count_temp_sound

        # Update widget
        self.update_tracks = False
        self.update_interval_tracks = 0.5 # Medio segundo.
        self.accum_update_tracks = 0 # Contador de delta time

        # Widgets | Sliders list
        self.sliders = []

        # Widget | DropDown | Menu
        self.dropdown = DropDown()
        self.menu_buttons = {
            "start": None,
            "stop": None,
            "settings": None,
            "help": None,
            "about": None
        }
        for key in self.menu_buttons.keys():
            button = Button( text=key, size_hint_y=None )
            self.menu_buttons[key] = button
            self.dropdown.add_widget( button )
        self.menu_buttons["about"].bind( on_press=self.on_about )
        self.menu_buttons["start"].bind( on_press=self.on_start_engine )
        self.menu_buttons["stop"].bind( on_press=self.on_stop_engine )
        self.menu_buttons["help"].bind( on_press=self.on_help )
        self.menu_buttons["settings"].bind( on_press=self.on_settings )
        self.button_menu.bind( on_press=self.on_menu )
        self.button_menu.bind( on_release=self.dropdown.open )

        # Metronome view
        self.label_numeric_metronome = Label()

        # Padding
        self.last_orientation = None
        self.vertical_padding_offsets = vertical_padding_offsets
        self.horizontal_padding_offsets = horizontal_padding_offsets

        # Eventos de PC (desktop, pero creo que lo usa android tambien)
        Window.bind(on_minimize=self._on_minimize)
        Window.bind(on_restore=self._on_restore)

    def refresh_text(self):
        #self.label_timer.text = get_text( 'timer' )
        self.label_tracks.text = get_text( 'tracks' )
        self.label_record_bars.text = get_text('bars')
        self.togglebutton_limit_record.text = get_text('limit-record')
        self.togglebutton_play_beat.text = get_text('play-beat')
        self.menu_buttons['stop'].text = get_text('stop')
        for key in self.menu_buttons.keys():
            if key in self.sticky_images.keys():
                continue
            self.menu_buttons[key].text = get_text(key)


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
            self.rect_window.pos=self.pos
            self.rect_window.size=self.size

        if not hasattr(self, "rect_scroll"):
            with self.scroll_widget.canvas.before:
                self.color_scroll = Color( *colors['base_less'] )
                self.rect_scroll = Rectangle(pos=self.scroll_widget.pos, size=self.scroll_widget.size)
            self.bind(
                pos=lambda inst, val: setattr(self.rect_scroll, 'pos', inst.pos),
                size=lambda inst, val: setattr(self.rect_scroll, 'size', inst.size)
            )
        else:
            self.color_scroll.rgba = colors['base_less']
            self.rect_scroll.pos = self.scroll_widget.pos
            self.rect_scroll.size = self.scroll_widget.size


    def resize_menu_buttons(self):
        for button in self.menu_buttons.values():
            button.height = self.height*0.1

    def on_menu(self, button):
        self.resize_menu_buttons()

    def get_screen_orientation(self):
        '''
        Determinar orientación de ventana, segun tamaño xy de ventana.
        '''
        if self.height > self.width:
            return "vertical"
        return "horizontal"

    def build_padding_offsets(self, orientation, using):
        if orientation == "vertical":
            number = self.height
            padding_offsets = self.vertical_padding_offsets
        else:
            number = self.width
            padding_offsets = self.horizontal_padding_offsets
        padding = []
        if using == "dpi":
            for x in padding_offsets:
                padding.append( dp(x) )
        elif using == "resolution":
            for x in padding_offsets:
                padding.append( number*x )
        return padding

    def _update_padding(self, orientation, using ):
        # Usa DP
        padding = self.build_padding_offsets( orientation, using )
        if (
            len(padding) == 4 #and
            #padding != self.main_layout.padding
        ):
            self.main_layout.padding = padding

    def _update_padding_using_dpi(self, orientation ):
        self._update_padding( orientation, "dpi" )

    def _update_padding_using_resolution(self, orientation ):
        self._update_padding( orientation, "resolution" )

    # Construir vista de metronomo
    def build_metronome_circles(self):
        # Establecer circulos
        self.circles.clear()
        self.metronome_container.clear_widgets()
        for x in range(0, self.metronome.beats_per_bar+1):
            circle = LoopstationCircle()
            self.circles.append( circle )
            self.metronome_container.add_widget(circle)

    def build_numeric_metronome(self):
        self.metronome_container.clear_widgets()
        self.label_numeric_metronome.text = "0"
        self.label_numeric_metronome.color = self.rgb_off_tempo
        self.metronome_container.add_widget( self.label_numeric_metronome )

    # Establecer vista de metronomo
    def set_metronome_view(self):
        if self.config.numerical_view:
            self.build_numeric_metronome()
        else:
            self.build_metronome_circles()

    # Administración de motor
    def stop_engine(self):
        self.engine.stop()
        self.set_metronome_view()
        self.set_widget_track_options()

    def start_engine(self):
        self.engine.start()
        self.set_widget_track_options()

    def on_start_engine(self, button):
        self.start_engine()

    def on_stop_engine(self, button):
        self.stop_engine()

    def _on_minimize(self, *args):
        # Puede que solo jale en PC
        print(f"Minimize Window")
        self.engine.pause()

    def _on_restore(self, *args):
        # Puede que solo jale en PC
        print(f"Restore Window")
        self.start_engine()

    ## Para Android
    def on_pause(self):
        self.engine.stop()
        return True

    def on_resume(self):
        self.engine.start()
        self.set_widget_track_options()

    # Contruir texto de opciones
    def build_bpm_text(self):
        return f"BPM: " + str(self.metronome.bpm)

    def build_beats_text(self):
        return f"{get_text('beats')}: " + str(self.metronome.beats_per_bar+1)

    # Establecer valores de opciones
    def set_slider_bpm(self):
        self.slider_bpm.value = self.metronome.bpm
        self.label_bpm.text = self.build_bpm_text()

    def set_slider_beats(self):
        self.slider_beats.value = self.metronome.beats_per_bar
        self.label_beats.text = self.build_beats_text()

    def set_textinput_timer(self):
        self.textinput_timer.text = str(self.timer.seconds)

    def set_textinput_record_bars(self):
        self.textinput_record_bars.text = str(self.recorder_controller.record_bars)

    def set_togglebutton_play_beat(self):
        state = "normal"
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




    # Eventos de controles
    def on_play_beat(self, obj, value):
        self.metronome.play_beat = value == "down"

    def on_beats_per_bar(self, obj, value):
        self.metronome.beats_per_bar = round(value)
        self.label_beats.text = self.build_beats_text()
        self.metronome.reset_settings()
        self.loopstation.update_all_track_bars()
        self.set_metronome_view()
        self.set_widget_track_options()


    def on_bpm(self, obj, value):
        self.metronome.bpm = round(value)
        self.metronome.reset_settings()
        self.loopstation.update_all_track_bars()
        self.label_bpm.text = self.build_bpm_text()
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

    def on_timer(self, obj, text):
        number = self.filter_text_to_number(text)
        if number > 0:
            obj.text = str(number)
        else:
            obj.text = ""
        self.timer.set_seconds( seconds=number )





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
        self.sliders.clear()
        self.sliders.extend( [self.slider_beats, self.slider_bpm] )
        self.grid_tracks.clear_widgets()
        for track_id in self.loopstation.get_track_ids():
            track = self.loopstation.get_track( track_id )

            label_name = Label( text=str(track_id) )
            self.grid_tracks.add_widget(label_name)

            label_bars = Label( text=f"{get_text('bars')}: {round(track['bars'])}" )
            self.grid_tracks.add_widget( label_bars )

            if track['loop']:
                state = "down"
            else:
                state = "normal"
            togglebutton_loop = ToggleButton( text=get_text("loop"), state=state )
            togglebutton_loop.bind( on_press=partial(self.on_track_loop, track_id) )
            self.grid_tracks.add_widget( togglebutton_loop )

            if track['mute']:
                state = "down"
            else:
                state = "normal"
            togglebutton_mute = ToggleButton( text=get_text("mute"), state=state )
            togglebutton_mute.bind( on_press=partial(self.on_track_mute, track_id) )
            self.grid_tracks.add_widget( togglebutton_mute )

            slider_volume = Slider(
                min=0, max=100, value=int(track['volume']*100),
                orientation=self.get_screen_orientation()
            )
            slider_volume.bind( value_normalized=partial(self.on_track_volume, track_id) )
            self.sliders.append( slider_volume )
            self.grid_tracks.add_widget( slider_volume )

            if track['sample']:
                label = Label( text=str("sample") )
                self.grid_tracks.add_widget(label)
            else:
                checkbox = CheckBox( group="focus" )
                checkbox.active = track['focus']
                checkbox.bind( active=partial(self.on_track_focus, track_id) )
                self.grid_tracks.add_widget(checkbox)
        self.set_colors( self.config_controller.get_current_rgba_theme() )




    def on_play_loop_of_all_tracks(self, widget, state):
        self.loopstation.play_loop_of_all_tracks()
        self.set_widget_track_options()

    def on_break_loop_of_all_tracks(self, widget, state):
        self.loopstation.break_loop_of_all_tracks()
        self.set_widget_track_options()

    def on_reset_loop_of_all_tracks(self, widget, state):
        self.loopstation.reset_loop_of_all_tracks()
        self.set_widget_track_options()


    def open_popup_information(self, title, text_information):
        popup = PopupInformation(
            title=title, size_hint=(0.8, 0.8),
            text_information=text_information, text_ok=get_text('ok')
        )
        popup.open()

    def on_about(self, button):
        self.open_popup_information(
            title=get_text("about"), text_information=(
                f"[b]{NAME}[/b]: {get_text('version')} {VERSION}\n\n"
                f"- {get_text('developer')}: [b]{DEVELOPER}[/b]\n"
                f"- {get_text('website')}: [b]{WEBSITE}[/b]"
            )
        )

    def on_help(self, button):
        self.open_popup_information(
            title=get_text("help"), text_information=get_text('fps-sound-loopstation-help')
        )

    def on_numeric_metronome(self, widget, active):
        self.config_controller.update_numerical_view( active )
        self.set_metronome_view()

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

    def on_theme_selected(self, name):
        if self.config_controller.update_theme(name):
            rgba = self.config_controller.get_rgba_theme( name )
            self.set_colors(rgba)


    def build(self):
        # Color
        self.set_colors( self.config_controller.get_current_rgba_theme() )

        # Loop
        self.engine.start()
        self.icon = ICON

        # Images
        self.sticky_images = {
            "record": StickyImage(
                image=record_image, widget=self.record_button
            ),
            "play": StickyImage(
                image=play_image, widget=self.button_play
            ),
            "stop": StickyImage(
                image=stop_image, widget=self.button_stop
            ),
            "restart": StickyImage(
                image=restart_image, widget=self.button_restart
            ),
            "about": StickyImage(
                image=about_image, widget=self.menu_buttons["about"]
            ),
            "menu": StickyImage(
                image=menu_image, widget=self.button_menu
            ),
            "timer": StickyImage(
                image=timer_image, widget=self.label_timer
            )
        }
        for sticky_image in self.sticky_images.values():
            sticky_image.widget.text = ""
            #sticky_image.widget.background_color = (0,0,0,0)
            #sticky_image.widget.background_color = (0, 0.5, 0.4, 1)
            #sticky_image.widget.background_color = (0,0.4,0.4,1)

        # Text
        self.refresh_text()

        # widgets
        self.set_metronome_view()

        self.slider_beats.min = 1
        self.slider_beats.max = self.metronome.beats_limit_per_bar
        self.slider_beats.step = 1

        self.slider_bpm.min = 30
        self.slider_bpm.max = self.metronome.bpm_limit
        self.slider_bpm.step = 10

        self.sliders.extend( [self.slider_beats, self.slider_bpm] )

        # Samples
        #self.loopstation.save_track( path=SAMPLE_FILES[0], sample=True )
        #self.loopstation.save_track( path=SAMPLE_FILES[1], sample=True )

        # Establecer primer estado de los widgets
        self.set_slider_bpm()
        self.set_slider_beats()
        self.set_textinput_timer()
        self.set_textinput_record_bars()
        self.set_togglebutton_play_beat()
        self.set_togglebutton_limit_record()
        self.set_label_tracks_number()
        self.set_widget_track_options()

        # Bind
        self.slider_beats.bind( value=self.on_beats_per_bar )
        self.textinput_timer.bind( text=self.on_timer )
        self.slider_bpm.bind( value=self.on_bpm )
        self.textinput_record_bars.bind( text=self.on_record_bars )
        self.togglebutton_play_beat.bind( state=self.on_play_beat )
        self.togglebutton_limit_record.bind( state=self.on_limit_record )
        self.button_play.bind( state=self.on_play_loop_of_all_tracks )
        self.button_stop.bind( state=self.on_break_loop_of_all_tracks )
        self.button_restart.bind( state=self.on_reset_loop_of_all_tracks )

    def guide_sliders(self, orientation):
        '''
        Acomodar orientación de sliders, segun tamaño xy de ventana.
        '''
        for slider in self.sliders:
            if slider.orientation != orientation:
                slider.orientation = orientation

    def update_last_record_state(self, recorder_controller_signals):
        # Señal | Cuando se para la grabación
        if recorder_controller_signals["stop_record"]:
            ## Parar con señal, pero aveces no jala.
            self.last_microphone_recorder_state = self.microphone_recorder.state
            self.record_button.state = "normal"
            self.update_tracks = True # Pedir actualización

        # Actualizar ultimo estado de grabación. Determinar parar o no.
        if self.last_microphone_recorder_state != self.microphone_recorder.state:
            ## Forzar parar, por que aveces no llega la señal de parar. (Es por el loop del kivy
            self.last_microphone_recorder_state = self.microphone_recorder.state

            ## Se supone que ya debe jalar mejor sin limit bars. Testear grabar sin limit bars.
            ## El Engine jala bien, el problema son las señales, pero pos ya deberian jalar.
            if self.microphone_recorder.state == "stop":
                self.record_button.state = "normal"
                self.update_tracks = True # Pedir actualización

    def insert_track_options(self):
        '''
        Obtener tracks | Insertar track
        '''
        if self.current_count_temp_sound != self.loopstation.count_temp_sound:
            self.update_tracks = False
            self.current_count_temp_sound = self.loopstation.count_temp_sound
            self.set_widget_track_options()
            self.set_label_tracks_number()
            return True
        return False

    def update_track_options(self, dt):
        '''
        Obtener tracks | Actualización de track
        '''
        if self.update_tracks == False:
            # Asegurarse de reiniciar conteo de actualización de tracks
            self.accum_update_tracks = 0.0

        if self.update_tracks:
            if self.accum_update_tracks >= self.update_interval_tracks:
                self.update_tracks = False
                self.set_widget_track_options()
                self.set_label_tracks_number()
                return True
            else:
                self.accum_update_tracks += dt
        return False


    def record_with_timer(self, timer_signals):
        '''
        Timer | Record
        '''
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
        return timer_current_fps

    def turn_off_metronome_view(self):
        for i in range( 0, len(self.circles) ):
            if self.circles[i].color.rgb != self.rgb_off_tempo:
                self.circles[i].color.rgb = self.rgb_off_tempo

    def metronome_view(self, loopstation_signals, metronome_signals):
        '''
        Metronomo | Visual
        '''
        for i in range( 0, len(self.circles) ):
            if not metronome_signals['current_beat'] == i:
                self.circles[i].color.rgb = self.rgb_off_tempo

        if ( metronome_signals['current_beat'] in range(0, len(self.circles) ) ):
            # Solo beats existentes en circles.
            if loopstation_signals['emphasis_of_beat']['emphasis']:
                self.circles[ metronome_signals['current_beat'] ].color.rgb = self.rgb_first_tempo
            elif loopstation_signals['emphasis_of_beat']['neutral']:
                self.circles[ metronome_signals['current_beat'] ].color.rgb = self.rgb_another_tempo

    def metronome_numerical_view(self, loopstation_signals, metronome_signals):
        self.label_numeric_metronome.text = str( metronome_signals['current_beat']+1 )
        if loopstation_signals['emphasis_of_beat']['emphasis']:
            self.label_numeric_metronome.color = self.rgb_first_tempo
        elif loopstation_signals['emphasis_of_beat']['neutral']:
            self.label_numeric_metronome.color = self.rgb_another_tempo


    def timer_view(self, timer_current_fps):
        '''
        Visual Timer
        '''
        if timer_current_fps > 0:
            self.label_center.text = str(
                round( (self.timer.seconds_in_fps-timer_current_fps) / self.timer.fps)
            )
        else:
            self.label_center.text = ""


    # Actualizar todo
    def update(self, dt):
        '''
        Para la sincronización
        '''
        orientation = self.get_screen_orientation()

        if orientation != self.last_orientation:
            # Optimización para Celus
            self.guide_sliders( orientation )
            self._update_padding_using_resolution( orientation ) # Jala mejor fuera de aca.
            self.last_orientation = orientation

        # Señales
        signals = self.engine.get_last_signals()
        if not signals:
            return

        loopstation_signals = signals['loopstation']
        metronome_signals = signals['metronome']
        recorder_controller_signals = signals['recorder_controller']
        timer_signals = signals['timer']

        self.update_last_record_state( recorder_controller_signals )
        insert = self.insert_track_options()
        if not insert:
            update = self.update_track_options(dt)
        timer_in_fps = self.record_with_timer( timer_signals )
        if self.engine.state.value == "running":
            if not self.config.numerical_view:
                self.metronome_view( loopstation_signals, metronome_signals )
            else:
                self.metronome_numerical_view( loopstation_signals, metronome_signals )
        if self.engine.state.value == "stopped":
            self.turn_off_metronome_view()
        self.timer_view( timer_in_fps )
