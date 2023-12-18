import matplotlib.pyplot as plt
from card import *
from copy import deepcopy
initial_cards = 4
initial_resources = 2
aggro_cards = {'storm_trooper': Card(name='storm_trooper', power=3, cost=1, hp=1),
               'rogue_operative': Card(name='rogue_operative', power=4, cost=3, hp=4)
               }
defending_cards = {'technician': Card(name='technician', power=2, cost=2, hp=1),
                   'cloud_guard': Card(name='cloud_guard', power=2, cost=3, hp=4, sentinel=1),
                   'goldfish': Card(name='None', power=0, cost=100, hp=0)
                   }


debug = True
base_health = 30



class Player:
    def __init__(self, max_resources: int, card: Card, defending_card: Card):
        self.cards = initial_cards
        self.cardname = card.name
        self.resources = initial_resources
        self.active_resources = self.resources
        self.card = card
        self.units = []
        self.max_resources = max_resources
        self.enemy_resources = initial_resources
        self.enemy_base = Card('enemy_base', 0, 0, base_health)
        self.turn_counter = 0
        self.defenders = []
        self.defending_card = defending_card

    def add_resource(self):
        if self.cards >= 1:
            self.resources += 1
            self.cards += -1

    def draw(self):
        self.cards += 1

    def refresh(self):
        for unit in self.units:
            unit.ready()
        for unit in self.defenders:
            unit.ready()
        self.active_resources = self.resources

    def play_card(self):
        if self.active_resources >= self.card.cost:
            if self.cards >= 1:
                self.cards += -1
                self.active_resources += -self.card.cost
                new_unit = deepcopy(self.card)
                self.units.append(new_unit)
                return True
        return False

    def attack(self):
        for unit in self.units:
            target = self.get_target()
            unit.attack(target)

    def get_target(self):
        for defender in self.defenders:
            if (defender.is_dead ==0) and (defender.sentinel ==1) and self.card.saboteur ==0:
                return defender
        return self.enemy_base

    def get_attacked(self, attacking_cards):
        for card in attacking_cards:
            target = self.get_next_vulnerable_card()
            if target is not None:
                card.attack(target)

    def get_next_vulnerable_card(self):
        for unit in self.units:
            if unit.is_dead == 0:
                return unit
        return None

    def get_n_enemies(self):
        count = 0
        for card in self.defenders:
            if not card.is_dead:
                count += 1
        return count

    def get_next_ready_card(self):
        for unit in self.units:
            if unit.is_dead == 0 and unit.exhausted == 0:
                return unit
        return None

    def get_living_units(self):
        count = 0
        for unit in self.units:
            if unit.is_dead == 0:
                count += 1
        return count

    def make_defenders(self):
        enemy_cards = 1
        available_resources = self.enemy_resources
        while (available_resources >= self.defending_card.cost) and enemy_cards >=1:
            enemy_cards += -1
            available_resources += -self.defending_card.cost
            self.defenders.append(deepcopy(self.defending_card))

    def do_turn(self):
        self.turn_counter += 1
        self.refresh()
        can_play = True
        while can_play:
            can_play = self.play_card()
        self.make_defenders()
        self.attack()
        self.get_attacked(self.defenders)
        if debug:
            print(f'Turn number: {self.turn_counter}')
            print(f'Living Units: {self.get_living_units()}')
            print(f'N Enemies: {self.get_n_enemies()}')
            print(f'Cards in hand: {self.cards}')
            print(f'Damage_Done: {self.enemy_base.damage}')
        self.draw()
        self.draw()
        if self.resources < self.max_resources:
            self.add_resource()
        self.enemy_resources += 1

    def play_game(self):
        turns = []
        damage = []
        while (not self.enemy_base.is_dead) and (self.turn_counter < 20):
            self.do_turn()
            turns.append(self.turn_counter)
            damage.append(self.enemy_base.damage)
        plt.plot(turns, damage, label=f'{self.cardname}, max_resources= {self.max_resources}')
        return self.turn_counter


def make_player(strat: dict, defending_card: Card):
    max_r = strat['max_resources']
    player = Player(max_resources=max_r, card=strat['card'], defending_card=defending_card)
    return player


strategies = [{'max_resources': 2, 'card': aggro_cards['storm_trooper']},
              {'max_resources': 3, 'card': aggro_cards['storm_trooper']},
              {'max_resources': 4, 'card': aggro_cards['storm_trooper']},
              {'max_resources': 3, 'card': aggro_cards['rogue_operative']},
              {'max_resources': 6, 'card': aggro_cards['rogue_operative']},
              {'max_resources': 9, 'card': aggro_cards['rogue_operative']},
              ]

defence_strats = {'goldfish': defending_cards['goldfish'],
                  'technicians': defending_cards['technician'],
                  'guard': defending_cards['cloud_guard']}

trooper_ttk = []
operative_ttk = []
trooper_rm = []
operative_rm = []
for defence in defence_strats:
    for strategy in strategies:
        if debug:
            print(f'Strategy: {strategy}')
            print(f'Defence: {defence}')
        player = make_player(strategy, defence_strats[defence])
        if strategy['card'].name == 'storm_trooper':
            trooper_rm.append(strategy['max_resources'])
            ttk = player.play_game()
            trooper_ttk.append(ttk)
        if strategy['card'].name == 'rogue_operative':
            operative_rm.append(strategy['max_resources'])
            ttk = player.play_game()
            operative_ttk.append(ttk)
    plt.axhline(25, label='25 health')
    plt.axhline(30, label='30 health')
    plt.xlabel('turn number')
    plt.ylabel('damage')
    plt.title(f'defending strategy: {defence}')
    plt.legend()
    plt.show()

plt.clf()
plt.plot(trooper_rm, trooper_ttk, color='r', marker='o',
             linestyle='None', label='troopers')
plt.plot(operative_rm, operative_ttk, color='b', marker='o',
             linestyle='None', label='operatives')
plt.xlabel('max resources')
plt.ylabel(f'turns to kill {base_health} health base')
plt.legend()
plt.show()