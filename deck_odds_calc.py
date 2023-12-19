import matplotlib.pyplot as plt
from scipy.stats import hypergeom

sample_low_curve = {0: 0, 1: 10, 2: 15, 3: 12, 4: 10, 5: 3}
sample_flat_curve = {0: 0, 1: 7, 2: 7, 3: 7, 4: 7, 5: 7, 6: 7, 7: 7, 8: 1}
sample_high_curve = {0: 0, 1: 0, 2: 5, 3: 5, 4: 10, 5: 10, 6: 5, 7: 5, 8: 5, 9: 5}


cards_seen_on_turn = [6+2*(i-1) for i in range(15)]

distros = {'low_curve': sample_low_curve, 'flat_curve': sample_flat_curve, "high_curve": sample_high_curve}


def get_prob_on_turn(turn_number: int, distro: dict) -> float:
    cards_seen = cards_seen_on_turn[turn_number]
    prob = hypergeom.cdf(0, 50, distro[turn_number+1], cards_seen)
    return 1-prob


prob_mass = {}
for distro in distros:
    print(f"{distro} sum : {sum(distros[distro].values())}")
    prob_mass[distro] = []
    for turn in range(1, 10):
        try:
            prob = get_prob_on_turn(turn, distros[distro])
        except KeyError:
            prob = 0
        prob_mass[distro].append(prob)


def make_plot(distros):
    with plt.xkcd():
        fig = plt.figure()
        ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_yticks([])
        ax.set_ylim([0, 1])
        ax.set_xlabel("turn_number")
        ax.set_ylabel("Prob of having a N-cost play on turn N")

    for distro in distros:
        x = range(1, 10)
        y = distros[distro]
        ax.plot(x, y, label=distro)
    ax.legend()
    plt.show()


make_plot(prob_mass)
