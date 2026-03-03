from kivy.uix.image import Image

class StickyImage():
    def __init__(self, image, widget):
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
        self.image.size = (shorter_side, shorter_side)
        self.image.center = instance.center
