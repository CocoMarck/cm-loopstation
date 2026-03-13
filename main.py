from core.microphone_recorder import MicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from controllers.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from core.fps_timer import FPSTimer
from core.fps_loop import FPSLoop
from core.fps_sound_loopstation_engine import FPSSoundLoopstationEngine

from config.paths import SAMPLE_FILES, TEMP_DIR, ICON

# Window
from views.fps_sound_loopstation_window import FPSSoundLoopstationWindow


# Config
from controllers.fps_sound_loopstation.config_engine_controller import ConfigEngineController
from entities.fps_sound_loopstation.config_engine import ConfigEngine
config_engine = ConfigEngine()
config_engine_controller = ConfigEngineController(
    config_engine, "./config/fps_sound_loopstation/engine.toml"
)


# Constantes necesarias
VOLUME = config_engine.volume
FPS_ENGINE = config_engine.fps
FPS_GUI = float(60)

## Colores
RGB_OFF_TEMPO = [1,1,1]
RGB_FIRST_TEMPO = [0,1,0]
RGB_ANOTHER_TEMPO = [1,0,0]

# FPSLoopstation Engine
loopstation = FPSSoundLoopstation(
    fps=FPS_ENGINE, volume=config_engine.volume, play_beat=config_engine.play_beat, beat_play_mode='emphasis_on_first',
    beats_per_bar=config_engine.beats, beats_limit_per_bar=config_engine.beats_limit,
    bpm=config_engine.bpm, bpm_limit=config_engine.bpm_limit
)
metronome = loopstation.fps_metronome
microphone_recorder = MicrophoneRecorder()
recorder_controller = FPSSoundLoopstationRecorderController(
    fps_sound_loopstation=loopstation, recorder=microphone_recorder,
    recorder_path=TEMP_DIR, fileformat="wav"
)
recorder_controller.limit_record = config_engine.limit_record
recorder_controller.record_bars = config_engine.record_bars
timer = FPSTimer( fps=FPS_ENGINE, seconds=config_engine.seconds, activate=False )
engine = FPSSoundLoopstationEngine(
    sound_loopstation=loopstation, recorder_controller=recorder_controller, timer=timer
)

# App
## Forzar FPS
from kivy.config import Config
Config.set('graphics', 'vsync', '0')
Config.set('graphics', 'maxfps', str(FPS_GUI))
Config.set('kivy', 'window_icon', str(ICON))

# Inicializar
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock

# Widgets a estilizar
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button

# Funciones para estilizar
from kivy.graphics import Color, Rectangle

# Color
from utils.colors import (
    get_rgba, invert_rgb, invert_rgba, rgba_to_normalized, scale_rgba, random_rgba
)

'''
Constructor de aplicación
'''
# Standard de celus: `16:9`, `20:9`, `19:9`.
#Window.size = (20*50, 9*50)
Window.size = (9*50, 20*50)
#Window.size = (16*50, 9*50)
#Window.size = (512, 512)
#Window.resizable = True
class FPSSoundLoopstationApp(App):
    def build(self):
        #x_color = get_rgba(31, 63, 15, 255)
        x_color = random_rgba()
        x_color_less = scale_rgba( x_color, 0.75 )
        invert_x_color = invert_rgba( x_color )
        invert_x_color_more = scale_rgba( invert_x_color, 1.2 )

        # Fondos
        Label.color = rgba_to_normalized( invert_x_color )
        TextInput.background_color = rgba_to_normalized( invert_x_color )
        TextInput.foreground_color = rgba_to_normalized( x_color )
        # Evitar modificar widgets que usan images. Como: Button, Slider, etc.
        Button.color = [1,1,1,1] # Esto lo tengo que poner, porque label remplaza esto.

        # Ventana
        window = FPSSoundLoopstationWindow(
            engine,
            vertical_padding_offsets=[0,0.05, 0,0.08],
            horizontal_padding_offsets=[0,0.05, 0.08,0],
        )

        # Fondo
        window.rgb_off_tempo = rgba_to_normalized( x_color_less )
        window.rgb_first_tempo = rgba_to_normalized( invert_x_color )
        window.rgb_another_tempo = rgba_to_normalized( invert_x_color_more )

        with window.canvas.before:
            Color(
                *rgba_to_normalized( x_color )
            )
            rect_window = Rectangle(pos=window.pos, size=window.size)
        window.bind(
            pos=lambda inst, val: setattr(rect_window, 'pos', inst.pos),
            size=lambda inst, val: setattr(rect_window, 'size', inst.size)
        )

        with window.scroll_widget.canvas.before:
            Color(
                *rgba_to_normalized( x_color_less )
            )
            rect = Rectangle(pos=window.scroll_widget.pos, size=window.scroll_widget.size)
        window.bind(
            pos=lambda inst, val: setattr(rect, 'pos', inst.pos),
            size=lambda inst, val: setattr(rect, 'size', inst.size)
        )

        # Construir
        window.build()

        # Delta Time, GUI loop
        Clock.schedule_interval(window.update, 1.0/FPS_GUI)

        return window

    # Pause y resume an android
    def on_pause(self):
        return self.window.on_pause()

    def on_resume(self):
        self.window.on_resume()




if __name__ == '__main__':
    FPSSoundLoopstationApp().run()

# A guardar al cerrar
config_engine_controller.update_beats( metronome.beats_per_bar )
config_engine_controller.update_bpm( metronome.bpm )
config_engine_controller.update_play_beat( metronome.play_beat )

config_engine_controller.update_limit_record( recorder_controller.limit_record )
config_engine_controller.update_record_bars( recorder_controller.record_bars )

config_engine_controller.update_seconds( timer.seconds )
