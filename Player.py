import random as r


class Player:
    pawnPromotionTypes = ['Q', 'R', 'B', 'N']
    pieceRatings = {'p': 1.1, 'B': 3.33, 'N': 3.05, 'Q': 9.5, 'R': 5.63}
    boardRating = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 2, 2, 1, 0, 0],
            [0, 0, 1, 2, 2, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]]
    kingRating = [
            [3, 3, 3, 0, 0, 3, 3, 3],
            [2, 1, 0, 0, 0, 0, 1, 2],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 1, 0, 0, 0, 0, 1, 2],
            [3, 3, 3, 0, 0, 3, 3, 3]]
    RECURSION_DEPTH = 2

    def __init__(self, gs):
        self.gs = gs

    def findRandMove(self):
        validMoves = self.gs.getValidMoves()
        if len(validMoves) == 0:
            return None
        move = r.choice(validMoves)

        if move.isPawnPromotion:
            move.pawnPromotionType = r.choice(self.pawnPromotionTypes)
        #print(self.ratePosition())
        return move

    def findMove(self, count= RECURSION_DEPTH):
        #return (self.findRandMove(), 0)
        validMoves = self.gs.getValidMoves()

        if len(validMoves) == 0:
            return (None, self.ratePosition())
        if count == 0:
            return (None, self.ratePosition())

        if self.gs.whiteToMove:
            best_move = (1, {'w': 0, 'b': 100})
        else:
            best_move = (1, {'w': 100, 'b': 0})

        for move in validMoves:
            self.gs.makeMove(move)

            opp_move, rating = self.findMove(count-1)
            if self.gs.whiteToMove:
                score = rating['b'] - rating['w']
                best_score = best_move[1]['b'] - best_move[1]['w']
            else:
                score = rating['w'] - rating['b']
                best_score = best_move[1]['w'] - best_move[1]['b']
            if score > best_score:
                best_move = (move, rating)
            self.gs.undoMove()

        return best_move

    def ratePosition(self):
        rating = {'w': 0, 'b': 0}
        if self.gs.checkMate:
            if self.gs.whiteToMove:
                return {'w': 0, 'b': 60}
            else:
                return {'w': 60, 'b': 0}
        elif self.gs.staleMate:
            return {'w': 0, 'b': 0}

        for r in range(len(self.gs.board)):
            for c in range(len(self.gs.board[r])):
                color = self.gs.board[r][c][0]
                piece = self.gs.board[r][c][1]
                if color != '-' and piece != 'K':
                    rating[color] += self.pieceRatings[piece]

                if len(self.gs.moveLog) < 15 and piece != 'Q' and piece != 'K':
                    move = self.gs.whiteToMove
                    self.gs.whiteToMove = True
                    if color == 'b':
                        rating['b'] += self.boardRating[r][c]

                    self.gs.whiteToMove = False

                    if color == 'w':
                        rating['w'] += self.boardRating[r][c]

                    self.gs.whiteToMove = move

        if rating['w'] + rating['b'] > 40:
            rating['w'] += self.kingRating[self.gs.whiteKingLocation[0]][self.gs.whiteKingLocation[1]]
            rating['b'] += self.kingRating[self.gs.blackKingLocation[0]][self.gs.blackKingLocation[1]]

        return rating

