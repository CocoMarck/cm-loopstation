from .popup_standard_buttons import PopupStandardButtons
from kivy.uix.gridlayout import GridLayout

class PopupGridLayout( PopupStandardButtons ):
    def __init__(self, *args, cols:int, rows:int, row_default_height:int, **kwargs):

        super().__init__(
            *args,
            second_container=GridLayout(
                cols=cols, rows=rows, row_force_default=True, row_default_height=row_default_height,
                size_hint=(1, 0.9)
            ),
            **kwargs
        )
