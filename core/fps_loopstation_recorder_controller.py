from core.microphone_recorder import MicrophoneRecorder
from core.fps_sound_loopstation import FPSSoudLoopstation

# Constantes necesarias
AUDIO_NAME_PREFIX = "track-"

class FPSLoopstationRecorderController():
    def __init__(self, recorder=MicrophoneRecorder(), fileformat="wav"):

        self.recorder = recorder
        self.fps_loopstation = FPSSoudLoopstation()
        self.fileformat = fileformat
