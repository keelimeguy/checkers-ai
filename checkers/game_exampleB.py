import os.path
import argparse
import json

from checkers.players import * # McCartneyServerPlayer, MinMaxClientPlayer
from checkers.game_api import CheckersGame

weights_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"weights_alternate.json")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Example of playing a game with LocalServerPlayer'
        ' and PoliteMinMaxClientPlayer.')
    parser.add_argument('-w', '--weights', default=weights_file,
                        help='File with weight constants')
    parser.add_argument('-s', '--server', action="store_true",
                        help="Play against the real remote server")
    parser.add_argument('-o', '--opponent', default=0,
                        help="Play against a specific opponent. Only user when running against server")
    parser.add_argument('-v', '--verbose', default=False,
                        help='\'True\' if you want to display each message'
                        ' sent between the client and server')
    args = parser.parse_args()

    with open(args.weights, 'r') as f:
        weights_learn = json.load(f)

    weights_teach = {"count_defender_pieces_friends": 2, "aggregate_distance_promotion_foes": 1, "count_diagonalmain_kings_foes": 1, "count_friends": -3, "count_loner_pawns_friends": 0, "bridge_foes": 2, "king_corner_friends": -3, "count_center_pawns_friends": -3, "count_diagonaldouble_kings_friends": 2, "count_movable_foes_pawns": -4, "oreo_friends": -3, "count_safe_foes_kings": -4, "count_movable_friends_kings": -3, "count_center_kings_foes": -3, "count_diagonalmain_kings_friends": -3, "count_center_pawns_foes": 5, "count_attack_pawns_friends": 2, "pawn_corner_friends": 2, "count_loner_kings_foes": 3, "count_loner_kings_friends": -3, "bridge_friends": -3, "count_foes_kings": 2, "king_corner_foes": -3, "count_attack_pawns_foes": -3, "count_holes_friends": 2, "aggregate_distance_promotion_friends": 5, "dog_foes": -3, "count_safe_friends_pawns": 0, "triangle_foes": -3, "count_foes": -4, "count_diagonalmain_pawns_friends": 2, "count_safe_friends_kings": -3, "count_diagonaldouble_pawns_friends": -3, "count_movable_foes_kings": 2, "count_unoccupied_promotion_foes": 2, "count_friends_pawns": 2, "count_movable_friends_pawns": -3, "oreo_foes": -3, "count_diagonaldouble_pawns_foes": 5, "count_center_kings_friends": 2, "count_diagonaldouble_kings_foes": -4, "count_unoccupied_promotion_friends": 2, "count_diagonalmain_pawns_foes": 2, "count_foes_pawns": -3, "count_loner_pawns_foes": -3, "pawn_corner_foes": 2, "dog_friends": 2, "count_defender_pieces_foes": 2, "count_holes_foes": 5, "count_safe_foes_pawns": -3, "triangle_friends": -4, "count_friends_kings": 1}
    if args.server:
        server = McCartneyServerPlayer(verbose=(1 if args.verbose else 0), opponent=int(args.opponent), is_B_client=True)
        client = MinMaxClientPlayer(weights=weights_learn, depth=5)
    else:
        server = LocalServerPlayer(verbose=args.verbose,
                                   weights=weights_teach, depth=0)
        client = PoliteMinMaxClientPlayer(weights=weights_learn, depth=0)


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
