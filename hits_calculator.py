import matplotlib.pyplot as plt
from scipy.stats import hypergeom
import math
import random

STARTING_DECK_SIZE = 30
MAX_HITS = 25
N_TRIALS = 10000

n_draws = {'Recruit / Mon Mothma': 5, 'Takeoff': 8, 'Vader for 3s': 10, 'Vader for 1s': 10, 'Tarkin': 5, 'Jabba': 8}
n_keeps = {'Recruit / Mon Mothma': 1, 'Takeoff': 2, 'Vader for 3s': 1, 'Vader for 1s': 3, 'Tarkin': 2, 'Jabba': 1}
cost = {'Recruit / Mon Mothma': 1, 'Takeoff': 2, 'Vader for 3s': 7, 'Vader for 1s': 7, 'Tarkin': 4, 'Jabba': 4}


def calc_deck_size(card_cost):
    turn = max(card_cost - 1, 1)
    cards_drawn = 6 + 2 * (turn - 1)
    return STARTING_DECK_SIZE - cards_drawn


results = {}
break_point = {}
for key in n_draws.keys():
    break_point[key] = MAX_HITS
    results[key] = []
    deck_size = calc_deck_size(cost[key])

    for n_hits in range(0, MAX_HITS):
        n_actual_hits = math.floor(deck_size/STARTING_DECK_SIZE*n_hits)
        prob = hypergeom.cdf(n_keeps[key] - 1, deck_size, n_actual_hits, n_draws[key])
        if prob < .05 and n_hits < break_point[key]:
            break_point[key] = n_hits
        results[key].append(1-prob)


def make_plot(hyper_results):
    with plt.xkcd():
        fig = plt.figure()
        ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_yticks([])
        ax.set_ylim([0, 1])
        ax.set_xlabel("Number of 'Hits' in the deck")
        ax.set_ylabel("Prob of Maximal Value")
        fig.suptitle(f'{STARTING_DECK_SIZE} Card Decks')

    for distro in hyper_results:
        x = range(0, MAX_HITS)
        y = hyper_results[distro]
        ax.plot(x, y, label=distro)

    with plt.xkcd():
        ax.legend()
    plt.show()


def calc_low_cost(N_low):
    """ We want an equal number of 1s, 2s and 3s
    going in the order +2 , +3, +1 up through N_low"""
    base_number = N_low // 3
    ones = base_number
    if N_low % 3 == 2:
        twos = base_number + 1
        threes = base_number + 1
    elif N_low % 3 == 1:
        twos = base_number + 1
        threes = base_number
    else:
        twos = base_number
        threes = base_number

    return ones, twos, threes


def make_vader_deck(ones, twos, threes):
    deck = []
    free_cards = STARTING_DECK_SIZE - (ones + twos + threes)
    deck += [1] * ones
    deck += [2] * twos
    deck += [3] * threes
    deck += [0] * free_cards
    random.shuffle(deck)
    assert len(deck) == STARTING_DECK_SIZE
    deck_size = calc_deck_size(7)
    return deck[:deck_size]


def check_results(sample):
    if 3 in sample:
        return 1
    if (2 in sample) and (1 in sample):
        return 1
    if (sum(sample) % 2) and (sum(sample) > 1):  # odd sum but no 3 and no 2 and 1 -> odd number of 1's
        return 1
    else:
        return 0


def full_vader_calc():
    hits = []
    for N_low in range(0,MAX_HITS):
        ones, twos, threes = calc_low_cost(N_low)
        hits.append(0)
        for i in range(N_TRIALS):
            deck = make_vader_deck(ones, twos, threes)
            random.shuffle(deck)
            sample = deck[0:10].copy()
            hits[N_low] += check_results(sample)
    results = [i / N_TRIALS for i in hits]
    return results


hits = full_vader_calc()
print(hits)
v_break = MAX_HITS
for i in range(len(hits)):
    if hits[i] > .95 and i < v_break:
        v_break = i

break_point['Realistic Vader'] = v_break
results['Realistic Vader'] = hits

print(break_point)
make_plot(results)