from NeuralNetworkPlayer import NeuralNetworkPlayer
import numpy as np
from PlayCompGame import play_game
import Engine
import random as rand


GAMES_LOG_FILE = 'neural_network_games.txt'
PLAYER_LOG_FILE = 'training_players.txt'
rounds = 0


def test():
    # comp1 = NeuralNetworkPlayer(weights=create_random_weights(-10, 10), biases=create_random_biases(-10, 10))
    # comp2 = NeuralNetworkPlayer(weights=create_random_weights(-10, 10), biases=create_random_biases(-10, 10))
    f = open(PLAYER_LOG_FILE, 'r')
    lines = f.readlines()
    f.close()
    comp1 = comp_from_logged_string(lines[2])
    comp2 = comp_from_logged_string(lines[3])
    gs = Engine.GameState()
    result = play_game(comp1, comp2, gs=gs)
    print(result)

    # open(GAMES_LOG_FILE, 'w').close()
    f = open(GAMES_LOG_FILE, 'a')
    log_game(gs, result, f)
    f.close()

    # open(PLAYER_LOG_FILE, 'w').close()
    f = open(PLAYER_LOG_FILE, 'a')
    log_player(comp1, f)
    log_player(comp2, f)
    f.close()


def train():
    response = input('Do you want to train and erase ' + GAMES_LOG_FILE + ' and ' + PLAYER_LOG_FILE + '. (y/n)')
    if response != 'y':
        return

    open(GAMES_LOG_FILE, 'w').close()
    open(PLAYER_LOG_FILE, 'w').close()

    best_comps = []

    while True:
        best_comps = do_round(best_comps)


def first_round():
    comps = create_first_comps()

    print('Doing round number' + str(rounds))

    winners = []

    games_file = open(GAMES_LOG_FILE, 'a')

    for i in range(len(comps)):
        for c in range(1, 4):
            index = i + c

            if index > len(comps) - 1:
                index = c - (len(comps) - i)

            gs = Engine.GameState()
            result = play_game(comps[i], comps[index], gs)

            log_game(gs, result, games_file)

            if result == 1:
                winners.append(comps[i])
            elif result == -1:
                winners.append(comps[index])

    games_file.close()

    if len(winners) == 0:
        return first_round()

    player_file = open(PLAYER_LOG_FILE, 'a')
    player_file.write('Round: ' + str(rounds))
    for i in winners:
        log_player(i, player_file)
    player_file.close()

    return winners


def do_round(prev_comps):
    global rounds
    rounds += 1

    comps = create_comps(prev_comps)

    print('Doing round number ' + str(rounds))
    print('Length of generation is: ' + str(len(comps)))

    scores = [0] * len(comps)

    games_file = open(GAMES_LOG_FILE, 'a')

    for i in range(len(comps)):
        for c in range(1, 3):
            index = i + c

            if index > len(comps) - 1:
                index = c - (len(comps) - i)

            gs = Engine.GameState()
            result = play_game(comps[i], comps[index], gs)

            log_game(gs, result, games_file)

            if result == 1:
                scores[i] += 3
            elif result == -1:
                scores[index] += 3
            else:
                scores[i] += 1
                scores[index] += 1

    games_file.close()

    best_comps = []
    best_scores = []

    for i in range(len(comps)):
        if len(best_comps) < 4:
            best_comps.append(comps[i])
            best_scores.append(scores[i])
        else:
            minimum = min(best_scores)

            if scores[i] > minimum:
                index = best_scores.index(minimum)
                best_comps[index] = comps[i]
                best_scores[index] = scores[i]

    player_file = open(PLAYER_LOG_FILE, 'a')
    player_file.write('Round: ' + str(rounds))
    for i in best_comps:
        log_player(i, player_file)
    player_file.close()

    print('End of Round ' + str(rounds) + ', best_comps length: ' + str(len(best_comps)))
    print()

    return best_comps


def create_first_comps():
    print('Running create_first_comps()')
    comps = []

    for i in range(70):
        comps.append(NeuralNetworkPlayer(weights=create_random_weights(-10, 10), biases=create_random_biases(-10, 10)))

    return comps


def create_comps(best_comps):
    global rounds
    if rounds == 1:
        return create_first_comps()

    comps = best_comps
    for i in range(70//2):
        parent1 = rand.choice(best_comps)
        parent2 = rand.choice(best_comps)

        split = rand.randint(0, len(parent1.weights) - 2)
        child1 = NeuralNetworkPlayer(weights=parent1.weights[0:split] + parent2.weights[split:],
                                     biases=parent1.biases[0:split] + parent2.biases[split:])
        child2 = NeuralNetworkPlayer(weights=parent2.weights[0:split] + parent1.weights[split:],
                                     biases=parent2.biases[0:split] + parent1.biases[split:])

        for c in range(3000):
            layer = rand.randint(0, len(child1.weights) - 1)
            rand1, rand2 = child1.weights[layer].shape
            num1 = rand.randint(0, rand1 - 1)
            num2 = rand.randint(0, rand2 - 1)

            child1.weights[layer][num1][num2] = np.random.uniform(-7, 7)
            child2.weights[layer][num1][num2] = np.random.uniform(-7, 7)

        comps.append(child1)
        comps.append(child2)

    return comps


def create_comps_old(best_comps):
    comps = []
    for c in best_comps:
        comps.append(c)

        for i in range(14):
            weights = average(c.weights, create_random_weights(-5, 5))
            biases = average(c.biases, create_random_biases(-5, 5))
            comps.append(NeuralNetworkPlayer(weights=weights, biases=biases))

    global rounds
    rounds += 1

    return comps


def average(variables, random):
    global rounds

    final = []

    for i in range(len(variables)):
        final.append((variables[i] * rounds + random[i])/(rounds + 1))

    return final


def create_random_weights(min, max):
    weights = [np.random.uniform(min, max, (NeuralNetworkPlayer.NODES_PER_LAYER, 64 * 12 + 1)),
               np.random.uniform(min, max, (NeuralNetworkPlayer.NODES_PER_LAYER, NeuralNetworkPlayer.NODES_PER_LAYER)),
               np.random.uniform(min, max, (NeuralNetworkPlayer.NODES_PER_LAYER, NeuralNetworkPlayer.NODES_PER_LAYER)),
               np.random.uniform(min, max, (NeuralNetworkPlayer.NODES_PER_LAYER, NeuralNetworkPlayer.NODES_PER_LAYER)),
               np.random.uniform(min, max, (NeuralNetworkPlayer.NODES_PER_LAYER, NeuralNetworkPlayer.NODES_PER_LAYER)),
               np.random.uniform(min, max, (2, NeuralNetworkPlayer.NODES_PER_LAYER))]

    return weights


def create_random_biases(min, max):
    biases = [np.random.uniform(min, max, NeuralNetworkPlayer.NODES_PER_LAYER),
              np.random.uniform(min, max, NeuralNetworkPlayer.NODES_PER_LAYER),
              np.random.uniform(min, max, NeuralNetworkPlayer.NODES_PER_LAYER),
              np.random.uniform(min, max, NeuralNetworkPlayer.NODES_PER_LAYER),
              np.random.uniform(min, max, NeuralNetworkPlayer.NODES_PER_LAYER),
              np.random.uniform(min, max, 2)]

    return biases


def log_game(gs, result, file):
    string = ''
    for move in gs.moveLog:
        string += move.getChessNotation() + ' '

    string += ';' + str(result)
    string += '\n'
    file.write(string)


def log_player(comp, file):
    string = ''
    for matrix in comp.weights:
        for vector in matrix:
            for value in vector:
                string += str(value) + ' '
            string += ','
        string += ';'

    string += ':'

    for vector in comp.biases:
        for value in vector:
            string += str(value) + ' '
        string += ','

    string += '\n'

    file.write(string)


def comp_from_logged_string(string):
    w, b = string.split(':')

    weights = []

    for matrix in w.split(';'):
        if matrix == '':
            continue
        array = []
        for vector in matrix.split(','):
            if vector == '':
                continue
            array.append([])
            for value in vector.split():
                array[-1].append(float(value))
        weights.append(np.array(array))
        # print(np.array(array).shape)

    biases = []

    for vector in b.split(','):
        if vector == '\n':
            continue
        array = []
        for value in vector.split():
            array.append(float(value))
        biases.append(np.array(array))

    # print(len(weights))
    # print(weights[0].shape)
    # print(len(biases))
    # print(biases[0].shape)

    return NeuralNetworkPlayer(weights=weights, biases=biases)


def get_best_comp():
    f = open(PLAYER_LOG_FILE, 'r')
    lines = f.readlines()
    f.close()

    comps = []
    lines = lines[len(lines)//2:]

    for i in lines:
        if 'ound' not in i:
            comps.append(comp_from_logged_string(i))

    lines = 0

    print(len(comps))

    scores = [0] * len(comps)

    for i in range(len(comps)):
        for c in range(3):
            index = rand.randint(0, len(comps) - 1)

            gs = Engine.GameState()
            result = play_game(comps[i], comps[index], gs)

            if result == 1:
                scores[i] += 3
            elif result == -1:
                scores[index] += 3
            else:
                scores[i] += 1
                scores[index] += 1

    best_comps = []
    best_scores = []
    best_indexes = []

    for i in range(len(comps)):
        if len(best_comps) < 3:
            best_comps.append(comps[i])
            best_scores.append(scores[i])
            best_indexes.append(i)
        else:
            minimum = min(best_scores)

            if scores[i] > minimum:
                index = best_scores.index(minimum)
                best_comps[index] = comps[i]
                best_scores[index] = scores[i]
                best_scores[index] = i

    print(best_indexes)
    print(best_scores)

    comps = best_comps
    scores = [0] * len(comps)

    for i in range(len(comps)):
        for c in range(1, 3):
            index = i + c

            if index > len(comps) - 1:
                index = c - (len(comps) - i)

            gs = Engine.GameState()
            result = play_game(comps[i], comps[index], gs)

            if result == 1:
                scores[i] += 3
            elif result == -1:
                scores[index] += 3
            else:
                scores[i] += 1
                scores[index] += 1

    best_score = -1
    best_comp = 0
    best_index = -1
    for i in range(len(comps)):
        if scores[i] > best_score:
            best_score = scores[i]
            best_comp = comps[i]
            best_index = i

    print(best_index)

    f = open('best_neural_network.txt', 'w')
    log_player(best_comp, f)
    f.close()


if __name__ == "__main__":
    # train()
    get_best_comp()
    # first_round()
