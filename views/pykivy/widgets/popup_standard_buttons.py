from .popup_box_layout import PopupBoxLayout
from kivy.uix.button import Button

class PopupStandardButtons( PopupBoxLayout ):
    def __init__(self, *args, second_container, text_ok="ok", **kwargs):
        super().__init__( *args, orientation="vertical", **kwargs)

        self.second_container = second_container
        self.second_container.size_hint = (1, 0.9)
        self.content.add_widget( self.second_container )

        self.button_ok = Button( text=text_ok, size_hint=(1, 0.1) )
        self.button_ok.bind( on_press=self.dismiss )
        self.content.add_widget( self.button_ok )
