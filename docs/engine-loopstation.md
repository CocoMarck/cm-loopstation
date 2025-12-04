# Motor de loopstation
Pienso hacer esta app con varios frameworks, kivy, pygame, qt, y gtk.

Sera simplemente un objeto con atributos relacionados al loop. Todo el funcionamiento se basara con fps. Seran FPS fijos.

Tendra metodos de detección de beats, de compass...

Determinar latencia, basado en FPS fijos. Calcular eso con método.

## Atributos
> Los compass se componen por beats.

`FPS`: Fotogramas por segundo. `INT`.

### Metronomo
**BPM y cantidad de latidos**
- `bpm`: beats por minuto
- `beats_per_compas`: cantidad de latidos que equivalen a un compass. Se cuenta desde cero.
- `current_beat`: tempo actual

**En segundos reales**
- `beat_in_seconds`: bpm a segundos.
- `compas_in_seconds`: equivalencia en segundos del compass.

**FPS**
- `beat_in_fps`: equivalencie de latido en fps
- `compas_in_fps`: equivalencia del compass en fps
- `count_fps`: contador de fps

**Boleanos para determinar posición tempo actual**
- `change_beat`: Cambiar de tempo.
- `change_compas`: Empezar de nuevo.
- `is_first_beat`: Esta en el primer frame del beat.
- `is_last_beat`: Esta en el ultimo frame del seundo beat.
- `is_another_beat`: Esta en el primer frame de cualquier beat que no sea ni el ultimo ni el primero.

**Pistas**
- `dict_track`: Diccionario de pistas, cada key es tiene un sonido y sus atributos. Con un `len()`, se obtendra la cantidad de pistas.
- `focus_track`: Se usara para remplazar `key` de `dict_track`. Para remplazar pista.
- `track_limit`: Limite de pistas.

**Grabación**
- `microphone_recorder`: `MicrophoneRecorder()` para grabar microfono.
- `record`: Grabando o no.
- `record_activated_limit`: Activar limite de grabación.
- `record_force_stop`: Parar grabación.
- `record_count`: Contar mienstras se graba.
- `record_compass_limit`: Cantidad de compases.
- `record_limit_in_fps`: Limite en fps.
- `current_file_to_save`: Archivo actual a guardar. Remplaza o guarda, da igual. De que se guarda se guarda.

**Timer**
- `timer`: Activar o no timer.
- `timer_completed`: `bool` Se completo el timer.
- `timer_in_seconds`: Segundos del timer.
- `timer_in_fps`: Cantidad de timer.
- `timer_count`: Contador en FPS.

**Debug** Usar logger.
- `save_debug`: Guardar debug.
- `verbose`: Mostrar o no debug en pantalla.


----

# Ejemplos de obtención de datos
## Cantidad de beats por compas

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
    "compass": int  # Cantidad de compases
    "current_compass": int
}
```

# `MicrophoneRecorder()`
Con que tenga método `record()`, `stop()`, y atributo `state`= `record` o `stop`. El stop guarda el archivo.