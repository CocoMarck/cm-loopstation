from kivy.uix.image import Image

class StickyImage():
    def __init__(self, image, widget, multiplier_padding_xy=[0.2,0.2]):
        self.multiplier_padding_xy = multiplier_padding_xy
        self.image = image
        self.image.size_hint = (None, None)
        self.widget = widget
        self.widget.add_widget(image)
        self.widget.bind(size=self.adjust_image, pos=self.adjust_image)
        self.adjust_image(self.widget)

    def adjust_image(self, instance, *args):
        # Buscamos el lado más corto del botón para que el icono quepa
        # Le restamos un pequeño margen (ej. dp(10)) para que no toque los bordes
        shorter_side = min(instance.width, instance.height)
        square_size = (
            shorter_side - shorter_side*self.multiplier_padding_xy[0],
            shorter_side - shorter_side*self.multiplier_padding_xy[1]
        )
        self.image.size = square_size
        center_pos = (
            instance.pos[0] + instance.size[0]*0.5 -square_size[0]*0.5,
            instance.pos[1] + instance.size[1]*0.5 -square_size[1]*0.5
        )
        self.image.pos = center_pos
