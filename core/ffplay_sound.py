import subprocess, json

class FFPlaySound:
    def __init__(self, source, volume=1.0):
        self.source = source
        self.volume = volume
        self.process = None
        self._length = None

    def play(self):
        self.process = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-af", f"volume={self.volume}", self.source],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

    def is_playing(self):
        return self.process and self.process.poll() is None

    def set_volume(self, volume):
        self.volume = volume
        if self.is_playing():
            self.stop()
            self.play()

    def _probe_length(self) -> float:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet",
             "-print_format", "json",
             "-show_streams", str(self.source)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        return float( data["streams"][0]["duration"] )

    def get_length(self) -> float:
        if self._length is None:
            self._length = self._probe_length()
        return self._length

    def __del__(self):
        # Para cerrar proceso.
        self.stop()

