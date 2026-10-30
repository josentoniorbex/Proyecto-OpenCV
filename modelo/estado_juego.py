import random

from config import ANCHO_VIRTUAL, CANTIDAD_ENEMIGOS, COOLDOWN_APARICION_MAX
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
        ancho_carril = ANCHO_VIRTUAL / CANTIDAD_ENEMIGOS
        for indice, enemigo in enumerate(self.enemigos):
            enemigo.x = ancho_carril * (indice + 0.5) - enemigo.ancho / 2
        self.balas.clear()
        self.explosiones.clear()
        self._reapariciones_pendientes.clear()
        self.pausado = False
        self.score = 0
        self.game_over = False

    def actualizar(self, delta_tiempo):
        if self.pausado or self.game_over:
            return
        self._actualizar_reapariciones(delta_tiempo)
        self.nave.actualizar(delta_tiempo)
        for enemigo in self.enemigos:
            y_anterior = enemigo.y
            enemigo.actualizar(self.nave, delta_tiempo, self.enemigos)
            if enemigo.y < y_anterior:
                self._colocar_enemigo_en_posicion_libre(enemigo)
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
                enemigo = Enemigo()
                self.enemigos.append(enemigo)
                self._colocar_enemigo_en_posicion_libre(enemigo)
            else:
                pendientes.append(tiempo_restante)
        self._reapariciones_pendientes = pendientes

    def _colocar_enemigo_en_posicion_libre(self, enemigo):
        posiciones_libres = [
            x for x in range(ANCHO_VIRTUAL - enemigo.ancho + 1)
            if not any(
                x < otro.x + otro.ancho
                and x + enemigo.ancho > otro.x
                and enemigo.y < otro.y + otro.alto
                and enemigo.y + enemigo.alto > otro.y
                for otro in self.enemigos
                if otro is not enemigo
            )
        ]
        if posiciones_libres:
            enemigo.x = random.choice(posiciones_libres)

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
