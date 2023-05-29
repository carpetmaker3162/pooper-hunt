import pygame
from utils import get_image

class Entity(pygame.sprite.Sprite):
    def __init__(self,
            image="none.png",
            spawn=(0, 0),
            size=(100, 100),
            distance=100,
            hp=-1):

        super().__init__()
        self.width, self.height = size
        self.x, self.y = spawn
        self.distance = distance

        self.image = get_image(image, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

        self.x_speed = 0
        self.y_speed = 0
        self.invulnerable = False

        self.hp = hp
        self.max_hp = self.hp

        if hp < 0:
            self.invulnerable = True

    def draw(self, screen):
        screen.blit(
            self.image, (self.rect.center[0] - self.width/2, self.rect.center[1] - self.height/2))
        if self.hp != self.max_hp and not self.invulnerable:
            self.draw_hp_bar(screen)

    def move(self, dx, dy):
        self.y += dy
        self.x += dx

        self.rect.move_ip((dx, dy))

    def update(self):
        self.move(self.x_speed, self.y_speed)
        if self.hp <= 0:
            self.kill()

    def draw_hp_bar(self, screen: pygame.Surface, x_offset=0):
        pos = (self.x - x_offset, self.y - 15)
        size = (self.width, 10)
        pygame.draw.rect(screen, (0, 0, 0), (pos, size), 1)
        bar_pos = (pos[0] + 3, pos[1] + 3)
        bar_size = ((size[0] - 6) * (self.hp / self.max_hp), size[1] - 6)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_pos, *bar_size))

    # return whether or not a point lies on the entity
    def lies_on(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)
