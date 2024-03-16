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
AUTOTILE_TYPES = {"grass", "stone"}
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(0, 1), (-1, 0)])): 2,
    tuple(sorted([(0, 1), (-1, 0), (0, -1)])): 3,
    tuple(sorted([(0, -1), (-1, 0)])): 4,
    tuple(sorted([(0, -1), (-1, 0), (1, 0)])): 5,
    tuple(sorted([(0, -1), (1, 0)])): 6,
    tuple(sorted([(0, -1), (1, 0), (0, 1)])): 7,
    tuple(sorted([(0, -1), (1, 0), (0, 1), (-1, 0)])): 8,
}
BASE_MAP_PATH = "data/maps/"


class Tilemap:
    def __init__(self, game, tile_size=16) -> None:
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def extract(self, id_pairs, keep=False):
        matches = []

        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for key in self.tilemap:
            tile = self.tilemap[key]
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                matches[-1]["pos"][0] *= self.tile_size
                matches[-1]["pos"][1] *= self.tile_size
                if not keep:
                    del self.tilemap[key]

        return matches

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

    def is_solid(self, pos):
        key = f"{int(pos[0]//self.tile_size)};{int(pos[1]//self.tile_size)}"
        if key in self.tilemap and self.tilemap[key]["type"] in PHYSICS_TILES:
            return True
        return False

    def autotile(self):
        for key in self.tilemap:
            tile = self.tilemap[key]
            neighbors = set()
            for shift in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                shifted_pos = f"{tile['pos'][0]+shift[0]};{tile['pos'][1]+shift[1]}"
                if (
                    shifted_pos in self.tilemap
                    and self.tilemap[shifted_pos]["type"] == tile["type"]
                ):
                    neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if tile["type"] in AUTOTILE_TYPES and (neighbors in AUTOTILE_MAP):
                tile["variant"] = AUTOTILE_MAP[neighbors]

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
