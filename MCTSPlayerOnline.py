import random
import datetime
from math import log, sqrt
from no_thanks import Board, NoThanksConfig, ACTION_TAKE, ACTION_PASS

import os, psutil

class MCTSPlayerOnline():
    def __init__(self, n_players = 3, thinking_time = 1, config = NoThanksConfig()):
        assert thinking_time > 0

        self.n_players = n_players
        self.thinking_time = thinking_time
        

        self.config = config

        # self.min_card = min_card
        # self.max_card = max_card
        # self.start_coins = start_coins
        # self.n_omit_cards = n_omit_cards

        self.max_moves = 200
        self.C = 1.4

    def make_state_packed(self, coins, cards, card_in_play, coins_in_play, n_cards_in_deck, current_player):
        details = (card_in_play, coins_in_play, n_cards_in_deck, current_player)
        packed_state = tuple(coins), tuple(map(tuple, cards)), details
        return packed_state
        
    def get_action(self, state, legal_actions):
        self.max_depth = 0

        board = Board(self.n_players, self.config)
        
        player = state[2][3]

        if not legal_actions:
            return
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        plays = {}
        wins = {}
        games = 0
        calculation_delta = datetime.timedelta(seconds = self.thinking_time)
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < calculation_delta:
            board = Board(self.n_players, self.config)
            plays, wins = self.run_simulation(state, board, plays, wins)
            games += 1

        print("player: ", player)
        for action in legal_actions:
            if action == ACTION_TAKE:
                print("action: TAKE")
            else:  
                print("action: PASS")
            print("plays: ", plays.get((player, state, action), 1))
            print("wins: ", wins.get((player, state, action), 0)) 

        percent_wins, action = max(
            (100 * wins.get((player, state, action), 0) / 
             plays.get((player, state, action), 1),
             action)
            for action in legal_actions
        )

        return action

    def run_simulation(self, state, board, plays, wins):

        visited_actions = set()
        player = board.current_player(state)

        phase = "selection"

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
                if phase == "selection":
                    phase = "expansion"
                # otherwise, just pick a random one
                action = random.choice(legal_actions)

            # states_copy.append(state)

            if phase == "expansion" and (player, state, action) not in plays:
                plays[(player, state, action)] = 0
                wins[(player, state, action)] = 0
                if t > self.max_depth:
                    self.max_depth = t
                phase = "end_expansion"

            if phase == "selection" or "phase" == "expansion":
                visited_actions.add((player, state, action))
            elif phase == "end_expansion":
                visited_actions.add((player, state, action))
                phase = "simulation"

            # move to next state
            state = board.next_state(state, action)

            player = board.current_player(state)
            winner = board.winner(state)
            if winner is not None:
                break

        phase = "backpropagation"
        for player, state, action in visited_actions:
            plays[(player, state, action)] += 1
            if player == winner:
                wins[(player, state, action)] += 1

        return plays, wins

if __name__ == "__main__":
    mcts_player = MCTSPlayerOnline()