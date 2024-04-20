import random

# this script calculates the odds of getting all parts of an N-card combo using a Monte Carlo Simulation

STARTING_DECK_SIZE = 50
CARD_COUNTS = [{'Heroic Sacrifice': 3, 'Traitorous': 3},
               {'DJ Death Star': 3, 'Wanted': 3, 'Resupply': 3},
               {'DJ Death Star': 3, 'Wanted': 3, 'Resupply': 3, 'Unit Boba': 3}]
labels = ["2-card", "3-card", "4-card"]

# let's say we have an N-card combo with M copies of each card
COMBO_COST = 6  # this is the resource we need to combo by, if you're ok with waiting, adjust upward
N_TRIALS = 100000  # how many times to run the Monte Carlo


def make_deck(card_counts) -> list:
    """
    make a deck of cards as a list, consisting of the cards we want in the appropriate proportions and "miss"
    :param card_counts: a dictionary of card names and counts
    :return: a list of cards
    """
    deck = []  # treating the deck as a list of cards which are either in the card_counts or a 'miss'
    for card in card_counts:
        cards = [card] * card_counts[card]
        deck += cards
    missing_cards = STARTING_DECK_SIZE - len(deck)
    deck += ['miss']*missing_cards
    return deck


def mulligan(hand, threshold, card_counts) -> bool:
    """
    figure out if we need to mulligan
    :param hand: our hand
    :param threshold: how many of the needed cards we want before we keep a hand
    :param card_counts: a dict of cards with counts
    :return: should we mulligan or not?
    """
    needed_cards = 0
    max_copies = max(card_counts.values())
    min_copies = min(card_counts.values())
    for key in card_counts:
        if key in hand:
            needed_cards += max_copies/card_counts[key]  # how many of the needed cards do we have?
            #  we weight the cards by how many copies they have. For example, if we have 12 copies of one card,
            #  it counts for 1/4 as much as a card we have 3 copies of
    # if we don't have at least threshold of value combo pieces, we throw it away
    return needed_cards < threshold*max_copies/min_copies  


def resource(hand, card_counts) -> list:
    if 'miss' in hand:  # if we have a miss, just resource that
        hand.pop(hand.index('miss'))
        return hand
    # if we don't, we figure out the piece we have the most copies of and resource that
    max_count = 0
    max_card = None
    for card in card_counts:
        if hand.count(card) > max_count:  # we have a new largest number of copies
            max_card = card
            max_count = hand.count(card)
    hand.pop(hand.index(max_card))
    return hand


def starting_hand(deck, threshold, card_count, mullable=True) -> tuple:
    random.shuffle(deck)  # shuffle the deck
    hand = deck[:6]  # draw 6
    if mullable:  # can we take a mulligan?
        if mulligan(hand, threshold, card_count):  # should we take a mulligan?
            # start over, but without the mulligan option
            deck, hand = starting_hand(deck, threshold, card_count, False)

    resource(hand, card_count)  # resource a card
    resource(hand, card_count)  # and again
    deck = deck[6:]  # remove them from the deck
    return deck, hand


def take_turn(deck, hand, card_counts) -> tuple:
    hand += deck[:2]  # draw 2
    deck = deck[2:]
    resource(hand, card_counts)  # resource a card
    return deck, hand


def combo_check(hand, card_counts) -> bool:
    check_value = 0
    for card in card_counts:  # we want at least 1 copy of each combo piece
        if card in hand:
            check_value += 1
    return check_value == len(card_counts)


def do_trial(n_successes, threshold, combo_cost, card_counts) -> int:
    starting_deck = make_deck(card_counts)  # make the deck
    deck, hand = starting_hand(starting_deck, threshold, card_counts)   # draw starting hand and do mulligan calculations
    if combo_check(hand, card_counts):  # did we strike gold?
        n_successes += 1
        return n_successes  # if so, we win

    current_resources = 2  # if not, let's start taking turns
    while current_resources < combo_cost:  # we're only checking up through the combo turn.
        deck, hand = take_turn(deck, hand, card_counts)  # take a turn
        if combo_check(hand, card_counts):  # did we win?
            n_successes += 1
            return n_successes
        current_resources += 1  # doing thing a little out of order, but it makes sense
    return n_successes  # we didn't hit, so don't count successes


def get_optimal_hold(card_counts) -> int:
    successes = []
    for hold in range(len(card_counts)+1):
        trial_successes = 0
        for i in range(N_TRIALS):
            trial_successes = do_trial(trial_successes, hold, COMBO_COST, card_counts)
        print(f"{trial_successes} successes in {N_TRIALS} trials, a {trial_successes / N_TRIALS:.2%} hit rate with a"
              f" Threshold of {hold} for an {len(card_counts)}-card combo by turn {COMBO_COST-1}")
        successes.append(trial_successes)
    return successes.index(max(successes))


for card_count in CARD_COUNTS:
    get_optimal_hold(card_count)

