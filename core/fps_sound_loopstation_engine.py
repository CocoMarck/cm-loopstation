from core.fps_sound_loopstation import FPSSoundLoopstation
from controller.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from core.fps_timer import FPSTimer
from core.fps_loop import FPSLoop

from threading import Lock
from enum import Enum


class EngineState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class FPSSoundLoopstationEngine():
    def __init__(
        self, sound_loopstation: FPSSoundLoopstation,
        recorder_controller: FPSSoundLoopstationRecorderController, timer: FPSTimer
    ):
        self.sound_loopstation = sound_loopstation
        self.metronome = self.sound_loopstation.fps_metronome
        self.recorder_controller = recorder_controller
        self.timer = timer

        self.loop = None

        self._last_signals = None

        # Estados
        self.state = EngineState.IDLE

        # Bloquear
        self._lock = Lock()

    def tick(self):
        loopstation_signals = self.sound_loopstation.update()
        metronome_signals = loopstation_signals['metronome']
        recorder_controller_signals = self.recorder_controller.update(
            metronome_signals=metronome_signals
        )
        timer_signals = self.timer.update()

        signals = {
            "loopstation": loopstation_signals,
            "metronome": metronome_signals,
            "recorder_controller": recorder_controller_signals,
            "timer": timer_signals,
        }

        with self._lock:
            self._last_signals = signals

    def get_last_signals(self):
        with self._lock:
            return dict(self._last_signals) if self._last_signals else None
        return None

    def pause(self):
        self.sound_loopstation.break_loop_of_all_tracks()
        self.loop.stop()
        self.loop.join()
        self.state = EngineState.PAUSED

    def stop(self):
        self.metronome.reset_settings()
        self.sound_loopstation.break_loop_of_all_tracks()
        self.loop.stop()
        self.loop.join()
        self.state = EngineState.STOPPED

    def start(self):
        if self.loop and self.loop.is_alive():
            return
        self.loop = FPSLoop(
            fps=self.metronome.fps,
            callback=self.tick
        )
        self.loop.start()
        self.state = EngineState.RUNNING
