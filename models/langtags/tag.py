from .control_fields import ControlFields

class Tag(ControlFields):
    def __init__(self):
        super().__init__()

        self.tag_id: int = None
        self.name: str = None
