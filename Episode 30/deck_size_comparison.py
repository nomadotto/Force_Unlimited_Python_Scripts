import random
import matplotlib.pyplot as plt
# this script calculates the odds of getting all parts of an N-card combo using a Monte Carlo Simulation

starting_deck_info = [{'size':50, 'hand':6,'mull':True, 'label':'standard', 'color':'k'},
                      {'size':60, 'hand':6,'mull':True, 'label':'Green', 'color':'g'},
                      {'size':45, 'hand':6,'mull':True, 'label':'Red', 'color':'r'},
                      {'size':50, 'hand':5, 'mull':True, 'label':'Blue', 'color':'b'},
                      {'size':50, 'hand':9, 'mull':False, 'label':'Yellow', 'color':'y'}]
# we're not going to model the full complexity of the Yellow base, because for most combos, it doesn't
# matter that we're putting back 3 cards
CARD_COUNTS = [1,3,12]
labels = []
REC_RANGE = range(2,9)


N_TRIALS = 100000  # how many times to run the Monte Carlo


def make_deck(deck_size, card_count) -> list:
    """
    make a deck of cards as a list, consisting of the cards we want in the appropriate proportions and "miss"
    :param deck_size: size of the starting deck
    :param card_count: number of cards of a type we care about
    :return: a list of cards
    """
    deck = []  # treating the deck as a list of cards which are either in the card_counts or a 'miss'

    cards = ['hit'] * card_count
    deck += cards
    missing_cards = deck_size - len(deck)
    deck += ['miss']*missing_cards
    return deck


def mulligan(hand, threshold) -> bool:
    """
    figure out if we need to mulligan
    :param hand: our hand
    :param threshold: how many of the needed cards we want before we keep a hand
    :return: should we mulligan or not?
    """
    hits = hand.count('hit')
    return hits < threshold


def resource(hand) -> list:
    if 'miss' in hand:  # if we have a miss, just resource that
        hand.pop(hand.index('miss'))
        return hand
    else: # ooops all bangers, just resource 1 card
        hand.pop()
    return hand


def starting_hand(deck, threshold, hand_size, mullable=True) -> tuple:
    random.shuffle(deck)  # shuffle the deck
    hand = deck[:hand_size]  # draw hand_size
    if mullable:  # can we take a mulligan?
        if mulligan(hand, threshold):  # should we take a mulligan?
            # start over, but without the mulligan option
            deck, hand = starting_hand(deck, threshold, hand_size = hand_size, mullable=False)
    deck = deck[hand_size:]  # remove them from the deck
    resource(hand)  # resource a card
    resource(hand)  # and again

    return deck, hand


def take_turn(deck, hand) -> tuple:
    hand += deck[:2]  # draw 2
    deck = deck[2:]
    resource(hand)  # resource a card
    return deck, hand


def hand_check(hand, needed) -> bool:
    check_value = hand.count('hit')
    return check_value >= needed


def do_trial(deck_info, card_count, resources) -> tuple:
    deck_size = deck_info['size']
    hand_size = deck_info['hand']
    mullable = deck_info['mull']
    starting_deck = make_deck(deck_size=deck_size, card_count=card_count)  # make the deck
    # draw starting hand and do mulligan calculations
    # we are assuming we need a single copy of a card
    deck, hand = starting_hand(deck = starting_deck, threshold=1, mullable=mullable, hand_size=hand_size)
    if hand_check(hand, 1):  # did we strike gold?
        return 1, 1  # if so, we win on turn 1

    current_resources = 2  # if not, let's start taking turns
    while current_resources < resources:  # we're only checking up through the Nth turn.
        deck, hand = take_turn(deck, hand)  # take a turn
        if hand_check(hand, 1):  # did we win?
            return 1, current_resources-1 # we won on the nth turn
        current_resources += 1  # doing thing a little out of order, but it makes sense
    return 0, None  # we didn't hit, so don't count successes


def calc_odds(deck_info, n_cards, resources):
    i=0
    hits = 0
    while i < N_TRIALS:
        hit, turn = do_trial(deck_info, n_cards, resources)
        i+=1
        hits += hit
    print(f"Hit {hits} times in {N_TRIALS} with {n_cards} cards in {deck_info['label']}-deck "
          f"{resources-1}")
    return hits

hit_rate = {}

for card_count in CARD_COUNTS:
    for starter in starting_deck_info:
        tag = f'{card_count} cards in {starter['label']} deck'
        hit_rate[tag] = [[],starter['color']]
        for resources in REC_RANGE:
            hits = float(calc_odds(deck_info=starter, n_cards=card_count, resources=resources))
            hit_rate[tag][0].append(hits/N_TRIALS)


with plt.xkcd():
    for tag in hit_rate.keys():

        plt.plot([i-1 for i in REC_RANGE],  [i*100 for i in hit_rate[tag][0]], label=tag,
                 color=hit_rate[tag][1])
    plt.xlabel('Turn Number')
    plt.ylabel('% chance of Drawing at least 1 card of type')
    plt.ylim(0,120)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=len(CARD_COUNTS), fancybox=True, shadow=True)
plt.show()
