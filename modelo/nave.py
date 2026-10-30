import math

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
        self.objetivo_y = self.y

    # ---------- control con teclado ----------
    def mover_direccion(self, dx, dy, delta_tiempo):
        """Mueve la nave directamente usando entradas de teclado (flechas / WASD).
        
        dx: Dirección horizontal (-1 izquierda, 1 derecha, 0 quieto)
        dy: Dirección vertical (-1 arriba, 1 abajo, 0 quieto)
        delta_tiempo: Tiempo entre fotogramas para mantener velocidad constante.
        """

        if dx and dy:       # en diagonal no va más rápido -> cos(45°) ≈ 0.7071
            dx *= 0.7071
            dy *= 0.7071
        
        self.x += dx * VELOCIDAD_TECLADO * delta_tiempo
        self.y += dy * VELOCIDAD_TECLADO * delta_tiempo
        self.x = min(max(self.x, 0), ANCHO_VIRTUAL - self.ancho)
        self.y = min(max(self.y, 0), ALTO_VIRTUAL - self.alto)
        self.objetivo_x = self.x            # así no vuelve atrás si luego se usa la mano
        self.objetivo_y = self.y

    # ---------- control con la mano ----------
    def mover_hacia(self, centro_x, centro_y):
        """Indica hacia dónde quiere ir la nave (centro). No se mueve aún."""

        # Centra la nave respecto al punto de detección recibido
        objetivo_x = centro_x - self.ancho / 2
        objetivo_y = centro_y - self.alto / 2
        # Actualizamos la posición real directamente (con límites de pantalla)
        self.objetivo_x = min(max(objetivo_x, 0), ANCHO_VIRTUAL - self.ancho)
        self.objetivo_y = min(max(objetivo_y, 0), ALTO_VIRTUAL - self.alto)

    def actualizar(self, delta_tiempo):
        """Se acerca al objetivo sin superar su velocidad máxima."""
        diferencia_x = self.objetivo_x - self.x
        diferencia_y = self.objetivo_y - self.y
        distancia = math.hypot(diferencia_x, diferencia_y)
        paso_maximo = VELOCIDAD_NAVE * delta_tiempo
        if distancia <= paso_maximo:
            self.x = self.objetivo_x
            self.y = self.objetivo_y
        elif distancia:
            factor = paso_maximo / distancia
            self.x += diferencia_x * factor
            self.y += diferencia_y * factor
