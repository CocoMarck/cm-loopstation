'''
Gemini crazy code
'''
from jnius import autoclass

# Cargamos las clases de Android una sola vez a nivel módulo
SoundPoolBuilder = autoclass("android.media.SoundPool$Builder")
AudioAttributesBuilder = autoclass("android.media.AudioAttributes$Builder")
AudioAttributes = autoclass("android.media.AudioAttributes")

# Información
from core.android_sound_info import get_audio_length

class AndroidSoundPoolAlone:
    """
    Wrapper que simula ser un objeto de sonido único (Duck Typing para tu ISoundManager)
    ideal para el BeatController (sonidos cortos/baterías sin latencia).
    """
    # Compartimos un único SoundPool estático entre todas las instancias para no saturar Android
    _pool = None

    @classmethod
    def _get_pool(cls):
        if cls._pool is None:
            attrs = AudioAttributesBuilder() \
                .setUsage(AudioAttributes.USAGE_GAME) \
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION) \
                .build()
            cls._pool = SoundPoolBuilder() \
                .setMaxStreams(10) \
                .setAudioAttributes(attrs) \
                .build()
        return cls._pool

    def __init__(self, source):
        self.source = str(source)
        self.pool = self._get_pool()
        self.volume = 1.0
        self._stream_id = 0  # Para poder pararlo individualmente si se ocupa

        # OJO: SoundPool maneja la carga asíncrona por defecto en Android.
        # Para archivos locales en el almacenamiento o assets, se pasa la ruta.
        self.sound_id = self.pool.load(self.source, 1)

    def is_valid(self) -> bool:
        return self.sound_id > 0

    def play(self) -> bool:
        try:
            # play(soundID, leftVolume, rightVolume, priority, loop, rate)
            # Guardamos el stream_id por si queremos darle stop() después
            self._stream_id = self.pool.play(self.sound_id, self.volume, self.volume, 1, 0, 1.0)
            return self._stream_id != 0
        except Exception as e:
            print("SoundPool play error:", e)
            return False

    def stop(self) -> bool:
        if self._stream_id != 0:
            try:
                self.pool.stop(self._stream_id)
                self._stream_id = 0
                return True
            except Exception as e:
                print(e)
        return False

    def set_volume(self, volume):
        self.volume = volume
        if self._stream_id != 0:
            try:
                self.pool.setVolume(self._stream_id, volume, volume)
                return True
            except Exception as e:
                print(e)
        return False

    def is_playing(self) -> bool:
        # SoundPool no tiene un método directo "isPlaying".
        # Si se requiere trackear, se puede simular con el estado de self._stream_id
        return self._stream_id != 0

    def get_length(self) -> float:
        # SoundPool no trackea duraciones largas, usualmente es para samples cortos (< 5-10s)
        try:
            return get_audio_length(self.source)
        except Exception as e:
            print(e)
            return 0.0

    def release(self):
        try:
            self.pool.unload(self.sound_id)
        except Exception as e:
            print(e)
        self.sound_id = 0
