from config import (ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_NAVE, ALTO_NAVE, VELOCIDAD_NAVE,
                    VELOCIDAD_TECLADO, MARGEN_INFERIOR_NAVE, COLOR_NAVE)
from modelo.entidad import Entidad


class Nave(Entidad):
    """Datos y reglas de la nave. Todo en unidades virtuales. No dibuja nada."""

    def __init__(self):
        super().__init__(0, ALTO_VIRTUAL - ALTO_NAVE - MARGEN_INFERIOR_NAVE,
                         ANCHO_NAVE, ALTO_NAVE, COLOR_NAVE)
        self.reiniciar()

    def reiniciar(self):
        self.x = (ANCHO_VIRTUAL - self.ancho) / 2
        self.y = ALTO_VIRTUAL - self.alto - MARGEN_INFERIOR_NAVE
        self.objetivo_x = self.x

    # ---------- control con teclado ----------
    def mover_direccion(self, dx, dy, delta_tiempo):
        """dx, dy valen -1, 0 o 1. Mueve la nave directamente, sin salirse del campo."""
        if dx and dy:                       # en diagonal no va más rápido
            dx *= 0.7071
            dy *= 0.7071
        self.x += dx * VELOCIDAD_TECLADO * delta_tiempo
        self.y += dy * VELOCIDAD_TECLADO * delta_tiempo
        self.x = min(max(self.x, 0), ANCHO_VIRTUAL - self.ancho)
        self.y = min(max(self.y, 0), ALTO_VIRTUAL - self.alto)
        self.objetivo_x = self.x            # así no vuelve atrás si luego se usa la mano

    # ---------- control con la mano ----------
    def mover_hacia(self, centro_x):
        """Indica hacia dónde quiere ir la nave (x del centro). No se mueve aún."""
        objetivo = centro_x - self.ancho / 2
        self.objetivo_x = min(max(objetivo, 0), ANCHO_VIRTUAL - self.ancho)

    def actualizar(self, delta_tiempo):
        """Se acerca al objetivo sin superar su velocidad máxima."""
        diferencia = self.objetivo_x - self.x
        paso_maximo = VELOCIDAD_NAVE * delta_tiempo
        self.x += min(max(diferencia, -paso_maximo), paso_maximo)
