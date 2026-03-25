from .control_fields import ControlFields

class Translation(ControlFields):
    def __init__(self):
        super().__init__()

        self.translation_id: int = None
        self.tag_id: int = None
        self.language_id: int = None
        self.value: str = None
