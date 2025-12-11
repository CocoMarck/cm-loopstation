# Registro
- `2025-11-20`: El atributo `tempo` de `LoopstationWindow` de preferencia que sea un entero. Igual jala con flotante, pero de manera por esto `self.count >= self.tempo`.
- `2025-11-25`: La grabación solo se reproduce cuando se empieza a grabar desde el segundo tempo. Bastante raro. Aun no se porque. La verdad ni estoy seguro si es así como digo, pero checar la versión de esta fecha por si surgen problemas.
- `2025-11-25`: La solución de la reproducción correcta del bucle es terminar al primer frame del ultimo tempo del compas. Eso da tiempo a reproducir el bucle. Parece que es un problema de como se reproducen los bucles.
- `2025-11-25`: En Wayland KDE PLasma AMD RX 6400, Kivy no respeta los fps indicados, el update esta en los `fps` que se le da la gana. Ese rompe por completo la funcionalidad del loop.
- `2025-11-28`: No era el wayland ni KDE, si era Kivy. Limitar a 20 fps si lo hace, pero mas de eso limita lo que quiere. Se tiene que importar y configurar primero `Config`, y despues se importa todo lo demas componentes de `Kivy`, `App, Widget, Label...`.
- `2025-11-30`: Muchas veces muestro flotntes como enteros, o los redondeo. Es por eso que aveces el contdor de compses de un track puede ser $0.7$, y me lo pone como uno, y pos no dura un compas. O puede ser $1.2$ y pos tampoco dura eso.
- `2025-12-02`: Por culpa de los numeros flotantes, la equivalencia de un compass en fps, tiende decimales, y el contador no esta a decimales, por lo que detención de grabación no es perfecta. Es decir, por los contadores al ser ser enteros, y los limites del contador ser flotantes, hay estos problemas.
- `2025-12-07`: El microphone recorder no acepta `pathlib` como ruta, solo str. Hay que solucionar eso.
- `2025-12-09`: Solucione eso, ahora si microphone si acepta pathlib. Implemente un fotograma mas en la app `self.recorder_count_fps >= self.recorder_limit_in_fps+1`. Parece funcionar bastante bien en 20 fps y 60 fps, en si el `limit_in_fps` es preciso, lo que pasa es que el loop en kivy parece no respetar al 100% los fps, e incluso respetando al 100%, la grabación de microfono no termina en el 100% en frame indicado. Incluso indicandole al `MicrophoneRecorder`, el limite en segundos, aun así no para al momento. Tambien agregre `FPSLoopstation`, este se puede usar en cualquier loop que jale con fps fijos. `FPSLoopstation` necesita hacerse mas modular, seria: `FPSMetronome`, y capaz un `SoundPlayer`. El `FPSLoopstation` usaria esto, y tendria para almacenar y administrar tracks.
- `2025-12-09`: El `record()` se envia en el frame cero, pero dado que solo se da la orden de grabar, aun no se graba, por lo que dar un frame mas al `self.recorder_count_fps >= self.recorder_limit_in_fps+1` si tiene sentido, y hasta es necesario.
- `2025-12-09`: Al terminar la grabación en compass_in_fps+1, pos no se inicia de una, sino hasta empezar el otro compas.

- `2025-12-09`: Ahora la grabación si entra al inicio del compass lo logre con:
```python
frame_before_the_bar = (
    (self.current_beat >= self.beats_per_bar) and
    (self.count_fps_of_beat >= self.beat_in_fps-1)
)
```
Cuando se este en el ultimo beat, y el contador de beat en fps este en el penultimo frame equivalente a un beat en fps, se empezara a grabar. El mas uno se queda, pero ya no es problema, porque ya si se inicia para el frame exacto final del compas.

- `2025-12-09`: Al grabar con obs el microfono y mi app loopstation kivy, se guarda valiendo mas que un coompas. (solo si tiene el +1). Pero en mi App CLI mientras grabo con OBS el microfono, y que tiene el mismo Loop, y mismos FPS, no pasa eso, el loop es estable, y la grabación se guarda con los frames indicados (incluso con el +1, de hecho el +1 es necesario para que tenga una amplitud aceptable). Otra vez, es culpa de kivy. Tengo la teoria de que este problema no deberia pasar en Android.
