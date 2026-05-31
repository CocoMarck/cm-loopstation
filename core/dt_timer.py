class DTTimer():
    def __init__(self, seconds=10, activate=False ):
        self._seconds = seconds
        self._count_dt = 0

        # Relacionado con activar timer
        self.activate = activate

    def reset(self):
        self._count_dt = 0

    def get_seconds(self):
        return self._seconds

    def set_seconds(self, seconds):
        self._seconds = seconds

    def determinate_stop(self, dt):
        if not self.activate:
            self.reset()

        current_dt = self._count_dt
        start_timer = (current_dt == 0) and (self.activate)
        timer_finished = current_dt >= self._seconds
        if timer_finished:
            self.reset()

        return {
            'current_dt': current_dt,
            'start_timer': start_timer,
            'timer_finished': timer_finished
        }

    def update(self, dt):
        signals = self.determinate_stop(dt)

        if not signals['timer_finished']:
            self._count_dt += dt

        return signals
