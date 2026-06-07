from jnius import autoclass

MediaPlayer = autoclass("android.media.MediaPlayer")
# Cargamos la clase de metadatos de Android para corregir el bug de duración
MediaMetadataRetriever = autoclass("android.media.MediaMetadataRetriever")

class AndroidMediaPlayer:
    '''
    MediaPlayer nativo de Android. Deberia soportar url y rutas de archivo.
    '''
    def __init__(self, source):
        self._media_player = None
        self._source = str(source)

        try:
            self._media_player = MediaPlayer()

            self._media_player.setDataSource(self._source)
            self._media_player.prepare()

        except Exception as e:
            print("MediaPlayer init error:", e)
            if self._media_player:
                try:
                    self._media_player.release()
                except:
                    pass

            self._media_player = None

    def is_valid(self) -> bool:
        return self._media_player is not None

    def play(self) -> bool:
        if not self._media_player:
            return False

        try:
            self._media_player.start()
            return True

        except Exception as e:
            print("ERROR:", e)
            return False

    def stop(self) -> bool:
        if not self._media_player:
            return False

        try:
            self._media_player.pause()
            self._media_player.seekTo(0)
            return True

        except Exception as e:
            print("ERROR:", e)
            return False

    def is_playing(self) -> bool:
        if not self._media_player:
            return False
        try:
            return self._media_player.isPlaying()
        except Exception:
            return False

    def set_volume(self, volume):
        try:
            self._media_player.setVolume(volume, volume)
            return True
        except Exception as e:
            print("ERROR:", e)
            return False

    def get_length(self) -> float:
        if not self._media_player:
            return 0.0
        try:
            return self._get_precise_length_from_source(self)
            #return self._media_player.getDuration() / 1000.0
        except Exception:
            return 0.0

    def _get_precise_length_from_source(self) -> float:
        """Método privado para interrogar al hardware usando nuestro self._source"""
        retriever = MediaMetadataRetriever()
        try:
            retriever.setDataSource(self._source)
            # Código 9 es METADATA_KEY_DURATION en Android
            time_str = retriever.extractMetadata(9)
            if time_str:
                return float(time_str) / 1000.0
        except Exception as e:
            print("Error interno en Retriever:", e)
        finally:
            try:
                retriever.release()
            except:
                pass
        return 0.0

    def release(self):
        if not self._media_player:
            return False

        try:
            self._media_player.release()
        except Exception:
            pass

        self._media_player = None

        return True
    # Otros que no se usan aca. No testados. jejej
    def get_position(self):
        if not self._media_player:
            return 0.0

        try:
            return self._media_player.getCurrentPosition() / 1000.0
        except Exception:
            return 0.0

    def pause(self):
        if not self._media_player:
            return False

        try:
            self._media_player.pause()
            return True
        except Exception:
            return False

    def seek(self, seconds):
        if not self._media_player:
            return False

        try:
            self._media_player.seekTo(
                int(seconds * 1000)
            )
            return True
        except Exception:
            return False
