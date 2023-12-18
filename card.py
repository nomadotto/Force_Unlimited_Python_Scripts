class Card:
    def __init__(self, name: str, power: int, cost: int, hp: int, sentinel:int=0,
                 saboteur:int=0):
        self.name = name
        self.power = power
        self.cost = cost
        self.hp = hp
        self.damage = 0
        self.is_dead = 0
        self.exhausted = 1
        self.sentinel= sentinel
        self.saboteur= saboteur


    def on_play(self, *kwargs):
        pass

    def take_damage(self, dam: int):
        self.damage += dam
        if self.damage >= self.hp:
            self.is_dead = 1

    def attack(self, target):
        if self.exhausted == 0 and self.is_dead == 0:
            target.take_damage(self.power)
            self.take_damage(target.power)
            self.exhausted = 1

    def ready(self):
        self.exhausted = 0




class Snowtrooper(Card):
    def on_play(self, buff_target, attack_target):
        buff_target.power += 2
        buff_target.attack(attack_target)



