from config import (ANCHO_BALA, ALTO_BALA, COLOR_NAVE, DIRECTORIO_ASSETS,
                    VELOCIDAD_BALA)
from modelo.entidad import EntidadConImagen


class Bala(EntidadConImagen):
    """Proyectil que sube desde la nave y se representa con un sprite."""

    def __init__(self, centro_x, y):
        '''Crea un proyectil centrado en la posición indicada de la nave.'''
        ruta_imagen = str(DIRECTORIO_ASSETS / "disparo01.png")
        # Restamos la mitad del ancho para que la bala quede centrada bajo la nave.
        # Restamos la altura de la bala para colocarla justo encima de la nave.
        super().__init__(centro_x - ANCHO_BALA / 2, y - ALTO_BALA,
                         ANCHO_BALA, ALTO_BALA, COLOR_NAVE, ruta_imagen)

    def actualizar(self, delta_tiempo):
        '''Mueve el proyectil hacia arriba según el tiempo transcurrido.'''
        self.y -= VELOCIDAD_BALA * delta_tiempo
