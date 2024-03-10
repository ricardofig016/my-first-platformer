import pygame

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
PHYSICS_TILES = ["grass", "stone"]


class Tilemap:
    def __init__(self, game, tile_size=16) -> None:
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        # mock tilemap
        for i in range(10):
            self.tilemap[str(3 + i) + ";10"] = {
                "type": "grass",
                "variant": 1,
                "pos": (3 + i, 10),
            }
            self.tilemap["10;" + str(5 + i)] = {
                "type": "stone",
                "variant": 1,
                "pos": (10, 5 + i),
            }

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
            if tile in PHYSICS_TILES:
                rects.append(
                    pygame.Rect(
                        tile.pos[0] * self.tile_size,
                        tile.pos[1] * self.tile_size,
                        self.tile_size,
                        self.tile_size,
                    )
                )
        return rects

    def render(self, surface):
        for tile in self.offgrid_tiles:
            surface.blit(self.game.assets[tile["type"]][tile["variant"]], tile["pos"])

        for key in self.tilemap:
            tile = self.tilemap[key]
            surface.blit(
                self.game.assets[tile["type"]][tile["variant"]],
                (
                    tile["pos"][0] * self.tile_size,
                    tile["pos"][1] * self.tile_size,
                ),
            )
