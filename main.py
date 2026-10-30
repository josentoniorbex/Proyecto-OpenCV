# PUNTO DE ENTRADA
#   python main.py                -> WASD + cámara (M cambia entre teclado y mano)
#   python main.py --sin-camara   -> solo teclado, sin abrir la cámara

import argparse

from controlador.app import App


def main():
    parser = argparse.ArgumentParser(description="El juego de las navecitas")
    parser.add_argument("--sin-camara", action="store_true",
                        help="no abrir la cámara (solo teclado)")
    argumentos = parser.parse_args()

    App(usar_camara=not argumentos.sin_camara).ejecutar()


if __name__ == "__main__":
    main()
