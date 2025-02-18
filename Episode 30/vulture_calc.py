import random
import matplotlib.pyplot as plt
from scipy.stats import hypergeom

DECKSIZES = [60, 50,45]
vultures = [i for i in range(1,16)]

# the goal of this script is to figure out how many vultures you'll want to make sure you have seen
# 4 by turn 3


prob_hit = {}
min_count = {}
seen_cards = 6
for decksize in DECKSIZES:
    label = f'Decksize : {decksize} '
    prob_hit[label] = []
    min_count[label] = max(vultures)
    for card_count in vultures:
        hypergeo = hypergeom(decksize,card_count, seen_cards)
        prob_miss = hypergeom.cdf(3, decksize, card_count, seen_cards)**4
        prob_hit[label].append(1-prob_miss)
        if (1-prob_miss> .95) and (min_count[label]>card_count):
            min_count[label] = card_count

for label in min_count:
    print(f"{label} - optimal 1st turn plays: {min_count[label]}")

with plt.xkcd():
    for label in prob_hit.keys():
        plt.plot(vultures, [i*100 for i in prob_hit[label]], label=label)
    plt.ylabel("% chance of getting 4 vultures in your starting hand")
    plt.xlabel("Number of vultures ")
    plt.ylim(0, 120)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
           ncol=3, fancybox=True, shadow=True)
    plt.show()
