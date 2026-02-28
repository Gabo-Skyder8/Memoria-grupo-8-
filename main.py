from src.juego import MiJuego


if __name__ == "__main__":
    # Se instancia y se corre.
    # El Core ya sabe qué hacer porque la lógica está en la base.
    game = MiJuego()
    game.run_preview()