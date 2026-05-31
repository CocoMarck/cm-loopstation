import imageio_ffmpeg as ffmpeg
import subprocess
import pyaudio
import numpy as np

from entities.isound_manager import ISoundManager

class SoundManagerFFmpeg(ISoundManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, name="SoundManagerFFmpeg", filename="sound_manager_ffmpeg", **kwargs)

        self._p = pyaudio.PyAudio()
        self._stream = self._p.open( format=pygame.paInt16, chanels=2, rate=44100, output=True )

        self._cmd = [
            ffmpeg.get_ffmpeg_exe(),
            "-i", url,
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "-ac", "2",
            "-ar", "44100",
            "-"
        ]
        self._chuck_size = 4096
        self._process = subprocess.Popen( cmd, stdout=subprocess.PIPE() )

    def play_sound(self, sound):
        while True:
            data = self._process.stdout.read(self._chuck_size)
            if not data:
                break
            pcm = np.frombuffer(data, dtype=np.int16)
            pcm = np.clip(pcm * self.volume )
            self._stream.write( pcm.tobytes() )
        self._stream.stop_stream()
        self._stream.close()
        self._p.terminate()
        self._process.terminate()

