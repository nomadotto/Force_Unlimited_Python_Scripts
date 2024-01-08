import matplotlib.pyplot as plt
from scipy.stats import hypergeom

STARTING_DECK_SIZE = 50
CARD_COUNTS = {'A': 6, 'B': 6}
COMBO_COST = 7


def calc_n_draws(card_cost):
    turn = max(card_cost - 1, 1)
    cards_drawn = 6 + 2 * (turn - 1)
    return cards_drawn


def get_draw_odds(combo_cost, n_copies):
    draws = calc_n_draws(combo_cost)
    prob_miss = hypergeom.cdf(0, STARTING_DECK_SIZE, n_copies, draws)
    prob_hit = 1-prob_miss
    return prob_hit


total_prob = 1
for card in CARD_COUNTS:
    card_prob = get_draw_odds(COMBO_COST, CARD_COUNTS[card])
    total_prob = total_prob * card_prob

print("Probability of Drawing all parts of an N-Card Combo by execution turn without mulligans")
print(f"N_Cards in combo: {len(CARD_COUNTS)}")
print(f"Combo Cost : {COMBO_COST}")
for card in CARD_COUNTS:
    print(f'Copies of card "{card}": {CARD_COUNTS[card]}')
print(f"Total Probability: {total_prob}")
