import sys
import math
import random
import pygame
import time

from icecream import ic

from scripts.utils import load_image, load_images
from classes.tilemap import Tilemap
from classes.entities import Player, Enemy
from classes.clouds import Clouds
from classes.animations import Animation
from classes.particle import Particle
from classes.spark import Spark

PLAYER_SIZE = (8, 15)
ENEMY_SIZE = (8, 15)


class Game:
    def __init__(self, tilemap_name="") -> None:
        pygame.init()

        pygame.display.set_caption("my first platformer")
        self.screen = pygame.display.set_mode((320 * 3, 240 * 3))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.secondary_display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]  # left, right

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "player/idle": Animation(load_images("entities/player/idle"), 6),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/run": Animation(load_images("entities/player/run"), 4),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide")),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), 6),
            "enemy/run": Animation(load_images("entities/enemy/run"), 4),
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
            "particle/leaf": Animation(load_images("particles/leaf"), 20, False),
            "particle/particle": Animation(load_images("particles/particle"), 6, False),
        }

        self.sfx = {
            "ambience": pygame.mixer.Sound("data/sfx/ambience.wav"),
            "dash": pygame.mixer.Sound("data/sfx/dash.wav"),
            "hit": pygame.mixer.Sound("data/sfx/hit.wav"),
            "jump": pygame.mixer.Sound("data/sfx/jump.wav"),
            "shoot": pygame.mixer.Sound("data/sfx/shoot.wav"),
        }

        self.sfx["ambience"].set_volume(0.2)
        self.sfx["dash"].set_volume(0.3)
        self.sfx["hit"].set_volume(0.8)
        self.sfx["jump"].set_volume(0.7)
        self.sfx["shoot"].set_volume(0.4)

        self.clouds = Clouds(self.assets["clouds"], 16)

        self.tilemap = Tilemap(self, 16)
        if tilemap_name:
            self.map_name = tilemap_name
        else:
            self.map_name = 0
        self.load_level()

        self.scroll = [0, 0]
        self.screenshake = 0

        self.total_elapsed_time = [0, 0]

    def load_level(self):
        self.tilemap.load(self.map_name)

        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], True):
            self.leaf_spawners.append(
                pygame.Rect(tree["pos"][0] + 4, tree["pos"][1] + 4, 23, 13)
            )

        self.player = Player(self, (0, 0), PLAYER_SIZE)
        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)], False):
            if spawner["variant"] == 0:  # player
                self.player.pos = spawner["pos"]
            else:
                self.enemies.append(Enemy(self, spawner["pos"], ENEMY_SIZE))

        self.projectiles = []
        self.sparks = []
        self.particles = []

        self.do_dash = False
        self.dead_for = 0
        self.transition = -30

    def run(self):
        # music
        pygame.mixer.music.load("data/music.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # ambience sfx
        self.sfx["ambience"].play(-1)

        while True:
            # calculate elapsed time per frame
            start_time = time.time()

            # level passed
            if not len(self.enemies):
                self.transition += 1
                if self.transition >= 30:
                    if type(self.map_name) == int:
                        self.map_name += 1
                    self.load_level()
            if self.transition < 0:
                self.transition += 1

            # player is dead
            if self.dead_for:
                # player died 40 frames ago
                self.dead_for += 1
                if self.dead_for >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead_for > 40:
                    self.load_level()

            # background
            self.display.fill((0, 0, 0, 0))
            self.secondary_display.blit(self.assets["background"], (0, 0))

            # scroll
            self.scroll[0] += (
                self.player.rect().centerx
                - self.display.get_width() / 2
                - self.scroll[0]
            ) / 20
            self.scroll[1] += (
                self.player.rect().centery
                - self.display.get_height() / 2
                - self.scroll[1]
            ) / 20
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # screenshake
            self.screenshake = max(0, self.screenshake - 1)

            # leaves
            for leaf_rect in self.leaf_spawners:
                if random.random() * 49999 < leaf_rect.width * leaf_rect.height:
                    pos = (
                        leaf_rect.x + random.random() * leaf_rect.width,
                        leaf_rect.y + random.random() * leaf_rect.height,
                    )
                    self.particles.append(
                        Particle(
                            self,
                            "leaf",
                            pos,
                            [-0.1, 0.3],
                            random.randint(
                                0, len(self.assets["particle/leaf"].images) - 1
                            ),
                        )
                    )

            # clouds
            self.clouds.update()
            self.clouds.render(self.secondary_display, render_scroll)

            # tilemap
            self.tilemap.render(self.display, render_scroll)

            # player
            if not self.dead_for:
                self.player.update(
                    self.tilemap, (self.movement[1] - self.movement[0], 0)
                )
                self.player.render(self.display, render_scroll)

            # player dash
            if self.do_dash:
                self.do_dash = False
                self.player.dash()

            # enemies
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            # projectiles
            # projectiles are very simple so we dont need a class
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]  # x += direction
                projectile[2] += 1  # timer += 1
                img = self.assets["projectile"]
                # render
                self.display.blit(
                    img,
                    (
                        projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                        projectile[0][1] - img.get_height() / 2 - render_scroll[1],
                    ),
                )
                # the projectile hits a wall
                if self.tilemap.is_solid(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.sfx["hit"].play()
                    for i in range(4):
                        self.sparks.append(
                            Spark(
                                projectile[0],
                                random.random()
                                - 0.5
                                + (math.pi if projectile[1] > 0 else 0),
                                random.random() + 2,
                            )
                        )
                # the projectile is is far away
                if projectile[2] > 400:
                    self.projectiles.remove(projectile)
                # player is not dashing AND is alive AND is hit
                elif (
                    abs(self.player.dashing) < 50
                    and not self.dead_for
                    and self.player.rect().collidepoint(projectile[0])
                ):
                    self.sfx["hit"].play()
                    # effects for death
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(
                            Spark(
                                self.player.rect().center,
                                angle,
                                random.random() + 2,
                            )
                        )
                        self.particles.append(
                            Particle(
                                self,
                                "particle",
                                self.player.rect().center,
                                [
                                    math.cos(angle + math.pi) * speed * 0.5,
                                    math.sin(angle + math.pi) * speed * 0.5,
                                ],
                                random.randint(
                                    0, len(self.assets["particle/particle"].images) - 1
                                ),
                            )
                        )
                    self.projectiles.remove(projectile)
                    self.dead_for += 1
                    self.screenshake = max(20, self.screenshake)

            # sparks
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, render_scroll)
                if kill:
                    self.sparks.remove(spark)

            # outlines
            display_mask = pygame.mask.from_surface(self.display)
            display_silhouette = display_mask.to_surface(
                setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0)
            )
            for offset in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                self.secondary_display.blit(display_silhouette, offset)

            # particles
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, render_scroll)
                if particle.type == "leaf":
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit()
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if (
                        event.key == pygame.K_UP
                        or event.key == pygame.K_w
                        or event.key == pygame.K_SPACE
                    ):
                        self.player.jump()
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        pass
                    if event.key == pygame.K_x:
                        self.do_dash = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False

            # level transition
            if self.transition:
                transition_suface = pygame.Surface(self.display.get_size())
                pygame.draw.circle(
                    transition_suface,
                    (255, 255, 255),
                    (self.display.get_width() // 2, self.display.get_height() // 2),
                    (30 - abs(self.transition)) * 8,
                )
                # make circle transparent
                transition_suface.set_colorkey((255, 255, 255))
                self.display.blit(transition_suface, (0, 0))

            # join displays
            self.secondary_display.blit(self.display, (0, 0))

            # screen
            screenshake_offset = (
                random.random() * self.screenshake - self.screenshake / 2,
                random.random() * self.screenshake - self.screenshake / 2,
            )
            self.screen.blit(
                pygame.transform.scale(self.secondary_display, self.screen.get_size()),
                screenshake_offset,
            )
            pygame.display.update()

            # time
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.total_elapsed_time[0] += elapsed_time
            self.total_elapsed_time[1] += 1

            # frame rate
            self.clock.tick(60)

    def exit(self):
        average_elapsed_time = self.total_elapsed_time[0] / self.total_elapsed_time[1]
        ic(average_elapsed_time)
        pygame.quit()
        sys.exit()
