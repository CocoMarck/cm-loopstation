from dataclasses import dataclass

@dataclass
class ConfigEngine:
    beats: int = None
    beats_limit: int = None
    bpm: int = None
    bpm_limit: int = None
    volume: float = None
    play_beat: bool = None
    fps: int = None

    limit_record: bool = None
    record_bars: int = None

    seconds: int = None
