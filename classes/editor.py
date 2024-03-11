import sys
import pygame
import time
import random

from icecream import ic

from scripts.utils import load_image, load_images
from classes.tilemap import Tilemap

RENDER_SCALE = 2.0


class Editor:
    def __init__(self, tilemap_name="") -> None:
        pygame.init()

        pygame.display.set_caption("editor")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
        }

        self.movement = [False, False, False, False]  # left, right, up, down

        self.tilemap = Tilemap(self, 16)

        self.tilemap_name = tilemap_name
        try:
            self.tilemap.load(self.tilemap_name)
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.left_clicking = False
        self.right_clicking = False
        self.shift = False
        self.on_grid = True

        self.total_elapsed_time = [0, 0]

    def run(self):
        while True:
            # calculate elapsed time per frame
            start_time = time.time()

            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, render_scroll)

            current_tile_image = self.assets[self.tile_list[self.tile_group]][
                self.tile_variant
            ].copy()
            current_tile_image.set_alpha(100)  # transparency

            mouse_pos = pygame.mouse.get_pos()  # display mouse pos
            mouse_pos = (
                mouse_pos[0] / RENDER_SCALE,
                mouse_pos[1] / RENDER_SCALE,
            )  # screen mouse pos
            tile_pos = (
                int((mouse_pos[0] + self.scroll[0]) // self.tilemap.tile_size),
                int((mouse_pos[1] + self.scroll[1]) // self.tilemap.tile_size),
            )  # tilemap mouse pos

            # tile preview
            if not self.right_clicking:
                if self.on_grid:
                    self.display.blit(
                        current_tile_image,
                        (
                            tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                            tile_pos[1] * self.tilemap.tile_size - self.scroll[1],
                        ),
                    )
                else:
                    self.display.blit(current_tile_image, mouse_pos)

            # place tiles
            if self.left_clicking and self.on_grid:
                self.tilemap.tilemap[f"{tile_pos[0]};{tile_pos[1]}"] = {
                    "type": self.tile_list[self.tile_group],
                    "variant": self.tile_variant,
                    "pos": tile_pos,
                }

            # delete tiles
            if self.right_clicking:
                key = f"{tile_pos[0]};{tile_pos[1]}"
                if key in self.tilemap.tilemap:
                    del self.tilemap.tilemap[key]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile["type"]][tile["variant"]]
                    tile_rect = pygame.Rect(
                        tile["pos"][0] - self.scroll[0],
                        tile["pos"][1] - self.scroll[1],
                        tile_img.get_width(),
                        tile_img.get_height(),
                    )
                    if tile_rect.collidepoint(mouse_pos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_image, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left click
                        self.left_clicking = True
                        if not self.on_grid:
                            self.tilemap.offgrid_tiles.append(
                                {
                                    "type": self.tile_list[self.tile_group],
                                    "variant": self.tile_variant,
                                    "pos": (
                                        mouse_pos[0] + self.scroll[0],
                                        mouse_pos[1] + self.scroll[1],
                                    ),
                                }
                            )
                    if event.button == 3:  # right click
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 2:  # middle click
                            self.tile_variant = random.randint(
                                0, len(self.assets[self.tile_list[self.tile_group]]) - 1
                            )
                        if event.button == 4:  # scroll up
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                        if event.button == 5:  # scroll down
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                    else:
                        if event.button == 2:  # middle click
                            self.tile_group = random.randint(0, len(self.tile_list) - 1)
                            self.tile_variant = 0
                        if event.button == 4:  # scroll up
                            self.tile_group = (self.tile_group - 1) % len(
                                self.tile_list
                            )
                            self.tile_variant = 0
                        if event.button == 5:  # scroll down
                            self.tile_group = (self.tile_group + 1) % len(
                                self.tile_list
                            )
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        self.left_clicking = False
                    if event.button == 3:  # right click
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = True
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.shift = True
                    elif event.key == pygame.K_g:
                        self.on_grid = not self.on_grid
                    elif event.key == pygame.K_o:
                        if self.tilemap_name:
                            self.tilemap.save(self.tilemap_name)
                        else:
                            self.tilemap.save(input("Save new map as: "))
                        print("Map successfully saved.")

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = False
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.shift = False

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
