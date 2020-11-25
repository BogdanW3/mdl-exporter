class War3AnimationAction:
    def __init__(self, name, start, end, non_looping=False, movement_speed=270, rarity=0):
        self.name = name
        self.length = end - start
        self.start = start
        self.end = end
        self.non_looping = non_looping
        self.movement_speed = movement_speed
        self.rarity = rarity
