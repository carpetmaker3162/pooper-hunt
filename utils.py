import pygame
import os
import math

cache = {}
DEFAULTDIR = "assets"

def get_image(image: str, width=100, height=100):
    imagepath = os.path.join(DEFAULTDIR, image)
    image_key = f"{imagepath.strip()} width={width} height={height}"
    if image_key in cache:
        pass
    else:
        image = pygame.image.load(imagepath).convert_alpha()
        image = pygame.transform.scale(image, (width, height))
        cache[image_key] = image
    return cache[image_key]

# find distance from coords1(x1, y1) to coords2(x2, y2)
def distance(coords1: tuple, coords2: tuple):
    x1, y1 = coords1
    x2, y2 = coords2
    
    dx = x2 - x1
    dy = y2 - y1

    return math.sqrt(dx**2 + dy**2)

def find_nearest(entity, group):
    x1, y1 = entity.x, entity.y

    nearest_d = float("inf")
    nearest_entity = None
    for other_entity in group:
        x2, y2 = other_entity.x, other_entity.y
        d = distance((x1, y1), (x2, y2))

        if d <= nearest_d:
            nearest_d = d
            nearest_entity = other_entity

    return nearest_entity

# given speed from pos to goal break down to x-speed and y-speed
def find_xy_speed(speed: float, pos: tuple, goal: tuple):
    x1, y1 = pos
    x2, y2 = goal

    dx = x2 - x1
    dy = y2 - y1

    distance = math.sqrt(dx**2 + dy**2)

    x_speed = (dx / distance) * speed
    y_speed = (dy / distance) * speed

    return math.ceil(x_speed), math.ceil(y_speed)
