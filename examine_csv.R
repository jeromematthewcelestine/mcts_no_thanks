library(tidyverse)

df <- read_csv("mcts_classic_2p_01.csv")
df <- df %>% arrange(player, coins, cards, card_in_play, coins_in_play)

df %>% head()
df %>% filter(player != current_player)

df %>% filter(coins == "(5, 5)")
by_coins <- df %>% group_by(coins) %>% summarize(count = n())
