import random
import math
import pygame
import sys
from pathlib import Path
from enfocate import GameBase, GameMetadata, COLORS
class GameBase:
        def __init__(self, meta):
            pass
GameMetadata = lambda **kwargs: None
COLORS = {"carbon_oscuro": (0, 0, 0)}

import constantes
from constantes import DIFICULTAD, IMG_TEMAS
from audio import play_efecto, reproducir_musica
from instrucciones import ejecutar_instrucciones
from menu import ejecutar_menu


fondo_global = None  

class Carta:
    def __init__(self, imagen, x, y, ancho, alto, volteada):
        self.imagen = imagen
        self._volteada = pygame.transform.scale(volteada, (ancho, alto))
        self._fondo = self._volteada
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.visible = False
        self.emparejada = False
        self.ancho_orig, self.alto_orig = ancho, alto
        self.animacion_volteo = None
        self.progreso_volteo = 0.0

    def actualizar_volteo(self, dt):
        if self.animacion_volteo is None:
            return
        self.progreso_volteo += dt / constantes.DURACION_VOLTEO
        if self.progreso_volteo >= 1.0:
            self.progreso_volteo = 0.0
            self.visible = self.animacion_volteo == "mostrar"
            self.animacion_volteo = None

    def dibujar(self, superficie):
        if self.animacion_volteo is not None:
            p = min(1.0, max(0.0, self.progreso_volteo))
            scale = math.sin(p * math.pi)
            w = max(2, int(self.ancho_orig * scale))
            mostrar_frente = p >= 0.5
            surf = self.imagen if mostrar_frente else self._volteada
            img_esc = pygame.transform.smoothscale(surf, (w, self.alto_orig))
            rect_esc = img_esc.get_rect(center=self.rect.center)
            superficie.blit(img_esc, rect_esc)
            return
        if self.visible or self.emparejada:
            superficie.blit(self.imagen, self.rect)
        else:
            superficie.blit(self._volteada, self.rect)

    def clic_en_carta(self, pos):
        return (
            self.rect.collidepoint(pos)
            and not self.visible
            and not self.emparejada
            and self.animacion_volteo is None
        )

    def iniciar_volteo_mostrar(self):
        self.animacion_volteo = "mostrar"
        self.progreso_volteo = 0.0

    def iniciar_volteo_ocultar(self):
        self.animacion_volteo = "ocultar"
        self.progreso_volteo = 0.0


class Boton:
    def __init__(
        self,
        texto,
        x,
        y,
        ancho,
        alto,
        fuente=None,
        color_texto=constantes.BLANCO,
        color_fondo=(100, 150, 200),
    ):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.fuente = fuente or pygame.font.SysFont(None, 36)
        self.color_texto = color_texto
        self.color_fondo = color_fondo
        self.superficie_texto = self.fuente.render(texto, True, color_texto)

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color_fondo, self.rect)
        pygame.draw.rect(superficie, constantes.BLANCO, self.rect, 3)
        text_rect = self.superficie_texto.get_rect(center=self.rect.center)
        superficie.blit(self.superficie_texto, text_rect)

    def clic_en_boton(self, pos):
        return self.rect.collidepoint(pos)


def dibujar_barra_tiempo(superficie, tiempo_restante, tiempo_limite, fuente):
    """Barra de tiempo fluida: color según % restante, relleno con decimales."""
    barra_ancho = 500
    barra_alto = 28
    x = (constantes.ANCHO - barra_ancho) // 2
    y = 12
    rect_fondo = pygame.Rect(x, y, barra_ancho, barra_alto)
    pygame.draw.rect(superficie, constantes.BARRA_TIEMPO_FONDO, rect_fondo)
    pygame.draw.rect(superficie, constantes.BLANCO, rect_fondo, 2)
    if tiempo_limite and tiempo_limite > 0 and tiempo_restante is not None:
        p = max(0.0, min(1.0, tiempo_restante / tiempo_limite))
        if p > 0.5:
            color_barra = constantes.BARRA_TIEMPO_AZUL
        elif p > 0.2:
            color_barra = constantes.BARRA_TIEMPO_AMARILLO
        else:
            color_barra = constantes.BARRA_TIEMPO_ROJO
        ancho_lleno = barra_ancho * p 
        if ancho_lleno > 0:
            pygame.draw.rect(superficie, color_barra, (x, y, int(ancho_lleno), barra_alto))
    tr = int(tiempo_restante) if tiempo_restante is not None else 0
    minutos = tr // 60
    segundos = tr % 60
    texto = f"{minutos:02}:{segundos:02}" if tiempo_limite else "∞"
    surf_texto = fuente.render(texto, True, constantes.BLANCO)
    rect_texto = surf_texto.get_rect(center=rect_fondo.center)
    superficie.blit(surf_texto, rect_texto)


def obtener_config(pares):
    for config in DIFICULTAD.values():
        if config["num_pares"] == pares:
            return config
    return DIFICULTAD["facil"]


def _directorio_tema():
    """Devuelve el directorio de imágenes del tema actual (resuelve 'aleatorio')."""
    tema = constantes.TEMA_CARTAS
    if tema == "aleatorio":
        opciones = [k for k in IMG_TEMAS if k != "aleatorio" and IMG_TEMAS[k]]
        tema = random.choice(opciones) if opciones else "instrumentos"
    return IMG_TEMAS.get(tema) or IMG_TEMAS["instrumentos"]


def crear_cartas(pares, dificultad):
    config = obtener_config(pares)
    cartas = []
    ancho, alto = config["ancho_alto"]
    margen = config["margen"]
    columnas, filas = config["columnas"], config["filas"]
    img_dir = _directorio_tema()

    try:
        img_ori = pygame.image.load(str(constantes.CARTA_VOLTEADA)).convert_alpha()
        volteada = pygame.transform.scale(img_ori, (ancho, alto))
    except (FileNotFoundError, pygame.error):
        volteada = pygame.Surface((ancho, alto))
        volteada.fill(constantes.MORADO_P)

    # Cargar imágenes desde el tema elegido
    imagenes = []
    for i in range(1, pares + 1):
        imagen = None
        for ext in ['.png', '.jpg']:
            ruta_img = img_dir / f"{i}{ext}"
            try:
                imagen_original = pygame.image.load(str(ruta_img)).convert_alpha()
                imagen = pygame.transform.scale(imagen_original, (ancho, alto))
                break
            except (FileNotFoundError, pygame.error):
                continue

        if imagen is None:
            imagen = pygame.Surface((ancho, alto))
            imagen.fill((random.randint(100, 255), 100, 150))

        imagenes.append(imagen)
        imagenes.append(imagen)

    random.shuffle(imagenes)

    # Posiciones centradas
    ancho_total = columnas * ancho + (columnas - 1) * margen
    x_inicial = (constantes.ANCHO - ancho_total) // 2
    alto_total = filas * alto + (filas - 1) * margen
    y_inicial = (constantes.ALTO - alto_total) // 2

    # crear rects y cartas
    idx = 0
    for fila in range(filas):
        for col in range(columnas):
            if idx < len(imagenes):
                x = x_inicial + col * (ancho + margen)
                y = y_inicial + fila * (alto + margen)
                carta = Carta(imagenes[idx], x, y, ancho, alto, volteada)
                cartas.append(carta)
                idx += 1
    return cartas

class MiJuego(GameBase):
    def __init__(self) -> None:
        meta = GameMetadata(
            title="FLIP IT",
            description="Juego de memoria por parejas con distintas dificultades y límite de tiempo opcional.",
            authors=["Gabriel Garanton", "Isabela Paraqueimo", "Cesar Moya"],
            group_number=3,
        )
        super().__init__(meta)
        self._clock = pygame.time.Clock()
        self._font = None
        self._fondo = None

    def on_start(self) -> None:
        """Carga de recursos y prepara la superficie global."""
        self._font = pygame.font.SysFont("arial", 32)
        global fondo_global
        fondo_global = pygame.transform.scale(
            constantes.FONDO, (constantes.ANCHO, constantes.ALTO)
        )
        self._fondo = fondo_global


    def update(self, dt: float) -> None:

        pass

    def draw(self) -> None:
        if self.surface:
            self.surface.fill(COLORS["carbon_oscuro"])

    def run_preview(self) -> None: 

        if not pygame.get_init():
            pygame.init()
        try:
            self.start()
        except Exception as exc:
            pass
        # la clase base normalmente ejecuta on_start tras iniciar
        try:
            self.on_start()
        except Exception:
            pass
        if not hasattr(self, "surface") or self.surface is None:
            self.surface = pygame.display.get_surface()
        ventana = self.surface
        if ventana is None:
            ventana = pygame.display.set_mode((constantes.ANCHO, constantes.ALTO))
            self.surface = ventana
        reloj = self._clock
        running = True

        while running:
            seleccion = ejecutar_menu(ventana, reloj)
            if not seleccion:
                running = False
                break
            dificultad, tiempo = seleccion

            accion = self._ejecutar_partida(ventana, reloj, dificultad, tiempo)
            if accion == "reiniciar":
                continue
            elif accion == "menu":
                continue
            elif accion == "salir":
                running = False
                break
            else:
                running = False
                break

        pygame.quit()

    def _ejecutar_partida(self, ventana, reloj, dificultad, tiempo_segundos=None):
        # limpieza de eventos residuales para evitar que un clic del menú
        # se interprete inmediatamente como QUIT o similar.
        pygame.event.clear()

        # reproducir la música específica del juego durante la partida
        if constantes.SONIDO_ACTIVADO and pygame.mixer.get_init():
            reproducir_musica(constantes.SONIDO_JUEGO)

        # asegurarnos de tener una superficie válida
        ventana = self.surface if hasattr(self, "surface") else None
        if ventana is None:
            ventana = pygame.display.get_surface()
        if ventana is None:
            ventana = pygame.display.set_mode((constantes.ANCHO, constantes.ALTO))
            self.surface = ventana

        if tiempo_segundos is not None:
            tiempo_limite = tiempo_segundos
        else:
            tiempo_limite = None

        config = DIFICULTAD[dificultad]
        num_pares = config["num_pares"]

        cartas = crear_cartas(num_pares, dificultad)

        tiempo_agotado = False
        tiempo_inicio = pygame.time.get_ticks()

        seleccionadas = []
        pares_encontrados = 0
        esperando_verificacion = False
        tiempo_voltear_atras = 0
        esperando_voltear_atras = False

        btn_reiniciar = Boton("Reiniciar", 10, constantes.ALTO - 60, 120, 50)
        btn_menu = Boton("Menú", 140, constantes.ALTO - 60, 120, 50)

        jugando = True
        while jugando:
            dt = reloj.tick(constantes.FPS) / 1000.0
            ventana.blit(self._fondo, (0, 0))

            if tiempo_limite and tiempo_limite > 0:
                tiempo_actual = pygame.time.get_ticks()
                tiempo_transcurrido_sec = (tiempo_actual - tiempo_inicio) / 1000.0
                tiempo_restante = max(0.0, tiempo_limite - tiempo_transcurrido_sec)
                if tiempo_restante <= 0:
                    tiempo_agotado = True
            else:
                tiempo_restante = None

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "salir"

                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    return "menu"

                if (
                    evento.type == pygame.MOUSEBUTTONDOWN
                    and evento.button == 1
                    and not esperando_verificacion
                    and not tiempo_agotado
                ):
                    for carta in cartas:
                        if carta.clic_en_carta(evento.pos) and len(seleccionadas) < 2:
                            play_efecto("carta")
                            carta.iniciar_volteo_mostrar()
                            seleccionadas.append(carta)

                    if btn_reiniciar.clic_en_boton(evento.pos):
                        play_efecto("boton")
                        return "reiniciar"
                    if btn_menu.clic_en_boton(evento.pos):
                        play_efecto("boton")
                        return "menu"

            if len(seleccionadas) == 2 and not esperando_verificacion:
                esperando_verificacion = True
                tiempo_voltear_atras = pygame.time.get_ticks()

            if esperando_verificacion and not esperando_voltear_atras:
                tiempo_actual = pygame.time.get_ticks()
                if tiempo_actual - tiempo_voltear_atras > 800:
                    c1, c2 = seleccionadas
                    if c1.imagen == c2.imagen:
                        play_efecto("correcto")
                        c1.emparejada = True
                        c2.emparejada = True
                        pares_encontrados += 1
                        seleccionadas = []
                        esperando_verificacion = False
                    else:
                        play_efecto("incorrecto")
                        c1.iniciar_volteo_ocultar()
                        c2.iniciar_volteo_ocultar()
                        esperando_voltear_atras = True
            if esperando_voltear_atras and seleccionadas:
                if all(c.animacion_volteo is None for c in seleccionadas):
                    seleccionadas = []
                    esperando_verificacion = False
                    esperando_voltear_atras = False

            for carta in cartas:
                carta.actualizar_volteo(dt)
                carta.dibujar(ventana)

            btn_reiniciar.dibujar(ventana)
            btn_menu.dibujar(ventana)

            fuente = pygame.font.SysFont(None, 28)
            nombre_dif = next(
                k for k, v in DIFICULTAD.items() if v["num_pares"] == num_pares
            )
            texto_dif = fuente.render(f"{nombre_dif.upper()}: {num_pares} pares", True, constantes.AZUL_P)
            ventana.blit(texto_dif, (10, 10))
            texto_prog = fuente.render(
                f"{pares_encontrados}/{num_pares} pares", True, constantes.MORADO_P
            )
            ventana.blit(texto_prog, (10, 40))

            dibujar_barra_tiempo(
                ventana,
                tiempo_restante if tiempo_restante is not None else 0.0,
                tiempo_limite,
                fuente,
            )

            if pares_encontrados == num_pares and not tiempo_agotado:
                accion = self._pantalla_victoria(ventana, reloj, cartas)
                return accion
            elif tiempo_agotado:
                accion = self._pantalla_derrota(ventana, reloj, cartas)
                return accion

            pygame.display.update()

    def _pantalla_victoria(self, ventana, reloj, cartas):
        fuente_victoria = pygame.font.SysFont(None, 60)
        texto_victoria = fuente_victoria.render("¡Nivel completado!", True, constantes.BLANCO)
        texto_rect_v = texto_victoria.get_rect(
            center=(constantes.ANCHO // 2, constantes.ALTO // 2 - 40)
        )
        fuente_sub = pygame.font.SysFont(None, 28)
        texto_sub = fuente_sub.render(
            "R = Reiniciar nivel  |  ESC = Menú  |  Enter = Siguiente nivel",
            True,
            constantes.BLANCO,
        )
        texto_rect_sub = texto_sub.get_rect(
            center=(constantes.ANCHO // 2, constantes.ALTO // 2 + 20)
        )
        btn_reiniciar_nivel = Boton("Reiniciar nivel", 80, constantes.ALTO - 70, 180, 50)
        btn_menu_principal = Boton("Menú principal", 340, constantes.ALTO - 70, 180, 50)
        btn_siguiente_nivel = Boton("Siguiente nivel", 600, constantes.ALTO - 70, 180, 50)
        victoria_activa = True
        while victoria_activa:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "salir"
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        return "reiniciar"
                    if evento.key == pygame.K_ESCAPE:
                        return "menu"
                    if evento.key == pygame.K_RETURN:
                        return "menu"
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if btn_reiniciar_nivel.clic_en_boton(evento.pos):
                        return "reiniciar"
                    if btn_menu_principal.clic_en_boton(evento.pos):
                        return "menu"
                    if btn_siguiente_nivel.clic_en_boton(evento.pos):
                        return "menu"
            ventana.blit(self._fondo, (0, 0))
            for carta in cartas:
                carta.dibujar(ventana)
            overlay_victoria = pygame.Surface((constantes.ANCHO, constantes.ALTO))
            overlay_victoria.fill((100, 150, 255))
            overlay_victoria.set_alpha(120)
            ventana.blit(overlay_victoria, (0, 0))
            ventana.blit(texto_victoria, texto_rect_v)
            ventana.blit(texto_sub, texto_rect_sub)
            btn_reiniciar_nivel.dibujar(ventana)
            btn_menu_principal.dibujar(ventana)
            btn_siguiente_nivel.dibujar(ventana)
            pygame.display.update()
            reloj.tick(60)
        return "menu"

    def _pantalla_derrota(self, ventana, reloj, cartas):
        fuente_derrota = pygame.font.SysFont(None, 60)
        texto_derrota = fuente_derrota.render("Fin del juego", True, constantes.BLANCO)
        texto_rect_d = texto_derrota.get_rect(
            center=(constantes.ANCHO // 2, constantes.ALTO // 2 - 40)
        )
        fuente_sub_d = pygame.font.SysFont(None, 32)
        texto_sub_d = fuente_sub_d.render(
            "Se acabo el tiempo, vuelve a intentarlo", True, constantes.BLANCO
        )
        texto_rect_sub_d = texto_sub_d.get_rect(
            center=(constantes.ANCHO // 2, constantes.ALTO // 2 + 20)
        )
        btn_reiniciar_nivel_d = Boton("Reiniciar nivel", 440, constantes.ALTO - 70, 180, 50)
        btn_menu_principal_d = Boton("Menú principal", 660, constantes.ALTO - 70, 180, 50)
        derrota_activa = True
        while derrota_activa:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "salir"
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        return "reiniciar"
                    if evento.key == pygame.K_ESCAPE:
                        return "menu"
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if btn_reiniciar_nivel_d.clic_en_boton(evento.pos):
                        return "reiniciar"
                    if btn_menu_principal_d.clic_en_boton(evento.pos):
                        return "menu"
            ventana.blit(self._fondo, (0, 0))
            for carta in cartas:
                carta.dibujar(ventana)
            overlay_derrota = pygame.Surface((constantes.ANCHO, constantes.ALTO))
            overlay_derrota.fill(constantes.OVERLAY_FIN_JUEGO)
            overlay_derrota.set_alpha(180)
            ventana.blit(overlay_derrota, (0, 0))
            ventana.blit(texto_derrota, texto_rect_d)
            ventana.blit(texto_sub_d, texto_rect_sub_d)
            btn_reiniciar_nivel_d.dibujar(ventana)
            btn_menu_principal_d.dibujar(ventana)
            pygame.display.update()
            reloj.tick(60)
        return "menu"

