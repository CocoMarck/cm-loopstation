#
# Drivared from
# https://github.com/Android-for-Python/record_audio_example/blob/main/android_media_recorder.py
#

from kivy.logger import Logger
import threading
from jnius import autoclass

# Poner esto para permisos de micro con kivy main: `android.permissions = RECORD_AUDIO`

MediaRecorder = autoclass('android.media.MediaRecorder')
AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

class AndroidMicrophoneRecorder():

    def __init__(
        self, output_filename:str="record-audio.3gp", record_seconds=0
    ):
        '''
        Creo que el MediaRecorder igual ya crea un hilo.
        Necesita guardar en 3gp, ya que este es el que maneja android. Tento codificador como decoficador.
        '''
        # Grabación
        self.output_filename = output_filename
        self.record_seconds = record_seconds

        # Grabador
        self._recorder = None

        # Estados
        self._states = ["stop", "record"]
        self.state = self._states[0]

    def record(self):
        if self.state == self._states[1]:
            Logger.warning("Ya esta grabando")
            return

        try:
            self._recorder = MediaRecorder()
            self._recorder.setAudioSource(AudioSource.MIC)
            self._recorder.setOutputFormat(OutputFormat.THREE_GPP)
            self._recorder.setAudioEncoder(AudioEncoder.AMR_NB)
            self._recorder.setOutputFile( self.output_filename )
            self._recorder.prepare()
            self._recorder.start()
            self.state = self._states[1]
        except Exception as e:
            Logger.error(f"MediaRecorder: {e}")
            self._recorder.release()
            self._recorder = None

    def stop(self):
        if self.state == self._states[0]:
            Logger.warning("No está grabando")
            return

        try:
            self._recorder.stop()
        except Exception as e:
            Logger.warning("MediaRecorder: {e}")
        finally:
            self._recorder.release()
            self._recorder = None
            self.state = "stop"
