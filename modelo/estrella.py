from config import ALTO_VIRTUAL


class Estrella:
    """Estrella del fondo con radio y velocidad propios."""

    def __init__(self, x, y, grosor, velocidad):
        self.x = x
        self.y = y
        self.grosor = grosor
        self.velocidad = velocidad

    def actualizar(self, delta_tiempo):
        # Le saco el resto para que cuando salga de la pantalla vuelva a 0
        self.y = (self.y + self.velocidad * delta_tiempo) % ALTO_VIRTUAL