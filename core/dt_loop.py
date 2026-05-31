# Engine Loop
import threading, time


class DTLoop(threading.Thread):
    def __init__(self, callback, frame_duration:float=None, deamon=True):

        super().__init__(deamon=deamon)

        self._prev_time = time.perf_counter()
        self.callback = callback

        self._running = threading.Event()
        self._running.set()

        self._frame_duration = frame_duration

    def stop(self):
        self._running.clear()

    def run(self):
        while self._running.is_set():
            # Calcular delta time
            now = time.perf_counter()
            dt = now - self._prev_time
            self._prev_time = now

            # Eventos importantes
            self.callback(dt)

            # Limitar FPS
            if self._frame_duration:
                elapsed = time.perf_counter() - now
                sleep_time = self._frame_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
