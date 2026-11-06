import cv2

from config import ANCHO_VIRTUAL, ALTO_VIRTUAL


def escalar_punto(punto, ancho_ventana, alto_ventana):
    """Pasa un punto (x, y) de unidades virtuales a píxeles de la ventana."""
    x, y = punto
    return (int(x * ancho_ventana / ANCHO_VIRTUAL),
            int(y * alto_ventana / ALTO_VIRTUAL))


def escalar_rect(x, y, ancho, alto, ancho_ventana, alto_ventana):
    """Rectángulo virtual -> (esquina superior izquierda, esquina inferior derecha) en píxeles."""
    return (escalar_punto((x, y), ancho_ventana, alto_ventana),
            escalar_punto((x + ancho, y + alto), ancho_ventana, alto_ventana))


def escalar_longitud(valor, alto_ventana):
    """Escala un tamaño suelto (radio, grosor, tamaño de letra)."""
    return valor * alto_ventana / ALTO_VIRTUAL


class Ventana:
    """Envuelve la ventana de OpenCV: tamaño, proporción 16:9, mostrar y detectar cierre."""

    def __init__(self, nombre, ancho, alto):
        '''Crea y configura una ventana redimensionable de OpenCV.'''
        self.nombre = nombre
        self.ancho = ancho
        self.alto = alto
        cv2.namedWindow(nombre, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(nombre, ancho, alto)

    def actualizar_dimensiones(self):
        """Lee el tamaño real de la ventana y corrige la proporción.
        Devuelve False si la ventana está minimizada (no hay nada que dibujar)."""
        _, _, ancho, alto = cv2.getWindowImageRect(self.nombre)
        if ancho <= 0 or alto <= 0:
            return False

        alto_correcto = int(ancho * ALTO_VIRTUAL / ANCHO_VIRTUAL)
        if abs(alto - alto_correcto) > 2:               # 2 píxeles de tolerancia
            cv2.resizeWindow(self.nombre, ancho, alto_correcto)

        self.ancho, self.alto = ancho, alto
        return True

    def mostrar(self, imagen):
        '''Muestra la imagen recibida en la ventana.'''
        cv2.imshow(self.nombre, imagen)

    def cerrada(self):
        '''Indica si el usuario ha cerrado la ventana.'''
        return cv2.getWindowProperty(self.nombre, cv2.WND_PROP_VISIBLE) < 1

    def pixel_a_virtual(self, x_pixel, y_pixel):
        """Convierte una posición de la ventana (píxeles) a unidades virtuales."""
        return (x_pixel * ANCHO_VIRTUAL / self.ancho,
                y_pixel * ALTO_VIRTUAL / self.alto)

    def poner_callback_raton(self, funcion):
        '''Registra la función que recibirá los eventos del ratón en esta ventana.'''
        cv2.setMouseCallback(self.nombre, funcion)

    def cerrar(self):
        '''Cierra las ventanas de OpenCV abiertas por la aplicación.'''
        cv2.destroyAllWindows()
