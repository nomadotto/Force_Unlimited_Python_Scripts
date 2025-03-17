import random
from matplotlib import pyplot as plt

PERFECT_RECORD = True # Set to True if you want our hero to win literally every other game

class Player:
    def __init__(self, is_special:bool=False, player_number:int = 0):
        self.game_wins = 0
        self.match_wins = 0
        self.games_played = 0
        self.matches_played =0
        self.set_wins = 0
        self.opponents = []
        self.is_special = is_special
        self.player_number = player_number


    def win_game(self):
        self.set_wins += 1
        self.game_wins += 1

    def make_match(self, oppo):
        self.opponents.append(oppo)
        self.matches_played +=1

    def play_game(self, win=False):
        self.games_played+=1
        if win:
            self.win_game()

    def win_match(self):
        self.set_wins = 0
        self.match_wins += 1

    def lose_match(self):
        self.set_wins = 0

    def get_match_wins(self):
        return self.match_wins

    def get_matches_played(self):
        return self.matches_played

    def get_games_played(self):
        return self.games_played

    def get_game_wins(self):
        return self.game_wins

    def get_oppo_match_win_percent(self):
        oppo_total = 0
        for oppo in self.opponents:
            oppo_percent = oppo.get_match_wins()/oppo.get_matches_played()
            oppo_total += oppo_percent
        return oppo_total/len(self.opponents)

    def get_game_win_percent(self):
        game_win_total = self.game_wins/self.games_played
        return game_win_total

    def get_oppo_game_win_percent(self):
        oppo_total = 0
        for oppo in self.opponents:
            oppo_percent = oppo.get_game_wins()/oppo.get_games_played()
        return oppo_total/len(self.opponents)

    def get_tiebreak_value(self):
        # order is match wins > oppo match wins > game win % > oppo game wins
        match_wins = self.get_match_wins()
        oppo_match_wins = self.get_oppo_match_win_percent()
        game_wins = self.get_game_win_percent()
        oppo_game_wins = self.get_oppo_game_win_percent()
        return [match_wins, oppo_match_wins, game_wins, oppo_game_wins]



def sort_player_list(player_list):
    def sort_critera(player):
        return player.get_tiebreak_value()
    player_list.sort(key = sort_critera, reverse=True)
    return player_list


def do_pairings(player_list):
    to_be_paired = player_list.copy()
    while len(to_be_paired) >1:
        j = 1

        unmatched = True
        while unmatched:
            unmatched = try_pairing(to_be_paired[0], to_be_paired[j])
            if not unmatched:
                player_num_1 = to_be_paired[0].player_number
                player_num_2 = to_be_paired[j].player_number
                #print(f"Player {player_num_1} plays Player{player_num_2}, "
                #      f"{player_num_1}'s record: {to_be_paired[0].match_wins} "
                #      f"{player_num_2}'s record: {to_be_paired[j].match_wins}")
                to_be_paired.pop(j)
                to_be_paired.pop(0)
            if j == len(to_be_paired) - 1:  # if we're at the end of the road just pair to the bottom
                force_pairing(to_be_paired[0], to_be_paired[j])
                to_be_paired.pop(j)
                to_be_paired.pop(0)
                unmatched = False

            j+=1


def try_pairing(player1, player2):
    if player2 in player1.opponents:
        # we can't double-match
        return True
    else:
        match(player1,player2)
        return False

def force_pairing(player1, player2):
    match(player1, player2)

def match(player1, player2):
    player1.make_match(player2)
    player2.make_match(player1)
    play_match(player1, player2)

def play_match(player1, player2):
    """
    Play a set of 2-3 games between two Players
    :param player1: A Player
    :param player2: Another Player
    """
    game_1 = play_game(player1, player2)
    game_2 = play_game(player1, player2)  # always play 2 games
    results = [0, 0]
    results[game_1] += 1
    results[game_2] += 1
    if results == [2, 0]:
        player1.win_match()
        player2.lose_match()
    elif (results == [0, 2]):  # if one player won twice
        player1.lose_match()
        player2.win_match()
    else:  # otherwise
        game_3 = play_game(player1, player2)
        if game_3 ==1: # player 2 wins
            player2.win_match()
            player1.lose_match()
        else:  # if player 2 doesn't win, player 1 does
            player1.win_match()
            player2.lose_match()


def play_game(player1, player2):
    if player1.is_special:
        win = play_special_game(player1, player2)
        result = win
    elif player2.is_special:
        win = play_special_game(player2, player1)
        result = int(not(win))  # we need to flip the result because our special player is player 2
    else:
        result = play_regular_game(player1, player2)
    return result

def play_special_game(special_player, normal_player):
    # if it's the round we're forcing a loss, lose
    if special_player.matches_played == MAGIC_ROUND:
        special_player.play_game(win=False)
        normal_player.play_game(win=True)
        return 1
    #otherwise, our special player will always win
    elif PERFECT_RECORD:
        special_player.play_game(win=True)
        normal_player.play_game(win=False)
        return 0
    else:
        result = play_regular_game(special_player, normal_player)
        return result

def play_regular_game(player1, player2):
    rand = random.random()  # roll a uniform random number between 0 and 1
    line = .5
    if rand <= line:  # if we're below the line, p1 wins
        player1.play_game(win=True)
        player2.play_game(win=False)
        return 0
    else:
        player1.play_game(win=False)
        player2.play_game(win=True)
        return 1


def make_players(n_players):
    player_list = [Player(is_special=False, player_number=i) for i in range(n_players)]
    player_list[0].is_special = True # always have our special boy
    return player_list

def play_tournament_round(player_list):
    do_pairings(player_list)


def get_special_position(player_list):
    for i in range(len(player_list)):
        if player_list[i].is_special:
            return i


N_TRIALS = 5000
MAGIC_ROUND =1
special_positions_0 = []
for trial in range(N_TRIALS):
    player_list = make_players(128)
    for i in range(7):
        #print(f"Round {i}")
        play_tournament_round(player_list)
        player_list = sort_player_list(player_list)
    special_positions_0.append(get_special_position(player_list))

print(f"Average Special Position with MAGIC_ROUND {MAGIC_ROUND}: "
      f"{sum(special_positions_0)/len(special_positions_0)}")

MAGIC_ROUND = 7
special_positions_7 = []
for trial in range(N_TRIALS):
    player_list = make_players(128)
    for i in range(7):
        #print(f"Round {i}")
        play_tournament_round(player_list)
        player_list = sort_player_list(player_list)
    special_positions_7.append(get_special_position(player_list))

print(f"Average Special Position with MAGIC_ROUND {MAGIC_ROUND}: "
      f"{sum(special_positions_7)/len(special_positions_7)}")

with plt.xkcd():
    plt.hist(special_positions_0,  histtype = 'step', label = 'Losing on round 1')
    plt.hist(special_positions_7,  histtype = 'step', label = 'Losing on round 7')
    plt.legend()
    plt.xlabel("Final Player Position")
    plt.ylabel(f"Occurrences in {N_TRIALS}")
    plt.show()