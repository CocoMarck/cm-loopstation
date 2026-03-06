# Recorder controller
`2026-03-06` `FPSSoundLoopstationRecorderController`: Error por salto de frames. Detectado por tener el engine a `20` fps, y opciones en `90` bpm, `3` beats.
```python
if limit_record:
    # Determinar limite, y si llego o paso el limite, parar grabación
    if count_fps >= self.fps_metronome.get_bars_to_fps(self.record_bars):
        self.record = False
        metronome_signals['frame_before_the_bar'] = True # Forzar parar. Para evitar errores por salta de frames.
```
