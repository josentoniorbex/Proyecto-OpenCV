import math
import random

from config import (ALTO_ENEMIGO, ANCHO_ENEMIGO, ALTO_VIRTUAL, ANCHO_VIRTUAL,
                    DIRECTORIO_ASSETS, VELOCIDAD_ENEMIGO)
from modelo.entidad import EntidadConImagen

IMAGENES_ENEMIGO = (
    "enemigo1-amarillo.png",
    "enemigo1-azul.png",
    "enemigo1-azulclaro.png",
    "enemigo1-gris.png",
    "enemigo1-naranja.png",
    "enemigo1-rojo.png",
)


class Enemigo(EntidadConImagen):
    """Enemigo que persigue a la nave y reaparece por encima de la pantalla."""

    def __init__(self, indice=0):
        ruta_imagen = str(
            DIRECTORIO_ASSETS / "enemigos" / random.choice(IMAGENES_ENEMIGO)
        )
        super().__init__(0, 0, ANCHO_ENEMIGO, ALTO_ENEMIGO, (0, 0, 0), ruta_imagen)
        self.reaparecer(indice)

    def reaparecer(self, indice=0):
        self.x = random.randint(0, ANCHO_VIRTUAL - self.ancho)
        self.y = -self.alto * (indice + 1)

    def actualizar(self, nave, delta_tiempo):
        diferencia_x = nave.x + nave.ancho / 2 - (self.x + self.ancho / 2)

        umbral = 1.0

        if abs(diferencia_x) > umbral:
            # Movimiento diagonal a 45° persiguiendo en X
            direccion_x = 1 if diferencia_x > 0 else -1

            paso_x = VELOCIDAD_ENEMIGO * 0.7071 * delta_tiempo
            paso_y = VELOCIDAD_ENEMIGO * 0.7071 * delta_tiempo

            self.x += direccion_x * paso_x
            self.y += paso_y  # Cambiado a += para avanzar hacia abajo
        else:
            # Movimiento recto hacia abajo
            paso_y = VELOCIDAD_ENEMIGO * delta_tiempo
            self.y += paso_y  # Cambiado a +=

        if self.y > ALTO_VIRTUAL:
            self.reaparecer()