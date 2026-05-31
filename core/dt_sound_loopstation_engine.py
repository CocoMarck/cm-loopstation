from core.dt_metronome import DTMetronome
from core.dt_sound_loopstation import DTSoundLoopstation
from controllers.dt_sound_loopstation_recorder_controller import DTSoundLoopstationRecorderController
from controllers.beat_controller import BeatController
from core.dt_timer import DTTimer


class DTSoundLoopstationEngine():
    def __init__(
        self, sound_loopstation: DTSoundLoopstation, recorder_controller: DTSoundLoopstationRecorderController, timer: DTTimer
    ):
        self.sound_loopstation = sound_loopstation
        self.metronome = sound_loopstation.metronome
        self.recorder_controller = recorder_controller
        self.timer = timer

    def update(self, dt):
        metronome_signals = self.metronome.update(dt)

        loopstation_signals = self.sound_loopstation.update(dt, metronome_signals)
        recorder_controller_signals = self.recorder_controller.update( dt, metronome_signals )
        timer_signals = self.timer.update(dt)

        return {
            "loopstation": loopstation_signals,
            "metronome": metronome_signals,
            "recorder_controller": recorder_controller_signals,
            "timer": timer_signals
        }
