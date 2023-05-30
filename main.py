import pygame
import random
from utils import get_image
from enemy import Enemy
from bullet import Bullet
from props import Crate

pygame.init()
pygame.font.init()

ENEMY_STATE_CHANGE = pygame.USEREVENT + 1

# crate locations (x, y, width, height)
CRATES = [
    (100, 400, 100, 100),
    (200, 300, 100, 100)
]

class Spawn:
    def __init__(self, spawn, frequency=range(5000, 10000)):
        self.x, self.y = spawn
        self.min = min(frequency)
        self.max = max(frequency)
        self.last_spawn = -float('inf')
        self.next_enemy = random.randint(self.min, self.max)

    def update(self):
        current_time = pygame.time.get_ticks()

        # indicate that an enemy should be spawned
        if current_time - self.last_spawn >= self.next_enemy:
            self.next_enemy = random.randint(self.min, self.max)
            self.last_spawn = current_time
            return True

        return False

class Game:
    def __init__(self, fps=60):
        # initialize window
        self.width, self.height = 900, 600
        self.screen = pygame.display.set_mode((self.width, self.height), flags=pygame.SCALED)
        pygame.display.set_caption("PooperHunt")
        self.background = get_image("background.png", self.width, self.height)

        # initialize game states and stuff
        self.fps = fps
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(ENEMY_STATE_CHANGE, 1000)
        self.stopped = False

        # create entity groups
        self.enemies = pygame.sprite.Group()
        self.crates = pygame.sprite.Group()
        self.spawns = []
        self.bullets = []
        self.MAX_DISTANCE = 1000
        self.spawns.append(Spawn((450, 300), range(1000, 2000))) # change later
        for crate in CRATES:
            x, y, w, h = crate
            self.crates.add(Crate((x, y), (w, h)))

    def process_events(self):
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return
            # 1 second game timer for updating enemy states
            elif event.type == ENEMY_STATE_CHANGE:
                for enemy in self.enemies:
                    if random.random() < 0.25:
                        enemy.change_dir()
            # mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_events()

    # ran when a mouse click is detected
    def process_mouse_events(self):
        mousex, mousey = self.mouse_pos
        self.shoot(mousex, mousey)

    # update entity groups
    def update(self):
        self.mouse_pos = pygame.mouse.get_pos()

        # draw + update enemies, + kill them if out of screen
        self.enemies.update(self.crates)
        for enemy in self.enemies:
            enemy.draw(self.screen)
            if enemy.x + enemy.width < 0 or enemy.x > self.width:
                enemy.kill()

        self.crates.draw(self.screen)
        
        # update bullets
        for bullet in self.bullets:
            bullet.move()

            # check if bullet is too far away or if it has hit a crate
            if bullet.distance > self.MAX_DISTANCE or \
                    bullet.check_for_hit(self.crates):
                self.bullets.remove(bullet)
                continue

            # check if an enemy is hit by bullet
            hits = bullet.check_for_hit(self.enemies)
            if hits:
                self.bullets.remove(bullet)
                for hit in hits:
                    hit.hp -= bullet.damage

        # update spawns
        for spawn in self.spawns:
            spawner_state = spawn.update()
            # spawn a new enemy (timer is in Spawn class)
            if spawner_state:
                new_enemy = Enemy(
                    spawn=(spawn.x, spawn.y), 
                    size=(50, 50), 
                    distance=100, 
                    hp=100, 
                    x_speed=2, 
                    y_speed=0)
                self.enemies.add(new_enemy)

        pygame.display.flip()

    # shoot a bullet at (x, y)
    def shoot(self, x, y):
        # keeping the bullet code but making it near hitscan for now
        self.bullets.append(Bullet(spawn=(x, y), speed=1000, dmg=80))

    def loop(self):
        while not self.stopped:
            pygame.event.pump()

            # draw background and fill screen
            self.screen.fill((255, 255, 255))
#            self.screen.blit(self.background, (0, 0))

            self.process_events()
            self.update()

            self.clock.tick(self.fps)

if __name__ == "__main__":
    window = Game(fps=60)
    # pygame.display.set_icon(get_image("assets/canpooper_right.png", 200, 200))
    window.loop()
    pygame.quit()
