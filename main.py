import pygame
import sys
import constantes
from menu import ejecutar_menu
from game import ejecutar_juego
from audio import reproducir_musica
from src.juego import MiJuego

if __name__ == "__main__":
    game = MiJuego()
    game.run_preview()
        
pygame.init()

# Recargar assets tras run_preview() (pygame.quit invalida superficies previas)
constantes.recargar_assets()

try:
    pygame.mixer.init()
except:
    print("Error inicializando el mixer")

ventana = pygame.display.set_mode((constantes.ANCHO, constantes.ALTO))
reloj = pygame.time.Clock()
pygame.display.set_caption("FLIP IT")

reproducir_musica(constantes.MUSICA_FONDO)
if not constantes.SONIDO_ACTIVADO and pygame.mixer.get_init():
    pygame.mixer.music.pause()

running = True

while running:

    resultado_menu = ejecutar_menu(ventana, reloj)

    if resultado_menu is None:
        break

    dificultad, tiempo_segundos = resultado_menu

    reproducir_musica(constantes.SONIDO_JUEGO)
    if not constantes.SONIDO_ACTIVADO and pygame.mixer.get_init():
        pygame.mixer.music.pause()

    while True:
        resultado = ejecutar_juego(ventana, reloj, dificultad, tiempo_segundos)

        if resultado in ["menu", None]:
            reproducir_musica(constantes.MUSICA_FONDO)
            if not constantes.SONIDO_ACTIVADO and pygame.mixer.get_init():
                pygame.mixer.music.pause()
            break
        elif resultado == "salir":
            running = False
            break

pygame.quit()
sys.exit()

    