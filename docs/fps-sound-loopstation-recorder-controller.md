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
