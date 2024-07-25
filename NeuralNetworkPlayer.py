import numpy as np
import Engine


class NeuralNetworkPlayer:
    # POSITIONS_TO_EXPLORE = [10, 6, 4, 2, 2]
    POSITIONS_TO_EXPLORE = [5, 4, 3]
    RECURSION_DEPTH = len(POSITIONS_TO_EXPLORE)
    NODES_PER_LAYER = 100

    piece_place_in_array = {'wp': 0, 'wN': 1, 'wB': 2, 'wR': 3, 'wQ': 4, 'wK': 5,
                            'bp': 6, 'bN': 7, 'bB': 8, 'bR': 9, 'bQ': 10, 'bK': 11}

    weights = [np.zeros((NODES_PER_LAYER, 64 * 12 + 1)),
               np.zeros((NODES_PER_LAYER, NODES_PER_LAYER)),
               np.zeros((2, NODES_PER_LAYER))]
    biases = [np.zeros(NODES_PER_LAYER), np.zeros(NODES_PER_LAYER), np.zeros(2)]

    def __init__(self, gs=None, weights=None, biases=None):
        self.gs = gs
        self.set_weights_and_biases(weights, biases)

    def set_gs(self, gs):
        self.gs = gs

    def set_weights_and_biases(self, weights, biases):
        if weights and biases:
            if len(weights) != len(biases):
                raise ValueError("Length of weights and biases has to be equal.")
            self.weights = weights
            self.biases = biases

    def find_move(self, count=RECURSION_DEPTH):
        if count == 0:
            return self.rate_position()

        valid_moves = self.gs.getValidMoves()

        if len(valid_moves) == 0:
            return self.rate_position()

        if self.gs.whiteToMove:
            best_move = (1, -5)
        else:
            best_move = (1, 5)

        if len(valid_moves) <= self.POSITIONS_TO_EXPLORE[count - 1]:
            moves_to_make = valid_moves
        else:
            moves_to_make = []
            ratings = []
            for move in valid_moves:
                self.gs.makeMove(move)

                rating = self.rate_position()

                self.gs.undoMove()

                if len(ratings) < self.POSITIONS_TO_EXPLORE[count - 1]:
                    ratings.append(rating)
                    moves_to_make.append(move)
                else:
                    if self.gs.whiteToMove:
                        minimum = min(ratings)
                        if rating > minimum:
                            index = ratings.index(minimum)
                            moves_to_make[index] = move
                            ratings[index] = rating
                    else:
                        maximum = max(ratings)
                        if rating < maximum:
                            index = ratings.index(maximum)
                            moves_to_make[index] = move
                            ratings[index] = rating

        for move in moves_to_make:
            self.gs.makeMove(move)

            rating = self.find_move(count - 1)

            self.gs.undoMove()

            if self.gs.whiteToMove:
                if rating > best_move[1]:
                    best_move = (move, rating)
            else:
                if rating < best_move[1]:
                    best_move = (move, rating)

        if count == self.RECURSION_DEPTH:
            return best_move[0]

        return best_move[1]

    def rate_position(self):
        if self.gs.checkMate:
            if self.gs.whiteToMove:
                return -2
            else:
                return 2
        elif self.gs.staleMate:
            return 0

        prev = self.board_to_array()
        for i in range(len(self.weights)):
            prev = self.calc_next_layer(prev, i)

        # Have 1st be white chance to win, second be black
        # If White is better, return will be higher
        return prev[0] - prev[1]

    def board_to_array(self):
        array = np.zeros((64 * 12 + 1))
        array[64 * 12] = 1 if self.gs.whiteToMove else 0
        count = 0
        for i in self.gs.board:
            for c in i:
                if c != '--':
                    array[count + self.piece_place_in_array[c]] = 1
                count += 12

        return array

    def calc_next_layer(self, prev, layer_number):
        x = np.dot(self.weights[layer_number], prev) + self.biases[layer_number]
        return 1 / (1 + np.exp(-x)) # sigmoid


if __name__ == '__main__':
    game = Engine.GameState()

    var = NeuralNetworkPlayer.NODES_PER_LAYER

    w = [np.random.randint(-10, 10, (var, 64 * 12 + 1)),
         np.random.randint(-10, 10, (var, var)),
         np.random.randint(-10, 10, (2, var))]
    b = [np.random.randint(-10, 10, var),
         np.random.randint(-10, 10, var),
         np.random.randint(-10, 10, 2)]

    player = NeuralNetworkPlayer(game, weights=w, biases=b)

    print(player.board_to_array())
    print(player.weights)
    print(player.biases)
