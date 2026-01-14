from core.microphone_recorder import MicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from controller.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from core.fps_timer import FPSTimer
from core.fps_loop import FPSLoop


class FPSSoundLoopstationEngine():
    def __init__(
        self, sound_loopstation: FPSSoundLoopstation,
        recorder_controller: FPSSoundLoopstationRecorderController, timer: FPSTimer
    ):
        self.sound_loopstation = sound_loopstation
        self.metronome = self.sound_loopstation.fps_metronome
        self.recorder_controller = recorder_controller
        self.timer = timer

        self.loop = FPSLoop(
            fps=self.metronome.fps,
            callback=self.tick
        )

        self.last_signals = None

    def tick(self):
        loopstation_signals = self.sound_loopstation.update()
        metronome_signals = loopstation_signals['metronome']
        recorder_controller_signals = self.recorder_controller.update(
            metronome_signals=metronome_signals
        )
        timer_signals = self.timer.update()

        self.last_signals = {
            "loopstation": loopstation_signals,
            "metronome": metronome_signals,
            "recorder_controller": recorder_controller_signals,
            "timer": timer_signals,
        }

    def start(self):
        self.loop.start()
