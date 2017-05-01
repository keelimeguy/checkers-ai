from checkers.players import * # McCartneyServerPlayer, MinMaxClientPlayer
from checkers.game_api import CheckersGame

if __name__ == '__main__':

    weights = {"count_friends" : 5,
               "count_foes" : -5,
               "count_friends_kings" : 2,
               "count_foes_kings" : -2}

    server = LocalServerPlayer(verbose=True, weights=weights, depth=2)
    client = PoliteMinMaxClientPlayer(weights=weights, depth=2)
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
    print(f"Game result: {game.result}")
