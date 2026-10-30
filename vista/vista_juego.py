import cv2
import numpy as np

from config import COLOR_FONDO_JUEGO
from vista.ventana import escalar_punto, escalar_rect, escalar_longitud


class VistaJuego:
    """Dibuja el EstadoJuego con el tamaño real de la ventana. No cambia ningún dato."""

    def dibujar(self, estado, ancho_ventana, alto_ventana, lineas_info=()):
        canvas = np.full((alto_ventana, ancho_ventana, 3), COLOR_FONDO_JUEGO, dtype=np.uint8)

        for entidad in estado.entidades():
            self._dibujar_rect(canvas, entidad, ancho_ventana, alto_ventana)

        for numero, linea in enumerate(lineas_info):
            self._dibujar_texto(canvas, linea, (20, 40 + 40 * numero), 0.9, (0, 255, 0),
                                ancho_ventana, alto_ventana)
        return canvas

    @staticmethod
    def _dibujar_rect(canvas, entidad, ancho_ventana, alto_ventana):
        esquina_1, esquina_2 = escalar_rect(entidad.x, entidad.y, entidad.ancho, entidad.alto,
                                            ancho_ventana, alto_ventana)
        cv2.rectangle(canvas, esquina_1, esquina_2, entidad.color, -1)

    @staticmethod
    def _dibujar_texto(canvas, texto, posicion_virtual, tamano_virtual, color,
                       ancho_ventana, alto_ventana):
        posicion = escalar_punto(posicion_virtual, ancho_ventana, alto_ventana)
        tamano = escalar_longitud(tamano_virtual, alto_ventana)
        grosor = max(1, round(escalar_longitud(2, alto_ventana)))
        cv2.putText(canvas, texto, posicion, cv2.FONT_HERSHEY_SIMPLEX, tamano, color, grosor)
