import math

class Bullet:
    def __init__(self,
            spawn=(0, 0),
            speed=5,
            dmg=80):
        
        self.x, self.y = spawn
        self.speed = speed # m/frame
        self.distance = 0 # floor distance when it is being used
        self.damage = dmg
        self.active = True

    def check_for_hit(self, group):
        res = []
        for entity in group:
            if entity.distance <= math.floor(self.distance) and entity.lies_on(self.x, self.y):
                self.active = False
                res.append(entity)
        return res

    def move(self): # called per frame
        self.distance += self.speed
