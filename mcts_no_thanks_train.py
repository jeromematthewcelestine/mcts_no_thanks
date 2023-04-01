import argparse
import no_thanks
from MCTSPlayer import MCTSPlayer

# Set up argument parsing
parser = argparse.ArgumentParser(description="Train an MCTSPlayer and save the model to a file.")
parser.add_argument("--output", dest="output_filename", default="mcts.model",
                    help="Filename for the trained model (default: mcts.model).")
parser.add_argument("--n_players", dest="n_players", default=3, type=int,
                    help="Number of players in the game (default: 3).")
parser.add_argument("--seconds", dest="seconds", default=100, type=int,)
args = parser.parse_args()

output_filename = args.output_filename
n_players = args.n_players

mcts_player = MCTSPlayer(n_players=n_players, thinking_time=1)

board = no_thanks.Board(n_players=n_players, start_coins=11, min_card=3, max_card=33, n_omit_cards=9)

current_player = 0

mcts_player.train(seconds=args.seconds)

mcts_player.write(output_filename)
