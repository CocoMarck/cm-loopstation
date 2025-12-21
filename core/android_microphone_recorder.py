from kivy.logger import Logger
import threading
import struct
import time
from jnius import autoclass

# Android classes
AudioRecord = autoclass('android.media.AudioRecord')
AudioFormat = autoclass('android.media.AudioFormat')
MediaRecorder = autoclass('android.media.MediaRecorder')
AudioSource = autoclass('android.media.MediaRecorder$AudioSource')

class AndroidMicrophoneRecorder:
    def __init__(
        self,
        output_filename: str = "record.wav",
        sample_rate: int = 44100,
        channels: int = 1,
        record_seconds: int = 0
    ):
        self.output_filename = output_filename
        self.sample_rate = sample_rate
        self.channels = channels
        self.record_seconds = record_seconds

        self._audio_record = None
        self._thread = None
        self._recording = False
        self._stop_event = threading.Event()

        self._states = ["stop", "record"]
        self.state = self._states[0]

    def _write_wav_header(self, f, data_size):
        byte_rate = self.sample_rate * self.channels * 2
        block_align = self.channels * 2

        f.seek(0)
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')

        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('<H', 1))  # PCM
        f.write(struct.pack('<H', self.channels))
        f.write(struct.pack('<I', self.sample_rate))
        f.write(struct.pack('<I', byte_rate))
        f.write(struct.pack('<H', block_align))
        f.write(struct.pack('<H', 16))  # bits

        f.write(b'data')
        f.write(struct.pack('<I', data_size))

    def _record_loop(self):
        buffer_size = AudioRecord.getMinBufferSize(
            self.sample_rate,
            AudioFormat.CHANNEL_IN_MONO if self.channels == 1 else AudioFormat.CHANNEL_IN_STEREO,
            AudioFormat.ENCODING_PCM_16BIT
        )

        self._audio_record = AudioRecord(
            AudioSource.MIC,
            self.sample_rate,
            AudioFormat.CHANNEL_IN_MONO if self.channels == 1 else AudioFormat.CHANNEL_IN_STEREO,
            AudioFormat.ENCODING_PCM_16BIT,
            buffer_size
        )

        FRAME_SIZE = self.channels * 2

        pcm_buffer = bytearray(buffer_size)

        with open(str(self.output_filename), "wb") as f:
            f.write(b'\x00' * 44)

            self._audio_record.startRecording()
            start_time = time.time()

            data_size = 0
            has_audio = False

            while True:
                read_frames = self._audio_record.read(pcm_buffer, 0, len(pcm_buffer))

                if read_frames > 0:
                    bytes_read = read_frames * FRAME_SIZE
                    f.write(pcm_buffer[:bytes_read])
                    data_size += bytes_read
                    has_audio = True

                if self._stop_event.is_set() and has_audio:
                    break

                if self.record_seconds > 0:
                    if time.time() - start_time >= self.record_seconds:
                        break


            Logger.info("AudioRecord: stopRecording")
            self._audio_record.stop()
            self._audio_record.release()
            self._audio_record = None

            self._write_wav_header(f, data_size)

        Logger.info(f"WAV guardado: {self.output_filename}")

        self.state = "stop"
        self._recording = False

    def record(self):
        self._stop_event.clear()
        if self.state == "record":
            Logger.warning("Ya está grabando")
            return

        Logger.info(f"Grabando WAV: {self.output_filename}")
        self._recording = True
        self.state = "record"

        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if self.state == "stop":
            return

        Logger.info("Deteniendo grabación")
        self._stop_event.set()

        if self._thread:
            self._thread.join()

        self.state = "stop"
