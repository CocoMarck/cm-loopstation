import pyaudio
import wave
import threading
import time
import os

class MicrophoneRecorder():
    def __init__(self, output_filename:str="record-audio.wav", record_seconds=0, channels=1, rate=44100):

        self.audio = pyaudio.PyAudio()
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self.RECORD_SECONDS = record_seconds
        self.WAVE_OUTPUT_FILENAME = output_filename

        self.stream = None
        self.frames = []

        # Control de estado
        self._is_recording = threading.Event()
        self.thread = None

        # Control
        self.__states = ["stop", "record"]
        self.state = self.__states[0]

        # degug
        self.verbose = True


    def debug(self, level:str, message:str):
        if self.verbose:
            print( f"{level.upper()}: {message.lower()}" )


    def __save(self):
        '''
        Guardar grabación
        '''
        if not self.frames:
            self.debug("warning", "No hay datos grabados para guardar")

        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes( b''.join(self.frames) )
        wf.close()

        self.debug("info", f"Archivo guardado `{self.WAVE_OUTPUT_FILENAME}`")


    def __cleanup(self):
        '''
        Cuando termina el stream, para el stream, y guarda el archivo.

        Establecer estado de grabación en stop
        '''
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.state = self.__states[0]

        self.__save()


    def _record_thread(self):
        '''
        Grabar
        '''
        # Inicializar stream
        self.audio = pyaudio.PyAudio() # Necesaria para grabar
        try:
            self.stream = self.audio.open(
             format=self.FORMAT, rate=self.RATE, input=True,
             channels=self.CHANNELS, frames_per_buffer=self.CHUNK
            )
        except Exception as e:
            self.debug("error", f"No se pudo abrir el stream de audio: {e}" )
            self._is_recording.clear()
            return

        self.debug("info", "Grabando en segundo plano...")
        self.frames = []

        # Limite y obtener tiempo de inicio de hilo
        limit = self.RECORD_SECONDS > 0
        start_time = time.time()

        # Bucle de grabación
        while self._is_recording.is_set():
            try:
                ## Leer datos del micrófono
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)

                if limit:
                    ### Limite | Determinar fin de grabación, por el inicio de hilo
                    current_time = time.time()
                    enlapsed_time = current_time -start_time

                    if enlapsed_time >= self.RECORD_SECONDS:
                        self.debug("info", f"Limite de tiempo {self.RECORD_SECONDS} alcanzado.")
                        self._is_recording.clear()

            except IOError as e:
                ## Evita que la grabación se detenga por un overFlow menor
                if e.errno == pyaudio.paInputOverFlowed:
                    debug("warning", "InputOverflowed - Ignorando el error.")
                    continue
                else:
                    debug("error", f"Error de lectura del stream: {e}")
                    break

        # Una vez que el bucle `while` termina (por tiempo o por stop externo)
        self.__cleanup()


    def record(self):
        '''
        Inicia la grabación de un nuevo hilo
        '''
        if self.thread is not None and self.thread.is_alive():
            self.debug("warning", "La grabación ya está en curso")
            return

        self._is_recording.set() # Activa el flag de grabación

        self.thread = threading.Thread(target=self._record_thread)
        self.thread.start()

        self.state = self.__states[1]

        self.debug("info", f"Grabación de `{self.WAVE_OUTPUT_FILENAME}` iniciada.")


    def stop(self):
        '''
        Finalizar todo adecuadamente (El sin limite)

        > Recursos de pyaudio terminados
        '''
        if not self._is_recording.is_set():
            self.debug("warning", "La grabación no está activa")
            return

        # Parar hilo
        self._is_recording.clear()
        self.thread.join()

        # Terminar instancia de PyAudio
        self.audio.terminate()

        self.state = self.__states[0]

        self.debug("info", "Grabación sin limite terminada")


# Test
#rcd = MicrophoneRecorder(name="./test_audio", record_seconds=5)
#rcd.record()
#time.sleep(5)
#rcd.stop()
