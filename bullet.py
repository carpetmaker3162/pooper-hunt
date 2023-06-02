import math

class Bullet:
    def __init__(self,
            spawn=(0, 0),
            speed=5,
            dmg=100,
            aoe_dmg=100,
            aoe_range=0, # <= 0 if no aoe
            apply_aoe_dropoff=True):
        
        self.x, self.y = spawn
        self.speed = speed # m/frame
        self.distance = 0 # floor distance when it is being used
        self.damage = dmg
        self.aoe_damage = aoe_dmg
        self.aoe_range = aoe_range
        self.apply_aoe_dropoff = apply_aoe_dropoff

    # find damage (no aoe), was previously utils.find_damage_multiplier()
    @staticmethod
    def find_dmg_multiplier(entity, bullet):
        center = entity.rect.center # center of entity
        radius = center[0] - entity.x # distance from entity center to the entity's edge
        
        # find how far the bullet landed from center of entity
        x, y = center
        dx = x - bullet.x
        dy = y - bullet.y
        dist_from_center = math.sqrt(dx**2 + dy**2)

        dropoff = (radius - dist_from_center) / radius

        return max(0, dropoff)

    @staticmethod
    def find_aoe_dmg_multiplier(entity, bullet):
        entity_x, entity_y = entity.rect.center
        dx = entity_x - bullet.x
        dy = entity_y - bullet.y
        entity_dist = math.sqrt(dx**2 + dy**2)

        if entity_dist > bullet.aoe_range:
            return 0

        if bullet.apply_aoe_dropoff:
            dropoff = (bullet.aoe_range - entity_dist) / bullet.aoe_range
        else:
            dropoff = 1
        
        return max(0, dropoff)

    def check_for_hit(self, group, check_aoe=True):
        res = []
        for entity in group:
            # check if entity is too far away
            if entity.distance > math.floor(self.distance):
                continue

            if self.aoe_range <= 0 and entity.lies_on(self.x, self.y):
                res.append(entity)
                continue

            entity_x, entity_y = entity.rect.center
            dx = entity_x - self.x
            dy = entity_y - self.y
            entity_dist = math.sqrt(dx**2 + dy**2)

            if self.aoe_range > 0 and entity_dist <= self.aoe_range and check_aoe:
                res.append(entity)
        return res

    def move(self): # called per frame
        self.distance += self.speed
