import os.path
import argparse
import json

from checkers.players import * # McCartneyServerPlayer, MinMaxClientPlayer
from checkers.game_api import CheckersGame

weights_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"weights.json")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Example of playing a game with LocalServerPlayer and PoliteMinMaxClientPlayer.')
    parser.add_argument('-w', '--weights', default=weights_file, help='File with weight constants')
    args = parser.parse_args()

    weights_learn = json.load(open(args.weights, 'r'))
    weights_teach = {"count_friends" : 5,
               "count_foes" : -5,
               "count_friends_kings" : 2,
               "count_foes_kings" : -2}

    # server = LocalServerPlayer(color="Black", verbose=True, weights=weights_learn, depth=2)
    server = McCartneyServerPlayer(verbose=True)
    client = PoliteMinMaxClientPlayer(weights=weights_teach, depth=2)

    server.start()
    client.start()
    server_first = server.going_first()
    client.set_going_first(not server_first)
    if server_first:
        game = CheckersGame(server, client)
    else:
        game = CheckersGame(client, server)
    game.start()
    game.join()  # wait for game to end
    print("Game result: {}".format(game.result))
