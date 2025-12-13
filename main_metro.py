from core.text_util import ignore_text_filter, PREFIX_NUMBER
from core.fps_metronome import FPSMetronome


# Constantes necesarias
VOLUME = float(1)
FPS = int(20)
BPM_TO_SECONDS = int(60)


## Colores
RGB_OFF_TEMPO = [1,1,1]
RGB_FIRST_TEMPO = [0,1,0]
RGB_ANOTHER_TEMPO = [1,0,0]


# Forzar FPS
from kivy.config import Config
Config.set('graphics', 'vsync', '0')
Config.set('graphics', 'maxfps', str(FPS))

# App
from kivy.app import App

# Kivy
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.lang import Builder
kv = '''
#:import Window kivy.core.window.Window
<Label>:
    font_size: min(Window.width, Window.height) * 0.05
<TextInput>
    font_size: min(Window.width, Window.height) * 0.05
    size_hint_y: None
    pos_hint: {"center_y": 0.5}
<ToggleButton>:
    font_size: min(Window.width, Window.height) * 0.05
'''
Builder.load_string(kv)


# Circulo
class GoodCircle(Widget):
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
class MetronomeRoot( BoxLayout ):
    '''
    El tempo de preferencia que sea un entero.
    '''
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # Reproducir o no
        self.start = True

        # Widgets
        ## BPM, Volume, Beats
        hbox = BoxLayout( orientation="horizontal" )
        self.add_widget( hbox )

        self.label_bpm = Label( text="bpm" )
        hbox.add_widget( self.label_bpm )

        self.textinput_bpm = TextInput()
        hbox.add_widget( self.textinput_bpm )

        self.label_volume = Label( text="volume" )
        hbox.add_widget( self.label_volume )

        self.textinput_volume = TextInput()
        hbox.add_widget( self.textinput_volume )

        self.label_beats = Label( text="beats" )
        hbox.add_widget( self.label_beats )

        self.textinput_beats = TextInput()
        hbox.add_widget( self.textinput_beats )

        ## Metronome circles
        self.hbox_metronome = BoxLayout( orientation="horizontal" )
        self.add_widget( self.hbox_metronome )

        ## Start, Title, Play beat
        hbox = BoxLayout( orientation="horizontal" )
        self.add_widget( hbox )

        self.togglebutton_start = ToggleButton( text="start" )
        hbox.add_widget( self.togglebutton_start )

        self.label_title = Label( text="fps-metronome" )
        hbox.add_widget( self.label_title )

        self.togglebutton_play_beat = ToggleButton( text="play-beat" )
        hbox.add_widget( self.togglebutton_play_beat )

        # FPSLoopstation
        self.fps_metronome = FPSMetronome(
            fps=FPS, bpm_limit=200, beats_limit_per_bar=7, volume=1, play_beat=True,
            beat_play_mode='emphasis_on_first', log_level="info"
        )

        self.circles = []


    # Posicionar metronomo
    def update_metronome_circles(self):
        # Establecer circulos
        self.circles.clear()
        self.hbox_metronome.clear_widgets()
        for x in range(0, self.fps_metronome.beats_per_bar+1):
            circle = GoodCircle()
            self.circles.append( circle )
            self.hbox_metronome.add_widget(circle)

    def set_textinput_bpm(self):
        self.textinput_bpm.text = str( self.fps_metronome.bpm )

    def set_textinput_beats(self):
        self.textinput_beats.text = str( self.fps_metronome.beats_per_bar+1 )

    def set_togglebutton_play_beat(self):
        if self.fps_metronome.play_beat:
            state = "down"
        else:
            state = "normal"
        self.togglebutton_play_beat.state = state

    def set_togglebutton_start(self):
        if self.start:
            state = "down"
        else:
            state = "normal"
        self.togglebutton_start.state = state


    def set_textinput_volume(self):
        self.textinput_volume.text = str( int(self.fps_metronome.volume*100) )




    def filter_text_to_number(self, textinput:str):
        '''
        Filtrar texto del numero de compases a grabar
        '''
        text = ignore_text_filter( textinput, PREFIX_NUMBER )
        if text == None:
            number = 0
        else:
            number = int(text)
        return number

    def on_bpm(self, obj, text):
        number = self.filter_text_to_number( text )
        if number >= 10:
            self.fps_metronome.bpm = number
            self.fps_metronome.reset_settings()
            self.set_textinput_bpm()

        if number == 0:
            obj.text = ""



    def on_beats(self, obj, text):
        number = self.filter_text_to_number( text )
        if number >= 2:
            self.fps_metronome.beats_per_bar = number-1
            self.fps_metronome.reset_settings()
            self.update_metronome_circles()
            self.set_textinput_beats()

        else:
            if number > 0:
                obj.text = str(number)
            else:
                obj.text = ""


    def on_play_beat(self, obj, state):
        self.fps_metronome.play_beat = state == "down"

    def on_start(self, obj, state):
        self.start = state == "down"
        self.fps_metronome.reset_settings()
        self.update_metronome_circles()

    def on_volume(self, obj, text):
        number = self.filter_text_to_number( text )
        divide = number > 0

        volume = 0
        if divide:
            if number > 100:
                number = 100
            volume = float(number/100)
        else:
            obj.text = ""
        self.fps_metronome.volume = volume
        self.fps_metronome.set_beat_sound_volume()
        if divide:
            self.set_textinput_volume()







    def init_the_essential(self):
        self.update_metronome_circles()

        # Establecer primer estado de los widgets
        self.set_textinput_bpm()
        self.set_textinput_beats()
        self.set_togglebutton_play_beat()
        self.set_togglebutton_start()
        self.set_textinput_volume()

        # Bind
        self.textinput_bpm.bind( text=self.on_bpm )
        self.textinput_beats.bind( text=self.on_beats )
        self.togglebutton_play_beat.bind( state=self.on_play_beat )
        self.togglebutton_start.bind( state=self.on_start )
        self.textinput_volume.bind( text=self.on_volume )




    # Actualizar todo
    def update(self, dt):
        '''
        Para la sincronización
        '''
        if self.start:
            signals = self.fps_metronome.update()

            # Metronomo | Visual
            for i in range( 0, len(self.circles) ):
                if not signals['metronome']['current_beat'] == i:
                    self.circles[i].color.rgb = RGB_OFF_TEMPO

            if signals['emphasis_of_beat']['emphasis']:
                self.circles[ signals['metronome']['current_beat'] ].color.rgb = RGB_FIRST_TEMPO
            elif signals['emphasis_of_beat']['neutral']:
                self.circles[ signals['metronome']['current_beat'] ].color.rgb = RGB_ANOTHER_TEMPO




'''
Constructor de aplicación
'''
class MetronomeApp(App):
    def build(self):
        root = MetronomeRoot()
        root.init_the_essential()
        Clock.schedule_interval(root.update, 1.0/FPS)
        return root

if __name__ == '__main__':
    MetronomeApp().run()
