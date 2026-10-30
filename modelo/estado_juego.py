from modelo.nave import Nave


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

    def entidades(self):
        """Todo lo que hay que dibujar."""
        return [self.nave, *self.enemigos, *self.balas]
