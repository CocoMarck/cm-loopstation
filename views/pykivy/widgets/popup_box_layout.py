from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class PopupBoxLayout(Popup):
    def __init__(self, *args, orientation="vertical", **kwargs):
        box_layout = BoxLayout( orientation=orientation )

        super().__init__( *args, content=box_layout, **kwargs)
