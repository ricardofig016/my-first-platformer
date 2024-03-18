import math
import pygame


class Spark:
    def __init__(self, pos, angle, speed) -> None:
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.speed -= 0.1
        # the spark will be deleted if speed <= 0
        return self.speed <= 0

    def render(self, surface, offset=(0, 0)):
        # diamond shape
        vertices = [
            (
                self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0],
                self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1],
            ),
            (
                self.pos[0]
                + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5
                - offset[0],
                self.pos[1]
                + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5
                - offset[1],
            ),
            (
                self.pos[0]
                + math.cos(self.angle + math.pi) * self.speed * 3
                - offset[0],
                self.pos[1]
                + math.sin(self.angle + math.pi) * self.speed * 3
                - offset[1],
            ),
            (
                self.pos[0]
                + math.cos(self.angle + math.pi * 1.5) * self.speed * 0.5
                - offset[0],
                self.pos[1]
                + math.sin(self.angle + math.pi * 1.5) * self.speed * 0.5
                - offset[1],
            ),
        ]

        pygame.draw.polygon(surface, (255, 255, 255), vertices)
