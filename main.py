from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.clock import Clock

FPS = float(60)
BPM_TO_SECONDS = 60

class LoopstationCircle(Widget):
    pass

class LoopstationWindow(Widget):
    circle = ObjectProperty(None)

    # Para el metrnomo
    bpm = BPM_TO_SECONDS / 120
    tempos = 4 # Cantidad de tiempos
    count_tempos = 0 # Contador de tiempos
    tempo = FPS*bpm # Tiempo individual.
    count = 0

    # Posicionar metronomo
    def init_metronome(self):
        self.circle.center = self.center

    # Actualizar todo
    def update(self, dt):
        change_time = self.count == self.tempo

        # Cambio de tempo
        if change_time:
            print(f"Cambio de tiempo: {self.count}")
            self.count = 0
            self.count_tempos += 1
            self.circle.x += 1

        # Inicio de compas
        init_compass = self.count == 0 and self.count_tempos == 0
        if init_compass:
            print("Compas iniciado")

        # Fin de compas
        change_compass = self.count_tempos == self.tempos
        if change_compass:
            print(f"Fin de compass: {self.tempos}")
            self.count_tempos = 0
            self.circle.x -= self.tempos

        # Contador de tempo
        self.count += 1

class LoopstationApp(App):
    def build(self):
        loopstation = LoopstationWindow()
        loopstation.init_metronome()
        Clock.schedule_interval(loopstation.update, 1.0/FPS)
        return loopstation

if __name__ == '__main__':
    LoopstationApp().run()
