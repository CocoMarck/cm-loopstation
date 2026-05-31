from .control_fields import ControlFields

class Language(ControlFields):
    def __init__(self):
        super().__init__()

        self.language_id: int = None
        self.code: str = None
