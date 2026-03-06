from .popup_standard_buttons import PopupStandardButtons
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

class PopupInformation( PopupStandardButtons ):
    def __init__(self, *args, text_information, **kwargs):
        super().__init__(
            *args,
            second_container=ScrollView( ),
            **kwargs
        )

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
        self.second_container.add_widget(self.label_information)
