import pygame
from pathlib import Path

pygame.init()

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "Assets"
IMG_DIR = ASSETS_DIR / "Images"
SND_DIR = ASSETS_DIR / "Sonido"
SFX_DIR = SND_DIR / "sfx" 
FONT_DIR = ASSETS_DIR / "fonts"

IMG_DIRS = {
    "facil": IMG_DIR / "facil",
    "medio": IMG_DIR / "medio",
    "dificil": IMG_DIR / "dificil",
    "libre": IMG_DIR / "libre"
}

IMG_TEMAS = {
    "instrumentos": IMG_DIR / "instrumentos",
    "frutas": IMG_DIR / "frutas",
    "planetas": IMG_DIR / "planetas",
    "animales": IMG_DIR / "animales",
    "todo junto": IMG_DIR / "todo_junto",
    "aleatorio": None, 
}
TEMA_CARTAS = "instrumentos" 

FONT_DIR = {
    "titulo": FONT_DIR / "titulo.ttf",
    "subtitulo": FONT_DIR / "subtitulo.ttf",
}

ANCHO = 1280
ALTO = 720


FONDO = pygame.image.load(str(IMG_DIR / "fondo.png"))

CARTA_VOLTEADA = (str(IMG_DIR / "volteada.png"))

FPS = 60

#colores
BLANCO = (255, 255, 255)
MORADO_P = (175, 126, 173)
AZUL_P = (132, 182, 244)
AZUL_OSCURO = (129, 127, 137) 
VERDE_PASTEL = (140, 200, 160)
ROJO_PASTEL = (200, 140, 140)

# Colores barra de tiempo (pastel)
BARRA_TIEMPO_AZUL = (180, 210, 255)   # >50%
BARRA_TIEMPO_AMARILLO = (255, 245, 180)  # 20%-50%
BARRA_TIEMPO_ROJO = (255, 180, 180)   # <20%
BARRA_TIEMPO_FONDO = (80, 80, 100)
OVERLAY_FIN_JUEGO = (120, 60, 80)  # rojo oscuro pastel


DURACION_VOLTEO = 0.20

fuente_titulo = pygame.font.Font(str(FONT_DIR["titulo"]), 60)
fuente_menu = pygame.font.Font(str(FONT_DIR["subtitulo"]), 36)


DIFICULTAD = {
    "facil": {
        "num_pares": 6,
        "ancho_alto": (120, 110),
        "margen": 20,
        "columnas": 4,
        "filas": 3,
        "tiempo": 600  # 10 minutos
    },
    "medio": {
        "num_pares": 8,
        "ancho_alto": (110, 100),
        "margen": 20,
        "columnas": 4,  
        "filas": 4,
        "tiempo": 420  # 7 minutos
    },
    "dificil": {
        "num_pares": 12,
        "ancho_alto": (100, 90),
        "margen": 20,
        "columnas": 6,
        "filas": 4,
        "tiempo": 300  # 5 minutos
    }
}

MUSICA_FONDO = SND_DIR / "sonido_fondo.mp3"
SONIDO_JUEGO = SND_DIR / "sonido_juego.mp3" 
SONIDO_INSTRUCCIONES = SND_DIR / "sonido_instrucciones.mp3"  
SONIDO_ACTIVADO = True 


VOLUMEN_GENERAL = 1.0
VOLUMEN_MUSICA = 1.0
VOLUMEN_EFECTOS = 1.0


def volumen_musica_final():
    return max(0, min(1.0, VOLUMEN_GENERAL * VOLUMEN_MUSICA))


def volumen_efectos_final():
    return max(0, min(1.0, VOLUMEN_GENERAL * VOLUMEN_EFECTOS))