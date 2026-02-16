import pygame
import constantes

_efectos_cache = {}

EFECTOS = ("boton", "carta", "correcto", "incorrecto")


def aplicar_volumen_musica():
    if pygame.mixer.get_init():
        v = constantes.volumen_musica_final()
        pygame.mixer.music.set_volume(v)


def reproducir_musica(ruta_path, en_bucle=True):
    try:
        pygame.mixer.music.load(str(ruta_path))
        pygame.mixer.music.play(-1 if en_bucle else 0)
        aplicar_volumen_musica()
    except (pygame.error, FileNotFoundError):
        pass


def volumen_efectos():
    return constantes.volumen_efectos_final()


def play_efecto(nombre):
    if not constantes.SONIDO_ACTIVADO or not pygame.mixer.get_init():
        return
    if nombre not in EFECTOS:
        return
    try:
        if nombre not in _efectos_cache:
            ruta = constantes.SFX_DIR / f"{nombre}.ogg"
            _efectos_cache[nombre] = pygame.mixer.Sound(str(ruta))
        snd = _efectos_cache[nombre]
        snd.set_volume(volumen_efectos())
        snd.play()
    except (pygame.error, FileNotFoundError):
        pass
