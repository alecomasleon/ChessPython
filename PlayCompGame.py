import Engine
# import TrainNeuralNetwork as tnn
import Player


def play_game(comp1, comp2, gs=Engine.GameState()):
    # Returns 1 if comp1 won, -1 if comp2 won, and 0 if it was a draw

    comp1.set_gs(gs)
    comp2.set_gs(gs)

    while True:
        if gs.whiteToMove:
            move = comp1.find_move()
            try:
                gs.makeMove(move)
            except:
                print('comp1 move not accepted')

        else:
            move = comp2.findRandMove()
            try:
                gs.makeMove(move)
            except:
                print('comp2 move not accepted')

        for i in gs.board:
            print(i)
        print("\n\n\n")

        gs.getValidMoves()

        if gs.checkMate:
            if gs.whiteToMove:
                return -1
            else:
                return 1
        elif gs.staleMate:
            return 0


if __name__ == "__main__":
    comp_file = open('training_players.txt', 'r')
    # comp1 = tnn.comp_from_logged_string(comp_file.readlines()[-2])
    comp_file.close()
    # print(play_game(comp1, Player.Player()))
