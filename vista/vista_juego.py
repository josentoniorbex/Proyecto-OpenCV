import cv2
import numpy as np

from config import COLOR_FONDO_JUEGO
from modelo.entidad import EntidadConImagen
from vista.ventana import escalar_punto, escalar_rect, escalar_longitud

DEBUG=False

class VistaJuego:
    """Dibuja el EstadoJuego con el tamaño real de la ventana. No cambia ningún dato."""

    def __init__(self):
        # diccionario clave-valor, esto es para cargar las imagenes en memoria
        self._imagenes = {}

    def dibujar(self, estado, ancho_ventana, alto_ventana, lineas_info=()):
        canvas = np.full((alto_ventana, ancho_ventana, 3), COLOR_FONDO_JUEGO, dtype=np.uint8)

        for estrella in estado.obtener_estrellas():
            centro = escalar_punto(
                (estrella.x, estrella.y), ancho_ventana, alto_ventana
            )
            radio_pantalla = max(
                1, round(escalar_longitud(estrella.grosor, alto_ventana))
            )
            cv2.circle(canvas, centro, radio_pantalla, (255, 255, 255), -1)

        for entidad in estado.entidades():
            if isinstance(entidad, EntidadConImagen):
                self._dibujar_imagen(canvas, entidad, ancho_ventana, alto_ventana)
            else:
                self._dibujar_rect(canvas, entidad, ancho_ventana, alto_ventana)

        if DEBUG:
            self.dibujar_debug(canvas, estado, ancho_ventana, alto_ventana)

        for numero, linea in enumerate(lineas_info):
            self._dibujar_texto(canvas, linea, (20, 40 + 40 * numero), 0.9, (0, 255, 0),
                                ancho_ventana, alto_ventana)
        return canvas

    @staticmethod
    def dibujar_debug(canvas, estado, ancho_ventana, alto_ventana):
        """Dibuja el contorno verde de los límites de todas las entidades."""
        for entidad in estado.entidades():
            esquina_1, esquina_2 = escalar_rect(
                entidad.x, entidad.y, entidad.ancho, entidad.alto,
                ancho_ventana, alto_ventana,
            )
            cv2.rectangle(canvas, esquina_1, esquina_2, (0, 255, 0), 2)

    def _dibujar_imagen(self, canvas, entidad, ancho_ventana, alto_ventana):
        esquina_1_entidad_pantalla_real, esquina_2_entidad_pantalla_real = escalar_rect(entidad.x, entidad.y, entidad.ancho, entidad.alto,
                                            ancho_ventana, alto_ventana)
        entidad_x1_pantalla, entidad_y1_pantalla = esquina_1_entidad_pantalla_real
        entidad_x2_pantalla, entidad_y2_pantalla = esquina_2_entidad_pantalla_real
        # pongo de minimo un pixel por si acaso xD
        # lo que hago es ver el ancho y alto entre los 2 puntos
        ancho_dibujo = max(1, entidad_x2_pantalla - entidad_x1_pantalla)
        alto_dibujo = max(1, entidad_y2_pantalla - entidad_y1_pantalla)

        # Cargo en memoria con la clave de la ruta, el tipo de pintado en cv2
        imagen = self._imagenes.get(entidad.ruta_imagen)
        if imagen is None:
            imagen = cv2.imread(entidad.ruta_imagen, cv2.IMREAD_UNCHANGED)
            if imagen is None:
                raise FileNotFoundError(f"No se pudo cargar la imagen: {entidad.ruta_imagen}")
            self._imagenes[entidad.ruta_imagen] = imagen

        # La interpolacion es la tecnica que utilizo para redimensionar la imagen
            #INTER_AREA: para encoger
            #INTER_LINEAR: para agrandar
        interpolacion = cv2.INTER_AREA if ancho_dibujo < imagen.shape[1] or alto_dibujo < imagen.shape[0] \
            else cv2.INTER_LINEAR
        # redimensiono
        imagen = cv2.resize(imagen, (ancho_dibujo, alto_dibujo), interpolation=interpolacion)
        # Límites de la zona visible dentro de la pantalla
        cuadro_dibujo_pantalla_x_inicio = max(0, entidad_x1_pantalla)
        cuadro_dibujo_pantalla_x_fin = min(canvas.shape[1], entidad_x2_pantalla)
        cuadro_dibujo_pantalla_y_inicio = max(0, entidad_y1_pantalla)
        cuadro_dibujo_pantalla_y_fin = min(canvas.shape[0], entidad_y2_pantalla)
        # si está furera de la pantalla no pinta nada, seguramente sea 0=0.
        if cuadro_dibujo_pantalla_x_inicio >= cuadro_dibujo_pantalla_x_fin or cuadro_dibujo_pantalla_y_inicio >= cuadro_dibujo_pantalla_y_fin:
            return

        # Calculamos el recorte interno de la imagen redimensionada
        corte_png_x_inicio = cuadro_dibujo_pantalla_x_inicio - entidad_x1_pantalla
        corte_png_x_fin = cuadro_dibujo_pantalla_x_fin - entidad_x1_pantalla
        corte_png_y_inicio = cuadro_dibujo_pantalla_y_inicio - entidad_y1_pantalla
        corte_png_y_fin = cuadro_dibujo_pantalla_y_fin - entidad_y1_pantalla

         # extraigo la imagen recortada de la imagen original
        png_recortado = imagen[
            corte_png_y_inicio:corte_png_y_fin, corte_png_x_inicio:corte_png_x_fin
        ]

        # extraigo la región exacta del canvas sobre la que vamos a pintar
        zona_canvas = canvas[cuadro_dibujo_pantalla_y_inicio:cuadro_dibujo_pantalla_y_fin, cuadro_dibujo_pantalla_x_inicio:cuadro_dibujo_pantalla_x_fin]


        # solo obntengo el canal 3 = Alfa (transparencia) en rango decimal [0.0 a 1.0]
            # recordatorio, png_recortado[eje_Y, eje_X, canal_color] = valor de max 255
        canal_alfa = png_recortado[:, :, 3:4] / 255.0

        # Canales 0, 1 y 2 = Colores BGR
           # recordatorio, png_recortado[eje_Y, eje_X, canal_color] = valor de max 255
        canales_bgr = png_recortado[:, :, :3]

        # Aplicamos la fórmula directa sobre los píxeles del canvas
        # Si el png, tiene canal alfa=1=100%
        # multiplica por 1 el color de png
        # Pero el fondo le quita 1-alfa, que es el restante de la imagen
        # es decir si alfa=1=100% el fondo (1-alfa)=(1-1)=0 se multiplica por el color
        # quedando 0
        # Es decir:
            # cuando la imagen viene alfa 1, pone la imagen cargada en el sitio.
            # Cuando pone alfa 0, pone el fondo canva.
        zona_canvas[:] = (
            canal_alfa * canales_bgr + (1.0 - canal_alfa) * zona_canvas
        ).astype(np.uint8)

    


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
