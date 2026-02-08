import pygame, sys, os
import constantes
import random
    
pygame.init()
ventana = pygame.display.set_mode((constantes.ANCHO, constantes.ALTO))
pygame.display.set_caption("Juego de Memoria")

fondo = pygame.transform.scale(constantes.FONDO, (constantes.ANCHO, constantes.ALTO))
reloj = pygame.time.Clock()

#config cartas 
num_pares = 6
ancho, alto = 80, 100
margen = 20
columnas = 4
filas = 3

# Cargar imágenes
imagenes = []
for i in range(1, num_pares + 1):
    path = os.path.join("Assets", "Images", f"{i}.png")
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, (ancho, alto))
    imagenes.append(img)

# Crear lista de cartas (pares) y barajar
valores = imagenes * 2
random.shuffle(valores)

# Calcular posición inicial para centrar
ancho_total = columnas * ancho + (columnas - 1) * margen
alto_total = filas * alto + (filas - 1) * margen
x_inicial = (constantes.ANCHO - ancho_total) // 2
y_inicial = (constantes.ALTO - alto_total) // 2

# Crear cartas
cartas = []
for i, img in enumerate(valores):
    x = x_inicial + (i % columnas) * (ancho + margen)
    y = y_inicial + (i // columnas) * (alto + margen)
    carta = {"imagen": img, "rect": pygame.Rect(x, y, ancho, alto),
             "visible": False, "encontrada": False}
    cartas.append(carta)

seleccionadas = []
pares_encontrados = 0

# Función para verificar pares
def verificar_par():
    global seleccionadas, pares_encontrados
    c1, c2 = seleccionadas
    if c1["imagen"] == c2["imagen"]:
        c1["encontrada"] = True
        c2["encontrada"] = True
        pares_encontrados += 1
    else:
        pygame.time.delay(600)
        c1["visible"] = False
        c2["visible"] = False
    seleccionadas = []

Running = True

while Running:
    reloj.tick(constantes.FPS)
    evento_lista = pygame.event.get()
    
    for evento in evento_lista:
        if evento.type == pygame.QUIT:
            Running = False
            
    if evento.type == pygame.MOUSEBUTTONDOWN:
            for carta in cartas:
                if (carta["rect"].collidepoint(evento.pos)
                    and not carta["visible"]
                    and not carta["encontrada"]
                    and len(seleccionadas) < 2):
                    carta["visible"] = True
                    seleccionadas.append(carta)
    
    # Verificar si hay dos cartas volteadas
    if len(seleccionadas) == 2:
        verificar_par()
    
    ventana.blit(fondo, (0, 0)) 
    
    # Dibujar cartas
    for carta in cartas:
        if carta["visible"] or carta["encontrada"]:
            ventana.blit(carta["imagen"], carta["rect"])
        else:
            pygame.draw.rect(ventana, (70, 130, 180), carta["rect"])

    # Mensaje si se completan todos los pares
    if pares_encontrados == num_pares:
        fuente = pygame.font.SysFont(None, 50)
        texto = fuente.render("¡Nivel completado!", True, (255, 255, 255))
        ventana.blit(texto, texto.get_rect(center=(constantes.ANCHO//2, 50)))
            
    pygame.display.update()

pygame.quit()
sys.exit()
    
