import random
import matplotlib.pyplot as plt
from Binomial_Calculator import calc_binom_limit, do_binom_test

deck_edges = {'En Vogue': .1}
n_rounds = 8
n_decks = {'En Vogue': 43,
           "SWV": 32,
           "Sade": 25,
           "TLC": 25,
           "Boyz II Men": 20,
           "Bell Biv DeVoe": 7,
           "Color Me Badd": 5,
           "PM Dawn": 3}  # must always have an even total. I don't handle byes in this code


class Player:  # this Player class is kinda bare-bones, but we can expand it in the future
    def __init__(self, deck):
        self.deck = deck
        self.record = {'Wins': 0, 'Loss': 0, 'Tie': 0}
        if self.deck in deck_edges:
            self.edge = deck_edges[self.deck]
        else:
            self.edge = 0

    def __repr__(self):
        return f"{self.deck}: {self.record}"


def play_game(player1: Player, player2: Player) -> int:
    """
    Play a single game, no Ties allowed. We're assuming things are a coin-flip, with some decks having an "edge"
    with the edge uniformly modifying their win rates by some amount, e.g. an edge of .1 -> 60% win rate against 0 edge
    :param player1: a Player
    :param player2: Another Player
    :return: 0 if P1 wins, 1 if P2 wins
    """
    rand = random.random()  # roll a uniform random number between 0 and 1
    line = .5 + player1.edge - player2.edge  # add P1's edge and subtract p2's edge

    if rand <= line:  # if we're below the line, p1 wins
        return 0
    else:
        return 1


def determine_winner(player1: Player, player2: Player, record: list) -> None:
    """
    figure out which player won and assign them the win
    :param player1: a Player
    :param player2: another Player
    :param record: a list of wins in the form [P1wins, P2wins]
    :return: none
    """
    if record[0] > record[1]:
        player1.record['Wins'] += 1
        player2.record['Loss'] += 1
    elif record[1] > record[0]:
        player1.record['Loss'] += 1
        player2.record['Wins'] += 1
    else:
        # it's a tie
        player1.record['Tie'] +=1
        player2.record['Tie'] += 1


def play_set(player1: Player, player2: Player) -> list:
    """
    Play a set of 2-3 games between two Players
    :param player1: A Player
    :param player2: Another Player
    :return: the results of the game [P1wins, P2wins]
    """
    game_1 = play_game(player1, player2)
    game_2 = play_game(player1, player2)  # always play 2 games
    results = [0, 0]
    results[game_1] += 1
    results[game_2] += 1
    if (results == [2, 0]) or (results == [0, 2]):  # if one player won twice
        determine_winner(player1, player2, results)
        return results  # we're done
    else:  # otherwise
        game_3 = play_game(player1, player2)
        results[game_3] += 1
        determine_winner(player1, player2, results)
        return results  # Play a 3rd game and we're done


def get_random(players: list) -> Player:
    """
    pop a random player from a list
    :param players: a list of Players
    :return: a Player
    """
    random_select = random.randrange(0, len(players))  # pick a random player, more efficient than shuffle (I'm told)
    return players.pop(random_select)


def make_win_groups(players: list) -> dict:
    """
    Sort players into lists based on N_wins, no Ties allowed
    :param players: a list of players
    :return: a dict of the form {N: [p1, p2, p3], N-1 [p4,p5,p6]}
    """
    p_lists = {}  # make a blank dict
    for player in players:
        if player.record["Wins"] in p_lists:  # if we have a key for N_wins
            p_lists[player.record["Wins"]].append(player)  # put that player into the list mapped by that key
        else:  # otherwise
            p_lists[player.record["Wins"]] = [player]  # make a new list, with that player with N_wins for a key
    return p_lists


def play_round(players):
    """
    Play a round of Tournment SWU, no Byes, Drops, or Ties allowed
    :param players: a list of Players
    :return: None
    """
    n_games = 0
    p_lists = make_win_groups(players)  # sort the players into lists by order of wins (since we don't allow ties)
    while p_lists:
        top = max(p_lists)  # get all players with the most wins
        to_be_paired = p_lists[top]
        while len(to_be_paired) > 1:  # if there's more than 1 player left
            p1 = get_random(to_be_paired)  # match two players from the group and play
            p2 = get_random(to_be_paired)
            results = play_set(p1, p2)
            n_games += 1
        if len(to_be_paired) == 1:  # if we have 1 player left
            if (top - 1) in p_lists:
                p_lists[top - 1].append(to_be_paired.pop())  # move them to the lower list if it exists
            else:
                p_lists[top - 1] = [to_be_paired.pop()]
        if len(to_be_paired) == 0:  # no-one is left
            del(p_lists[top])


def make_players(n_decks: dict) -> list:
    """
    make players with the appropriate number of decks
    :param n_decks: a dict of decks and counts, like so {"Boba": N, "Kiki": M"
    :return: a list of players
    """
    players = []
    for deck in n_decks:
        for n in range(n_decks[deck]):
            players.append(Player(deck))
    return players


def make_histogram(players):
    """
    Code for making win Histogram distributions. Looks awful, don't recommend. Will want to expand on in the future
    :param players: a list of Players
    :return: None, just plots
    """
    max_wins = n_rounds*3

    deck_wins = {}
    for player in players:
        if player.deck in deck_wins:
            wins = player.record['Wins']
            deck_wins[player.deck][wins] += 1
        else:
            deck_wins[player.deck] = [0]*max_wins
            wins = player.record['Wins']
            deck_wins[player.deck][wins] += 1
    with plt.xkcd():
        plt.clf()
        bins = max_wins
        for deck in deck_wins:
            plt.hist(deck_wins[deck], label=deck, bins=bins)
        plt.legend()
        plt.xlabel("Number of Wins")
        plt.ylabel("Number of Decks")
        plt.show()


def make_deck_info(players: list) -> dict:
    """
    make deck information from simulation results, so we can feed it into the Binomial Calculator I wrote
    :param players: a list of Players
    :return: a deck info dictionary  of the form {"deckname" : {"Wins": X, "Loss": Y, "Tie": Z}, "deckname2": ...}
    """
    decks = {}
    for player in players:
        if player.deck in decks:
            for k in ['Wins', 'Loss', 'Tie']:
                decks[player.deck][k] += player.record[k]
        else:
            decks[player.deck] = {"Wins": 0, "Loss": 0, "Tie": 0}
            for k in ['Wins', 'Loss']:
                decks[player.deck][k] += player.record[k]

    return decks
    

players = make_players(n_decks)
for i in range(n_rounds):
    play_round(players)

fake_deck_info = make_deck_info(players)  # make the fake deck info


def plot_decks(decks):
    """
    Make a plot of the expected wins based on observed performance vs. hypothetical coin-flip performance
    not rigorous, but useful for quick evaluation. Not using the one in Binomial Calculator because
    we want to pull out the "power" deck specifically
    :param decks: a dict of dicts of the form {"deckname" : {"Wins": X, "Loss": Y, "Tie": Z}, "deckname2": ...}
    :return: None, just makes a plot
    """
    # I'm assuming deck 0 is the advantaged deck, should re-write to pull out things procedurally
    #
    base_lows = [decks[deck]['base_region'][0] for deck in decks]  # List comprehension FTW
    base_highs = [decks[deck]['base_region'][1] for deck in decks]
    expected_lows = [decks[deck]['exp_region'][0] for deck in decks]
    expected_highs = [decks[deck]['exp_region'][1] for deck in decks]
    observed_wins = [decks[deck]['Wins'] for deck in decks]
    ylabels = [deck for deck in decks]
    ys = [i for i in range(len(decks))]
    y1s = [y - .15 for y in ys]  # adjusting down slightly for one
    y2s = [y+.15 for y in ys]  # and up slightly for the other
    with plt.xkcd():
        plt.clf()
        plt.hlines(y1s, xmin=base_lows, xmax=base_highs, color="black", label="Coinflip vs Field")
        plt.hlines(y2s[1:], xmin=expected_lows[1:], xmax=expected_highs[1:], color='red', linestyles="dashed",
                   label="Assuming Observed Winrate")
        plt.scatter(observed_wins[1:], y2s[1:], c="blue", marker='o', label="Observed Wins")

        # plotting the power-deck on its own
        plt.hlines(y2s[0], xmin=expected_lows[0], xmax=expected_highs[0], color='green', linestyles="dotted",
                   label="Advantaged Winrate")
        plt.scatter(observed_wins[0], y2s[0], c="purple", marker='o', label="Observed Advantaged Wins")
        plt.yticks(ys, ylabels)
        plt.xlabel("Number of Wins")
        plt.legend()
        plt.show()


for deck in fake_deck_info:
    base_region, exp_region = calc_binom_limit(fake_deck_info[deck])
    fake_deck_info[deck]['base_region'] = base_region
    fake_deck_info[deck]['exp_region'] = exp_region
    print(f"{deck}: chance results could come from a coinflip - {do_binom_test(fake_deck_info[deck]):.1%}")

plot_decks(fake_deck_info)
