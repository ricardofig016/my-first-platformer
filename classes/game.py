import sys
import pygame
import time

from icecream import ic

from scripts.utils import load_image, load_images
from classes.entities import PhysicsEntity, Player
from classes.tilemap import Tilemap
from classes.clouds import Clouds
from classes.animations import Animation


class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption("my first platformer")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]  # left, right

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "player/idle": Animation(load_images("entities/player/idle"), 6),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/run": Animation(load_images("entities/player/run"), 4),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide")),
        }

        self.clouds = Clouds(self.assets["clouds"], 16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, 16)
        self.tilemap.load("mock_map")

        self.scroll = [0, 0]

        self.total_elapsed_time = [0, 0]

    def run(self):
        while True:
            # calculate elapsed time per frame
            start_time = time.time()

            self.display.blit(self.assets["background"], (0, 0))

            self.scroll[0] += (
                self.player.rect().centerx
                - self.display.get_width() / 2
                - self.scroll[0]
            ) / 30
            self.scroll[1] += (
                self.player.rect().centery
                - self.display.get_height() / 2
                - self.scroll[1]
            ) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.display, render_scroll)

            self.tilemap.render(self.display, render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.velocity[1] = -3
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        pass
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
            pygame.display.update()

            end_time = time.time()
            elapsed_time = end_time - start_time
            self.total_elapsed_time[0] += elapsed_time
            self.total_elapsed_time[1] += 1

            self.clock.tick(60)

    def exit(self):
        average_elapsed_time = self.total_elapsed_time[0] / self.total_elapsed_time[1]
        ic(average_elapsed_time)
        pygame.quit()
        sys.exit()
