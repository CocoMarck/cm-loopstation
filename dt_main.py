from core.microphone_recorder import MicrophoneRecorder
from core.dt_metronome import DTMetronome
from core.dt_sound_loopstation import DTSoundLoopstation
from controllers.dt_sound_loopstation_recorder_controller import DTSoundLoopstationRecorderController
from core.dt_timer import DTTimer
from core.dt_sound_loopstation_engine import DTSoundLoopstationEngine
from controllers.beat_controller import BeatController
from core.sound_manager_kivy import SoundManagerKivy

from config.paths import SAMPLE_FILES, TEMP_DIR, ICON, CONFIG_ENGINE_FILE, CONFIG_GUI_FILE, THEMES_FILE

# Window
from views.dt_sound_loopstation_window import DTSoundLoopstationWindow


# Config
from controllers.fps_sound_loopstation.config_gui_controller import ConfigGUIController
from controllers.fps_sound_loopstation.config_engine_controller import ConfigEngineController
from entities.fps_sound_loopstation.config_engine import ConfigEngine
from entities.fps_sound_loopstation.config_gui import ConfigGUI
config_engine = ConfigEngine()
config_engine_controller = ConfigEngineController(
    config_engine, CONFIG_ENGINE_FILE
)
config_gui = ConfigGUI()
config_gui_controller = ConfigGUIController(
    config_gui, CONFIG_GUI_FILE, THEMES_FILE
)
print(
    config_gui_controller.get_theme_names(), config_gui.theme,
    config_gui_controller.get_current_rgba_theme()
)


# Constantes necesarias
VOLUME = 0.1#config_engine.volume
FPS_ENGINE = config_engine.fps
FPS_GUI = float(60)

## Colores
RGB_OFF_TEMPO = [1,1,1]
RGB_FIRST_TEMPO = [0,1,0]
RGB_ANOTHER_TEMPO = [1,0,0]

# FPSLoopstation Engine
sound_manager = SoundManagerKivy()
beat_controller = BeatController( sound_manager )
metronome = DTMetronome(
    beats_per_bar=config_engine.beats+1, beats_limit_per_bar=config_engine.beats_limit+1,
    bpm=config_engine.bpm, bpm_limit=config_engine.bpm_limit
)
loopstation = DTSoundLoopstation(
    dt_metronome=metronome, sound_manager=sound_manager, volume=VOLUME

)
microphone_recorder = MicrophoneRecorder()
recorder_controller = DTSoundLoopstationRecorderController(
    dt_sound_loopstation=loopstation, recorder=microphone_recorder,
    recorder_path=TEMP_DIR, fileformat="wav"
)
recorder_controller.limit_record = config_engine.limit_record
recorder_controller.record_bars = config_engine.record_bars
timer = DTTimer( seconds=config_engine.seconds, activate=False )
engine = DTSoundLoopstationEngine(
    sound_loopstation=loopstation, recorder_controller=recorder_controller, timer=timer
)

# App
## Forzar FPS
from kivy.config import Config
Config.set('kivy', 'window_icon', str(ICON))

# Inicializar
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock

# Color
from utils.colors import (
    get_rgba, invert_rgb, invert_rgba, rgba_to_normalized, scale_rgba, random_rgba,
    is_the_rgba_color_bright
)

'''
Constructor de aplicación
'''
# Standard de celus: `16:9`, `20:9`, `19:9`.
#Window.size = (20*50, 9*50)
#Window.size = (9*50, 20*50)
#Window.size = (16*50, 9*50)
#Window.size = (512, 512)
#Window.resizable = True
loopstation.save_track(path=SAMPLE_FILES[0], loop=True, sample=True)
loopstation.save_track(path=SAMPLE_FILES[3], loop=True, sample=True)
#recorder_controller.record = True
class FPSSoundLoopstationApp(App):
    def build(self):
        #x_color = random_rgba()

        # Ventana
        window = DTSoundLoopstationWindow(
            engine=engine,
            vertical_padding_offsets=[0,0.05, 0,0.08], # Margen pa celu
            horizontal_padding_offsets=[0,0.05, 0.08,0], # Margen pa celu
            config_controller=config_gui_controller
        )

        # Construir
        window.build()

        # Delta Time, GUI loop
        Clock.schedule_interval(window.update, 0)

        return window

    # Pause y resume an android
    def on_pause(self):
        return self.window.on_pause()

    def on_resume(self):
        self.window.on_resume()




if __name__ == '__main__':
    FPSSoundLoopstationApp().run()
