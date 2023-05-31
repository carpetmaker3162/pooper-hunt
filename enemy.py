from entity import Entity
from utils import find_nearest, find_xy_speed, get_image
import random
import pygame
import math

MODES = ["wander", "panic", "hide"]

IMAGES = {
    "right": "canpooper_right_angry.png",
    "left": "canpooper_left_angry.png",
    "right_dead": "canpooper_right_angry_dead.png",
    "left_dead": "canpooper_left_angry_dead.png",
}

class Action:
    def __init__(self, dx, dy, start, duration, y_accel=0):
        self.x_speed = round(dx / 60) # assuming 60 frames
        self.y_speed = round(dy / 60)
        self.start = start
        self.duration = duration # ms
        self.y_acceleration = y_accel

class Enemy(Entity):
    name = "enemy"
    def __init__(self,
            image="canpooper_right_angry.png",
            spawn=(0, 0),
            size=(100, 100),
            distance=100,
            hp=-1,
            x_speed=0,
            y_speed=0):

        super().__init__(image, spawn, size, distance, hp)

        # speed variables
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.default_x_speed = x_speed
        self.default_y_speed = y_speed
        self.panic_multiplier = 1

        # enemy state variables
        self.goal = None
        self.mode = "wander"
        self.scheduled = []
        self.recovery_time = float("inf") # time at which enemy stops hiding
        self.comfort_hp = self.max_hp # enemy panics if below comfort hp
        self.dead = False
    
    def update(self, crates):
        current_time = pygame.time.get_ticks()

        # sort scheduled actions by start times
        self.scheduled.sort(key=lambda a: a.start)

        for i, action in enumerate(self.scheduled):
            if action.start + action.duration < current_time:
                self.scheduled.remove(action)
            elif action.start <= current_time <= action.start + action.duration:
                self.x_speed = action.x_speed
                self.y_speed = action.y_speed
                self.y_speed += action.y_acceleration
                self.scheduled[i].y_speed = self.y_speed
                break

        # move and other
        super().update()
        
        # play death animation if enemy dies
        if self.hp <= 0:
            self.dead = True
            self.death_animation()

        # hide if shot at
        if self.hp < self.comfort_hp and self.mode != "panic":
            self.panic(crates)
            self.comfort_hp = self.hp

        # stop if enemy is now hiding behind a crate
        if self.mode == "panic":
            for crate in crates:
                if crate.encloses(self):
                    self.mode = "hide"
                    self.x_speed = 0
                    self.y_speed = 0
                    self.recovery_time = current_time + random.randint(8000, 18000)

        if self.mode == "hide":
            if current_time >= self.recovery_time:
                self.mode = "wander"
                self.scheduled = []
                self.x_speed = self.default_x_speed
                self.y_speed = self.default_y_speed
            else:
                if not self.scheduled:
                    next_peek = random.randint(1000, 5000)
                    self.peek(start = current_time + next_peek, duration=1000, dx=100, dy=0)
                # stop when enemy is back behind crate
                if any(crate.encloses(self) for crate in crates):
                    self.x_speed = 0
                    self.y_speed = 0
        
        if self.x_speed < 0 and not self.dead:
            self.image = get_image(IMAGES["left"], 50, 50)
        elif self.x_speed >= 0 and not self.dead:
            self.image = get_image(IMAGES["right"], 50, 50)

    def schedule_action(self, action: Action):
        self.scheduled.append(action)

    # change direction (left/right)
    def change_dir(self):
        self.x_speed *= -1
    
    def death_animation(self):
        current_time = pygame.time.get_ticks()

        if self.x_speed < 0:
            self.image = get_image(IMAGES["left_dead"], 50, 50)
        elif self.x_speed >= 0:
            self.image = get_image(IMAGES["right_dead"], 50, 50)

        self.schedule_action(Action(0, -1000, current_time, 10000, 0.5))

    def peek(self, start, duration, dx, dy):
        duration //= 2
        self.schedule_action(Action(dx, dy, start, duration))
        self.schedule_action(Action(-dx, -dy, start + duration, duration))

    # hide behind a crate
    def panic(self, crates):
        self.mode = "panic"

        # find nearest crate
        nearest = find_nearest(self, crates)
        self.goal = (nearest.x, nearest.y)

        # find what the diagonal speed would be normally
        default_speed = abs(self.default_x_speed**2 + self.default_y_speed**2)
        default_speed *= self.panic_multiplier
        
        # update x-speed and y-speed
        pos = (self.x, self.y)
        self.x_speed, self.y_speed = find_xy_speed(
            default_speed, pos, self.goal)
