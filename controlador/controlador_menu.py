import cv2

from config import (ANCHO_VIRTUAL, ALTO_VIRTUAL, TECLA_ENTER, TECLA_ESPACIO,
                    TECLA_ESC, ESC_PULSADO)


class ControladorMenu:
    """Maneja un menú (principal o de pausa): teclas W/S/ENTER/ESPACIO/ESC y ratón.
    Cuando el jugador elige algo, deja la acción guardada para que la lea la App."""

    def __init__(self, modelo, vista, detector_de_mano=None):
        self.modelo = modelo
        self.vista = vista
        self.detector_de_mano = detector_de_mano
        self._accion = None
        self._puntero_mano = None
        self._mano_abierta_previa = None

    def reiniciar(self):
        self.modelo.reiniciar()
        self._accion = None
        self._mano_abierta_previa = None

    def tecla(self, tecla):
        if tecla in (ord('w'), ord('W')):
            self.modelo.subir()
        elif tecla in (ord('s'), ord('S')):
            self.modelo.bajar()
        elif tecla in (TECLA_ENTER, TECLA_ESPACIO):
            self._accion = self.modelo.opcion_actual
        elif tecla == TECLA_ESC:
            self._accion = ESC_PULSADO

    def raton(self, evento, x_virtual, y_virtual):
        """Pasar por encima = seleccionar, clic = elegir."""
        boton = self._seleccionar_boton(x_virtual, y_virtual)
        if boton is not None and evento == cv2.EVENT_LBUTTONDOWN:
            self._accion = self.modelo.opciones[boton]

    def actualizar(self, ancho_ventana, alto_ventana):
        """Devuelve la imagen del menú."""
        self._actualizar_control_mano()
        return self.vista.dibujar(
            self.modelo, ancho_ventana, alto_ventana, self._puntero_mano
        )

    def _actualizar_control_mano(self):
        # si hay detector de mano y además no hay errores al abrir la camara
        if self.detector_de_mano is not None and not self.detector_de_mano.error:
            posicion, mano_abierta = self.detector_de_mano.obtener()
            if posicion is None:
                self._puntero_mano = None
                self._mano_abierta_previa = None
            else:
                x = min(max(posicion[0], 0.0), 1.0) * ANCHO_VIRTUAL
                y = min(max(posicion[1], 0.0), 1.0) * ALTO_VIRTUAL
                self._puntero_mano = (x, y)
                boton = self._seleccionar_boton(x, y)

                # Si antes tenía la mano cerrada y ahora la tengo abierta y además estoy en un boton
                if (self._mano_abierta_previa is True and not mano_abierta and boton is not None):
                    self._accion = self.modelo.opciones[boton] # seleccionamos la opción
                self._mano_abierta_previa = mano_abierta
        else:
            self._puntero_mano = None
            self._mano_abierta_previa = None

    def _seleccionar_boton(self, x, y):
        for numero, (boton_x, boton_y, ancho, alto) in enumerate(self.modelo.botones):
            if boton_x <= x <= boton_x + ancho and boton_y <= y <= boton_y + alto:
                self.modelo.opcion = numero
                return numero
        return None

    def consumir_accion(self):
        accion, self._accion = self._accion, None
        return accion
