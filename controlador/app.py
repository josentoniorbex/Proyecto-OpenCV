# APLICACIÓN: único bucle principal con una máquina de estados (MENU / JUGANDO / PAUSA).
# Todo lo de ventanas y OpenCV ocurre en el hilo principal. Solo la cámara usa otro hilo.

import threading
import time
import cv2

from config import (NOMBRE_VENTANA, ANCHO_INICIAL, ALTO_INICIAL, FPS_OBJETIVO, MOSTRAR_CAMARA,
                    TITULO_JUEGO, TITULO_PAUSA, OPCIONES_MENU, OPCIONES_PAUSA,
                    ACCION_JUGAR, ACCION_VOLVER_AL_MENU, ACCION_FIN_PARTIDA)
from modelo.estado_juego import EstadoJuego
from modelo.menu import MenuModelo
from vista.ventana import Ventana
from vista.vista_menu import VistaMenu
from vista.vista_juego import VistaJuego
from controlador.controlador_menu import ControladorMenu
from controlador.controlador_juego import ControladorJuego
from vision.seguidor_mano import DetectorDeMano

MENU = "MENU"
JUGANDO = "JUGANDO"
PAUSA = "PAUSA"


class App:
    def __init__(self, usar_camara=True):
        '''Prepara la ventana, los controladores y los estados de la aplicación.'''
        self.ventana = Ventana(NOMBRE_VENTANA, ANCHO_INICIAL, ALTO_INICIAL)
        self.detector_de_mano, aviso_camara = (
            self._crear_detector_de_mano() if usar_camara else (None, "desactivada")
        )

        vista_menu = VistaMenu()
        self.controlador_menu = ControladorMenu(
            MenuModelo(TITULO_JUEGO, OPCIONES_MENU), vista_menu, self.detector_de_mano
        )
        self.controlador_pausa = ControladorMenu(
            MenuModelo(TITULO_PAUSA, OPCIONES_PAUSA), vista_menu, self.detector_de_mano
        )
        self.controlador_juego = ControladorJuego(
            EstadoJuego(), VistaJuego(), self.detector_de_mano, aviso_camara
        )

        self.estado = MENU
        self.corriendo = True
        self.frame_actual = None
        self._tamano_ventana = (ANCHO_INICIAL, ALTO_INICIAL)
        self._hilo_controlador = None
        self.ventana.poner_callback_raton(self._evento_raton)

    # ---------- preparación ----------
    @staticmethod
    def _crear_detector_de_mano():
        '''Inicia el detector de mano o devuelve el motivo por el que no está disponible.'''
        detector_de_mano = DetectorDeMano()
        if detector_de_mano.iniciar():
            return detector_de_mano, None
        print("Se jugará solo con el teclado (WASD).")
        return None, detector_de_mano.error

    @property
    def controlador_activo(self):
        '''Devuelve el controlador correspondiente al estado actual de la aplicación.'''
        if self.estado == JUGANDO:
            return self.controlador_juego
        if self.estado == PAUSA:
            return self.controlador_pausa
        return self.controlador_menu

    def _evento_raton(self, evento, x_pixel, y_pixel, flags, parametro):
        '''Convierte la posición del ratón a coordenadas virtuales y la envía al controlador.'''
        x_virtual, y_virtual = self.ventana.pixel_a_virtual(x_pixel, y_pixel)
        self.controlador_activo.raton(evento, x_virtual, y_virtual)

    # ---------- bucle principal ----------
    def ejecutar(self):
        '''Ejecuta el bucle principal y libera los recursos al terminar.'''
        self._hilo_controlador = threading.Thread(target=self._bucle_controlador, daemon=True)
        self._hilo_controlador.start()
        try:
            while self.corriendo:
                if self.ventana.medir():
                    self._tamano_ventana = (self.ventana.ancho, self.ventana.alto)
                    if self.frame_actual is not None:
                        self.ventana.mostrar(self.frame_actual)
                self._mostrar_camara()

                tecla = cv2.waitKey(1) & 0xFF
                if tecla != 255:
                    self.controlador_activo.tecla(tecla)

                if self.ventana.cerrada():
                    break
                self.corriendo = self._procesar_accion(
                    self.controlador_activo.consumir_accion())
        finally:
            self.corriendo = False
            if self._hilo_controlador is not None:
                self._hilo_controlador.join()
            if self.detector_de_mano is not None:
                self.detector_de_mano.detener()
            self.ventana.cerrar()

    def _bucle_controlador(self):
        '''Actualiza el controlador activo a la frecuencia objetivo y guarda cada fotograma.'''
        periodo_objetivo = 1 / FPS_OBJETIVO
        while self.corriendo:
            inicio = time.perf_counter()
            imagen = self.controlador_activo.actualizar(*self._tamano_ventana)
            self.frame_actual = imagen

            restante = periodo_objetivo - (time.perf_counter() - inicio)
            if restante > 0:
                time.sleep(restante)

    def _mostrar_camara(self):
        '''Muestra las imágenes auxiliares de la cámara cuando la depuración está activada.'''
        if MOSTRAR_CAMARA and self.detector_de_mano is not None:
            frame = self.detector_de_mano.obtener_frame()
            if frame is not None:
                cv2.imshow("webcam", frame)

            mascara = self.detector_de_mano.obtener_mascara()
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
                self.controlador_menu.modelo.titulo = TITULO_JUEGO
                self.controlador_menu.modelo.subtitulo = None
                self.estado = JUGANDO
            else:                                   # SALIR o ESC
                return False

        elif self.estado == JUGANDO and accion == ACCION_FIN_PARTIDA:
            self.controlador_menu.reiniciar()
            self.controlador_menu.modelo.titulo = "GAME OVER"
            self.controlador_menu.modelo.subtitulo = (
                f"Score: {self.controlador_juego.estado.score}"
            )
            self.estado = MENU

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
