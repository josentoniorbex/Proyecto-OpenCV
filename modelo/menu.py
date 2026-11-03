from config import (ANCHO_VIRTUAL, ALTO_VIRTUAL, ANCHO_BOTON, ALTO_BOTON,
                    SEPARACION_BOTONES)


class MenuModelo:
    """Datos de un menú: título, opciones, cuál está seleccionada y dónde están los botones."""

    def __init__(self, titulo, opciones):
        '''Inicializa el título, las opciones y la posición de los botones del menú.'''
        self.titulo = titulo
        self.subtitulo = None
        self.opciones = opciones
        self.opcion = 0
        self.botones = self._calcular_botones(len(opciones))

    @property
    def opcion_actual(self):
        '''Devuelve el texto de la opción que está seleccionada actualmente.'''
        return self.opciones[self.opcion]

    def subir(self):
        '''Mueve la selección a la opción anterior, volviendo al final si hace falta.'''
        self.opcion = (self.opcion - 1) % len(self.opciones)

    def bajar(self):
        '''Mueve la selección a la opción siguiente, volviendo al inicio si hace falta.'''
        self.opcion = (self.opcion + 1) % len(self.opciones)

    def reiniciar(self):
        '''Selecciona de nuevo la primera opción del menú.'''
        self.opcion = 0

    @staticmethod
    def _calcular_botones(cantidad):
        """Lista de (x, y, ancho, alto) en unidades virtuales, centrados."""
        alto_total = cantidad * ALTO_BOTON + (cantidad - 1) * SEPARACION_BOTONES
        y_primer_boton = ALTO_VIRTUAL // 2 - alto_total // 2 + 80
        x_botones = (ANCHO_VIRTUAL - ANCHO_BOTON) // 2
        return [(x_botones, y_primer_boton + n * (ALTO_BOTON + SEPARACION_BOTONES),
                 ANCHO_BOTON, ALTO_BOTON) for n in range(cantidad)]
