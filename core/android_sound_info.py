from jnius import autoclass

MediaMetadataRetriever = autoclass("android.media.MediaMetadataRetriever")

def get_audio_length(path: str) -> float:
    retriever = MediaMetadataRetriever()
    retriever.setDataSource(path)
    duration = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)
    retriever.release()
    return float(duration) / 1000.0 if duration else 0.0
