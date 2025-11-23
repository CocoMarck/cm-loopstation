# PyKivy Loopstation
Sera una aplicación para pc y para android. Hecha en PyKivy.

Su función sera grabar y reproducir bucles, basado en el tempo.

Por defecto el tempo sera $4 \over 4$, 120 bpm.

Sera visible el cambio de tiempo con puntituos representativos. Y se escuchara un sonidito cada que cambia de tiempo. El primer tiempo tendra un enfasis visual y sonoro.

Es un concepto perse sencillo, lo dificil sera grabar microfono y sincronizar audio.

# Sincronización
Aca se mencionara el fundamento sobre el cual, los loops esten sincronizados.

El metronomo simpre estara activado.

Cuando se dice "el compas" se refiere al compaz actual.

Al darle a grabar, no empezara la grabación, se esperara a que empieze un compas, y al darle a parar, no se parara de una, sino que parara al terminar el compas.

Al darle a reproducir una grabación, solo se reproducira al empezar un compas, y al darle a parar, solo se parara al terminar el compas.

# Volumen
- El metronomo tendra opciones de volumen.
- La reproducción tendra opciones de volumen.

# Reproductor de grabaciones
Tendra opciones de parar, iniciar, eliminar, y pos el volumen anteriormente mencionado.

# Lo que se tiene que aprender
- A cuantos milisegundos equivale un bpm: $1 bpm = 60000 ms$
- Como grabar con el microfono por defecto.
- Como reproducir audios desde un loop PyKivy.

# Conclusión
Primemro desarrollar el metronomo, tener claro cuando empiza el primer tempo y cuando termina. Esto determinaran los compases.