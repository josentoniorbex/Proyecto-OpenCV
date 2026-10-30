import cv2

from config import TECLA_ENTER, TECLA_ESPACIO, TECLA_ESC, ESC_PULSADO


class ControladorMenu:
    """Maneja un menú (principal o de pausa): teclas W/S/ENTER/ESPACIO/ESC y ratón.
    Cuando el jugador elige algo, deja la acción guardada para que la lea la App."""

    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self._accion = None

    def reiniciar(self):
        self.modelo.reiniciar()
        self._accion = None

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
        for n, (x, y, ancho, alto) in enumerate(self.modelo.botones):
            if x <= x_virtual <= x + ancho and y <= y_virtual <= y + alto:
                self.modelo.opcion = n
                if evento == cv2.EVENT_LBUTTONDOWN:
                    self._accion = self.modelo.opcion_actual

    def actualizar(self, ancho_ventana, alto_ventana):
        """Devuelve la imagen del menú."""
        return self.vista.dibujar(self.modelo, ancho_ventana, alto_ventana)

    def consumir_accion(self):
        accion, self._accion = self._accion, None
        return accion
