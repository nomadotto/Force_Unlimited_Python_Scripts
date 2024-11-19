import random

from scipy.stats import hypergeom
from matplotlib import pyplot as plt


DECKSIZES = [50,56]

COMBO_RESOURCE = 3
CARD_COPIES = 6

def cards_seen_by_resource(resource):
    return 6 +max([(resource-2)*2,0])

seen_cards = cards_seen_by_resource(COMBO_RESOURCE)
prob_hit = []
for decksize in DECKSIZES:
    hypergeo = hypergeom(decksize,CARD_COPIES, seen_cards)
    prob_miss = hypergeom.cdf(0, decksize, CARD_COPIES, seen_cards)**2
    prob_hit.append(1-prob_miss)

print(prob_hit)
# gives 67% vs. 62%, so you're losing 5% chance to draw your ramp

# let's say you have the following odds of winning [with / without ramp]-
# Aggro - [25, 20]
# Midrange - [70,60]
# Fringe - [70,60]
# Now for the control breakdown -
# Control (56 card deck) - [65, 55]
# Control (50 card deck) - [55,45]

# metagame = [% Aggro, % Midrange, % Control, % Fringe]


BIG_DECK_EDGE = .02
BASE_WIN = {'Aggro':.20, 'Midrange':.40, 'Control_Big':.5 + BIG_DECK_EDGE, 'Control_Small':.50}
#EDGE = {'Aggro':.05, 'Midrange':.1, 'Control_Big':.1, 'Control_Small':.1}
N_TRIALS = 100000
DRAW_ODDS = {'Small':prob_hit[0], 'Big':prob_hit[1]}
METAGAMES = {'even':[5,5,5], 'control':[1,1,8]}

def do_matchup(win_odds):
    return random.random() <= win_odds


def get_win_odds(oppo, us, edge):
    if oppo == 'Control':
        win_key = f'{oppo}_{us}'
    else:
        win_key = f'{oppo}'
    win_odds = BASE_WIN[win_key]
    # check if we draw our ramp
    if random.random() <= DRAW_ODDS[us]:
        win_odds += edge
    return win_odds


def determine_opponent(n_aggro, n_midrange, n_control):
    oppo_list = []
    aggro_list = ['Aggro']*n_aggro
    midrange_list = ['Midrange']*n_midrange
    control_list = ['Control']*n_control
    oppo_list += aggro_list
    oppo_list += midrange_list
    oppo_list += control_list
    oppo = random.choice(oppo_list)
    return oppo

observed_wins = {}
for metagame in METAGAMES:
    for us in ['Big', 'Small']:
        key = f'metagame: {metagame} us:{us}'
        observed_wins[key] =[]
        for edge in [.01*i for i in range(1,20)]:
            wins = 0
            for trial in range(N_TRIALS):
                oppo = determine_opponent(*METAGAMES[metagame])
                odds = get_win_odds(oppo, us, edge)
                if do_matchup(odds):
                    wins += 1
            observed_wins[key].append(wins/N_TRIALS)
print(observed_wins)

with plt.xkcd():
    for key in observed_wins:
        plt.plot([.01*i for i in range(1,20)], observed_wins[key], label=key)

    plt.title("Deck Size Analysis")
    plt.ylabel("Win Percentage")
    plt.xlabel("Edge")
    plt.legend(loc='upper left')
plt.show()