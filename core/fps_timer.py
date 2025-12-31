class FPSTimer():
    def __init__(self, fps=30, seconds=10, activate=False ):
        self.fps = fps
        self.seconds = seconds
        self.seconds_in_fps = self.get_seconds_in_fps()
        self.count_fps = 0

        # Relacionado con activar timer
        self.activate = activate

    def reset(self):
        self.count_fps = 0

    def get_seconds_in_fps(self):
        return self.seconds*self.fps

    def set_seconds_in_fps(self):
        self.seconds_in_fps = self.get_seconds_in_fps()

    def set_seconds(self, seconds):
        self.seconds = seconds
        self.set_seconds_in_fps()

    def determinate_stop(self):
        if not self.activate:
            self.reset()

        current_fps = self.count_fps
        start_timer = (current_fps == 0) and (self.activate)
        timer_finished = current_fps >= self.seconds_in_fps
        if timer_finished:
            self.reset()

        return {
            'current_fps': current_fps,
            'start_timer': start_timer,
            'timer_finished': timer_finished
        }

    def update(self):
        signals = self.determinate_stop()

        if not signals['timer_finished']:
            self.count_fps += 1

        return signals
