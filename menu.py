import pygame
import sys
import constantes
from constantes import DIFICULTAD
from instrucciones import ejecutar_instrucciones
from audio import reproducir_musica, play_efecto

def ejecutar_menu(ventana, reloj):

    pygame.display.set_caption("FLIP IT (Version 4)")

    # asegúrate de tener música de fondo activa desde el inicio del menú
    if constantes.SONIDO_ACTIVADO:
        reproducir_musica(constantes.MUSICA_FONDO)

    # si pasamos del menú a un nivel, el mismo fondo musical debe continuar;
    # reproducir_musica no detiene la música si ya está sonando, por lo que
    # no es necesario volver a llamarlo dentro de _ejecutar_partida.

    fondo = pygame.transform.scale(
        constantes.FONDO,
        (constantes.ANCHO, constantes.ALTO)
    )


    ESTADO_MENU = "menu"
    ESTADO_DIFICULTAD = "dificultad"
    ESTADO_TIEMPO = "tiempo"
    ESTADO_PERSONALIZADO = "personalizado"
    ESTADO_CONFIG = "config"

    estado = ESTADO_MENU
    dificultad_elegida = None
    input_segundos = ""
    arrastrando_slider = None  # 0=general, 1=musica, 2=efectos
    config_seccion = "sonido"

    slider_w, slider_h = 400, 22
    slider_x = (constantes.ANCHO - slider_w) // 2
    rect_slider_general = pygame.Rect(slider_x, 220, slider_w, slider_h)
    rect_slider_musica = pygame.Rect(slider_x, 320, slider_w, slider_h)
    rect_slider_efectos = pygame.Rect(slider_x, 420, slider_w, slider_h)
    rect_boton_sonido = pygame.Rect(constantes.ANCHO // 2 - 100, 480, 200, 44)
    temas_lista = list(constantes.IMG_TEMAS.keys())
    rects_temas = [(clave, pygame.Rect(constantes.ANCHO // 2 - 160, 220 + idx * 52 - 22, 320, 44))
                   for idx, clave in enumerate(temas_lista)]
    ancho_tab, alto_tab = 250, 44
    sep_tab = 12
    total_tabs = ancho_tab * 3 + sep_tab * 2
    x_tabs = (constantes.ANCHO - total_tabs) // 2
    y_tabs = 115
    rect_btn_sonido = pygame.Rect(x_tabs, y_tabs - alto_tab // 2, ancho_tab, alto_tab)
    rect_btn_pantalla = pygame.Rect(x_tabs + ancho_tab + sep_tab, y_tabs - alto_tab // 2, ancho_tab, alto_tab)
    rect_btn_temas = pygame.Rect(x_tabs + (ancho_tab + sep_tab) * 2, y_tabs - alto_tab // 2, ancho_tab, alto_tab)

    def dibujar_texto(texto, fuente, color, x, y):
        superficie = fuente.render(texto, True, color)
        rect = superficie.get_rect(center=(x, y))
        ventana.blit(superficie, rect)
        return rect
    

    def dibujar_boton_cuadro(texto, x_centro, y_centro, ancho=320, alto=50):
        rect = pygame.Rect(x_centro - ancho // 2, y_centro - alto // 2, ancho, alto)
        pygame.draw.rect(ventana, constantes.AZUL_OSCURO, rect)
        pygame.draw.rect(ventana, constantes.BLANCO, rect, 2)
        surf = constantes.fuente_menu.render(texto, True, constantes.BLANCO)
        r_texto = surf.get_rect(center=rect.center)
        ventana.blit(surf, r_texto)
        return rect


    while True:

        reloj.tick(constantes.FPS)
        ventana.blit(fondo, (0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return None

            if evento.type == pygame.KEYDOWN and estado == ESTADO_PERSONALIZADO:
                if evento.key == pygame.K_RETURN and input_segundos.strip():
                    try:
                        seg = int(input_segundos.strip())
                        if 10 <= seg <= 3600:
                            return (dificultad_elegida, seg)
                    except ValueError:
                        pass
                elif evento.key == pygame.K_BACKSPACE:
                    input_segundos = input_segundos[:-1]
                elif evento.unicode.isdigit() and len(input_segundos) < 4:
                    input_segundos += evento.unicode

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado == ESTADO_MENU:
                    if boton_dificultad.collidepoint(evento.pos):
                        play_efecto("boton")
                        estado = ESTADO_DIFICULTAD
                        # limpiar cualquier evento pendiente antes de salir
                        pygame.event.clear()
                    elif boton_config.collidepoint(evento.pos):
                        play_efecto("boton")
                        estado = ESTADO_CONFIG
                        config_seccion = "sonido"
                    elif boton_instrucciones.collidepoint(evento.pos):
                        play_efecto("boton")
                        reproducir_musica(constantes.SONIDO_INSTRUCCIONES)
                        if not constantes.SONIDO_ACTIVADO and pygame.mixer.get_init():
                            pygame.mixer.music.pause()
                        ejecutar_instrucciones(ventana, reloj)
                        if constantes.SONIDO_ACTIVADO:
                            reproducir_musica(constantes.MUSICA_FONDO)
                        else:
                            pygame.mixer.music.stop()
                    elif boton_salir.collidepoint(evento.pos):
                        play_efecto("boton")
                        return None

                elif estado == ESTADO_DIFICULTAD:
                    if boton_facil.collidepoint(evento.pos):
                        play_efecto("boton")
                        dificultad_elegida = "facil"
                        estado = ESTADO_TIEMPO
                    elif boton_medio.collidepoint(evento.pos):
                        play_efecto("boton")
                        dificultad_elegida = "medio"
                        estado = ESTADO_TIEMPO
                    elif boton_dificil.collidepoint(evento.pos):
                        play_efecto("boton")
                        dificultad_elegida = "dificil"
                        estado = ESTADO_TIEMPO
                    elif boton_volver.collidepoint(evento.pos):
                        play_efecto("boton")
                        estado = ESTADO_MENU

                elif estado == ESTADO_TIEMPO:
                    if boton_sin_tiempo.collidepoint(evento.pos):
                        play_efecto("boton")
                        return (dificultad_elegida, None)
                    elif boton_60.collidepoint(evento.pos):
                        play_efecto("boton")
                        return (dificultad_elegida, 60)
                    elif boton_120.collidepoint(evento.pos):
                        play_efecto("boton")
                        return (dificultad_elegida, 120)
                    elif boton_180.collidepoint(evento.pos):
                        play_efecto("boton")
                        return (dificultad_elegida, 180)
                    elif boton_personalizado.collidepoint(evento.pos):
                        play_efecto("boton")
                        input_segundos = ""
                        estado = ESTADO_PERSONALIZADO
                    elif boton_volver.collidepoint(evento.pos):
                        play_efecto("boton")
                        estado = ESTADO_DIFICULTAD

                elif estado == ESTADO_PERSONALIZADO:
                    if boton_confirmar_tiempo.collidepoint(evento.pos) and input_segundos.strip():
                        play_efecto("boton")
                        try:
                            seg = int(input_segundos.strip())
                            if 10 <= seg <= 3600:
                                return (dificultad_elegida, seg)
                        except ValueError:
                            pass
                    elif boton_volver_tiempo.collidepoint(evento.pos):
                        play_efecto("boton")
                        estado = ESTADO_TIEMPO

                elif estado == ESTADO_CONFIG:
                    if boton_volver_config.collidepoint(evento.pos):
                        play_efecto("boton")
                        estado = ESTADO_MENU
                    elif rect_btn_sonido.collidepoint(evento.pos):
                        play_efecto("boton")
                        config_seccion = "sonido"
                    elif rect_btn_pantalla.collidepoint(evento.pos):
                        play_efecto("boton")
                        config_seccion = "pantalla"
                    elif rect_btn_temas.collidepoint(evento.pos):
                        play_efecto("boton")
                        config_seccion = "temas"
                    elif rect_boton_sonido.collidepoint(evento.pos) and config_seccion == "sonido":
                        constantes.SONIDO_ACTIVADO = not constantes.SONIDO_ACTIVADO
                        if pygame.mixer.get_init():
                            if constantes.SONIDO_ACTIVADO:
                                reproducir_musica(constantes.MUSICA_FONDO)
                            else:
                                pygame.mixer.music.pause()
                    elif config_seccion == "temas" and evento.pos[1] >= 220:
                        for i, (clave, r) in enumerate(rects_temas):
                            if r.collidepoint(evento.pos):
                                play_efecto("boton")
                                constantes.TEMA_CARTAS = clave
                                break
                    else:
                        for i, r in enumerate([rect_slider_general, rect_slider_musica, rect_slider_efectos]):
                            if r.collidepoint(evento.pos) and config_seccion == "sonido":
                                arrastrando_slider = i
                                t = max(0, min(1, (evento.pos[0] - r.x) / r.width))
                                if i == 0:
                                    constantes.VOLUMEN_GENERAL = t
                                elif i == 1:
                                    constantes.VOLUMEN_MUSICA = t
                                else:
                                    constantes.VOLUMEN_EFECTOS = t
                                from audio import aplicar_volumen_musica
                                aplicar_volumen_musica()
                                break

            if evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    arrastrando_slider = None

            if evento.type == pygame.MOUSEMOTION and arrastrando_slider is not None and estado == ESTADO_CONFIG:
                rects = [rect_slider_general, rect_slider_musica, rect_slider_efectos]
                r = rects[arrastrando_slider]
                t = max(0, min(1, (evento.pos[0] - r.x) / r.width))
                if arrastrando_slider == 0:
                    constantes.VOLUMEN_GENERAL = t
                elif arrastrando_slider == 1:
                    constantes.VOLUMEN_MUSICA = t
                else:
                    constantes.VOLUMEN_EFECTOS = t
                from audio import aplicar_volumen_musica
                aplicar_volumen_musica()

# COMIENZO DE LA UI
        if estado == ESTADO_MENU:

            dibujar_texto("FLIP IT",
                          constantes.fuente_titulo,
                          constantes.MORADO_P,
                          constantes.ANCHO // 2, 120)

            boton_dificultad = dibujar_boton_cuadro("Iniciar Juego", constantes.ANCHO // 2, 260)
            boton_instrucciones = dibujar_boton_cuadro("Instrucciones", constantes.ANCHO // 2, 330)
            boton_config = dibujar_boton_cuadro("Configuración", constantes.ANCHO // 2, 400)
            boton_salir = dibujar_boton_cuadro("Salir", constantes.ANCHO // 2, 470)

        elif estado == ESTADO_CONFIG:
            dibujar_texto("CONFIGURACIÓN",
                          constantes.fuente_titulo,
                          constantes.MORADO_P,
                          constantes.ANCHO // 2, 55)
            fuente_slider = pygame.font.SysFont("arial", 26)
            for rect, label, sel in [(rect_btn_sonido, "Sonido", config_seccion == "sonido"),
                                     (rect_btn_pantalla, "Pantalla", config_seccion == "pantalla"),
                                     (rect_btn_temas, "Temas de cartas", config_seccion == "temas")]:
                c = constantes.AZUL_P if sel else constantes.AZUL_OSCURO
                pygame.draw.rect(ventana, c, rect)
                pygame.draw.rect(ventana, constantes.BLANCO, rect, 2)
                s = fuente_slider.render(label, True, constantes.BLANCO)
                ventana.blit(s, s.get_rect(center=rect.center))

            if config_seccion == "sonido":
                dibujar_texto("Volumen general", fuente_slider, constantes.BLANCO, constantes.ANCHO // 2, 195)
                pygame.draw.rect(ventana, (60, 60, 80), rect_slider_general)
                pygame.draw.rect(ventana, constantes.AZUL_P,
                                 (rect_slider_general.x, rect_slider_general.y,
                                  int(rect_slider_general.width * constantes.VOLUMEN_GENERAL), rect_slider_general.height))
                pygame.draw.rect(ventana, constantes.BLANCO, rect_slider_general, 2)
                dibujar_texto(f"{int(constantes.VOLUMEN_GENERAL * 100)}%", fuente_slider, constantes.BLANCO,
                              rect_slider_general.right + 50, rect_slider_general.centery)
                dibujar_texto("Música / fondo", fuente_slider, constantes.BLANCO, constantes.ANCHO // 2, 295)
                pygame.draw.rect(ventana, (60, 60, 80), rect_slider_musica)
                pygame.draw.rect(ventana, constantes.AZUL_P,
                                 (rect_slider_musica.x, rect_slider_musica.y,
                                  int(rect_slider_musica.width * constantes.VOLUMEN_MUSICA), rect_slider_musica.height))
                pygame.draw.rect(ventana, constantes.BLANCO, rect_slider_musica, 2)
                dibujar_texto(f"{int(constantes.VOLUMEN_MUSICA * 100)}%", fuente_slider, constantes.BLANCO,
                              rect_slider_musica.right + 50, rect_slider_musica.centery)
                dibujar_texto("Efectos", fuente_slider, constantes.BLANCO, constantes.ANCHO // 2, 395)
                pygame.draw.rect(ventana, (60, 60, 80), rect_slider_efectos)
                pygame.draw.rect(ventana, constantes.AZUL_P,
                                 (rect_slider_efectos.x, rect_slider_efectos.y,
                                  int(rect_slider_efectos.width * constantes.VOLUMEN_EFECTOS), rect_slider_efectos.height))
                pygame.draw.rect(ventana, constantes.BLANCO, rect_slider_efectos, 2)
                dibujar_texto(f"{int(constantes.VOLUMEN_EFECTOS * 100)}%", fuente_slider, constantes.BLANCO,
                              rect_slider_efectos.right + 50, rect_slider_efectos.centery)
                color_sonido = constantes.VERDE_PASTEL if constantes.SONIDO_ACTIVADO else constantes.ROJO_PASTEL
                pygame.draw.rect(ventana, color_sonido, rect_boton_sonido)
                pygame.draw.rect(ventana, constantes.BLANCO, rect_boton_sonido, 2)
                texto_sonido = f"Sonido: {'ON' if constantes.SONIDO_ACTIVADO else 'OFF'}"
                surf_son = fuente_slider.render(texto_sonido, True, constantes.BLANCO)
                ventana.blit(surf_son, surf_son.get_rect(center=rect_boton_sonido.center))
            elif config_seccion == "pantalla":
                dibujar_texto("AQUI PARA DESPUES QUE ME SIENTO CANSADO XD", fuente_slider, constantes.BLANCO,
                              constantes.ANCHO // 2, 280)
            else:
                dibujar_texto("Tema de las cartas", fuente_slider, constantes.BLANCO, constantes.ANCHO // 2, 165)
                for clave, r in rects_temas:
                    sel = constantes.TEMA_CARTAS == clave
                    pygame.draw.rect(ventana, constantes.AZUL_P if sel else constantes.AZUL_OSCURO, r)
                    pygame.draw.rect(ventana, constantes.BLANCO, r, 2)
                    s = fuente_slider.render(clave.capitalize(), True, constantes.BLANCO)
                    ventana.blit(s, s.get_rect(center=r.center))

            boton_volver_config = dibujar_boton_cuadro("Volver", constantes.ANCHO // 2, 560)

        elif estado == ESTADO_DIFICULTAD:

            dibujar_texto("SELECCIONA DIFICULTAD",
                          constantes.fuente_titulo,
                          constantes.MORADO_P,
                          constantes.ANCHO // 2, 100)

            boton_facil = dibujar_texto("Fácil (6 pares)",
                                        constantes.fuente_menu,
                                        constantes.AZUL_P,
                                        constantes.ANCHO // 2, 200)

            boton_medio = dibujar_texto("Medio (8 pares)",
                                        constantes.fuente_menu,
                                        constantes.AZUL_P,
                                        constantes.ANCHO // 2, 260)

            boton_dificil = dibujar_texto("Difícil (12 pares)",
                                          constantes.fuente_menu,
                                          constantes.AZUL_P,
                                          constantes.ANCHO // 2, 320)

            boton_volver = dibujar_texto("Volver",
                                         constantes.fuente_menu,
                                         constantes.AZUL_P,
                                         constantes.ANCHO // 2, 450)

        elif estado == ESTADO_TIEMPO:
            dibujar_texto("ELIGE EL TIEMPO",
                          constantes.fuente_titulo,
                          constantes.MORADO_P,
                          constantes.ANCHO // 2, 80)
            boton_sin_tiempo = dibujar_texto("Sin tiempo",
                                             constantes.fuente_menu,
                                             constantes.AZUL_P,
                                             constantes.ANCHO // 2, 180)
            boton_60 = dibujar_texto("60 segundos",
                                     constantes.fuente_menu,
                                     constantes.AZUL_P,
                                     constantes.ANCHO // 2, 240)
            boton_120 = dibujar_texto("120 segundos",
                                      constantes.fuente_menu,
                                      constantes.AZUL_P,
                                      constantes.ANCHO // 2, 300)
            boton_180 = dibujar_texto("180 segundos",
                                      constantes.fuente_menu,
                                      constantes.AZUL_P,
                                      constantes.ANCHO // 2, 360)
            boton_personalizado = dibujar_texto("Personalizado",
                                                constantes.fuente_menu,
                                                constantes.AZUL_P,
                                                constantes.ANCHO // 2, 420)
            boton_volver = dibujar_texto("Volver",
                                         constantes.fuente_menu,
                                         constantes.AZUL_P,
                                         constantes.ANCHO // 2, 480)

        elif estado == ESTADO_PERSONALIZADO:
            dibujar_texto("TIEMPO PERSONALIZADO (segundos)",
                          constantes.fuente_titulo,
                          constantes.MORADO_P,
                          constantes.ANCHO // 2, 120)
            texto_input = input_segundos if input_segundos else "0"
            rect_input = dibujar_texto(f"Segundos: {texto_input}",
                                       constantes.fuente_menu,
                                       constantes.BLANCO,
                                       constantes.ANCHO // 2, 260)
            dibujar_texto("Mín: 10 — Máx: 3600. Enter o clic en Confirmar.",
                          constantes.fuente_menu,
                          constantes.AZUL_P,
                          constantes.ANCHO // 2, 320)
            boton_confirmar_tiempo = dibujar_texto("Confirmar",
                                                   constantes.fuente_menu,
                                                   constantes.AZUL_P,
                                                   constantes.ANCHO // 2, 380)
            boton_volver_tiempo = dibujar_texto("Volver",
                                                constantes.fuente_menu,
                                                constantes.AZUL_P,
                                                constantes.ANCHO // 2, 440)

        pygame.display.update()
