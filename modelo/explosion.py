from config import (ANCHO_ENEMIGO, ALTO_ENEMIGO, DIRECTORIO_ASSETS,
                    DURACION_EXPLOSION)
from modelo.entidad import EntidadConImagen


class Explosion(EntidadConImagen):
    """Efecto visual temporal que sustituye a un enemigo destruido."""

    def __init__(self, centro_x, centro_y):
        '''Crea una explosión centrada en el punto indicado con su duración inicial.'''
        ruta_imagen = str(DIRECTORIO_ASSETS / "explosion01.png")
        super().__init__(centro_x - ANCHO_ENEMIGO / 2,
                         centro_y - ALTO_ENEMIGO / 2,
                         ANCHO_ENEMIGO, ALTO_ENEMIGO, (0, 0, 0), ruta_imagen)
        self.tiempo_restante = DURACION_EXPLOSION

    def actualizar(self, delta_tiempo):
        '''Reduce el tiempo restante de visualización de la explosión.'''
        self.tiempo_restante -= delta_tiempo
