import argparse
import csv
import pickle

# Set up argument parsing
parser = argparse.ArgumentParser(description="Train an MCTSPlayer and save the model to a file.")
parser.add_argument("--input", dest="input_filename", default=None)
parser.add_argument("--output", dest="output_filename", default="model.csv",
                    help="Filename for the model output (default: model.csv).")
# parser.add_argument("--n_players", dest="n_players", default=3, type=int,
#                     help="Number of players in the game (default: 3).")
args = parser.parse_args()

with open(args.input_filename, "rb") as input_file:
    input_object = pickle.load(input_file)
data_plays = input_object["plays"]
data_wins = input_object["wins"]

# iterate through the plays and wins dictionaries and write to a csv file  
with open(args.output_filename, "w") as output_file:
    writer = csv.writer(output_file)
    # write header (state, plays, wins)
    writer.writerow(["player", "coins", "cards", "card_in_play", "coins_in_play", "n_cards_in_deck", "current_player", "action", "plays", "wins"])
    i = 0
    for key, plays in data_plays.items():
        player, state, action = key
        coins, cards, details = state
        card_in_play, coins_in_play, n_cards_in_deck, current_player = details
        writer.writerow([player, coins, cards, card_in_play, coins_in_play, n_cards_in_deck, current_player, action, plays, data_wins[key]])

        # if i % 1000 == 0:
            # print(f"coins {coins}, cards {cards}, card_in_play {card_in_play}, coins_in_play {coins_in_play}, n_cards_in_deck {n_cards_in_deck}, current_player {current_player}")
        i += 1