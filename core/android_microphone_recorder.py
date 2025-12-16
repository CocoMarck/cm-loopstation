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
OutputFormat = autoclass('android.media.MediarRecorder$OutputFormat')
AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

class AndroidMicrophoneRecorder():

    def __init__(
        self, output_filename:str="record-audio.wav", record_seconds=0
    ):
        '''
        Creo que el MediaRecorder igual ya crea un hilo, así que esta app crea dos hilos, pero creo que no debe ser mucho problema jajaj.
        '''
        # Grabación
        self.WAVE_OUTPUT_FILENAME = output_filename
        self.record_seconds = record_seconds

        # Grabador
        self._recorder = MediaRecorder()
        self._recorder.setAudioSource(AudioSource.MIC)
        self._recorder.setOutputSource(OutputFormat.THREE_GPP)
        self._recorder.setAudioEncoder(AudioEncoder.AMR_NB)

        # Hilo
        self._is_recording = threading.Event()
        self._thread = threading.Thread(target=self._record_thread)

        # Estados
        self._states = ["stop", "record"]
        self.state = self._states[0]

    def _save(self):
        self._recorder.setOutputFile(self.WAVE_OUTPUT_FILENAME)

    def _cleanup(self):
        '''
        Cuando termina el stream, para el stream, y guarda el archivo.

        Establecer estado de grabación en stop
        '''
        self._recorder.release()

        self.state = self.__states[0]

        self._save()

    def _record_thread(self):
        # Bucle de grabación
        while self._is_recording.is_set():
            try:
                # Preparar grabador
                self._recorder.prepare()
            except Exception as e:
                Logger.warning( f'Android Media Recorder Perapre() failed\n{str(e)}' )
            else:
                # Si se pudo preparar
                self._recorder.start()

        # Una vez que el bucle `while` termina (por tiempo o por stop externo)
        self._cleanup()


    def record(self):
        self._is_recording.set()
        self._thread.start()

        # Estado
        self.state = self.__states[1]


    def stop(self):
        # Calmando hilo perro
        if not self._is_recording.is_set():
            self.Logger.Warning("La grabación no está activa")
            return

        self._is_recording.clear()
        self._thread.join()

        self._recorder.release()

        # Estado
        self.state = self.__states[0]

