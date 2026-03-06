# FPS Sound Loopstation Recorder Controller
Controler de Recorder y `FPSSoundLoopstation`, de preferencia un `MicrophoneRecorder()`, el cual tendra como atributo `state`, el cual debera indicar `record`, o `stop`.

Recomendado configurar el recorder y el loopstation antes de ponerlos como parametros.

`RecorderController` no hace calculos referentes al loop y sus frames, nada de eso. Solo cosas referentes al recording.

Ejemplo de uso:
```bash
loopstation = FPSSoundLoopstation(
    fps=FPS, volume=0.05, play_beat=True, beat_play_mode='emphasis_on_first'
)
recorder_controller = FPSSoundLoopstationRecorderController(
    fps_sound_loopstation=loopstation, recorder=MicrophoneRecorder()
)
metronome = loopstation.fps_metronome

loop = True
while loop:
    loopstation_signals = loopstation.update()
    recorder_controller_signals = recorder_controller.update( loopstation_signals['metronome']  )
```


`2026-03-06` `FPSSoundLoopstationRecorderController`: Error por salto de frames. Detectado por tener el engine a `20` fps, y opciones en `90` bpm, `3` beats.
```python
if limit_record:
    # Determinar limite, y si llego o paso el limite, parar grabación
    if count_fps >= self.fps_metronome.get_bars_to_fps(self.record_bars):
        self.record = False
        metronome_signals['frame_before_the_bar'] = True # Forzar parar. Para evitar errores por salta de frames.
```
