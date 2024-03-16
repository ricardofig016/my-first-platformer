import pygame
import math
import random

from icecream import ic

from classes.particle import Particle


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size) -> None:
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.last_movement = [0, 0]
        self.collisions = {"up": False, "down": False, "right": False, "left": False}

        self.action = ""
        self.animation_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[f"{self.type}/{self.action}"].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {"up": False, "down": False, "right": False, "left": False}

        frame_movement = (
            movement[0] + self.velocity[0],
            movement[1] + self.velocity[1],
        )

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.velocity[1] = min(
            5, self.velocity[1] + 0.1
        )  # 5 is the terminal downwards velocity

        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0

        self.last_movement = list(movement)

        self.animation.update()

    def render(self, surface, offset=(0, 0)):
        surface.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
            (
                self.pos[0] - offset[0] + self.animation_offset[0],
                self.pos[1] - offset[1] + self.animation_offset[1],
            ),
        )


class Player(PhysicsEntity):
    def __init__(self, game, pos, size) -> None:
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.available_jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.available_jumps = 1

        self.wall_slide = False
        if (self.collisions["left"] or self.collisions["right"]) and self.air_time > 4:
            self.wall_slide = True
            # 0.5 is the terminal downwards velocity while wall sliding
            self.velocity[1] = min(0.5, self.velocity[1])
            self.flip = self.collisions["left"]
            self.set_action("wall_slide")
        elif self.air_time >= 5:  # player has been in the air for 5 frames
            self.set_action("jump")
        elif movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        # start and end of the dash
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                particle_angle = random.random() * math.pi * 2
                particle_speed = random.random() * 0.5 + 0.5
                particle_velocity = [
                    math.cos(particle_angle) * particle_speed,
                    math.sin(particle_angle) * particle_speed,
                ]  # this is the correct way to spread things out in a circle shape
                self.game.particles.append(
                    Particle(
                        self.game,
                        "particle",
                        self.rect().center,
                        particle_velocity,
                        random.randint(0, 3),
                    )
                )

        # during the dash
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            # abruptly shorten x-axis velocity after 10 frames to stop the dash
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            particle_velocity = [
                abs(self.dashing) / self.dashing * random.random() * 3,
                0,
            ]
            self.game.particles.append(
                Particle(
                    self.game,
                    "particle",
                    self.rect().center,
                    particle_velocity,
                    random.randint(0, 3),
                )
            )

        # update dashing value
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        elif self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        # air resistance
        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)

    def render(self, surface, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surface, offset)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.available_jumps -= 1
                self.velocity = [3.5, -2.5]
                self.air_time = 5
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.available_jumps -= 1
                self.velocity = [-3.5, -2.5]
                self.air_time = 5
                return True

        elif self.available_jumps > 0:
            self.available_jumps -= 1
            self.velocity[1] = -3.1
            self.air_time = 5
            return True

        return False

    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size) -> None:
        super().__init__(game, "enemy", pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])  #!!!!!!!
            self.walking = max(0, self.walking - 1)
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement)
