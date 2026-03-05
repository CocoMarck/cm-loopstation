from .popup_box_layout import PopupBoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

class PopupInformation( PopupBoxLayout ):
    def __init__(self, *args, text_information, text_ok="ok", **kwargs):
        super().__init__( *args, orientation="vertical", **kwargs)

        self.label_information = Label(
            text=text_information,
            #size_hint_y=None,
            markup=True,
            halign="left",
            valign="top"
        )
        self.label_information.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None))
        )
        self.scroll_view = ScrollView( size_hint=(1, 0.9) )
        self.scroll_view.add_widget(self.label_information)
        self.content.add_widget( self.scroll_view )

        self.button_ok = Button( text=text_ok, size_hint=(1, 0.1) )
        self.button_ok.bind( on_press=self.dismiss )
        self.content.add_widget( self.button_ok )
