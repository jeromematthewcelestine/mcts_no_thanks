from __future__ import division

import random
from itertools import cycle
import datetime
from math import log, sqrt
import no_thanks

class BasicComputerPlayer():
    def __init__(self, board):
        self.calculation_time = datetime.timedelta(seconds = 1)
        self.board = board

    def get_action(self, history):
        moves = {}

        state = history[-1]
        state = self.board.pack_state(state)

        default_action = ACTION_PASS
        other_action = ACTION_TAKE

        if self.board.is_legal(state, default_action):
            action = default_action
        else:
            action = other_action

        return action

class MCTSPlayer():
    def __init__(self, board):
        self.board = board

        self.calculation_time = datetime.timedelta(seconds=1)
        self.max_moves = 200

        self.wins = {}
        self.plays = {}

        self.C = 1.4

    def get_action(self, state):
        self.max_depth = 0
        
        player = self.board.current_player(state)
        legal_actions = self.board.legal_actions(state)

        if not legal_actions:
            return
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation(state)
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
            # print("{3}: {0:.2f}% ({1} / {2})".format(*x))

        # print("Maximum depth searched:", self.max_depth)

        return action

    def run_simulation(self, state):
        plays, wins = self.plays, self.wins

        visited_actions = set()
        # states_copy = self.states[:]
        # state = states_copy[-1]
        player = self.board.current_player(state)

        expand = True

        for t in range(1, self.max_moves + 1):
            legal_actions = self.board.legal_actions(state)

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
            state = self.board.next_state(state, action)

            player = self.board.current_player(state)
            winner = self.board.winner(state)
            if winner is not None:
                break


        for player, state, action in visited_actions:
            if (player, state, action) not in plays:
                continue
            plays[(player, state, action)] += 1
            if player == winner:
                wins[(player, state, action)] += 1


class GameMaster():
    def __init__(self, n_players = 3):
        self.n_players = n_players
        self.board = no_thanks.Board(self.n_players)

        mcts_player = MCTSPlayer(self.board)

        self.players = []
        self.players.append(no_thanks.HumanPlayer())
        self.players.append(mcts_player)
        self.players.append(mcts_player)

    def start(self):
        current_player = 0
        state = self.board.starting_state()
        history = []
        history.append(state)

        while True:
            self.board.display_state(state)
            action = self.players[current_player].get_action(state)

            if not self.board.is_legal(state, action):
                continue

            state = self.board.next_state(state, action)
            history.append(state)

            if self.board.is_ended(state):
                self.board.display_state(state)
                self.board.display_scores(state)
                winner = self.board.winner(state)
                print("The winner is Player {0}".format(winner))
                break

            current_player += 1
            if current_player == self.n_players:
                current_player = 0


if __name__=="__main__":
    gm = GameMaster()
    gm.start()


