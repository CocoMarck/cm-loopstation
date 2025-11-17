from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import (
    ListProperty, NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock

FPS = float(60)
BPM_TO_SECONDS = 60

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

class LoopstationWindow(Widget):
    # Variables para el metrnomo
    bpm = BPM_TO_SECONDS / 120
    tempos = 4 # Cantidad de tiempos
    count_tempos = 0 # Contador de tiempos
    tempo = FPS*bpm # Tiempo individual.
    count = 0

    # Para dibujar el tempo
    circles = []

    # Posicionar metronomo
    def init_metronome(self):
        # Establecer circulos
        self.circles.clear()
        for x in range(0, self.tempos):
            circle = LoopstationCircle()
            self.circles.append( circle )
            self.add_widget(circle)

    def on_size(self, *args):
        '''
        Se llama automáticamente cada vez que cambia el tamaño del widget
        '''
        self.set_circle_position(0)

    def set_circle_position(self, dt):
        # Posicionar
        first_position = [self.width * 0.4, self.height * 0.75]
        multipler = 0
        for circle in self.circles:
            circle.x = first_position[0] + circle.width * multipler
            circle.y = first_position[1]
            multipler += 1



    # Actualizar todo
    def update(self, dt):
        '''
        Relacionado con el metronomo.
        '''
        change_time = self.count == self.tempo

        # Cambio de tempo
        if change_time:
            print(f"Cambio de tiempo: {self.count}")
            self.count = 0
            self.count_tempos += 1

        # Fin de compas
        change_compass = self.count_tempos == self.tempos
        if change_compass:
            print(f"Fin de compass: {self.tempos}")
            #self.count = 0
            self.count_tempos = 0

        # Inicio de compas
        init_compass = self.count == 0 and self.count_tempos == 0
        if init_compass:
            print("Compas iniciado")

        # Contador de tempo
        self.count += 1


        '''
        Visual de metronomo
        '''
        # Cambiar de color
        RGB_OFF_TEMPO = [1,1,1]
        RGB_FIRST_TEMPO = [0,1,0]
        RGB_TEMPO = [1,0,0]
        if self.count_tempos == 0:
            rgb = RGB_FIRST_TEMPO
        else:
            rgb = RGB_TEMPO
        self.circles[self.count_tempos].color.r = rgb[0]
        self.circles[self.count_tempos].color.g = rgb[1]
        self.circles[self.count_tempos].color.b = rgb[2]

        for index in range(0, len(self.circles)):
            if self.count_tempos != index:
                self.circles[index].color.r = RGB_OFF_TEMPO[0]
                self.circles[index].color.g = RGB_OFF_TEMPO[1]
                self.circles[index].color.b = RGB_OFF_TEMPO[2]



'''
Constructor de aplicación
'''
Window.size = (960, 540)
Window.resizable = True
class LoopstationApp(App):
    def build(self):
        loopstation = LoopstationWindow()
        loopstation.init_metronome()
        Clock.schedule_interval(loopstation.update, 1.0/FPS)
        return loopstation

if __name__ == '__main__':
    LoopstationApp().run()
