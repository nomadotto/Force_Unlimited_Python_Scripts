import statsmodels.stats.proportion as prop
import matplotlib.pyplot as plt


deck_info = {'Boba': {"Wins": 198, "Loss": 128, "Tie": 0},
             'Sabine': {"Wins": 101, "Loss": 112, "Tie": 0},
             'Darth': {"Wins": 73, "Loss": 98, "Tie": 0},
             'Iden': {"Wins": 90, "Loss": 93, "Tie": 0},
             "Leia": {"Wins": 72, "Loss": 70, "Tie": 0},
             "GI": {"Wins": 14, "Loss": 14, "Tie": 0},
             "Chirrut": {"Wins": 25, "Loss": 24, "Tie": 0},
             "Palp": {"Wins": 22, "Loss": 18, "Tie": 0},
             "Han": {"Wins": 23, "Loss": 17, "Tie": 0}
             }


def calc_ngames(deck: dict) -> int:
    """
    calculate the number of games played by a deck
    :param deck: a deck record, of the form {"Wins": X, "Loss": Y, "Tie": Z}
    :return: X + Y + Z (Wins + Losses + Ties)
    """
    ngames = deck['Wins'] + deck['Loss'] + deck["Tie"]
    return ngames


def calc_binom_limit(deck: dict) -> tuple:
    """
    Calculate the expected limits on the number of wins for a deck which has played N games
    give both an evaluation of expected limits based on an assumed .5 win-rate against the field
    and the observed win-rate from the results
    :param deck: a deck record, of the form {"Wins": X, "Loss": Y, "Tie": Z}
    :return: (base_lower, base_upper), (expected_lower, expected_upper)
    """
    ngames = calc_ngames(deck)
    wins = deck['Wins']  # number of games played
    # first, calculate the expected limits on wins for a deck which plays N games with a win-rate of .5
    base_odds = .5
    base_region = prop.binom_test_reject_interval(value=base_odds, nobs=ngames)  # alpha = .05 by default

    # then, calculate the expected limits for a deck which plays N games with a win-rate of whatever was observed
    observed_odds = wins/ngames
    expected_region = prop.binom_test_reject_interval(observed_odds, ngames)
    return base_region, expected_region


def do_binom_test(deck: dict) -> float:
    ngames = calc_ngames(deck)
    wins = deck['Wins']
    prob = prop.binom_test(wins, ngames)
    return prob


def plot_decks(decks):
    """
    Make a plot of the expected wins based on observed performance vs. hypothetical coin-flip performance
    not rigorous, but useful for quick evaluation
    :param decks: a dict of dicts of the form {"deckname" : {"Wins": X, "Loss": Y, "Tie": Z}, "deckname2": ...}
    :return: None, just makes a plot
    """
    base_lows = [[decks[deck]['base_region'][0] for deck in decks]]  # List comprehension FTW
    base_highs = [[decks[deck]['base_region'][1] for deck in decks]]
    expected_lows =[[decks[deck]['exp_region'][0] for deck in decks]]
    expected_highs =[[decks[deck]['exp_region'][1] for deck in decks]]
    observed_wins = [decks[deck]['Wins'] for deck in decks]
    ylabels = [deck for deck in decks]
    ys = [i for i in range(len(decks))]
    y1s = [y - .15 for y in ys]  # adjusting down slightly for one
    y2s = [y+.15 for y in ys]  # and up slightly for the other
    with plt.xkcd():
        plt.clf()
        plt.hlines(y1s, xmin=base_lows, xmax=base_highs, color="black", label="Coinflip vs Field")
        plt.hlines(y2s, xmin=expected_lows, xmax=expected_highs, color='red', linestyles="dashed",
                   label="Assuming Observed Winrate")
        plt.scatter(observed_wins, y2s, c="blue", marker='o', label="Observed Wins")
        plt.yticks(ys, ylabels)
        plt.xlabel("Number of Wins")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    # actually run the calculations
    for deck in deck_info:
        base_region, exp_region = calc_binom_limit(deck_info[deck])
        deck_info[deck]['base_region'] = base_region
        deck_info[deck]['exp_region'] = exp_region
        print(f"{deck}: chance results could come from a coinflip - {do_binom_test(deck_info[deck]):.1%}")
    plot_decks(deck_info)
