import pygame
import random
from utils import get_image, find_damage_multiplier
from enemy import Enemy
from bullet import Bullet
from props import Crate, PopupText

pygame.init()
pygame.font.init()

ENEMY_STATE_CHANGE = pygame.USEREVENT + 1

# crate locations (x, y, width, height)
CRATES = [
    (100, 400, 100, 100),
    (600, 300, 100, 100)
]

heading_font = pygame.font.Font("assets/VT323.ttf", 48)
small_font = pygame.font.Font("assets/VT323.ttf", 24)

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
        self.canvas_width, self.canvas_height = 900, 700
        self.width, self.height = 900, 600
        self.screen = pygame.display.set_mode((self.canvas_width, self.canvas_height), flags=pygame.SCALED)
        pygame.display.set_caption("PooperHunt")
        pygame.mouse.set_visible(False)

        # initialize assets
        self.background = get_image("background.png", self.width, self.height)
        self.ammo_icon = get_image("ammo.png", 50, 50)
        self.scope = get_image("scope.png", 100, 100)

        # initialize game states and stuff
        self.frame_cap = fps
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(ENEMY_STATE_CHANGE, 1000)
        self.stopped = False
        self.score = 0

        # create entity groups
        self.enemies = pygame.sprite.Group()
        self.crates = pygame.sprite.Group()
        self.popup_text = pygame.sprite.Group()
        self.spawns = []
        self.bullets = []
        self.MAX_DISTANCE = 1000
        self.spawns.append(Spawn((450, 300), range(500, 2000)))
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
        current_time = pygame.time.get_ticks()
        mousex, mousey = self.mouse_pos
        # change bounds if a left menu is added (canvas x-y offset or something)
        if mousex <= self.width and mousey <= self.height:
            self.shoot(mousex, mousey)

    # update entity groups
    def update(self):
        current_time = pygame.time.get_ticks()
        self.mouse_pos = pygame.mouse.get_pos()

        # draw + update enemies, + kill them if out of screen
        self.enemies.update(self.crates)
        for enemy in self.enemies:
            enemy.draw(self.screen)
            if enemy.x + enemy.width < 0 or enemy.x > self.width:
                enemy.kill()

        self.crates.draw(self.screen)

        self.popup_text.update()
        for popuptext in self.popup_text:
            if current_time >= popuptext.destroy:
                popuptext.kill()
            else:
                popuptext.draw(self.screen)
        
        # update bullets
        for bullet in self.bullets:
            bullet.move()

            # check if bullet is too far away or if it has hit a crate
            if bullet.distance > self.MAX_DISTANCE or \
                    bullet.check_for_hit(self.crates, check_aoe=False):
                self.bullets.remove(bullet)
                continue

            # check if an enemy is hit by bullet
            hits = bullet.check_for_hit(self.enemies)
            if hits:
                self.bullets.remove(bullet)
                score_added = 0
                for hit in hits:
                    # find direct damage
                    dmg_multiplier = Bullet.find_dmg_multiplier(hit, bullet)
                    direct_damage = bullet.damage * dmg_multiplier

                    # find aoe damage
                    dmg_multiplier = Bullet.find_aoe_dmg_multiplier(hit, bullet)
                    aoe_damage = bullet.aoe_damage * dmg_multiplier

                    # apply the larger damage
                    damage = max(direct_damage, aoe_damage)
                    hit.hp -= damage

                    # find hitmarker position
                    if direct_damage < aoe_damage: # if using aoe damage
                        dmg_x, dmg_y = hit.rect.center
                    else:
                        dmg_x, dmg_y = bullet.x, bullet.y
                    offset_x = random.randint(-20, 10)
                    offset_y = random.randint(-20, 10)

                    # draw hitmarker
                    new_hitmarker = PopupText(
                        text=str(int(damage)),
                        spawn=(dmg_x + offset_x, dmg_y + offset_y),
                        font=small_font,
                        color=(0, 0, 255),
                        destroy=current_time + 200)
                    self.popup_text.add(new_hitmarker)
                    new_hitmarker.x_speed = random.random() * 2 - 1
                    new_hitmarker.y_speed = random.random() * -1

                    # multiply score by 2 for each enemy killed with 1 bullet
                    if hit.hp <= 0:
                        score_added = max(score_added * 2, 100)
                        new_hitmarker = PopupText(
                            text="+" + str(score_added),
                            spawn=(dmg_x, dmg_y),
                            font=small_font,
                            color=(205, 205, 0),
                            destroy=current_time + 400)
                        self.popup_text.add(new_hitmarker)
                        new_hitmarker.y_speed = -2

                # add score
                self.score += score_added

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

        # draw scope
        x, y = self.mouse_pos
        self.screen.blit(self.scope, (x - 50, y - 50))

        pygame.display.flip()

    # shoot a bullet at (x, y)
    def shoot(self, x, y):
        # keeping the bullet code but making it near hitscan for now
        self.bullets.append(Bullet(
            spawn=(x, y),
            speed=1000,
            dmg=120,
            aoe_dmg=0,
            aoe_range=0,
            apply_aoe_dropoff=False))

    def loop(self):
        while not self.stopped:
            pygame.event.pump()

            # draw background and fill screen
            self.screen.fill((255, 255, 255))
#            self.screen.blit(self.background, (0, 0))
            self.screen.blit(
                heading_font.render("Score: " + str(self.score), True, (255, 221, 0)),
                (10, 550))
#            self.screen.blit(self.ammo_icon, (0, 550))

            self.process_events()
            self.update()

            self.clock.tick(self.frame_cap)

if __name__ == "__main__":
    window = Game(fps=60)
    # pygame.display.set_icon(get_image("assets/canpooper_right.png", 200, 200))
    window.loop()
    print(f"Score: {window.score}")
    pygame.quit()
