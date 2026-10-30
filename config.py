# CONFIGURACIÓN GLOBAL
# Aquí van todas las constantes del proyecto, para tocarlas desde un solo sitio.

# ---------------- Campo de juego (unidades virtuales, NO son píxeles) ----------------
ANCHO_VIRTUAL = 1280
ALTO_VIRTUAL = 720

# ---------------- Ventana ----------------
NOMBRE_VENTANA = "main"
ANCHO_INICIAL = 960
ALTO_INICIAL = 540
FPS_OBJETIVO = 60

# ---------------- Textos y acciones de los menús ----------------
# Sin tildes: la fuente de OpenCV no las dibuja
TITULO_JUEGO = "El juego de las navecitas"
TITULO_PAUSA = "PAUSA"

ACCION_JUGAR = "JUGAR"
ACCION_SALIR = "SALIR"
ACCION_CONTINUAR = "CONTINUAR"
ACCION_VOLVER_AL_MENU = "VOLVER AL MENU"
ESC_PULSADO = "__ESC__"

OPCIONES_MENU = [ACCION_JUGAR, ACCION_SALIR]
OPCIONES_PAUSA = [ACCION_CONTINUAR, ACCION_VOLVER_AL_MENU]

# ---------------- Teclas ----------------
TECLA_ENTER = 13
TECLA_ESPACIO = 32
TECLA_ESC = 27

# ---------------- Control de la nave ----------------
TECLAS_MOVIMIENTO = {
    "izquierda": (ord('a'), ord('A')),
    "derecha": (ord('d'), ord('D')),
    "arriba": (ord('w'), ord('W')),
    "abajo": (ord('s'), ord('S')),
}
# OpenCV no sabe si una tecla sigue pulsada, solo recibe "pulsaciones". Se considera que una
# dirección sigue activa este tiempo (en segundos) después de la última pulsación recibida.
TIEMPO_TECLA_ACTIVA = 0.15

# ---------------- Nave ----------------
ANCHO_NAVE = 60
ALTO_NAVE = 40
VELOCIDAD_NAVE = 1500.0    # unidades virtuales por segundo (lo rápido que persigue a la mano)
VELOCIDAD_TECLADO = 600.0  # unidades virtuales por segundo con WASD
MARGEN_INFERIOR_NAVE = 20

# ---------------- Botones de los menús (unidades virtuales) ----------------
ANCHO_BOTON = 400
ALTO_BOTON = 80
SEPARACION_BOTONES = 40
POSICION_Y_TITULO = 200

# ---------------- Colores (BGR) ----------------
COLOR_FONDO_MENU = (30, 20, 10)
COLOR_FONDO_JUEGO = (0, 0, 0)
COLOR_BOTON = (90, 70, 50)
COLOR_BOTON_SELECCIONADO = (0, 220, 255)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_SELECCIONADO = (0, 0, 0)
COLOR_TITULO = (0, 220, 255)
COLOR_NAVE = (0, 255, 255)

# ---------------- Visión (cámara) ----------------
INDICE_CAMARA = 0
MOSTRAR_CAMARA = True      # ventana auxiliar con la cámara para depurar
MARGEN_MANO = 0.15         # la mano se mueve en [0.15, 0.85] del ancho de la cámara y eso
                           # se estira a todo el ancho del juego (así llegas a los bordes)
