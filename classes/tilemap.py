import os
import pygame
import json

from icecream import ic


NEIGHBOR_OFFSETS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 0),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]

PHYSICS_TILES = {"grass", "stone"}

BASE_MAP_PATH = "data/maps/"


class Tilemap:
    def __init__(self, game, tile_size=16) -> None:
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def tiles_around(self, pos):
        tiles = []
        tile_location = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_location = (
                str(tile_location[0] + offset[0])
                + ";"
                + str(tile_location[1] + offset[1])
            )
            if check_location in self.tilemap:
                tiles.append(self.tilemap[check_location])
        return tiles

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile["type"] in PHYSICS_TILES:
                rects.append(
                    pygame.Rect(
                        tile["pos"][0] * self.tile_size,
                        tile["pos"][1] * self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    )
                )
        return rects

    def render(self, surface, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surface.blit(
                self.game.assets[tile["type"]][tile["variant"]],
                (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]),
            )

        # render only the tiles that will be on screen
        for x in range(
            offset[0] // self.tile_size,
            (offset[0] + surface.get_width()) // self.tile_size + 1,
        ):
            for y in range(
                offset[1] // self.tile_size,
                (offset[1] + surface.get_height()) // self.tile_size + 1,
            ):
                key = f"{x};{y}"
                if key in self.tilemap:
                    tile = self.tilemap[key]
                    surface.blit(
                        self.game.assets[tile["type"]][tile["variant"]],
                        (
                            tile["pos"][0] * self.tile_size - offset[0],
                            tile["pos"][1] * self.tile_size - offset[1],
                        ),
                    )

    def save(self, map_name):
        with open(os.path.join(BASE_MAP_PATH, f"{map_name}.json"), "w") as file:
            json.dump(
                {
                    "tilemap": self.tilemap,
                    "tile_size": self.tile_size,
                    "offgrid": self.offgrid_tiles,
                },
                file,
            )

    def load(self, map_name):
        with open(os.path.join(BASE_MAP_PATH, f"{map_name}.json"), "r") as file:
            data = json.load(file)

        self.tilemap = data["tilemap"]
        self.tile_size = data["tile_size"]
        self.offgrid_tiles = data["offgrid"]
