from entity import Entity

class Crate(Entity):
    name = "crate"
    def __init__(self, spawn=(0, 0), size=(200, 200)):
        super().__init__("crate.png", spawn, size, 0, -1)
