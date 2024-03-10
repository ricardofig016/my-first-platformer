import os
import pygame

BASE_IMG_PATH = "data/images/"


def load_image(path):
    img = pygame.image.load(os.path.join(BASE_IMG_PATH, path)).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path):
    image_names = sorted(os.listdir(os.path.join(BASE_IMG_PATH, path)))
    image_paths = [os.path.join(path, image_name) for image_name in image_names]
    return [load_image(image_path) for image_path in image_paths]
