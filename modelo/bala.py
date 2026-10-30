from config import (ANCHO_BALA, ALTO_BALA, COLOR_NAVE, DIRECTORIO_ASSETS,
                    VELOCIDAD_BALA)
from modelo.entidad import EntidadConImagen


class Bala(EntidadConImagen):
    """Proyectil que sube desde la nave y se representa con un sprite."""

    def __init__(self, centro_x, y):
        ruta_imagen = str(DIRECTORIO_ASSETS / "disparo01.png")
        super().__init__(centro_x - ANCHO_BALA / 2, y - ALTO_BALA,
                         ANCHO_BALA, ALTO_BALA, COLOR_NAVE, ruta_imagen)

    def actualizar(self, delta_tiempo):
        self.y -= VELOCIDAD_BALA * delta_tiempo
