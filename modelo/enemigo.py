import math
import random

from config import (ALTO_ENEMIGO, ANCHO_ENEMIGO, ALTO_VIRTUAL, ANCHO_VIRTUAL,
                    DIRECTORIO_ASSETS, VELOCIDAD_ENEMIGO, ANCHO_NAVE)
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
        self.gap_diferencia_lados = random.randint(0, ANCHO_NAVE)
        super().__init__(0, 0, ANCHO_ENEMIGO, ALTO_ENEMIGO, (0, 0, 0), ruta_imagen)
        self.reaparecer(indice)

    def reaparecer(self, indice=0):
        self.x = random.randint(0, ANCHO_VIRTUAL - self.ancho)
        self.y = -self.alto * (indice + 1)

    def getPosicionMovimiento(self, nave, delta_tiempo):
        objetivo_x = nave.x + self.gap_diferencia_lados + nave.ancho / 2
        objetivo_y = nave.y + nave.alto / 2
        diferencia_x = objetivo_x - (self.x + self.ancho / 2)
        diferencia_y = objetivo_y - (self.y + self.alto / 2)
        angulo = math.atan2(diferencia_y, diferencia_x)
        paso = VELOCIDAD_ENEMIGO * delta_tiempo

        paso_x = math.cos(angulo) * paso
        paso_y = paso
        return self.x + paso_x, self.y + paso_y

    def actualizar(self, nave, delta_tiempo, otros_enemigos=()):
        siguiente_x, siguiente_y = self.getPosicionMovimiento(nave, delta_tiempo)
        
        choca = any(
            siguiente_x < otro.x + otro.ancho
            and siguiente_x + self.ancho > otro.x
            and siguiente_y < otro.y + otro.alto
            and siguiente_y + self.alto > otro.y
            for otro in otros_enemigos
            if otro is not self
        )

        if not choca:
            self.x = siguiente_x
            
        self.y = siguiente_y

        if self.y > ALTO_VIRTUAL:
            self.reaparecer()
