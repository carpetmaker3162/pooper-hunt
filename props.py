from entity import Entity
import pygame

pygame.font.init()
arial = pygame.font.SysFont('arial', 20)

class Crate(Entity):
    name = "crate"
    def __init__(self,
            spawn=(0, 0),
            size=(200, 200)):

        super().__init__(image="crate.png", spawn=spawn, size=size)

class PopupText(Entity):
    name = "popuptext"
    def __init__(self,
            text="",
            spawn=(0, 0),
            font=arial,
            color=(0, 0, 0),
            destroy=0):

        super().__init__(spawn=spawn)

        self.text = text
        self.font = font
        self.color = color
        self.destroy = destroy # removal time

    def draw(self, screen):
        rendered_text = self.font.render(self.text, True, self.color)
        screen.blit(rendered_text, (self.x, self.y))
