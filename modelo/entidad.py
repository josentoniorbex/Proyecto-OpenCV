class Entidad:
    """Cualquier objeto rectangular del juego. Todo en unidades virtuales."""

    def __init__(self, x, y, ancho, alto, color):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.color = color

    def estaColisionando(self, otra_entidad):
        '''Comprobar si hay colisión'''
        return (
        self.x < otra_entidad.x + otra_entidad.ancho
        and self.x + self.ancho > otra_entidad.x
        and self.y < otra_entidad.y + otra_entidad.alto
        and self.y + self.alto > otra_entidad.y
        )


class EntidadConImagen(Entidad):
    """Entidad rectangular que se representa usando una imagen."""

    def __init__(self, x, y, ancho, alto, color, ruta_imagen):
        super().__init__(x, y, ancho, alto, color)
        self.ruta_imagen = ruta_imagen