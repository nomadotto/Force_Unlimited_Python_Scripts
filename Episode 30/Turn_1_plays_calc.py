import random
import matplotlib.pyplot as plt
from scipy.stats import hypergeom

DECKSIZES = [60, 50,45]
turn_1_plays = [i for i in range(1,20)]

# the goal of this script is to figure out how many turn-1 plays you need to guarentee a turn-1 play

prob_hit = {}
min_count = {}
seen_cards = 6
for decksize in DECKSIZES:
    label = f'Decksize : {decksize} '
    prob_hit[label] = []
    min_count[label] = max(turn_1_plays)
    for card_count in turn_1_plays:
        hypergeo = hypergeom(decksize,card_count, seen_cards)
        prob_miss = hypergeom.cdf(0, decksize, card_count, seen_cards)**2
        prob_hit[label].append(1-prob_miss)
        if (1-prob_miss> .95) and (min_count[label]>card_count):
            min_count[label] = card_count

for label in min_count:
    print(f"{label} - optimal 1st turn plays: {min_count[label]}")

with plt.xkcd():
    for label in prob_hit.keys():
        plt.plot(turn_1_plays, [i*100 for i in prob_hit[label]], label=label)
    plt.ylabel("% chance of getting a turn-1 play")
    plt.xlabel("Number of turn-1 plays in the deck")
    plt.ylim(0, 120)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
           ncol=3, fancybox=True, shadow=True)
    plt.show()
