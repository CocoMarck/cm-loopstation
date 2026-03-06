# Problemas con el Edge-to-Edge
Los celus android 15-16, forzan esto. El problema que generan, es que el programa se dibuja debajo del especio reservado para los botones de control, **navigation bar** `triangulo, circulo, cuadrado`, y **status bar** `hora tiempo`.

Si se detecta un celu que jala con esto, se tiene que hacer un padding.

**Aspecto ratio estandar de celus: `16:9`, `20:9`, `19:9`.**

# Padding, Multiplicadores de `width` y `height` funcionales.
- vertical_padding_offsets=[0,0.05, 0,0.08]
- horizontal_padding_offsets=[0,0.05, 0.08,0]
