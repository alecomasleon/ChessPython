class GameState:
    piecesForNotation = ('Q', 'K', 'B', 'N', 'R')
    piece_to_num = {'--': 0, 'wp': 1, 'bp': 2, 'wR': 3, 'bR': 4, 'wN': 5, 'bN': 6, 'wB': 7, 'bB': 8, 'wQ': 9, 'bQ': 10,
                    'wK': 11, 'bK': 12}
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.pieceMoves = {'p':self.getPawnMoves, 'Q':self.getQueenMoves, 'R':self.getRookMoves, 'B':self.getBishopMoves, 'K': self.getKingMoves, 'N':self.getKnightMoves}
        self.anpassenSq = ()

        self.castleRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.castleRights.wkc, self.castleRights.bkc, self.castleRights.wqc, self.castleRights.bqc)]

        self.boardLog = {}

        self.fiftyMoveDraw = [0]


    def makeMove(self, move):
        self.moveLog.append(move)
        self.board[move.startRow][move.startCol] = '--'

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pawnPromotionType
        else:
            self.board[move.endRow][move.endCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove

        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.anpassen:
            #print('Chess Notation of moveMade: ' + move.getChessNotation())
            self.board[move.startRow][move.endCol] = '--'

        self.anpassenSq = move.createAnpassen
        self.updateCastleRights(move)

        if move.castleK:
            self.board[move.endRow][move.endCol + 1] = '--'
            self.board[move.endRow][move.endCol - 1] = move.pieceMoved[0] + 'R'
        elif move.castleQ:
            self.board[move.endRow][move.endCol - 2] = '--'
            self.board[move.endRow][move.endCol + 1] = move.pieceMoved[0] + 'R'

        if len(self.moveLog) >= 8:
            if (self.moveLog[-1] == self.moveLog[-5]) and (self.moveLog[-2] == self.moveLog[-6]) and (self.moveLog[-3] == self.moveLog[-7]) and (self.moveLog[-4] == self.moveLog[-8]):
                self.staleMate = True

        num = 0
        for i in self.board:
            for c in i:
                if c != '--' and c != 'wK' and c != 'bK':
                    num = -1
                    break
        if num == 0:
            self.staleMate = True

        if 'p' in move.pieceMoved or move.pieceCaptured != '--' or move.anpassen:
            self.fiftyMoveDraw.append(0)
        else:
            self.fiftyMoveDraw.append(self.fiftyMoveDraw[-1] + 1)

        if self.fiftyMoveDraw[-1] >= 100:
            self.staleMate = True


    def undoMove(self):
        #print(self.moveLog[0].getChessNotation())
        #print(self.moveLog)

        self.staleMate = False
        self.checkMate = False

        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.anpassen:
                if move.pieceMoved[0] == 'w':
                    self.board[move.endRow + 1][move.endCol] = 'bp'
                else:
                    self.board[move.endRow-1][move.endCol] = 'wp'

            #print(len(self.castleRightsLog))
            self.castleRightsLog.pop()
            castleRights = self.castleRightsLog[-1]
            self.castleRights = CastleRights(castleRights.wkc, castleRights.bkc, castleRights.wqc, castleRights.bqc)

            if move.castleK:
                self.board[move.endRow][move.endCol + 1] = move.pieceMoved[0] + 'R'
                self.board[move.endRow][move.endCol - 1] = '--'
            elif move.castleQ:
                self.board[move.endRow][move.endCol - 2] = move.pieceMoved[0] + 'R'
                self.board[move.endRow][move.endCol + 1] = '--'

            if len(self.moveLog) != 0:
                self.anpassenSq = self.moveLog[-1].createAnpassen
            else:
                self.anpassenSq = ()

            if len(self.fiftyMoveDraw) >= 1:
                self.fiftyMoveDraw.pop()


    def updateCastleRights(self, move):
        color = move.pieceMoved[0]
        piece = move.pieceMoved[1]
        castlingK = {'w':(False, self.castleRights.bkc, False, self.castleRights.bqc), 'b': (self.castleRights.wkc, False, self.castleRights.wqc, False)}
        castlingR = {(0, 0):(self.castleRights.wkc, self.castleRights.bkc, self.castleRights.wqc, False),
                     (0, 7): (self.castleRights.wkc, False, self.castleRights.wqc, self.castleRights.bqc),
                     (7, 0): (self.castleRights.wkc, self.castleRights.bkc, False, self.castleRights.bqc),
                     (7, 7): (False, self.castleRights.bkc, self.castleRights.wqc, self.castleRights.bqc)}

        if piece == 'K':
            self.castleRights = CastleRights(castlingK[color][0], castlingK[color][1], castlingK[color][2], castlingK[color][3])

        elif piece == 'R':
            # (0, 0), (0, 7), (7, 0), (7, 7)
            castle = castlingR.get((move.startRow, move.startCol), (self.castleRights.wkc, self.castleRights.bkc, self.castleRights.wqc, self.castleRights.bqc))
            self.castleRights = CastleRights(castle[0], castle[1], castle[2], castle[3])

        else:
            self.castleRights = CastleRights(self.castleRights.wkc, self.castleRights.bkc, self.castleRights.wqc,self.castleRights.bqc)

        self.castleRightsLog.append(CastleRights(self.castleRights.wkc, self.castleRights.bkc, self.castleRights.wqc, self.castleRights.bqc))




    def getValidMoves(self):
        tupleBoard = tuple(tuple(c) for c in self.board)
        #print('a', end=' ')
        if (tupleBoard, self.whiteToMove) in self.boardLog:
            self.updateGameOver(self.boardLog[(tupleBoard, self.whiteToMove)])
            return self.boardLog[(tupleBoard, self.whiteToMove)]
        #print('b')

        moves = self.getAllPossibleMoves()
        kingPos = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        self.getCastleMoves(kingPos[0], kingPos[1], moves)

        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        self.updateGameOver(moves)
        self.boardLog.update({(tuple(tuple(c) for c in self.board), self.whiteToMove): moves})

        return moves

    def updateGameOver(self, moves):
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False

    def getCheckMate(self):
        self.getValidMoves()
        return self.checkMate

    def getStaleMate(self):
        self.getValidMoves()
        return self.staleMate

    def inCheck(self):
        if self.whiteToMove:
            return self.sqUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.sqUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def sqUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove

        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True

        return False

    def getAllPossibleMoves(self):
        moves = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                pieceColor = self.board[r][c][0]
                turn = 'w' if self.whiteToMove else 'b'
                if pieceColor == turn:
                    piece = self.board[r][c][1]
                    self.pieceMoves[piece](r, c, moves)

        finalMoves = []
        for val in moves:
            if val != None:
                finalMoves.append(val)

        #print(len(finalMoves))
        return finalMoves

    def getPawnMoves(self, r, c, moves):
        #self.getKingMoves(r, c, moves)
        pawnMoves = {'w':{'push': -1, 'row': 6, 'push2': -2, 'takes': ((-1, 1), (-1, -1))}, 'b':{'push': 1, 'row': 1, 'push2': 2, 'takes': ((1, 1), (1, -1))}}
        color = pawnMoves[self.board[r][c][0]]

        move = None

        if self.board[r+color['push']][c] == '--':
            move = self.createMove(r, c, r+(color['push']), c)
            moves.append(move)

        if move and (r == color['row']) and self.board[r+color['push2']][c] == '--':
            anpassenSq=(r+(color['push']), c)
            moves.append(self.createMove(r, c, r + color['push2'], c, createAnpassen=anpassenSq))

        takes = color['takes']
        for i in range(2):
            endRow = r + takes[i][0]
            endCol = c + takes[i][1]

            if (-1 < endRow < 8) and (-1 < endCol < 8):
                if self.board[endRow][endCol] != '--':
                    moves.append(self.createMove(r, c, endRow, endCol))
                elif (endRow, endCol) == self.anpassenSq:
                    moves.append(self.createMove(r, c, endRow, endCol, anpassen=True))


    def getRookMoves(self, r, c, moves):
        rookMoves = (1, -1)
        for m in rookMoves:
            endRow = r
            endCol = c
            for i in range(len(self.board)):
                endRow += m
                move = self.createMove(r, c, endRow, endCol)
                if not move:
                    break

                moves.append(move)

                if move.pieceCaptured[0] != '-':
                    break

            endRow = r
            endCol = c
            for i in range(len(self.board)):
                endCol += m
                move = self.createMove(r, c, endRow, endCol)
                if not move:
                    break

                moves.append(move)

                if move.pieceCaptured[0] != '-':
                    break


    def getBishopMoves(self, r, c, moves):
        bishopMoves = ((1, 1), (-1, -1), (1, -1), (-1, 1))
        for m in bishopMoves:
            endRow = r
            endCol = c
            for i in range(len(self.board)):
                endRow += m[0]
                endCol += m[1]
                move = self.createMove(r, c, endRow, endCol)

                if not move:
                    break

                moves.append(move)

                if move.pieceCaptured[0] != '-':
                    break

    def getKnightMoves(self, r, c, moves):
        lis1 = (2, -2)
        lis2 = (1, -1)
        for i in lis1:
            for e in lis2:
                endRow = r+i
                endCol = c+e

                moves.append(self.createMove(r, c, endRow, endCol))

                endRow = r + e
                endCol = c + i

                moves.append(self.createMove(r, c, endRow, endCol))



    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))
        for i, e in kingMoves:
            endRow = r+i
            endCol = c+e
            moves.append(self.createMove(r, c, endRow, endCol))


        #self.getCastleMoves(r, c, moves)


        # color = self.board[r][c][0]
        #
        # if color == 'w':
        #     self.whiteKingMove = True
        # elif color == 'b':
        #     self.blackKingMove = True
        #
        # if color == 'w' and not self.whiteKingMove:
        #     pass
    def getCastleMoves(self, r, c, moves):
        if self.inCheck():
            return

        self.getKingSideCastleMoves(r, c, moves)
        self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.whiteToMove and (not self.castleRights.wkc):
            return
        elif not self.whiteToMove and (not self.castleRights.bkc):
            return

        if self.board[r][c+3][1] != 'R':
            return
        for i in range(1, 3):
            if self.board[r][c+i] != '--' or self.sqUnderAttack(r, c+i):
                return

        moves.append(Move((r, c), (r, c+2), self.board))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.whiteToMove and (not self.castleRights.wqc):
            return
        elif not self.whiteToMove and (not self.castleRights.bqc):
            return

        if self.board[r][c-4][1] != 'R':
            return

        for i in range(1, 3):
            if self.board[r][c - i] != '--' or self.sqUnderAttack(r, c - i):
                return

        if self.board[r][c - 3] != '--':
            return

        moves.append(Move((r, c), (r, c - 2), self.board))

    def createMove(self, startRow, startCol, endRow, endCol, anpassen=False, createAnpassen=()):
        if (-1 < endRow < 8) and (-1 < endCol < 8):
            if self.board[endRow][endCol][0] != self.board[startRow][startCol][0]:
                return Move((startRow, startCol), (endRow, endCol), self.board, anpassen=anpassen, createAnpassen=createAnpassen)

        return None


    def notationToMove(self, notation):
        startRow, startCol, endRow, endCol = None, None, None, None
        #print(notation)
        pieceMoved = 'p'
        isPawnPromotion = False
        pawnPromotionType = 'Q'
        anpassen = False
        start = ''
        end = ''

        # if notation[0] in self.piecesForNotation:
        #     pieceMoved = notation[0]
        #     if notation[1] in Move.filesToCols:

        if 'O-O' in notation:
            startRow, startCol = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
            endRow = startRow
            endCol = startCol+2
            #print('a')
            return Move((startRow, startCol), (endRow, endCol), self.board)
        elif 'O-O-O' in notation:
            startRow, startCol = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
            endRow = startRow
            endCol = startCol - 2
            #print('b')
            return Move((startRow, startCol), (endRow, endCol), self.board)

        if notation[0] in self.piecesForNotation:
            pieceMoved = notation[0]
            if notation[1] == 'x':
                start = notation[0]
                end = notation[2] + notation[3]
            elif notation[1] in Move.filesToCols:
                if notation[2] == 'x':
                    start = notation[0]+notation[1]
                    end = notation[3]+notation[4]
                elif notation[2] in Move.filesToCols:
                    start = notation[0]+notation[1]
                    end = notation[2]+notation[3]
                elif notation[2] in Move.ranksToRows:
                    start = notation[0]
                    end = notation[1]+notation[2]
            elif notation[1] in Move.ranksToRows:
                if notation[2] == 'x':
                    start = notation[0]+notation[1]
                    end = notation[3]+notation[4]
                elif notation[2] in Move.filesToCols:
                    start = notation[0]+notation[1]
                    end = notation[2]+notation[3]
        else:
            if 'x' in notation:
                start, end = notation.split('x')
            else:
                end = notation
            if '=' in end:
                index = end.find('=')
                pawnPromotionType = end[index + 1]
                end = end.replace('=', '')
                end = end.replace(pawnPromotionType, '')
            end = end.replace('+', '')

        return self.get_move(start, end, pieceMoved, pawnPromotionType)

    def get_move(self, start, end, pieceMoved, pawnPromotionType):
        #print('Start:  ' + start + '  End:  ' + end)
        #print('Piece Moved:  ' + pieceMoved)
        endRow, endCol = self.get_SQ_from_Notation(end)
        start2 = start.replace(pieceMoved, '')
        validMoves = self.getValidMoves()

        for move in validMoves:
            if (move.pieceMoved[1] == pieceMoved) and (move.endRow == endRow) and (move.endCol == endCol):
                move.pawnPromotionType = move.pieceMoved[0] + pawnPromotionType
                if start2 != '':
                    if start2 in Move.filesToCols and (Move.filesToCols[start2] == move.startCol):
                        return move
                    elif start2 in Move.ranksToRows and (Move.ranksToRows[start2] == move.startRow):
                        return move
                else:
                    return move

        return None

    def get_SQ_from_Notation(self, notation):
        row = Move.ranksToRows[notation[1]]
        col = Move.filesToCols[notation[0]]
        return row, col

    def board_to_nums(self):
        lis = []
        for i in self.board:
            for c in i:
                lis.append(self.piece_to_num[c])
        return lis


class Move:

    ranksToRows = {'1':7, '2':6, '3':5, '4':4, '5':3, '6':2, '7':1, '8':0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSQ, endSQ, board, anpassen=False, createAnpassen=(), pawnPromotionType='Q'):
        self.startRow = startSQ[0]
        self.startCol = startSQ[1]
        self.endRow = endSQ[0]
        self.endCol = endSQ[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isPawnPromotion = ((self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))
        self.pawnPromotionType = self.pieceMoved[0] + pawnPromotionType

        #self.castle = castle
        self.anpassen = anpassen
        self.createAnpassen = createAnpassen

        self.castleK = (((self.endCol-self.startCol) == 2) and self.pieceMoved[1] == 'K')
        self.castleQ = (((self.endCol-self.startCol) == -2) and self.pieceMoved[1] == 'K')

    def __eq__(self, other):
        if isinstance(other, Move):
            #if (self.startRow == other.startRow) and (self.startCol == other.startCol) and (self.endRow == other.endRow) and (self.endCol == other.endCol):
            #    return True
            if self.getChessNotation() == other.getChessNotation():
                return True
            return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def setPawnPromotionType(self, type):
        self.pawnPromotionType = self.pieceMoved[0] + type



class CastleRights:
    def __init__(self, wkc, bkc, wqc, bqc):
        self.wkc = wkc
        self.bkc = bkc
        self.wqc = wqc
        self.bqc = bqc