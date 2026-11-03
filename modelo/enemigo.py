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
        '''Crea un enemigo con un sprite aleatorio y lo sitúa en su posición inicial.'''
        ruta_imagen = str(
            DIRECTORIO_ASSETS / "enemigos" / random.choice(IMAGENES_ENEMIGO)
        )
        self.gap_diferencia_lados = random.randint(0, ANCHO_NAVE)
        super().__init__(0, 0, ANCHO_ENEMIGO, ALTO_ENEMIGO, (0, 0, 0), ruta_imagen)
        self.reaparecer(indice)

    def reaparecer(self, indice=0):
        '''Coloca al enemigo en una posición horizontal aleatoria encima de la pantalla.'''
        self.x = random.randint(0, ANCHO_VIRTUAL - self.ancho)
        self.y = -self.alto * (indice + 1)

    def getPosicionMovimiento(self, nave, delta_tiempo):
        '''Calcula y devuelve la siguiente posición del enemigo al perseguir la nave.'''
        objetivo_x = nave.x + self.gap_diferencia_lados + nave.ancho / 2
        objetivo_y = nave.y + nave.alto / 2

        # Calcula la distancia horizontal y vertical desde el centro del enemigo hasta el objetivo.
        diferencia_x = objetivo_x - (self.x + self.ancho / 2)
        diferencia_y = objetivo_y - (self.y + self.alto / 2)
        # Obtiene el ángulo que apunta desde el enemigo hacia el objetivo.
        angulo = math.atan2(diferencia_y, diferencia_x)
        paso = VELOCIDAD_ENEMIGO * delta_tiempo

        # Usa el ángulo para calcular el desplazamiento horizontal hacia la nave.
        paso_x = math.cos(angulo) * paso

        # Hace que el enemigo siempre baje a la misma velocidad.
        paso_y = paso

        return self.x + paso_x, self.y + paso_y

    def actualizar(self, nave, delta_tiempo, otros_enemigos=()):
        '''Avanza al enemigo y evita que se mueva horizontalmente a través de otros.'''
        siguiente_x, siguiente_y = self.getPosicionMovimiento(nave, delta_tiempo)

        # Obtenemos los que chocan
        choca = any(
            siguiente_x < otro.x + otro.ancho
            and siguiente_x + self.ancho > otro.x
            and siguiente_y < otro.y + otro.alto
            and siguiente_y + self.alto > otro.y
            for otro in otros_enemigos
            if otro is not self
        )

        # Si no choca con otros enemigos se puede mover en a x
        if not choca:
            self.x = siguiente_x

        # Siempre movemos el la y   
        self.y = siguiente_y

        # Si se sale de la pantalla
        if self.y > ALTO_VIRTUAL:
            self.reaparecer()
