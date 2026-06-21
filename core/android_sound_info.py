from jnius import autoclass

MediaExtractor = autoclass('android.media.MediaExtractor')
MediaFormat = autoclass('android.media.MediaFormat')

def get_audio_length(path: str) -> float:
    extractor = MediaExtractor()
    try:
        extractor.setDataSource(path)
        fmt = extractor.getTrackFormat(0)
        duration_us = fmt.getLong(MediaFormat.KEY_DURATION)
        return duration_us / 1_000_000.0
    finally:
        extractor.release()
