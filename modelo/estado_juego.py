import random

from config import CANTIDAD_ENEMIGOS, COOLDOWN_APARICION_MAX, GAP_ENEMIGOS
from modelo.nave import Nave
from modelo.bala import Bala
from modelo.enemigo import Enemigo
from modelo.explosion import Explosion


class EstadoJuego:
    """Todo lo que existe en una partida. Aquí irán enemigos, balas, puntuación..."""

    def __init__(self):
        self.nave = Nave()
        self.enemigos = []
        self.balas = []
        self.explosiones = []
        self._reapariciones_pendientes = []
        self.pausado = False
        self.score = 0
        self.game_over = False
        self.reiniciar()

    def reiniciar(self):
        self.nave.reiniciar()
        self.enemigos = [Enemigo(indice) for indice in range(CANTIDAD_ENEMIGOS)]
        self.balas.clear()
        self.explosiones.clear()
        self._reapariciones_pendientes.clear()
        self.pausado = False
        self.score = 0
        self.game_over = False
        self._separar_enemigos()

    def actualizar(self, delta_tiempo):
        if self.pausado or self.game_over:
            return
        self._actualizar_reapariciones(delta_tiempo)
        self.nave.actualizar(delta_tiempo)
        for enemigo in self.enemigos:
            enemigo.actualizar(self.nave, delta_tiempo)
        self._separar_enemigos()
        for bala in self.balas:
            bala.actualizar(delta_tiempo)
        for explosion in self.explosiones:
            explosion.actualizar(delta_tiempo)

        self._resolver_colisiones()
        self.balas[:] = [bala for bala in self.balas if bala.y + bala.alto > 0]
        self.explosiones[:] = [
            explosion for explosion in self.explosiones
            if explosion.tiempo_restante > 0
        ]

    def _actualizar_reapariciones(self, delta_tiempo):
        pendientes = []
        for tiempo_restante in self._reapariciones_pendientes:
            tiempo_restante -= delta_tiempo
            if tiempo_restante <= 0:
                self.enemigos.append(Enemigo())
            else:
                pendientes.append(tiempo_restante)
        self._reapariciones_pendientes = pendientes
        self._separar_enemigos()

    def _separar_enemigos(self):
        for _ in range(len(self.enemigos)):
            for indice, enemigo in enumerate(self.enemigos):
                for otro in self.enemigos[indice + 1:]:
                    diferencia_x = (otro.x + otro.ancho / 2) - (enemigo.x + enemigo.ancho / 2)
                    diferencia_y = (otro.y + otro.alto / 2) - (enemigo.y + enemigo.alto / 2)
                    separacion_x = (enemigo.ancho + otro.ancho) / 2 + GAP_ENEMIGOS
                    separacion_y = (enemigo.alto + otro.alto) / 2 + GAP_ENEMIGOS
                    solapamiento_x = separacion_x - abs(diferencia_x)
                    solapamiento_y = separacion_y - abs(diferencia_y)

                    if solapamiento_x > 0 and solapamiento_y > 0:
                        if solapamiento_x < solapamiento_y:
                            desplazamiento = solapamiento_x / 2
                            direccion = 1 if diferencia_x >= 0 else -1
                            enemigo.x -= direccion * desplazamiento
                            otro.x += direccion * desplazamiento
                        else:
                            desplazamiento = solapamiento_y / 2
                            direccion = 1 if diferencia_y >= 0 else -1
                            enemigo.y -= direccion * desplazamiento
                            otro.y += direccion * desplazamiento

    def disparar(self):
        """Crea un proyectil centrado en la parte superior de la nave."""
        self.balas.append(Bala(self.nave.x + self.nave.ancho / 2, self.nave.y))

    def _resolver_colisiones(self):
        enemigos_destruidos = set()
        balas_usadas = set()

        for indice_bala, bala in enumerate(self.balas):
            for indice_enemigo, enemigo in enumerate(self.enemigos):
                if indice_enemigo not in enemigos_destruidos \
                        and bala.estaColisionando(enemigo):
                    centro_x = enemigo.x + enemigo.ancho / 2
                    centro_y = enemigo.y + enemigo.alto / 2
                    self.explosiones.append(Explosion(centro_x, centro_y))
                    enemigos_destruidos.add(indice_enemigo)
                    balas_usadas.add(indice_bala)
                    self.score += 1
                    break

        self.enemigos[:] = [
            enemigo for indice, enemigo in enumerate(self.enemigos)
            if indice not in enemigos_destruidos
        ]
        for _ in enemigos_destruidos:
            self._reapariciones_pendientes.append(
                random.uniform(0, COOLDOWN_APARICION_MAX)
            )
        self.balas[:] = [
            bala for indice, bala in enumerate(self.balas)
            if indice not in balas_usadas
        ]

        if any(enemigo.estaColisionando(self.nave) for enemigo in self.enemigos):
            self.game_over = True

    def entidades(self):
        """Todo lo que hay que dibujar."""
        return [self.nave, *self.enemigos, *self.balas, *self.explosiones]
