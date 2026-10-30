from modelo.nave import Nave
from modelo.bala import Bala


class EstadoJuego:
    """Todo lo que existe en una partida. Aquí irán enemigos, balas, puntuación..."""

    def __init__(self):
        self.nave = Nave()
        self.enemigos = []     # TODO
        self.balas = []        # TODO
        self.pausado = False

    def reiniciar(self):
        self.nave.reiniciar()
        self.enemigos.clear()
        self.balas.clear()
        self.pausado = False

    def actualizar(self, delta_tiempo):
        if self.pausado:
            return
        self.nave.actualizar(delta_tiempo)
        for bala in self.balas:
            bala.actualizar(delta_tiempo)
        self.balas[:] = [bala for bala in self.balas if bala.y + bala.alto > 0]

    def disparar(self):
        """Crea un proyectil centrado en la parte superior de la nave."""
        self.balas.append(Bala(self.nave.x + self.nave.ancho / 2, self.nave.y))

    def entidades(self):
        """Todo lo que hay que dibujar."""
        return [self.nave, *self.enemigos, *self.balas]
