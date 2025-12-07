# Motor de loopstation
Pienso hacer esta app con varios frameworks, kivy, pygame, qt, y gtk.

Sera simplemente un objeto con atributos relacionados al loop. Todo el funcionamiento se basara con fps. Seran FPS fijos.

Tendra metodos de detección de beats, de bars...

Determinar latencia, basado en FPS fijos. Calcular eso con método.

## Atributos
> Los bars se componen por beats.

`FPS`: Fotogramas por segundo. `INT`.

### Metronomo
**BPM y cantidad de latidos**
- `bpm`: beats por minuto
- `beats_per_bar`: cantidad de latidos que equivalen a un bars. Se cuenta desde cero.
- `current_beat`: tempo actual

**En segundos reales**
- `beat_in_seconds`: bpm a segundos.
- `bar_in_seconds`: equivalencia en segundos del bars.

**FPS**
- `beat_in_fps`: equivalencie de latido en fps
- `bar_in_fps`: equivalencia del bars en fps
- `count_fps`: contador de fps

**Boleanos para determinar posición tempo actual**
- `change_beat`: Cambiar de tempo.
- `change_bar`: Empezar de nuevo.
- `is_first_beat`: Esta en el primer frame del beat.
- `is_last_beat`: Esta en el ultimo frame del seundo beat.
- `is_another_beat`: Esta en el primer frame de cualquier beat que no sea ni el ultimo ni el primero.

**Pistas**
- `DEFAULT_VOLUME`: Volumen default. Valor flotante. 1.0
- `volume`: Volumen real. Por defecto, el `DEFAULT_VOLUME`
- `dict_track`: Diccionario que contendra las pistas y sus atributos.
- `count_saved_track`: Contador de pistas guardadas.
- `count_temp_sound`: Contador de sonidos temporales.
- `temp_sound_limit`: Limite de sonidos temporales.
- `count_sample_sound`: Contador de sonidos tipo sample.
- `sample_sound_limit`: Limite de sonidos tipo sample.

**Grabación**
- `microphone_recorder`: Objeto que sirve para grabar el mocrofono. Tiene atributo de state, deben ser `record` y `stop`
- `recording`: Grabando.
- `recorder_limit_in_bars`: Limite de grabador en compases.
- `recorder_limit_in_seconds`: Limite de grabador en segundos.
- `recorder_limit_in_fps`: Limite de grabador en fps.
- `recorder_count_fps`: Contador de grabación en fps.

**Timer**
- `timer`: Activar o no timer.
- `timer_completed`: `bool` Se completo el timer.
- `timer_in_seconds`: Segundos del timer.
- `timer_in_fps`: Cantidad de timer.
- `timer_count`: Contador en FPS.

**Debug** Usar logger.
- `save_debug`: Guardar debug.
- `verbose`: Mostrar o no debug en pantalla.


## Metodos a detacar:
- `determine_current_beat()`: Establce en los atributos el beat actual. Indica en boleanos si es el primer beat, o el ultimo.

- `save_track()`: Guarda una pista en el diccionario `dict_track`. Con donde cada key tendra contendra este diccionario: `sound, source, length, volume, length, mute, loop, sample, focus, bars, length_in_fps, count_fps`. Sola añadira dentro de los limites, de lo contrario se ignora. Devolvera si actualizo o incerto, mediante un `dict`.

- `playback_track()`: Reprodcir pistas, de manera sincronizada con el metronomo. Usa parametros de track, y inicia solo al inicio del compas, y termina en la `length_in_fps`, determinado por el track, sin importar otra cosa.

- `track_recording()`: Con el boleano `recording`, se encarga de grabar con `microphone_recorder`. Solo si este esta inactivo, y si se inicia en el inicio del compas, primer frame del compas. Se detiene si se determina un limite de grabación, de lo contrario `recording` tiene que establecerse en falso. Este guardara siempre un `temp_sound`.

----

# Ejemplos de obtención de datos
## Cantidad de beats por bar

---

# `SoundObject`
El sound object se le debera poder obtener su duración y su volumen. Y claro, reproducir y parar.

## `dict_track`
```python
{
    "track": SoundObject(),
    "loop": bool,   # Reproducir o no.
    "volume": 1.0,  # 1.0 es el maximo de volumen
    "mute": bool,
    "bars": int  # Cantidad de bares
    "current_bars": int
}
```

# `MicrophoneRecorder()`
Con que tenga método `record()`, `stop()`, y atributo `state`= `record` o `stop`. El stop guarda el archivo.
