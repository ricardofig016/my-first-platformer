import sys
import pygame

from scripts.utils import load_image, load_images
from classes.entities import PhysicsEntity
from classes.tilemap import Tilemap


class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption("my first platformer")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "player": load_image("entities/player.png"),
        }

        self.player = PhysicsEntity(self, "player", (50, 50), (8, 15))

        self.tilemap = Tilemap(self, 16)

    def run(self):
        while True:
            self.display.fill((14, 219, 248))

            self.tilemap.render(self.display)

            self.player.update((self.movement[1] - self.movement[0], 0))
            self.player.render(self.display)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
            pygame.display.update()
            self.clock.tick(60)
