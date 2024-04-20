import matplotlib.pyplot as plt
from scipy.stats import hypergeom

# we're using this to calculate the number of 2-cost units you need in your deck, assuming
# 1) you always want a turn-1 play and
# 2) you will always mulligan if you don't have a 2-cost unit and
# 3) will never mulligan if you have a 2-cost unit

STARTING_DECK_SIZE = 50
UNIT_COST = 2


def calc_n_draws(card_cost) -> int:
    """
    Given the cost of a combo, calculate the number of draws needed to get there, assuming no ramp
    :param card_cost: the cost of the combo
    :return: the number of cards drawn
    """
    turn = max(card_cost - 1, 1)
    cards_drawn = 6 + 2 * (turn - 1)
    return cards_drawn


def get_draw_odds(card_cost, n_copies) -> float:
    """
    get the hypergeometric odds of NOT drawing at least one copy of a card
    :param card_cost: the cost of the card
    :param n_copies: the number of copies of the card in the deck
    :return: the hypergeometric odds of drawing at least one of the copies of the card
    """
    draws = calc_n_draws(card_cost)
    prob_miss = hypergeom.cdf(0, STARTING_DECK_SIZE, n_copies, draws)
    return prob_miss


def make_plot(results) -> None:
    """
    make a plot of the likihood of drawing at least 1 2-cost unit, depending on the number of 2-cost units in your deck
    :param results: a list of probabilities
    :return: None
    """
    with plt.xkcd():
        fig = plt.figure()
        ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_yticks([])
        ax.set_ylim([0, 1])
        ax.set_xlabel(f"Number of {UNIT_COST} units in the deck")
        ax.set_ylabel(f"Prob of Seeing at least one Unit on {UNIT_COST-1}th turn")
        fig.suptitle(f'{STARTING_DECK_SIZE} Card Decks')
        x = range(1, 30)
        y = results
        ax.plot(x, y)
    plt.show()


success_rate = []
for copies in range(1, 30):
    hit_rate = 1-(get_draw_odds(UNIT_COST, copies)**2)
    # need to miss on both initial hand and mulligan, so we want to calculate the odds of missing twice and taking
    # the conjugate probability
    success_rate.append(hit_rate)
    if hit_rate > .95:  # we're assuming we want a 95% or greater hit rate
        print(f"copies: {copies}, {hit_rate}")
make_plot(success_rate)
