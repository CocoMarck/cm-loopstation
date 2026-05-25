import subprocess

class FFPlaySound:
    def __init__(self, source, volume=1.0):
        self.source = source
        self.volume = volume
        self.process = None

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
