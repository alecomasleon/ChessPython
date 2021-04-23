import pygame as p
import Engine
import Player

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
images = {}
MAX_FPS = 15
pawnPromotionTypes = ['Q', 'R', 'B', 'N']

def load_images():
    pieces = ('wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK')
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("Images/"+ piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = Engine.GameState()
    validMoves = gs.getValidMoves()
    #gs.boardLog.update({(gs.board.copy, gs.whiteToMove): validMoves})

    moveMade = False

    load_images()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    printGameOver = 0

    comp = Player.Player(gs)

    while running:
        if gs.whiteToMove or gs.checkMate or gs.staleMate:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    if not gameOver:
                        location = p.mouse.get_pos()
                        col = location[0]//SQ_SIZE
                        row = location[1]//SQ_SIZE
                        if sqSelected == (row, col):
                            sqSelected = ()
                            playerClicks = []
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)

                        if len(playerClicks) == 2:
                            move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    if validMoves[i].isPawnPromotion:
                                        validMoves[i].pawnPromotionType = pawnPromotionScreen(screen, validMoves[i].pieceMoved[0])
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    sqSelected = ()
                                    playerClicks = []
                                    if len(gs.moveLog) != 0:
                                        animate_move(gs.moveLog[-1], screen, gs.board, clock)
                                        draw_game_state(screen, gs, validMoves, sqSelected)
                                        break

                        if not moveMade:
                            playerClicks = [sqSelected]
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_LEFT:
                        gs.undoMove()
                        gs.undoMove()
                        moveMade = True
                        printGameOver = 0
                    elif e.key == p.K_r:
                        if gs.checkMate or gs.staleMate:
                            gs = Engine.GameState()
                            comp = Player.Player(gs)
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                            printGameOver = 0
        else:
            if not gs.staleMate and not gs.checkMate:
                compMove = comp.findMove()[0]
                try:
                    gs.makeMove(compMove)
                except:
                    print('a')
                moveMade = True
                p.event.clear()

                if len(gs.moveLog) != 0:
                    animate_move(gs.moveLog[-1], screen, gs.board, clock)
                        #e = None

        if gs.checkMate:
            gameOver = True
            if printGameOver == 0:
                printGameOver = 1
            if printGameOver == 1:
                if gs.whiteToMove:
                    draw_text(screen, 'Black Wins By Checkmate')
                else:
                    draw_text(screen, 'White Wins By Checkmate')
                printGameOver = -1
            #running = False
        elif gs.staleMate:
            gameOver = True
            if printGameOver == 0:
                printGameOver = 1
            if printGameOver == 1:
                draw_text(screen, 'Draw')
                printGameOver = -1
        else:
            gameOver = False
            printGameOver = 0

        if moveMade and not gameOver:
            validMoves = gs.getValidMoves()
            moveMade = False
            #print((gs.castleRights.wqc, gs.castleRights.wkc, gs.castleRights.bqc, gs.castleRights.bkc))
            #print(gs.boardLog)

        if not gameOver:
            draw_game_state(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

TRANSPARENCY = 150

def pawnPromotionScreen(screen, color):
    sq = SQ_SIZE*2

    clock = p.time.Clock()

    s = p.Surface((WIDTH, HEIGHT))
    s.set_alpha(200)
    s.fill(p.Color('white'))
    screen.blit(s, (0, 0))

    for i in range(len(pawnPromotionTypes)):
        screen.blit(images[color+pawnPromotionTypes[i]], p.Rect(i*sq + SQ_SIZE/2, HEIGHT/2 - SQ_SIZE/2, sq, sq))

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//sq
                row = location[1]/sq
                if 1.5 < row < 2.5:
                    return color + pawnPromotionTypes[col]

        clock.tick(MAX_FPS)
        p.display.flip()

def highlightLastMove(screen, gs):
    if len(gs.moveLog) != 0:
        move = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(225)
        i = 28
        a = p.draw.circle(s, p.Color('purple'), (SQ_SIZE / 2, SQ_SIZE / 2), i)
        b = p.draw.circle(s, p.Color('purple'), (SQ_SIZE / 2, SQ_SIZE / 2), i-2)
        s.fill(p.Color('purple'), a)
        s.fill(p.Color(0), b)
        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
        screen.blit(s, (move.startCol*SQ_SIZE, move.startRow*SQ_SIZE))

def highlightCurrentSQ(screen, gs, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(TRANSPARENCY)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

def highlightMoves(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(225)
            a = p.draw.circle(s, p.Color('green'), (SQ_SIZE / 2, SQ_SIZE / 2), 7)

            for move in validMoves:
                #s.fill(p.Color('white'))
                s.fill(p.Color('green'), a)
                if move.startRow == r and move.startCol == c:
                    if move.pieceCaptured != '--':
                        s.fill(p.Color('red'), a)
                    elif move.castleK or move.castleQ:
                        s.fill(p.Color('purple'), a)
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def draw_game_state(screen, gs, validMoves, sqSelected):
    draw_board(screen)
    highlightLastMove(screen, gs)
    if sqSelected:
        highlightCurrentSQ(screen, gs, sqSelected)
    draw_pieces(screen, gs.board)
    if sqSelected:
        highlightMoves(screen, gs, validMoves, sqSelected)

def draw_board(screen):
    global colors
    colors = (p.Color('white'), p.Color('dark gray'))
    for i in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(i+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                image = images[piece]
                screen.blit(image, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animate_move(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSQ = 7
    frameCount = (abs(dR) + abs(dC)) * framesPerSQ

    capturedPiece = move.pieceCaptured
    pieceColor = board[move.endRow][move.endCol][0]

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        SQ_color = colors[(move.endRow + move.endCol) % 2]
        endSQ = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, SQ_color, endSQ)


        if move.anpassen:
            #print('a')
            # pieceColor = board[move.endRow][move.endCol][0]
            if pieceColor == 'w':
                #print('a')
                endSQ = p.Rect(move.endCol*SQ_SIZE, (move.endRow+1)*SQ_SIZE, SQ_SIZE, SQ_SIZE)
                capturedPiece = 'bp'
            else:
                endSQ = p.Rect(move.endCol * SQ_SIZE, (move.endRow-1) * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                capturedPiece = 'wp'

        if move.castleK:
            rookSQ = p.Rect((move.endCol - 1) * SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            rookSQ_color = colors[0] if pieceColor == 'w' else colors[1]

            rookSQ2 = p.Rect((move.endCol + 1)*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)

        elif move.castleQ:
            rookSQ = p.Rect((move.endCol + 1) * SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            rookSQ_color = colors[0] if pieceColor == 'w' else colors[1]

            rookSQ2 = p.Rect((move.endCol - 2) * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        if move.castleQ or move.castleK:
            p.draw.rect(screen, rookSQ_color, rookSQ)
            screen.blit(images[pieceColor + 'R'], rookSQ2)
        #p.draw.rect(screen, p.Color('green'), endSQ)

        if move.pieceCaptured != '--' or move.anpassen:
            screen.blit(images[capturedPiece], endSQ)

        screen.blit(images[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

    if move.castleK:
        dC = -2
        frameCount = abs(dC) * framesPerSQ
        startCol = move.startCol + 3
        endCol = move.endCol - 1
    elif move.castleQ:
        dC = 3
        frameCount = abs(dC) * framesPerSQ
        startCol = move.startCol -4
        endCol = move.endCol + 1
    if move.castleK or move.castleQ:
        for frame in range(frameCount + 1):
            r, c = (move.startRow, startCol + dC*frame/frameCount)
            draw_board(screen)
            draw_pieces(screen, board)
            SQ_color = colors[(move.endRow + endCol) % 2]

            endSQ = p.Rect(endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, SQ_color, endSQ)
            screen.blit(images[pieceColor+'R'], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            p.display.flip()
            clock.tick(60)

def draw_text(screen, text):
    #print('a')
    s = p.Surface((WIDTH, HEIGHT))
    s.set_alpha(TRANSPARENCY)
    s.fill(p.Color('white'))
    screen.blit(s, (0, 0))
    #print('b')

    font = p.font.SysFont('Helvitca', 32, True, False)
    #print('c')
    textObject = font.render(text, 0, p.Color('dark gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('black'))
    screen.blit(textObject, textLocation.move(-2, -2))


if __name__ == "__main__": main()