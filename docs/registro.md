# Registro
- `2025-11-20`: El atributo `tempo` de `LoopstationWindow` de preferencia que sea un entero. Igual jala con flotante, pero de manera por esto `self.count >= self.tempo`.
- `2025-11-25`: La grabación solo reproduce cuando se empieza a grabar desde el segundo tempo. Bastante raro. Aun no se porque. La verdad ni estoy seguro si es así como digo, pero checar la ver de esta fecha por si surgen problemas.
- `2025-11-25`: La solución de la reproducción correcta del bucle es terminar al primer frame del ultimo tempo del compas. Eso da tiempo a reproducir el bucle. Parece que es un problema de como se reproducen los bucles.
- `2025-11-25`: En Wayland KDE PLasma AMD RX 6400, Kivy no respeta los fps indicados, el update esta en los `fps` que se le da la gana. Ese rompe por completo la funcionalidad del loop.
