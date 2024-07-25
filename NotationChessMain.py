import pygame as p
import Main as m
import Engine
import TrainNeuralNetwork as tnn


def main(game):
    p.init()
    screen = p.display.set_mode((m.WIDTH, m.HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = Engine.GameState()

    m.load_images()
    #game = input()
    # game = MakeModel.main()

    moveLis = simplified_notation_to_moveLis(game)

    print(len(moveLis))
    #print(len(boardLis))
    #print(boardLis)

    for i in moveLis:
        gs.undoMove()

    running = True
    index = -1
    while running:
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    if index != -1:
                        gs.undoMove()
                        index -= 1
                    else:
                        index = len(moveLis) - 1
                        for i in moveLis:
                            gs.makeMove(i)
                elif e.key == p.K_RIGHT or e.key == p.K_SPACE:
                    if index != len(moveLis)-1:
                        index += 1
                        gs.makeMove(moveLis[index])
                        m.animate_move(moveLis[index], screen, gs.board, clock)
            elif e.type == p.QUIT:
                running = False

        m.draw_game_state(screen, gs, (), None)
        clock.tick(m.MAX_FPS)
        p.display.flip()


def notation_to_moveLis(game):
    gs = Engine.GameState()

    game = game.split()

    moveLis = []

    for i in game:
        move = gs.notationToMove(i)
        try:
            gs.makeMove(move)
        except:
            return []
        # print(i)
        # print(type(move))
        moveLis.append(move)

    return moveLis


def simplified_notation_to_moveLis(game):
    gs = Engine.GameState()

    game = game.split(';')
    game = game[0].split()

    moveLis = []

    for i in game:
        move = gs.createMove(Engine.Move.ranksToRows[i[1]],
                             Engine.Move.filesToCols[i[0]],
                             Engine.Move.ranksToRows[i[3]],
                             Engine.Move.filesToCols[i[2]])
        try:
            gs.makeMove(move)
        except:
            return []

        moveLis.append(move)

    return moveLis


def copy(board):
    copyied = []
    for i in board:
        lis = []
        for c in i:
            lis.append(c)
        copyied.append(lis)
    return copyied


if __name__ == '__main__':
    f = open(tnn.GAMES_LOG_FILE, 'r')
    game = f.readline()
    f.close()
    main(game=game)
