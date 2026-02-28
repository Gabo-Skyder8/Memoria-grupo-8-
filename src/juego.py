import sys
from pathlib import Path

_raiz = Path(__file__).resolve().parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))

from enfocate import GameBase, GameMetadata, COLORS


class MiJuego(GameBase):
    def __init__(self) -> None:
        metadata = GameMetadata(
            title="FLIP IT",
            description="Juego de memoria con cartas para emparejar.",
            authors=["Gabriel Garanton" "Isabela Paraqueimo" "Cesar Moya"],
            group_number=3,
        )
        # 2. Inyección de metadatos al Core
        super().__init__(metadata)
        
        # 3. Inicialización de estado interno
        self.puntuacion = 0

    def on_start(self):
        """Carga de recursos dinámicos (assets)."""
        pass

    def update(self, dt: float):
        """Actualización de lógica física y estados (dt = delta time)."""
        pass

    def draw(self) -> None:
        """Renderiza el preview del juego."""
        screen = self.surface
        color_fondo = (55, 55, 60)
        screen.fill(color_fondo)

        try:
            import pygame
            fuente = pygame.font.SysFont("arial", 48, bold=True)
            titulo = fuente.render("FLIP IT", True, (255, 255, 255))
            rect = titulo.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 40))
            screen.blit(titulo, rect)

            sub = pygame.font.SysFont("arial", 24).render(
                "Juego de Memoria - Grupo 9", True, (200, 200, 200)
            )
            rect_sub = sub.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20))
            screen.blit(sub, rect_sub)

            sub = pygame.font.SysFont("arial", 24).render(
                "Hecho por Gabriel Garanton; Isabela Paraqueimo y Cesar Moya", True, (200, 200, 200)
            )
            rect_sub = sub.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
            screen.blit(sub, rect_sub)


            hint = pygame.font.SysFont("arial", 18).render(
                "Cerrar ventana para continuar al juego completo", True, (150, 150, 150)
            )
            rect_hint = hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40))
            screen.blit(hint, rect_hint)
        except Exception:
            pass
