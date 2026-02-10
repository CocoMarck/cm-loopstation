# GUI usar FPS Sound Loopstation Engine.
Pon el loop de FPS sound por separado, y la gui consume señales.

Usar microphone recorder, para determinar si se esta grabando o no. Y actualizar pistas.

El GUI no reacciona al tiempo, reacciona a cambios de estado.

Se podria hacer por tiempo, pero depende de que el loop del loopstation, sea el mismo que el de la GUI, y eso, no es estable.

# Problemas con update tracks `2026-02-09`
Tenia problemas con grabar sin limites, pero ya no hay, ya hize testing, y los problemas de antes, los intente forzar, y paso prueba. Si le daba stop no en last frame perfect de grabación de pista (siempre se graba con compases aceptables aunque des stop en un copas "chueco". Eso hacia que el `.record` fuera suficiente para update pistas limit bars, pero no para update pistas sin limite
