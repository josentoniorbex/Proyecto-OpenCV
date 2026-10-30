# APLICACIÓN: único bucle principal con una máquina de estados (MENU / JUGANDO / PAUSA).
# Todo lo de ventanas y OpenCV ocurre en el hilo principal. Solo la cámara usa otro hilo.

import time
import cv2

from config import (NOMBRE_VENTANA, ANCHO_INICIAL, ALTO_INICIAL, FPS_OBJETIVO, MOSTRAR_CAMARA,
                    TITULO_JUEGO, TITULO_PAUSA, OPCIONES_MENU, OPCIONES_PAUSA,
                    ACCION_JUGAR, ACCION_VOLVER_AL_MENU)
from modelo.estado_juego import EstadoJuego
from modelo.menu import MenuModelo
from vista.ventana import Ventana
from vista.vista_menu import VistaMenu
from vista.vista_juego import VistaJuego
from controlador.controlador_menu import ControladorMenu
from controlador.controlador_juego import ControladorJuego
from vision.seguidor_mano import SeguidorMano

MENU = "MENU"
JUGANDO = "JUGANDO"
PAUSA = "PAUSA"


class App:
    def __init__(self, usar_camara=True):
        self.ventana = Ventana(NOMBRE_VENTANA, ANCHO_INICIAL, ALTO_INICIAL)
        self.seguidor, aviso_camara = self._crear_seguidor() if usar_camara else (None, "desactivada")

        vista_menu = VistaMenu()
        self.controlador_menu = ControladorMenu(MenuModelo(TITULO_JUEGO, OPCIONES_MENU), vista_menu)
        self.controlador_pausa = ControladorMenu(MenuModelo(TITULO_PAUSA, OPCIONES_PAUSA), vista_menu)
        self.controlador_juego = ControladorJuego(EstadoJuego(), VistaJuego(), self.seguidor, aviso_camara)

        self.estado = MENU
        self._ultimo_frame = None
        self._fps = 0.0
        self.ventana.poner_callback_raton(self._evento_raton)

    # ---------- preparación ----------
    @staticmethod
    def _crear_seguidor():
        seguidor = SeguidorMano()
        if seguidor.iniciar():
            return seguidor, None
        print("Se jugará solo con el teclado (WASD).")
        return None, seguidor.error

    @property
    def controlador_activo(self):
        if self.estado == JUGANDO:
            return self.controlador_juego
        if self.estado == PAUSA:
            return self.controlador_pausa
        return self.controlador_menu

    def _evento_raton(self, evento, x_pixel, y_pixel, flags, parametro):
        x_virtual, y_virtual = self.ventana.pixel_a_virtual(x_pixel, y_pixel)
        self.controlador_activo.raton(evento, x_virtual, y_virtual)

    def _calcular_fps(self, ahora):
        if self._ultimo_frame is not None:
            periodo = ahora - self._ultimo_frame
            if periodo > 0:
                fps_actual = 1 / periodo
                self._fps = fps_actual if self._fps == 0 else 0.8 * self._fps + 0.2 * fps_actual
        self._ultimo_frame = ahora
        return self._fps

    # ---------- bucle principal ----------
    def ejecutar(self):
        try:
            corriendo = True
            while corriendo:
                inicio = time.perf_counter()
                fps = self._calcular_fps(inicio)

                if self.ventana.medir():
                    imagen = self.controlador_activo.actualizar(self.ventana.ancho,
                                                                self.ventana.alto)
                    cv2.putText(imagen, f"FPS: {fps:.1f}",
                                (imagen.shape[1] - 150, 35), cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 255, 0), 2)
                    self.ventana.mostrar(imagen)
                self._mostrar_camara()

                # Esperamos lo justo para ir a FPS_OBJETIVO
                gastado_ms = (time.perf_counter() - inicio) * 1000
                espera_ms = max(1, int(1000 / FPS_OBJETIVO - gastado_ms))
                tecla = cv2.waitKey(espera_ms) & 0xFF
                if tecla != 255:
                    self.controlador_activo.tecla(tecla)

                if self.ventana.cerrada():
                    break
                corriendo = self._procesar_accion(self.controlador_activo.consumir_accion())
        finally:
            if self.seguidor is not None:
                self.seguidor.detener()
            self.ventana.cerrar()

    def _mostrar_camara(self):
        if MOSTRAR_CAMARA and self.seguidor is not None:
            frame = self.seguidor.obtener_frame()
            if frame is not None:
                cv2.imshow("webcam", frame)

            mascara = self.seguidor.obtener_mascara()
            if mascara is not None:
                cv2.imshow("mascara", mascara)

    def _procesar_accion(self, accion):
        """Cambia de estado según lo que haya elegido el jugador.
        Devuelve False si hay que cerrar el programa."""
        if accion is None:
            return True

        if self.estado == MENU:
            if accion == ACCION_JUGAR:
                self.controlador_juego.reiniciar()
                self.estado = JUGANDO
            else:                                   # SALIR o ESC
                return False

        elif self.estado == JUGANDO:                # solo llega ESC
            self.controlador_juego.pausar()
            self.controlador_pausa.reiniciar()
            self.estado = PAUSA

        elif self.estado == PAUSA:
            if accion == ACCION_VOLVER_AL_MENU:
                self.controlador_menu.reiniciar()
                self.estado = MENU
            else:                                   # CONTINUAR o ESC
                self.controlador_juego.reanudar()
                self.estado = JUGANDO
        return True
