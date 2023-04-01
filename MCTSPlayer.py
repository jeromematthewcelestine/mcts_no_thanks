import random
from itertools import cycle
import datetime
from math import log, sqrt
import pickle
import no_thanks

import os, psutil


class MCTSPlayer():
    def __init__(self, n_players = 3, thinking_time = 1, min_card = 3, max_card = 33, filepath = None):

        self.thinking_time = thinking_time
        self.max_moves = 200

        self.wins = {}
        self.plays = {}

        self.min_card = 3
        self.max_card = 33

        self.n_players = n_players

        if filepath:
            self.load_from(filepath)

        self.C = 1.4

        process = psutil.Process(os.getpid())
        print("memory (in bytes): ", process.memory_info().rss)  # in bytes 

    def make_state_packed(self, coins, cards, card_in_play, coins_in_play, n_cards_in_deck, current_player):
        details = (card_in_play, coins_in_play, n_cards_in_deck, current_player)
        packed_state = tuple(coins), tuple(map(tuple, cards)), details
        return packed_state

    def train(self, seconds = 1):
        self.max_depth = 0
        games = 0

        calculation_time = datetime.timedelta(seconds = seconds)

        

        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < calculation_time:
            board = no_thanks.Board(self.n_players, min_card = self.min_card, max_card = self.max_card)
            initial_state = board.pack_state(board.starting_state())
            self.run_simulation(initial_state, board)
            games += 1

        print("Games played: ", games)
        print("Maximum depth searched:", self.max_depth)
        
    def get_action(self, state, legal_actions):
        self.max_depth = 0

        board = no_thanks.Board(self.n_players)
        
        player = state[2][3]
        # legal_actions = self.board.legal_actions(state)

        if not legal_actions:
            return
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        if self.thinking_time > 0:
            

            games = 0
            calculation_delta = datetime.timedelta(seconds = self.thinking_time)
            begin = datetime.datetime.utcnow()
            while datetime.datetime.utcnow() - begin < calculation_delta:
                board = no_thanks.Board(self.n_players)
                self.run_simulation(state, board)
                games += 1

        percent_wins, action = max(
            (100 * self.wins.get((player, state, action), 0) / 
             self.plays.get((player, state, action), 1),
             action)
            for action in legal_actions
        )

        for x in sorted(
            ((100 * self.wins.get((player, state, action), 0) / self.plays.get((player, state, action), 1), 
                self.wins.get((player, state, action), 0),
                self.plays.get((player, state, action), 0), action)
            for action in legal_actions),
            reverse=True
        ):
            pass
            print("{3}: {0:.2f}% ({1} / {2})".format(*x))

        print("Maximum depth searched:", self.max_depth)

        return action

    def run_simulation(self, state, board):
        plays, wins = self.plays, self.wins

        visited_actions = set()
        # states_copy = self.states[:]
        # state = states_copy[-1]
        player = board.current_player(state)

        expand = True

        for t in range(1, self.max_moves + 1):
            legal_actions = board.legal_actions(state)

            # moves_states = [(p, self.board.next_state(state, p)) for p in legal]
            # moves_states = [(p, self.board.next_state(state, p)) for p in legal]

            if all(plays.get((player, state, action)) for action in legal_actions):
                # if we have stats on all of the legal moves here, use them
                log_total = log(
                    sum(plays[(player, state, action)] for action in legal_actions))
                value, action = max(
                    ((wins[(player, state, action)] / plays[(player, state, action)]) + self.C *
                        sqrt(log_total / plays[(player, state, action)]), action)
                        for action in legal_actions
                )
            else:
                # otherwise, just pick a random one
                action = random.choice(legal_actions)

            # states_copy.append(state)

            if expand and (player, state, action) not in plays:
                expand = False
                plays[(player, state, action)] = 0
                wins[(player, state, action)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_actions.add((player, state, action))

            # move to next state
            state = board.next_state(state, action)

            player = board.current_player(state)
            winner = board.winner(state)
            if winner is not None:
                break


        for player, state, action in visited_actions:
            if (player, state, action) not in plays:
                continue
            plays[(player, state, action)] += 1
            if player == winner:
                wins[(player, state, action)] += 1

    def write(self, filepath):
        output_object = {"wins": self.wins,
                      "plays": self.plays}
        with open(filepath, "wb") as output_file:
            pickle.dump(output_object, output_file)
    
    def load_from(self, filepath):
        with open(filepath, "rb") as input_file:
            input_object = pickle.load(input_file)
            self.plays = input_object["plays"]
            self.wins = input_object["wins"]


if __name__ == "__main__":
    mcts_player = MCTSPlayer("mcts_classic_4p_20230324_01.model")