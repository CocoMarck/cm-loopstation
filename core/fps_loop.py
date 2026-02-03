import threading
import time


class FPSLoop(threading.Thread):
    """
    FPSLoop
    -------
    Simple fixed-FPS loop running in a background thread.

    This implementation is based on common game-loop and
    fixed-timestep patterns widely used in game engines
    and real-time applications.

    No external code was copied verbatim.
    """

    def __init__(self, fps, callback, daemon=True):
        super().__init__(daemon=daemon)
        self.fps = fps
        self.callback = callback

        self._running = threading.Event()
        self._running.set()

        self._frame_duration = 1.0 / fps

    def stop(self):
        self._running.clear()

    def run(self):
        next_frame_time = time.perf_counter()

        while self._running.is_set():
            self.callback()

            next_frame_time += self._frame_duration
            sleep_time = next_frame_time - time.perf_counter()

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                next_frame_time = time.perf_counter()
