import cv2
import numpy as np

from config import (ANCHO_VIRTUAL, ALTO_VIRTUAL, POSICION_Y_TITULO, COLOR_FONDO_MENU,
                    COLOR_BOTON, COLOR_BOTON_SELECCIONADO, COLOR_TEXTO,
                    COLOR_TEXTO_SELECCIONADO, COLOR_TITULO,
                    COLOR_CURSOR_NORMAL,COLOR_CURSOR_PRESIONADO)
from vista.ventana import escalar_punto


class VistaMenu:
    """Dibuja un MenuModelo. No cambia ningún dato."""

    def dibujar(self, menu, ancho_ventana, alto_ventana, puntero=None,
                is_mano_abierta=True):
        canvas = np.full((alto_ventana, ancho_ventana, 3), COLOR_FONDO_MENU, dtype=np.uint8)

        self._texto_centrado(canvas, menu.titulo, (ANCHO_VIRTUAL / 2, POSICION_Y_TITULO),
                             3.5, 8, COLOR_TITULO, ancho_ventana, alto_ventana)

        for n, (x, y, ancho, alto) in enumerate(menu.botones):
            seleccionado = (n == menu.opcion)
            color_boton = COLOR_BOTON_SELECCIONADO if seleccionado else COLOR_BOTON
            color_texto = COLOR_TEXTO_SELECCIONADO if seleccionado else COLOR_TEXTO

            esquina_1 = escalar_punto((x, y), ancho_ventana, alto_ventana)
            esquina_2 = escalar_punto((x + ancho, y + alto), ancho_ventana, alto_ventana)
            cv2.rectangle(canvas, esquina_1, esquina_2, color_boton, -1)

            self._texto_centrado(canvas, menu.opciones[n], (x + ancho / 2, y + alto / 2),
                                 1.6, 3, color_texto, ancho_ventana, alto_ventana)
        if puntero is not None:
            self._dibujar_cursor_circulo(canvas, puntero, ancho_ventana, alto_ventana, is_mano_abierta)
        return canvas

    @staticmethod
    def _dibujar_cursor_circulo(canvas, cursor_pos, ancho_ventana, alto_ventana,
                         is_mano_abierta=True):
        centro = escalar_punto(cursor_pos, ancho_ventana, alto_ventana)
        radio = max(6, round(12 * alto_ventana / ALTO_VIRTUAL))
        color = COLOR_CURSOR_NORMAL if is_mano_abierta else COLOR_CURSOR_PRESIONADO
        cv2.circle(canvas, centro, radio, color, -1)

    @staticmethod
    def _texto_centrado(canvas, texto, centro_virtual, tamano_virtual, grosor_virtual,
                        color, ancho_ventana, alto_ventana):
        """Texto centrado en un punto virtual; tamaño y grosor se escalan con la ventana."""
        escala = alto_ventana / ALTO_VIRTUAL
        tamano_letra = tamano_virtual * escala
        grosor = max(1, round(grosor_virtual * escala))

        (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX,
                                                       tamano_letra, grosor)
        centro_x, centro_y = escalar_punto(centro_virtual, ancho_ventana, alto_ventana)
        esquina = (centro_x - ancho_texto // 2, centro_y + alto_texto // 2)
        cv2.putText(canvas, texto, esquina, cv2.FONT_HERSHEY_SIMPLEX,
                    tamano_letra, color, grosor)
