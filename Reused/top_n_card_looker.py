import matplotlib.pyplot as plt
from numpy.ma.extras import average
from scipy.stats import hypergeom


# we're using this to calculate number of matching cards you need if you're
# 1) using a card that looks at the top N cards of your deck
# 2) You want MAX VALUE
# 3) you have no card selection

STARTING_DECK_SIZE = 50
LOOKS = 8
N_CARDS = 2



def get_draw_odds(draws, n_copies, n_cards) -> float:
    """
    get the hypergeometric odds of NOT drawing at least n_cards copy of a card from the top draws cards
    :param draws: the number of cards you're looking at from the top of the deck
    :param n_copies: the number of copies of the card in the deck
    :param n_cards: the number of cards for MAX VALUE
    :return: the hypergeometric odds of drawing at least one of the copies of the card
    """
    prob_miss = hypergeom.cdf(n_cards -1, STARTING_DECK_SIZE, n_copies, draws)
    return prob_miss

def get_average_number_of_cards(draws, n_copies, max_cards):
    average_cards = 0
    for cards in range(max_cards+1):
        average_cards += cards*hypergeom.pmf(cards, STARTING_DECK_SIZE, n_copies, draws)
    average_cards += max_cards*(1-hypergeom.cdf(max_cards, STARTING_DECK_SIZE, n_copies, draws))
    return average_cards

def make_odds_plot(results) -> None:
    """
    make a plot of the likihood of drawing at least 1 2-cost unit, depending on the number of 2-cost units in your deck
    :param results: a list of probabilities
    :return: None
    """
    with plt.xkcd():
        fig = plt.figure()
        ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_ylim([0, 1])
        ax.set_xlabel(f"Number of matching cards in the deck")
        ax.set_ylabel(f"Prob of seeing at least {N_CARDS} matching cards from the top {LOOKS} cards")
        fig.suptitle(f'{STARTING_DECK_SIZE} Card Decks')
        x = range(1, 30)
        y = results
        ax.plot(x, y)
    plt.show()

def make_average_cards_plot(results):
    with plt.xkcd():
        fig = plt.figure()
        ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_ylim([0, N_CARDS+1])
        ax.set_xlabel(f"Number of matching cards in the deck")
        ax.set_ylabel(f"average number of  matching cards from the top {LOOKS} cards, with a max of {N_CARDS}")
        fig.suptitle(f'{STARTING_DECK_SIZE} Card Decks')
        x = range(1, 30)
        y = results
        ax.plot(x, y)
    plt.show()


success_rate = []
average_cards = []
for copies in range(1, 30):
    hit_rate = 1-get_draw_odds(draws = LOOKS, n_copies=copies, n_cards=N_CARDS)
    c = get_average_number_of_cards(draws=LOOKS, n_copies=copies, max_cards=N_CARDS)
    # need to miss on both initial hand and mulligan, so we want to calculate the odds of missing twice and taking
    # the conjugate probability
    success_rate.append(hit_rate)
    average_cards.append(c)
    if hit_rate > .95:  # we're assuming we want a 95% or greater hit rate
        pass
        # print(f"copies: {copies}, max_hit_rate: {hit_rate}")
    if c > 1:
        print(f"copies: {copies}, average_cards_drawn: {c}")
make_odds_plot(success_rate)
make_average_cards_plot(average_cards)
