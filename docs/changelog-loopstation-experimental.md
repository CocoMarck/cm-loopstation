# Features

## `0.3.9-alpha`
- Nuevo margen, basado en px/resolución.
- Nuevas opciónes de menu: `settings` y `help`.
- Opción de settings: `metronomo vista numerica`

## `0.4.0-alpha`
- Archivo de configuracion de Engine y GUI.
- Forzar limite de grabación, en `FPSSoundLoopstationRecorderController`.
- Nuevos temas para GUI.
- GUI con opción a random theme. Básicametne tendra de fondo un color `x`, y de color de botones el color inverso a `x`, y de color de texto de boton `x`, y de color labels la inversa a `x`.

# `0.5.0-alpha`
- Refactor jalando a `dt`.

# `0.5.1-alpha`
**Correcciones imporantes, aunque sa solo un path.**
- Ahora el dt_metronome tiene `near_end_of_bar` signal. Que indica que estas en el `95%` de la barra.

- El `dt` jala bien, pero necesita minimo `40` fps. Trabajar con low fps, seria un dolor de cabeza.
    En PyKivy sin limite de fps, en android y pc mete un vsync, limite por hz de screen.
    En otros loops mas precizos y con fps fijos respetados, 100 fps basta.

- Ahora el `DTSoundLoopstation`. Paso a determinar el stop a `round( get_bars_to_seconds( track['bars']) ) -dt`. Le meti un `-dt`, para asegurar que se rompa el bucle. Pasa mas en kivy loop.
    Ya lo cambie y pase a hace esto:
    ```python
    # Obtener valor duración aceptable para parar track
    math_ceil_of_bar_length_minus_one_step = self.metronome.get_bars_to_seconds(
        math.ceil(track['bars'])
    ) -dt
    # Determinar cuando parar
    real_count_dt = track['count_dt']
    stopping = real_count_dt >= math_ceil_of_bar_length_minus_one_step
    ```
    Asi siempre cuando el bar sea `0.1` pasa a `1`. O `3.2`, pos a `4`. Es la lib `math` del python.

- Crear opcion en ajustes de fps: `0, 40, 60, y 100`.
    Listo. Jala bien.
