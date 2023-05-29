from entity import Entity
import random
from utils import find_nearest, find_xy_speed

MODES = ["wandering", "hide"]

class Enemy(Entity):
    def __init__(self,
            image="canpooper_right_angry.png",
            spawn=(0, 0),
            size=(100, 100),
            distance=100,
            hp=-1,
            x_speed=0,
            y_speed=0):

        super().__init__(image, spawn, size, distance, hp)
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.default_x_speed = x_speed
        self.default_y_speed = y_speed
        self.panic_multiplier = 2
        self.goal = None
        self.mode = "wandering"
    
    def update(self, crates):
        super().update()
        if self.hp < self.max_hp and self.mode != "hide":
            self.hide(crates)
    
    def change_dir(self):
        self.x_speed *= -1

    def hide(self, crates):
        self.mode = "hide"
        nearest = find_nearest(self, crates)
        self.goal = (nearest.x, nearest.y)

        # find what the diagonal speed would be normally
        default_speed = abs(self.default_x_speed**2 + self.default_y_speed**2)
        default_speed *= self.panic_multiplier
        pos = (self.x, self.y)
        self.x_speed, self.y_speed = find_xy_speed(
            default_speed, pos, self.goal)
