import pygame
import constantes

TEXTO_INSTRUCCIONES = [
    "BIENVENIDOS AL JUEGO DE MEMORIA :D",
    "Este proyecto de objeto y abstraccion de Datos se esta haciendo por:",
    "",
    "Gabriel Garanton",
    "Isabela Paraqueimo",
    "Cesar Moya"
    "",
    "",
    "¿CÓMO JUGAR?",
    "",
    "El objetivo es encontrar todas las parejas de cartas. Asi de simple",
    "",
    "Haz clic en una carta para voltearla. Luego elige otra.",
    "Si las dos son iguales, se quedan descubiertas.",
    "Si no, se dan la vuelta otra vez.",
    "",
    "Cuando encuentres todas las parejas, ¡ganas!",
    "Si se acaba el tiempo antes, puedes volver a intentarlo.",
    "",
    "SUUUERTEE"
    ]

# Diseno
MARGEN = 40
ANCHO_AREA_TEXTO = constantes.ANCHO - 2 * MARGEN - 24  
ALTO_AREA_TEXTO = constantes.ALTO - 180 
Y_TITULO = 50
Y_AREA = 120
ALTO_BOTON = 60
ANCHO_BARRA = 16
MARGEN_BARRA = 8
PASO_RUEDA = 50
FUENTE_TITULO_SIZE = 48
FUENTE_TEXTO_SIZE = 22
COLOR_FONDO_BARRA = (60, 60, 80)
COLOR_THUMB = (132, 182, 244)
COLOR_THUMB_BORDE = (180, 210, 255)
#Fondo oscuro
OVERLAY_OSCURO = (20, 22, 35, 200)


def _crear_superficie_texto(fuente_titulo, fuente_texto):
    lineas_rendered = []
    for linea in TEXTO_INSTRUCCIONES:
        if linea.startswith("BIENVENIDOS"):
            surf = fuente_titulo.render(linea, True, constantes.MORADO_P)
        elif linea.strip():
            surf = fuente_texto.render(linea, True, constantes.BLANCO)
        else:
            surf = fuente_texto.render(" ", True, constantes.BLANCO)
        lineas_rendered.append(surf)
    espaciado = 6
    y = 0
    for surf in lineas_rendered:
        y += surf.get_height() + espaciado
    altura_total = y + 40
    ancho = ANCHO_AREA_TEXTO
    superficie = pygame.Surface((ancho, altura_total), pygame.SRCALPHA)
    y = 0
    for surf in lineas_rendered:
        superficie.blit(surf, (0, y))
        y += surf.get_height() + espaciado
    return superficie, altura_total


def ejecutar_instrucciones(ventana, reloj):
    fondo = pygame.transform.scale(constantes.FONDO, (constantes.ANCHO, constantes.ALTO))
    fuente_titulo = pygame.font.SysFont("arial", FUENTE_TITULO_SIZE)
    fuente_texto = pygame.font.SysFont("arial", FUENTE_TEXTO_SIZE)
    contenido_surf, contenido_altura = _crear_superficie_texto(fuente_titulo, fuente_texto)

    scroll_y = 0.0
    arrastrando_barra = False
    offset_click_barra = 0 

    area_rect = pygame.Rect(MARGEN, Y_AREA, ANCHO_AREA_TEXTO, ALTO_AREA_TEXTO)
    track_rect = pygame.Rect(
        constantes.ANCHO - MARGEN - ANCHO_BARRA - MARGEN_BARRA,
        Y_AREA,
        ANCHO_BARRA,
        ALTO_AREA_TEXTO,
    )
    max_scroll = max(0, contenido_altura - ALTO_AREA_TEXTO)
    if max_scroll > 0:
        thumb_altura = max(30, int((ALTO_AREA_TEXTO / contenido_altura) * ALTO_AREA_TEXTO))
    else:
        thumb_altura = ALTO_AREA_TEXTO
    boton_volver_rect = pygame.Rect(
        constantes.ANCHO // 2 - 80,
        constantes.ALTO - 70,
        160,
        ALTO_BOTON,
    )
    fuente_boton = pygame.font.SysFont("arial", 32)
    texto_volver = fuente_boton.render("Volver", True, constantes.BLANCO)

    running = True
    while running:
        reloj.tick(constantes.FPS)
        ventana.blit(fondo, (0, 0))

        titulo_surf = fuente_titulo.render("Instrucciones", True, constantes.MORADO_P)
        titulo_rect = titulo_surf.get_rect(center=(constantes.ANCHO // 2, Y_TITULO))
        ventana.blit(titulo_surf, titulo_rect)

        overlay = pygame.Surface((area_rect.width, area_rect.height), pygame.SRCALPHA)
        overlay.fill(OVERLAY_OSCURO)
        ventana.blit(overlay, (area_rect.x, area_rect.y))

        ventana.set_clip(area_rect)
        ventana.blit(
            contenido_surf,
            (area_rect.x, area_rect.y),
            (0, int(scroll_y), ANCHO_AREA_TEXTO, min(ALTO_AREA_TEXTO, contenido_altura - int(scroll_y))),
        )
        ventana.set_clip(None)

        # Barra de desplazamiento
        if max_scroll > 0:
            pygame.draw.rect(ventana, COLOR_FONDO_BARRA, track_rect)
            thumb_y = track_rect.y + int((scroll_y / max_scroll) * (ALTO_AREA_TEXTO - thumb_altura))
            thumb_rect = pygame.Rect(track_rect.x, thumb_y, ANCHO_BARRA, thumb_altura)
            pygame.draw.rect(ventana, COLOR_THUMB, thumb_rect)
            pygame.draw.rect(ventana, COLOR_THUMB_BORDE, thumb_rect, 2)
        else:
            thumb_rect = pygame.Rect(track_rect.x, track_rect.y, ANCHO_BARRA, thumb_altura)

        pygame.draw.rect(ventana, constantes.AZUL_P, boton_volver_rect)
        pygame.draw.rect(ventana, constantes.BLANCO, boton_volver_rect, 2)
        volver_texto_rect = texto_volver.get_rect(center=boton_volver_rect.center)
        ventana.blit(texto_volver, volver_texto_rect)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return

            if evento.type == pygame.MOUSEWHEEL:
                scroll_y -= evento.y * PASO_RUEDA
                scroll_y = max(0, min(max_scroll, scroll_y))

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if boton_volver_rect.collidepoint(evento.pos):
                        return
                    if max_scroll > 0 and thumb_rect.collidepoint(evento.pos):
                        arrastrando_barra = True
                        offset_click_barra = evento.pos[1] - thumb_rect.y
                    elif max_scroll > 0 and track_rect.collidepoint(evento.pos):
                        if evento.pos[1] < thumb_rect.y:
                            scroll_y = max(0, scroll_y - ALTO_AREA_TEXTO * 0.8)
                        else:
                            scroll_y = min(max_scroll, scroll_y + ALTO_AREA_TEXTO * 0.8)
                        scroll_y = max(0, min(max_scroll, scroll_y))

            if evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    arrastrando_barra = False
#moverlo con el raton
            if evento.type == pygame.MOUSEMOTION:
                if arrastrando_barra and max_scroll > 0:
                    raton_y = evento.pos[1] - offset_click_barra
                    t = (raton_y - track_rect.y) / (ALTO_AREA_TEXTO - thumb_altura)
                    t = max(0, min(1, t))
                    scroll_y = t * max_scroll

        pygame.display.update()
