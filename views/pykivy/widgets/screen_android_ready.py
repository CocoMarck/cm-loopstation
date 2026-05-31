from kivy.uix.screenmanager import Screen
from kivy.metrics import dp

class ScreenAndroidReady(Screen):
    def __init__(
        self, vertical_padding_offsets=[0,0,0,0], horizontal_padding_offsets=[0,0,0,0], **kwargs
    ):
        '''
        Simplemente posee de facilidades como padding, y deteccion de orientacion.

        Padding pa modo horiziontal o modo vertical. Cambiante.
        '''
        super().__init__(**kwargs)

        self._vertical_padding_offsets = vertical_padding_offsets
        self._horizontal_padding_offsets = horizontal_padding_offsets
        self._last_orientation = None
        self._last_size = [self.size[0], self.size[1]]

    # Orientacion
    def get_orientation(self):
        if self.height > self.width:
            return "vertical"
        return "horizontal"

    def get_last_orientation(self):
        return self._last_orientation

    # Construir padding
    def build_padding_offsets(self, orientation, using):
        if orientation == "vertical":
            number = self.height
            padding_offsets = self._vertical_padding_offsets
        else:
            number = self.width
            padding_offsets = self._horizontal_padding_offsets
        padding = []
        if using == "dpi":
            for x in padding_offsets:
                padding.append( dp(x) )
        elif using == "resolution":
            for x in padding_offsets:
                padding.append( number*x )
        return padding

    # Actualizar padding en layout
    def _update_layout_padding(self, layout, orientation, using):
        padding = self.build_padding_offsets( orientation, using )
        if len(padding) == 4:
            layout.padding = padding

    def update_layout_padding_using_dpi(self, layout, orientation):
        self._update_layout_padding( layout, orientation, "dpi")

    def update_layout_padding_using_resolution(self, layout, orientation):
        self._update_layout_padding( layout, orientation, "resolution")

    def set_layout_padding_using_dpi(self, layout, orientation):
        self.update_layout_padding_using_dpi( layout, self.get_orientation() )

    def set_layout_padding_using_resolution(self, layout):
        self.update_layout_padding_using_resolution( layout, self.get_orientation() )

    # Change size only if change orientation
    def change_padding_using_dpi(self, layout):
        current = self.get_orientation()
        if current != self._last_orientation or (self.last_size != self.size):
            self.update_layout_padding_using_dpi(layout, current)
            self._last_orientation = current
            self.last_size = self.size

    def change_padding_using_resolution(self, layout):
        current = self.get_orientation()
        if current != self._last_orientation or (self.last_size != [self.size[0], self.size[1]]):
            self.update_layout_padding_using_resolution(layout, current)
            self._last_orientation = current
            self.last_size = [self.size[0], self.size[1]]
