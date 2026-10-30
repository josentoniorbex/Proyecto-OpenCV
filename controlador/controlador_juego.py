import time

from config import (ANCHO_VIRTUAL, ALTO_VIRTUAL, TECLA_ESC, ESC_PULSADO, MARGEN_MANO,
                    TECLAS_MOVIMIENTO, TIEMPO_TECLA_ACTIVA)


class ControladorJuego:
    """Lee la entrada, actualiza el modelo y pide a la vista que dibuje.

    Control automático: si la cámara ve la mano, manda la mano; si no, mandan WASD.

    seguidor_mano: un SeguidorMano ya iniciado, o None si no hay cámara.
    aviso_camara:  texto que se enseña en pantalla si la cámara no pudo arrancar."""

    def __init__(self, estado, vista, seguidor_mano=None, aviso_camara=None):
        self.estado = estado
        self.vista = vista
        self.seguidor_mano = seguidor_mano
        self.aviso_camara = aviso_camara
        self._tiempo_anterior = time.perf_counter()
        self._ultimo_frame_fps = None
        self._fps = 0.0
        self._ultima_pulsacion = {direccion: -1.0 for direccion in TECLAS_MOVIMIENTO}
        self._accion = None

    # ---------- ciclo de la partida ----------
    def reiniciar(self):
        self.estado.reiniciar()
        self._tiempo_anterior = time.perf_counter()
        self._ultimo_frame_fps = None
        self._fps = 0.0
        self._ultima_pulsacion = {direccion: -1.0 for direccion in TECLAS_MOVIMIENTO}
        self._accion = None

    def pausar(self):
        self.estado.pausado = True

    def reanudar(self):
        self.estado.pausado = False
        self._tiempo_anterior = time.perf_counter()   # evita un salto de tiempo al volver

    # ---------- entradas ----------
    def tecla(self, tecla):
        if tecla == TECLA_ESC:
            self._accion = ESC_PULSADO
        else:
            for direccion, teclas in TECLAS_MOVIMIENTO.items():
                if tecla in teclas:
                    self._ultima_pulsacion[direccion] = time.perf_counter()

    def raton(self, evento, x_virtual, y_virtual):
        pass        # el juego no usa el ratón

    def consumir_accion(self):
        accion, self._accion = self._accion, None
        return accion

    def _direccion_teclado(self, ahora):
        """(dx, dy) en -1, 0, 1 según las teclas pulsadas hace poco."""
        def activa(direccion):
            return ahora - self._ultima_pulsacion[direccion] < TIEMPO_TECLA_ACTIVA
        dx = int(activa("derecha")) - int(activa("izquierda"))
        dy = int(activa("abajo")) - int(activa("arriba"))
        return dx, dy

    def _leer_mano(self):
        """Devuelve ((x, y) objetivo virtual o None, abierta, texto de estado)."""
        if self.seguidor_mano is None:
            return None, False, f"Sin camara: {self.aviso_camara}"
        if self.seguidor_mano.error:
            return None, False, f"Camara parada: {self.seguidor_mano.error}"

        posicion, abierta = self.seguidor_mano.obtener()
        if posicion is None:
            return None, False, "Camara: no veo la mano"

        # Estiramos [MARGEN, 1 - MARGEN] a [0, 1] para poder llegar a los bordes
        x_normalizada = (posicion[0] - MARGEN_MANO) / (1 - 2 * MARGEN_MANO)
        x_normalizada = min(max(x_normalizada, 0.0), 1.0)
        y_normalizada = min(max(posicion[1], 0.0), 1.0)
        objetivo = (x_normalizada * ANCHO_VIRTUAL, y_normalizada * ALTO_VIRTUAL)
        return objetivo, abierta, ("Mano abierta" if abierta else "Mano cerrada")

    def calcularFPS(self, ahora):
        """Calcula los FPS reales suavizados mediante un filtro exponencial."""
        if self._ultimo_frame_fps is not None:
            delta = ahora - self._ultimo_frame_fps
            if delta > 0:
                fps_instantaneo = 1 / delta
                # Para que no varie mucho y me de un derrame visual
                # 80% de historia y 20% fps generado
                if self._fps == 0:
                    self._fps = fps_instantaneo
                else:
                    self._fps = 0.8 * self._fps + 0.2 * fps_instantaneo 
        self._ultimo_frame_fps = ahora

    # ---------- bucle ----------
    def actualizar(self, ancho_ventana, alto_ventana):
        """Actualiza el modelo y devuelve la imagen del juego."""
        ahora = time.perf_counter()
        delta_tiempo = min(ahora - self._tiempo_anterior, 0.1)
        self._tiempo_anterior = ahora
        self.calcularFPS(ahora)

        objetivo_mano, _, texto_camara = self._leer_mano()
        hay_mano = objetivo_mano is not None
        lineas = [
            "Control: " + ("MANO" if hay_mano else "TECLADO (WASD)"),
            texto_camara,
            f"FPS: {self._fps:.1f}",
        ]

        if not self.estado.pausado:
            if hay_mano:                                   # 1) si hay mano, manda la mano
                self.estado.nave.mover_hacia(*objetivo_mano)
            else:                                          # 2) si no, WASD
                dx, dy = self._direccion_teclado(ahora)
                if dx or dy:
                    self.estado.nave.mover_direccion(dx, dy, delta_tiempo)
            self.estado.actualizar(delta_tiempo)

        return self.vista.dibujar(self.estado, ancho_ventana, alto_ventana, lineas)
