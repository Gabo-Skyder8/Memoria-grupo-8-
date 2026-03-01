import random
import math
import pygame
import sys
from pathlib import Path
from enfocate import GameBase, GameMetadata, COLORS

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
        img_ori = constantes.get_carta_volteada()
        volteada = pygame.transform.scale(img_ori, (ancho, alto))
    except (FileNotFoundError, pygame.error):
        volteada = pygame.Surface((ancho, alto))
        volteada.fill(constantes.MORADO_P)

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
            description="Juego de memoria excepcional",
            authors=["Gabriel Garanton", "Isabela Paraqueimo", "Cesar Moya"],
            group_number=9,
        )
        super().__init__(meta)
        self._clock = pygame.time.Clock()
        self._font = None
        self._fondo = None
        self._mouse_presionado_antes = False

    def on_start(self) -> None:
        """Carga de recursos y prepara la superficie global."""
        self._font = pygame.font.SysFont("arial", 32)
        fondo_global = pygame.transform.scale(
            constantes.get_fondo(), (constantes.ANCHO, constantes.ALTO)
        )
        self._fondo = fondo_global
        
        # Inicializar estado del juego
        self._game_state = "menu"


    def update(self, dt: float) -> None: 
        if not hasattr(self, '_game_state'):
            return
            
        if self._game_state == "menu":
            self._update_menu(dt)
        elif self._game_state == "playing":
            self._update_game(dt)
        elif self._game_state in ("victory", "defeat"):
            self._update_endgame(dt)

    def _update_menu(self, dt):
        if not hasattr(self, '_menu_result'):
            # Si ejecutamos desde launcher, mostrar menú del juego
            if hasattr(self, 'surface') and self.surface:
                self._menu_result = ejecutar_menu(self.surface, self._clock)
            else:
                # Ejecución independiente - mostrar menú
                self._menu_result = ejecutar_menu(self.surface, self._clock)
        
        if hasattr(self, '_menu_result') and self._menu_result:
            dificultad, tiempo = self._menu_result
            self._start_game(dificultad, tiempo)
            self._game_state = "playing"
        elif hasattr(self, '_menu_result') and not self._menu_result:
            self._stop_context()

    def _update_game(self, dt):
        if not hasattr(self, '_game_initialized') or not self._game_initialized:
            return
            
        accion = self._handle_game_events()
    
        if accion == "reiniciar":
            self._start_game(self._current_dificultad, self._tiempo_limite)
            return 
        
        elif accion == "ir_al_menu":
            # Limpieza total para que el Launcher detecte el cambio de estado
            self._game_initialized = False
            self._game_state = "menu"
            if hasattr(self, '_menu_result'): 
                delattr(self, '_menu_result') 
            if hasattr(self, '_btn_victory_menu'):
                delattr(self, '_btn_victory_menu')
            if hasattr(self, '_btn_defeat_menu'):
                delattr(self, '_btn_defeat_menu')
            return

        self._update_game_logic(dt)
        self._draw_game()

    def _start_game(self, dificultad, tiempo_segundos=None):
        pygame.event.clear()
        
        if constantes.SONIDO_ACTIVADO and pygame.mixer.get_init():
            from audio import reproducir_musica
            reproducir_musica(constantes.SONIDO_JUEGO)
        
        config = DIFICULTAD[dificultad]
        self._num_pares = config["num_pares"]
        self._cartas = crear_cartas(self._num_pares, dificultad)
        
        self._tiempo_limite = tiempo_segundos
        self._tiempo_inicio = pygame.time.get_ticks()
        self._tiempo_agotado = False
        
        self._seleccionadas = []
        self._pares_encontrados = 0
        self._esperando_verificacion = False
        self._tiempo_voltear_atras = 0
        self._esperando_voltear_atras = False
        
        self._btn_menu = Boton("Menú", 10, constantes.ALTO - 60, 120, 50)
        
        self._game_initialized = True
    
    def _handle_game_events(self):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        clic_izquierdo = mouse_buttons[0]
    
        resultado = None # Cambiamos False por None para mayor claridad

        if clic_izquierdo and not self._mouse_presionado_antes:
            # 1. BOTÓN MENÚ
            if hasattr(self, '_btn_menu') and self._btn_menu.clic_en_boton(mouse_pos):
                from audio import play_efecto
                play_efecto("boton")
                self._mouse_presionado_antes = True
                return "ir_al_menu" # Enviamos una señal clara

            # 3. CLIC EN CARTAS
            elif not self._esperando_verificacion and not self._tiempo_agotado:
                for carta in self._cartas:
                    if carta.clic_en_carta(mouse_pos) and len(self._seleccionadas) < 2:
                        from audio import play_efecto
                        play_efecto("carta")
                        carta.iniciar_volteo_mostrar()
                        self._seleccionadas.append(carta)
                        break

        self._mouse_presionado_antes = clic_izquierdo
        return resultado
    
    def _update_endgame(self, dt):
        """Maneja eventos en pantallas de victoria y derrota"""
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        clic_izquierdo = mouse_buttons[0]
        
        # Manejar clic en botón de menú
        if clic_izquierdo and not self._mouse_presionado_antes:
            if self._game_state == "victory" and hasattr(self, '_btn_victory_menu'):
                if self._btn_victory_menu.clic_en_boton(mouse_pos):
                    from audio import play_efecto
                    play_efecto("boton")
                    self._mouse_presionado_antes = True
                    self._go_to_menu()
                    return
            elif self._game_state == "defeat" and hasattr(self, '_btn_defeat_menu'):
                if self._btn_defeat_menu.clic_en_boton(mouse_pos):
                    from audio import play_efecto
                    play_efecto("boton")
                    self._mouse_presionado_antes = True
                    self._go_to_menu()
                    return
        
        # Manejar tecla ESC
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._stop_context()
                return
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self._go_to_menu()
                    return
        
        self._mouse_presionado_antes = clic_izquierdo
    
    def _go_to_menu(self):
        """Vuelve al menú principal del juego"""
        self._game_initialized = False
        self._game_state = "menu"
        if hasattr(self, '_menu_result'): 
            delattr(self, '_menu_result')
        # Limpiar botones de pantallas finales
        if hasattr(self, '_btn_victory_menu'):
            delattr(self, '_btn_victory_menu')
        if hasattr(self, '_btn_defeat_menu'):
            delattr(self, '_btn_defeat_menu')
    
    def _update_game_logic(self, dt):
        if self._tiempo_limite and self._tiempo_limite > 0:
            tiempo_actual = pygame.time.get_ticks()
            tiempo_transcurrido_sec = (tiempo_actual - self._tiempo_inicio) / 1000.0
            self._tiempo_restante = max(0.0, self._tiempo_limite - tiempo_transcurrido_sec)
            if self._tiempo_restante <= 0:
                self._tiempo_agotado = True
        else:
            self._tiempo_restante = None

        if len(self._seleccionadas) == 2 and not self._esperando_verificacion:
            self._esperando_verificacion = True
            self._tiempo_voltear_atras = pygame.time.get_ticks()

        if self._esperando_verificacion and not self._esperando_voltear_atras:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - self._tiempo_voltear_atras > 800:
                c1, c2 = self._seleccionadas
                if c1.imagen == c2.imagen:
                    from audio import play_efecto
                    play_efecto("correcto")
                    c1.emparejada = True
                    c2.emparejada = True
                    self._pares_encontrados += 1
                    self._seleccionadas = []
                    self._esperando_verificacion = False
                else:
                    from audio import play_efecto
                    play_efecto("incorrecto")
                    c1.iniciar_volteo_ocultar()
                    c2.iniciar_volteo_ocultar()
                    self._esperando_voltear_atras = True
                    
        if self._esperando_voltear_atras and self._seleccionadas:
            if all(c.animacion_volteo is None for c in self._seleccionadas):
                self._seleccionadas = []
                self._esperando_verificacion = False
                self._esperando_voltear_atras = False

        for carta in self._cartas:
            carta.actualizar_volteo(dt)

    def _draw_game(self, surface=None):
        # Usar la superficie proporcionada o buscar una disponible
        if surface:
            target_surface = surface
        elif hasattr(self, '_ventana') and self._ventana:
            target_surface = self._ventana
        elif hasattr(self, 'surface') and self.surface:
            target_surface = self.surface
        else:
            # No hay superficie disponible, no dibujar
            return
        
        if hasattr(self, '_fondo') and self._fondo:
            target_surface.blit(self._fondo, (0, 0))
        else:
            target_surface.fill((50, 50, 50))

        for carta in self._cartas:
            carta.dibujar(target_surface)

        if hasattr(self, '_btn_menu'):
            self._btn_menu.dibujar(target_surface)

        fuente = pygame.font.SysFont(None, 28)
        if hasattr(self, '_num_pares'):
            nombre_dif = next(k for k, v in DIFICULTAD.items() if v["num_pares"] == self._num_pares)
            texto_dif = fuente.render(f"{nombre_dif.upper()}: {self._num_pares} pares", True, constantes.AZUL_P)
            target_surface.blit(texto_dif, (10, 10))
            texto_prog = fuente.render(f"{self._pares_encontrados}/{self._num_pares} pares", True, constantes.MORADO_P)
            target_surface.blit(texto_prog, (10, 40))

            dibujar_barra_tiempo(
                target_surface,
                self._tiempo_restante if hasattr(self, '_tiempo_restante') and self._tiempo_restante is not None else 0.0,
                self._tiempo_limite,
                fuente,
            )

            if self._pares_encontrados == self._num_pares and not self._tiempo_agotado:
                self._game_state = "victory"
            elif self._tiempo_agotado:
                self._game_state = "defeat"

    def _draw_game_surface(self, surface):
        """Método wrapper para dibujar el juego en una superficie específica"""
        self._draw_game(surface)

    def draw(self) -> None:
        if self.surface:
            if hasattr(self, '_game_state') and self._game_state == "playing":
                self._draw_game()
            elif hasattr(self, '_game_state') and self._game_state == "menu":
                # Dibujar menú cuando se ejecuta desde launcher
                self.surface.fill(COLORS["carbon_oscuro"])
            elif hasattr(self, '_game_state') and self._game_state == "victory":
                self._draw_victory_screen()
            elif hasattr(self, '_game_state') and self._game_state == "defeat":
                self._draw_defeat_screen()
            else:
                self.surface.fill(COLORS["carbon_oscuro"])

    def _draw_victory_screen_surface(self, surface):
        """Versión para ejecución independiente"""
        self._draw_victory_screen()
        if hasattr(self, '_temp_surface'):
            surface.blit(self._temp_surface, (0, 0))

    def _draw_defeat_screen_surface(self, surface):
        """Versión para ejecución independiente"""
        self._draw_defeat_screen()
        if hasattr(self, '_temp_surface'):
            surface.blit(self._temp_surface, (0, 0))

    def _draw_victory_screen(self):

        self._temp_surface = pygame.Surface((constantes.ANCHO, constantes.ALTO))
        
        if hasattr(self, '_fondo') and self._fondo:
            self._temp_surface.blit(self._fondo, (0, 0))
        else:
            self._temp_surface.fill((50, 50, 50))
        
        # Dibujar cartas
        if hasattr(self, '_cartas'):
            for carta in self._cartas:
                carta.dibujar(self._temp_surface)
        
        # Overlay de victoria
        overlay_victoria = pygame.Surface((constantes.ANCHO, constantes.ALTO))
        overlay_victoria.fill((100, 150, 255))
        overlay_victoria.set_alpha(120)
        self._temp_surface.blit(overlay_victoria, (0, 0))
        
        fuente_victoria = pygame.font.SysFont(None, 60)
        texto_victoria = fuente_victoria.render("¡Nivel completado!", True, constantes.BLANCO)
        texto_rect_v = texto_victoria.get_rect(center=(constantes.ANCHO//2, constantes.ALTO//2 - 60))
        self._temp_surface.blit(texto_victoria, texto_rect_v)
        
        # Botón para ir al menú
        if not hasattr(self, '_btn_victory_menu'):
            self._btn_victory_menu = Boton("Menú", constantes.ANCHO//2 - 60, constantes.ALTO//2 + 20, 120, 50)
        self._btn_victory_menu.dibujar(self._temp_surface)
        
        # Dibujar en self.surface para el launcher
        if hasattr(self, 'surface') and self.surface:
            self.surface.blit(self._temp_surface, (0, 0))

    def _draw_defeat_screen(self):
        # Crear superficie temporal
        self._temp_surface = pygame.Surface((constantes.ANCHO, constantes.ALTO))
        
        if hasattr(self, '_fondo') and self._fondo:
            self._temp_surface.blit(self._fondo, (0, 0))
        else:
            self._temp_surface.fill((50, 50, 50))
        
        # Dibujar cartas
        if hasattr(self, '_cartas'):
            for carta in self._cartas:
                carta.dibujar(self._temp_surface)
        
        # Overlay de derrota
        overlay_derrota = pygame.Surface((constantes.ANCHO, constantes.ALTO))
        overlay_derrota.fill((120, 60, 80))
        overlay_derrota.set_alpha(180)
        self._temp_surface.blit(overlay_derrota, (0, 0))
        
        fuente_derrota = pygame.font.SysFont(None, 60)
        texto_derrota = fuente_derrota.render("Fin del juego", True, constantes.BLANCO)
        texto_rect_d = texto_derrota.get_rect(center=(constantes.ANCHO//2, constantes.ALTO//2 - 60))
        self._temp_surface.blit(texto_derrota, texto_rect_d)
        
        fuente_sub_d = pygame.font.SysFont(None, 28)
        texto_sub_d = fuente_sub_d.render("Se acabó el tiempo, vuelve a intentarlo", True, constantes.BLANCO)
        texto_rect_sub_d = texto_sub_d.get_rect(center=(constantes.ANCHO//2, constantes.ALTO//2 - 10))
        self._temp_surface.blit(texto_sub_d, texto_rect_sub_d)
        
        # Botón para ir al menú
        if not hasattr(self, '_btn_defeat_menu'):
            self._btn_defeat_menu = Boton("Menú", constantes.ANCHO//2 - 60, constantes.ALTO//2 + 40, 120, 50)
        self._btn_defeat_menu.dibujar(self._temp_surface)
               
        # Dibujar en self.surface para el launcher
        if hasattr(self, 'surface') and self.surface:
            self.surface.blit(self._temp_surface, (0, 0))

    def run_preview(self) -> None: 
        """Método para ejecución independiente - no modificar para integración con launcher."""
        if not pygame.get_init():
            pygame.init()
        
        # Create display surface first
        ventana = pygame.display.set_mode((constantes.ANCHO, constantes.ALTO))
        
        # Store the window reference for internal use
        self._ventana = ventana
        
        try:
            self.start()
        except Exception as exc:
            pass
        # la clase base normalmente ejecuta on_start tras iniciar
        try:
            self.on_start()
        except Exception:
            pass
        
        # Forzar la superficie para modo independiente
        self._ventana = ventana
        # Usar _ventana en lugar de intentar modificar surface
        
        reloj = self._clock
        running = True

        while running:
            seleccion = ejecutar_menu(ventana, reloj)
            if not seleccion:
                running = False
                break
            dificultad, tiempo = seleccion

            # Iniciar el juego usando el nuevo sistema
            self._start_game(dificultad, tiempo)
            self._game_state = "playing"
            
            # Loop del juego para ejecución independiente
            while self._game_state == "playing":
                dt = self._clock.tick(constantes.FPS) / 1000.0
                self._update_game(dt)
                self._draw_game_surface(ventana)
                pygame.display.update()
                
                # Manejar estados de victoria/derrota
                if hasattr(self, '_game_state'):
                    if self._game_state == "victory":
                        self._draw_victory_screen_surface(ventana)
                        pygame.display.update()
                        # Esperar input para reiniciar o menú
                        waiting = True
                        while waiting:
                            for evento in pygame.event.get():
                                if evento.type == pygame.QUIT:
                                    waiting = False
                                    running = False
                                    break
                                elif evento.type == pygame.KEYDOWN:
                                    if evento.key == pygame.K_ESCAPE:
                                        running = False
                                        waiting = False
                                        break
                    elif self._game_state == "defeat":
                        self._draw_defeat_screen_surface(ventana)
                        pygame.display.update()
                        # Esperar input para reiniciar o menú
                        waiting = True
                        while waiting:
                            for evento in pygame.event.get():
                                if evento.type == pygame.QUIT:
                                    waiting = False
                                    running = False
                                    break
                                elif evento.type == pygame.KEYDOWN:
                                    if evento.key == pygame.K_ESCAPE:
                                        running = False
                                        waiting = False
                                        break

        pygame.quit()

