from core.text_util import ignore_text_filter, PREFIX_NUMBER
from core.fps_metronome import FPSMetronome
from config.paths import TEMPO_DIR


# Constantes necesarias
VOLUME = float(1)
FPS = int(20)
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
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock


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
        self.ellipse.pos = self.pos
        self.ellipse.size = ( min(self.size), min(self.size) )


# Ventana, el loop del porgrama
class MetronomeWindow(Widget):
    '''
    El tempo de preferencia que sea un entero.
    '''
    # Objetos del `archivo.kv`
    label_bpm = ObjectProperty(None)
    textinput_bpm = ObjectProperty(None)
    label_beats = ObjectProperty(None)
    textinput_beats = ObjectProperty(None)
    hbox_metronome = ObjectProperty(None)

    # FPSLoopstation
    fps_metronome = FPSMetronome(
        fps=FPS, bpm_limit=200, beats_limit_per_bar=7, volume=1, play_beat=True,
        beat_play_mode='emphasis_on_first', log_level="info"
    )

    circles = []


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
            self.fps_metronome.bpm = number
            self.fps_metronome.reset_settings()
            self.set_textinput_bpm()


    def on_beats(self, obj, text):
        number = self.filter_text_to_number( text )
        if number >= 2:
            self.fps_metronome.beats_per_bar = number-1
            self.fps_metronome.reset_settings()
            self.update_metronome_circles()
            self.set_textinput_beats()




    def init_the_essential(self):
        self.update_metronome_circles()

        # Establecer primer estado de los widgets
        self.set_textinput_bpm()
        self.set_textinput_beats()

        # Bind
        self.textinput_bpm.bind( text=self.on_bpm )
        self.textinput_beats.bind( text=self.on_beats )




    # Actualizar todo
    def update(self, dt):
        '''
        Para la sincronización
        '''
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
Window.size = (540, 960)
Window.resizable = True
class MetronomeApp(App):
    def build(self):
        window = MetronomeWindow()
        window.init_the_essential()

        Clock.schedule_interval(window.update, 1.0/FPS)

        return window

if __name__ == '__main__':
    MetronomeApp().run()
