# Sonido igual a compas
Cuando un sonido en tiempo sea equivalente a un compas. Simplemente se determinara que cada inicio de compas se inicia, y el final se para. Sin importar nadota, siempre forzar.

Tambien si el tiempo del sonido es equivalente al compas en un $\times cualquier entero$.
Sonidos que duren exactamente 2, 3, 4 o más compases completos.
Sonidos cuya duración sea un múltiplo entero del compás.

No es lo mejor, pero deberia funcionar.

Como obtener tiempo en segundos:
```python
sound.length
```
> Eeto es para un `kivy.core.audio` `SoundLoader`

Hacer un diccionario que con tag/id de audio, y con veces de repetición.
```python
self.super_loop_sounds = {
    "audio": 4
}
```
> Recordar que ya existe el diccionario `self.sounds`, el cual tiene los `SondLoader`.

Obtener veces de reperición:
```python
compass = self.tempo*self.tempos
repeated_times = ( sound.length / (self.compass/FPS) )
```
> Recordar que `tempo` es lo que vale un tempo, y `tempos` la cantidad de tempos en el compas. El tempo es `segundos * FPS`, es por es la divición.

```python
def get_sound_repetition_limit(self, name):
    return self.sounds[name][2]*self.compass

def get_sound_reached_repetition_limit(self, name):
    limit = self.get_sound_repetition_limit(name)
    count = self.sound_count_repeated_times[name]
    return count >= limit
```

> El contador sumara de uno en uno, todo se basara en los FPS.

Se puede hacer con todos los sonidos. Se puede hacer con flotantes para mayor precisión.
