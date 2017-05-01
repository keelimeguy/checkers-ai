import os.path
import argparse
import json

from checkers.players import * # McCartneyServerPlayer, MinMaxClientPlayer
from checkers.game_api import CheckersGame

weights_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"weights.json")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Example of playing a game with LocalServerPlayer and PoliteMinMaxClientPlayer.')
    parser.add_argument('-w', '--weights', default=weights_file, help='File with weight constants')
    parser.add_argument('-v', '--verbose', default=False, help='\'True\' if you want to display each message sent between the client and server')
    args = parser.parse_args()

    with open(args.weights, 'r') as f:
        weights_learn = json.load(f)

    weights_teach = {"count_friends" : 3,
                     "count_foes" : -3,
                     "count_friends_kings" : 5,
                     "count_foes_kings" : -5}

    # server = McCartneyServerPlayer(verbose=(1 if args.verbose else 0))
    server = LocalServerPlayer(color="Black", verbose=args.verbose, weights=weights_teach, depth=5)
    client = PoliteMinMaxClientPlayer(weights=weights_learn, depth=2)
    # client = MinMaxClientPlayer(weights=weights_learn, depth=2)

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
    print("Client Win?: {}".format(game.client_win))
