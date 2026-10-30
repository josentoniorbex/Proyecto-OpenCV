class Entidad:
    """Cualquier objeto rectangular del juego. Todo en unidades virtuales."""

    def __init__(self, x, y, ancho, alto, color):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.color = color
