# SEGUIMIENTO DE LA MANO (antes camara.py)
# Corre en un hilo propio y solo guarda el último resultado. NO abre ventanas.
#
# Cómo funciona (cada paso es una función o proceso):
# 1) detectar_cara():             Busca la cara en la imagen para usarla como referencia de posición y color.
# 2) calcular__rango_color_cara():Calcula un rango de color dinámico analizando la luz en la nariz y mejillas.
# 3) calcular_mascara_piel():     Crea la máscara combinando un rango de color FIJO (para evitar fallos por sombras) y el rango de la cara.
# 4) tapar_cara_en_mascara():     Pinta un cuadrado negro sobre la cara y el cuello en la máscara para que no interfieran.
# 5) elegir_bloque_mano():        Agrupa los píxeles (connectedComponents) y selecciona el bloque de la mano.
# 6) separar_mano():              Corta el brazo analizando el ancho de la piel fila por fila para encontrar la muñeca.
# 7) calcular_solidez():          Detecta mano abierta/cerrada evaluando el área y los huecos profundos entre dedos.
# 8) meanShift y suavizado:       Sigue la caja de la mano y suaviza el movimiento para que no parpadee.

import threading
import traceback  # Lo necesito para el trycach

import numpy as np
import cv2

from config import INDICE_CAMARA

# ---------------- AJUSTES ----------------
FRAMES_MAX_SIN_CARA = 1
AREA_MINIMA_MANO = 3000
LARGO_MANO_POR_DEFECTO = 200
UMBRAL_SOLIDEZ = 0.6          # por debajo = abierta, por encima = cerrada
COLOR_CAJA_MANO = (0, 255, 255)
GROSOR_LINEA = 2
CRITERIOS_MEANSHIFT = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 15, 2)
KERNEL_PEQUENO = np.ones((5, 5), np.uint8)
KERNEL_GRANDE = np.ones((15, 15), np.uint8)

NOMBRE_CASCADA = "haarcascade_frontalface_default.xml"

# Rango de color de piel en YCrCb
PIEL_MIN = (0, 138, 80)
PIEL_MAX = (255, 175, 130)
KERNEL_ELIPSE = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

# =============================================================================
# CARA
# =============================================================================

def detectar_cara(detector, imagen):
    """Cara más grande como (x, y, ancho, alto), o None."""
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    caras = detector.detectMultiScale(imagen_gris, 1.2, 5, minSize=(80, 80))
    if len(caras) == 0:
        return None
    return max(caras, key=lambda cara: cara[2] * cara[3])


def tapar_cara_en_mascara(mascara_piel, cara):
    """Cuadrado negro sobre la cara y el cuello en la máscara de piel."""
    cara_x, cara_y, cara_ancho, cara_alto = cara

    multiplicador_altura=1.1
    cv2.rectangle(mascara_piel, (cara_x, cara_y),
                  (cara_x + cara_ancho, cara_y + int(cara_alto * multiplicador_altura)), 0, -1)


def pintar_cuadro_cara(imagen, cara):
    cara_x, cara_y, cara_ancho, cara_alto = cara
    cv2.rectangle(imagen, (cara_x, cara_y),
                  (cara_x + cara_ancho, cara_y + cara_alto), (255, 0, 0), GROSOR_LINEA)


# =============================================================================
# PIEL Y MANO
# =============================================================================

def calcular__rango_color_cara(imagen, cara, debug=True):
    """Rango (minimo, maximo) de color de piel, sacado de nariz y mejillas."""
    cara_x, cara_y, cara_ancho, cara_alto = cara
    
    # 1. Calculamos las coordenadas exactas de la zona (nariz y mejillas)
    x1 = cara_x + int(0.25 * cara_ancho)
    y1 = cara_y + int(0.3 * cara_alto)
    x2 = cara_x + int(0.75 * cara_ancho)
    y2 = cara_y + int(0.75 * cara_alto)
    
    # 2. MODO DEBUG: Dibuja un rectángulo verde fosforito donde está leyendo el color
    if debug:
        cv2.rectangle(imagen, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
    # 3. Recortamos la zona usando esas coordenadas
    zona = imagen[y1:y2, x1:x2]
    zona_ycrcb = cv2.cvtColor(zona, cv2.COLOR_BGR2YCrCb).reshape(-1, 3)

    tipico = np.median(zona_ycrcb, axis=0)           # la mediana ignora reflejos y sombras
    minimo = (0,   int(tipico[1]) - 8, int(tipico[2]) - 8)    # brillo (Y) libre, Cr y Cb ±8
    maximo = (255, int(tipico[1]) + 8, int(tipico[2]) + 8)
    
    return minimo, maximo


def calcular_mascara_piel(imagen, rango_cara=None):
    """Máscara de piel: rango fijo O rango sacado de la cara (blanco = piel)."""
    imagen_ycrcb = cv2.cvtColor(imagen, cv2.COLOR_BGR2YCrCb)

    # Todo lo que tenga color de piel dentro del rango fijo
    mascara = cv2.inRange(imagen_ycrcb, PIEL_MIN, PIEL_MAX)

    # Además, lo que entre en el rango de la cara (rescata la mano con luz rara)
    if rango_cara is not None:
        mascara_cara = cv2.inRange(imagen_ycrcb, rango_cara[0], rango_cara[1])
        mascara = cv2.bitwise_or(mascara, mascara_cara)

    # Quita puntos sueltos (abrir) y tapa agujeros pequeños (cerrar)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, KERNEL_ELIPSE, iterations=2)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, KERNEL_ELIPSE, iterations=2)

    # Suaviza los bordes y vuelve a dejar solo blanco/negro
    mascara = cv2.GaussianBlur(mascara, (5, 5), 0)
    _, mascara = cv2.threshold(mascara, 127, 255, cv2.THRESH_BINARY)

    # Pone en blanco el negro que está rodeado de blanco
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(mascara, contornos, -1, 255, -1)

    return mascara


def elegir_bloque_mano(mascara_piel, ventana_mano):
    """Bloque de piel que es la mano (True donde hay piel), o None."""

    # separa la máscara en manchas blancas independientes
    # (la mano, el cuello, un trozo de pared...) y numerarlas.
    # cv2.connectedComponents: agrupa los píxeles blancos que están pegados entre sí
    #   y a cada grupo le pone un número (1, 2, 3...). El fondo negro es 0.
    _, etiquetas = cv2.connectedComponents(mascara_piel)

    # Se intenta: saber cuánto mide cada mancha.
    areas = np.bincount(etiquetas.ravel())
    areas[0] = 0        # el fondo negro es lo más grande. Se anula para que no gane

    # mirar qué manchas hay donde estaba la mano en el frame anterior,
    # ampliando la zona 50 px por cada lado por si se ha movido.
    x, y, ancho, alto = ventana_mano
    zona = etiquetas[max(0, y - 50):y + alto + 50, max(0, x - 50):x + ancho + 50]
    etiquetas_en_zona = zona[zona > 0]      # quitamos el fondo

    # Hay que elegir cuál de las manchas es la mano.
    # Si hay piel en la zona anterior,  se elige la mancha que más aparece ahí, es decir "la que sigue donde estaba".
    # Si no hay nada, la mancha más grande de toda la imagen.
    if etiquetas_en_zona.size > 0:
        etiqueta_mano = np.bincount(etiquetas_en_zona).argmax()
    else:
        etiqueta_mano = areas.argmax()

    # Se intenta: descartar el ruido. Borro las manchas más pequeñas
    if areas[etiqueta_mano] <= AREA_MINIMA_MANO:
        return None

    # Se devuelve una imagen True/False con True solo en los píxeles de la mano.
    return etiquetas == etiqueta_mano


def separar_mano(bloque_piel, largo_mano=None):
    """Corta el brazo detectando el estrechamiento de la muñeca por filas."""
    mascara_mano = (bloque_piel * 255).astype(np.uint8)
    
    # 1. Calcular la "anchura" de piel en cada fila (sumando los píxeles True/1)
    anchura_por_fila = bloque_piel.sum(axis=1)
    
    if not anchura_por_fila.any():
        return mascara_mano
        
    filas_con_piel = np.nonzero(anchura_por_fila)[0]
    y_punta = filas_con_piel.min()
    
    # 2. Encontrar la palma: la fila más ancha desde la punta hacia abajo
    y_palma = y_punta + anchura_por_fila[y_punta:].argmax()
    anchura_maxima = anchura_por_fila[y_palma]
    
    # 3. Buscar la muñeca iterando desde la palma hacia abajo
    # Consideramos que es la muñeca cuando la anchura se reduce a un 90% de la palma
    umbral_muneca = anchura_maxima * 0.90
    limite_muneca = y_palma
    
    for y in range(y_palma, len(anchura_por_fila)):
        if anchura_por_fila[y] < umbral_muneca:
            limite_muneca = y
            break
    else:
        # Si el brazo es muy gordo y nunca se estrecha, usamos un límite de seguridad
        limite_muneca = y_palma + int(anchura_maxima * 0.8)

    # 4. Cortar todo lo que esté por debajo del límite
    mascara_mano[limite_muneca:, :] = 0
    
    return mascara_mano


def calcular_solidez(mascara_mano):
    """Área de la mano / área de su envolvente convexa (baja = dedos abiertos).

    Además de la solidez normal, resta un poco por cada hueco profundo entre dedos.
    Así, con los dedos juntos, los huecos siguen delatando que la mano está abierta.
    """
    contornos, _ = cv2.findContours(mascara_mano, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contorno = max(contornos, key=cv2.contourArea)
    area_envolvente = max(cv2.contourArea(cv2.convexHull(contorno)), 1)
    solidez = cv2.contourArea(contorno) / area_envolvente

    # Huecos profundos entre dedos (valles respecto a la "goma elástica")
    _, _, ancho, alto = cv2.boundingRect(contorno)
    profundidad_minima = 0.1 * max(ancho, alto)
    indices_envolvente = cv2.convexHull(contorno, returnPoints=False)
    defectos = cv2.convexityDefects(contorno, indices_envolvente)

    huecos = 0
    if defectos is not None:
        for _, _, _, profundidad in defectos.reshape(-1, 4):
            if profundidad / 256.0 > profundidad_minima:
                huecos += 1

    # Cada hueco resta 0.08 a la solidez (2 huecos = -0.16, suficiente para pasar a "abierta")
    return solidez - 0.08 * huecos


def suavizar_caja(caja_anterior, ventana_mano):
    """Mezcla la caja anterior (70 %) con la nueva (30 %) para que no parpadee."""
    caja_nueva = np.array(ventana_mano, dtype=float)
    if caja_anterior is None:
        return caja_nueva
    return 0.7 * caja_anterior + 0.3 * caja_nueva


def pintar_mano(imagen, caja_mano):
    x, y, ancho, alto = caja_mano.astype(int)
    cv2.rectangle(imagen, (x, y), (x + ancho, y + alto), COLOR_CAJA_MANO, GROSOR_LINEA)
    cv2.circle(imagen, (x + ancho // 2, y + alto // 2), 6, (0, 0, 255), -1)


# =============================================================================
# CLASE PRINCIPAL (la usa el controlador)
# =============================================================================

class SeguidorMano:
    """Lee la webcam en un hilo y guarda la última posición de la mano.

    Uso:
        seguidor = SeguidorMano()
        if seguidor.iniciar():
            posicion, abierta = seguidor.obtener()   # posicion = (x, y) entre 0 y 1, o None
        seguidor.detener()
    """

    def __init__(self, indice_camara=INDICE_CAMARA):
        self._indice_camara = indice_camara
        self._camara = None
        self._hilo = None
        self._corriendo = False
        self._lock = threading.Lock()
        self.error = None          # texto con el motivo si la cámara falla

        # Resultado compartido con el hilo principal (protegido por el lock)
        self._posicion = None
        self._abierta = False
        self._frame = None
        self._mascara = None

        # Estado interno del algoritmo (solo lo toca el hilo de la cámara)
        self._detector = None
        self._ultima_cara = None
        self._frames_sin_cara = 0
        self._histograma_piel = None
        self._ventana_mano = (0, 0, 100, 100)
        self._caja_suavizada = None
        self._solidez = UMBRAL_SOLIDEZ
        self._mascara_mano = None   # máscara del último frame (None hasta conocer el color de piel)
        self._frameAnterior = None
        self.__rango_color_cara = None

    # ---------- ciclo de vida ----------
    def iniciar(self):
        """Abre la cámara y arranca el hilo. Devuelve False (y guarda self.error) si falla."""
        self.error = None
        self._detector = cv2.CascadeClassifier(NOMBRE_CASCADA)
        if self._detector.empty():
            self.error = f"falta {NOMBRE_CASCADA} en la carpeta del proyecto"
            print("ERROR CAMARA:", self.error)
            return False

        self._camara = cv2.VideoCapture(self._indice_camara)
        if not self._camara.isOpened():
            self.error = "No es posible abrir la cámara"
            print(self.error)
            return False

        self._corriendo = True
        self._hilo = threading.Thread(target=self._bucle, daemon=True)
        self._hilo.start()
        return True

    def detener(self):
        self._corriendo = False
        if self._hilo is not None:
            self._hilo.join(timeout=2)

    # ---------- lectura de resultados (hilo principal) ----------
    def obtener(self):
        """Devuelve (posicion, abierta). posicion = (x, y) normalizada o None si no hay mano."""
        with self._lock:
            return self._posicion, self._abierta

    def obtener_mascara(self):
        """Última máscara de la mano (la 'retroproyeccion' de camarav3), o None."""
        with self._lock:
            return self._mascara

    def obtener_frame(self):
        """Última imagen de la cámara con lo detectado dibujado (para depurar), o None."""
        with self._lock:
            return self._frame

    # ---------- hilo de la cámara ----------
    def _bucle(self):
        try:
            while self._corriendo:
                lectura_correcta, imagen = self._camara.read()
                if not lectura_correcta:
                    self.error = "No es posible obtener la imagen"
                    print(self.error)
                    break
                imagen = cv2.flip(imagen, 1)     # efecto espejo

                posicion = self._procesar(imagen)
                abierta = self._solidez < UMBRAL_SOLIDEZ

                with self._lock:
                    self._posicion = posicion
                    self._abierta = abierta
                    self._frame = imagen
                    self._mascara = self._mascara_mano
        except Exception as fallo:               # que no muera en silencio
            self.error = f"{type(fallo).__name__}: {fallo}"
            traceback.print_exc()
        finally:
            self._camara.release()
            with self._lock:
                self._posicion = None

    def _procesar(self, imagen):
        """Analiza un frame, dibuja sobre él y devuelve la posición normalizada o None."""
        alto_imagen, ancho_imagen = imagen.shape[:2]

        # ---------- Cara (solo para taparla en la máscara) ----------
        cara = detectar_cara(self._detector, imagen)
        if cara is not None:
            self._ultima_cara = cara
            self._frames_sin_cara = 0
            self.__rango_color_cara = calcular__rango_color_cara(imagen, cara)
        else:
            self._frames_sin_cara += 1
            if self._frames_sin_cara > FRAMES_MAX_SIN_CARA:
                self._ultima_cara = None

        texto_estado = "Sin mano"
        posicion = None

        mascara_piel = calcular_mascara_piel(imagen,None)

        largo_mano = LARGO_MANO_POR_DEFECTO
        if self._ultima_cara is not None:
            tapar_cara_en_mascara(mascara_piel, self._ultima_cara)
            pintar_cuadro_cara(imagen, self._ultima_cara)
            largo_mano = self._ultima_cara[2]

        mascara_mano = np.zeros_like(mascara_piel)
        bloque_piel = elegir_bloque_mano(mascara_piel, self._ventana_mano)
        if bloque_piel is not None:
            mascara_mano = separar_mano(bloque_piel, largo_mano)
            self._solidez = 0.8 * self._solidez + 0.2 * calcular_solidez(mascara_mano)
            texto_estado = "Abierta" if self._solidez < UMBRAL_SOLIDEZ else "Cerrada"

        self._mascara_mano = mascara_mano
        _, self._ventana_mano = cv2.meanShift(mascara_mano, self._ventana_mano,
                                              CRITERIOS_MEANSHIFT)
        if mascara_mano.any():
            self._ventana_mano = cv2.boundingRect(mascara_mano)
            self._caja_suavizada = suavizar_caja(self._caja_suavizada, self._ventana_mano)
            pintar_mano(imagen, self._caja_suavizada)

            x, y, ancho, alto = self._caja_suavizada
            posicion = ((x + ancho / 2) / ancho_imagen, (y + alto / 2) / alto_imagen)

        cv2.putText(imagen, f"{texto_estado}  ({self._solidez:.2f})", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return posicion