import pandas as pd
import NotationChessMain as ncm
import Engine
from sklearn.model_selection import train_test_split
import pickle as p
import numpy as np
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
import random as rand
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt
from sklearn import metrics


move_dict_indexes = []


def main():
    games = pd.read_csv('chess_games_data.csv')
    #print(games.sample(1))
    #print(games.columns)
    game = list(games.sample(1)['game'])
    game = game[0]
    print(game)
    #print(type(game))
    return game
    #games.sample(1)['White Player Rating']


def average_elo_points():
    games = pd.read_csv('games.csv')
    white_average = 0
    black_average = 0
    for i in games['white_rating']:
        white_average += i/len(games['white_rating'])

    for i in games['black_rating']:
        black_average += i/len(games['black_rating'])
    print(white_average)
    print(black_average)

def eloPoints():
    games = pd.read_csv('games.csv')
    over_2000 = 0
    int = 2000
    for i in games['white_rating']:
        if i > int:
            over_2000+=1

    for i in games['black_rating']:
        if i > int:
            over_2000+=1
    print(len(games))
    print(over_2000)

def open_games_file():
    f = open('raw_downloaded_data.txt', 'r')
    file = f.readlines()
    categories = file[4]
    for i in range(5):
        file.remove(file[0])
    #print(file[0:5])
    categories = categories.split()
    categories.remove(categories[0])
    temp = []
    for i in categories:
        index = i.find('.')
        num = i[index - 1]
        i = i.replace('.', '')
        i = i.replace(num, '')
        temp.append(i)
    categories = temp
    print(categories)

    data_dict = {}
    for i in file:
        data = split_line(i, categories)
        data_dict[data['t']] = data
    data = pd.DataFrame.from_dict(data_dict, orient='index')
    data.drop(columns=['t'])
    data.to_csv('chess_games_data.csv')


def split_line(line, categories):
    index = line.find('###')

    data = line[:index]
    game = line[index:]
    game = game.replace('###', '')

    data = data.split()
    game = game.split()

    dict = {}
    final_game = ''
    for i in range(len(data)):
        dict[categories[i]] = data[i]
    for i in game:
        index = i.find('.')
        num = i[:index]
        i = i.replace('.', '')
        i = i.replace(num, '')
        final_game += i
        final_game += ' '

    dict['game'] = final_game

    return dict


def e():
    games = pd.read_csv('chess_games_data.csv')
    #games = games.to_dict()
    a = games['welo']
    b = games['belo']
    average = 0
    i = 0
    nones = 0
    for elo in a:
        i += 1
        try:
            average += int(elo)
        except:
            nones += 1

    for elo in b:
        i += 1
        try:
            average += int(elo)
        except:
            nones += 1


    average = average/i
    print('Average:  ' + str(average))
    print('Nones:  ' + str(nones))


def create_num_dataset():
    games = pd.read_csv('chess_games_data.csv')
    notations = games['game']
    moves_dict = {}
    index = 0
    package_size = 20000
    f = open('chess_games_modified_data.csv', 'a')
    create_move_dict_indexes()
    for game in notations:
        print(index)
        if not index % package_size:
            if index != 0:
                if index <= package_size:
                    df = pd.DataFrame.from_dict(moves_dict, orient='index')
                    df.to_csv('chess_games_modified_data.csv')
                    moves_dict = {}
                    df = 0
                else:
                    add_str = dict_to_csv_str_format(moves_dict)
                    f.write(add_str)
                    moves_dict = {}
        gs = Engine.GameState()
        try:
            moveLis = ncm.notation_to_moveLis(game)
        except:
            continue
        # prev = 0
        for move in moveLis:
            startBoard = gs.board_to_nums()
            # print(prev == startBoard)
            # prev = startBoard
            validMoves = gs.getValidMoves()
            for i in validMoves:
                gs.makeMove(i)
                endBoard = gs.board_to_nums()
                if i == move:
                    correctMove = 1
                else:
                    correctMove = 0
                move_dict = create_move_dict(startBoard, endBoard, correctMove)
                moves_dict[index] = move_dict
                index += 1
                gs.undoMove()
            gs.makeMove(move)
        return

    add_str = dict_to_csv_str_format(moves_dict)
    f.write(add_str)
    f.close()


def create_balanced_num_dataset():
    games = pd.read_csv('chess_games_data.csv')
    notations = games['game']
    moves_dict = {}
    index = 0
    first = True
    package_size = 10000
    # open('chess_games_modified_data.csv', 'w').close()
    f = open('chess_games_modified_data.csv', 'a')
    create_move_dict_indexes()
    for game in notations:
        print(index)
        if index % package_size <= 200 and index > 200:
            if first:
                df = pd.DataFrame.from_dict(moves_dict, orient='index')
                df.to_csv('chess_games_modified_data.csv')
                moves_dict = {}
                df = 0
                first = False
            else:
                add_str = dict_to_csv_str_format(moves_dict)
                f.write(add_str)
                moves_dict = {}
        gs = Engine.GameState()
        try:
            moveLis = ncm.notation_to_moveLis(game)
        except:
            continue
        # prev = 0
        for move in moveLis:
            startBoard = gs.board_to_nums()
            # print(prev == startBoard)
            # prev = startBoard
            validMoves = gs.getValidMoves()

            for i in validMoves:
                if i == move:
                    gs.makeMove(i)
                    endBoard = gs.board_to_nums()
                    move_dict = create_move_dict(startBoard, endBoard, 1)
                    moves_dict[index] = move_dict
                    index += 1
                    gs.undoMove()
                    validMoves.remove(i)

            if len(validMoves) > 0:
                n = rand.randint(0, len(validMoves) - 1)
                m = validMoves[n]

                gs.makeMove(m)
                endBoard = gs.board_to_nums()
                move_dict = create_move_dict(startBoard, endBoard, 0)
                moves_dict[index] = move_dict
                index += 1
                gs.undoMove()

            gs.makeMove(move)

    add_str = dict_to_csv_str_format(moves_dict)
    f.write(add_str)
    f.close()


def create_move_dict_indexes():
    global move_dict_indexes
    #move_dict_indexes = []
    for i in range(64):
        move_dict_indexes.append('Start' + str(i+1))
    for i in range(64):
        move_dict_indexes.append('End' + str(i+1))
    move_dict_indexes.append('correct_move')
    move_dict_indexes = tuple(move_dict_indexes)


def create_move_dict(startBoard, endBoard, correctMove):
    global move_dict_indexes
    move_dict = {}
    i = 0
    for c in startBoard:
        move_dict[move_dict_indexes[i]] = c
        i += 1
    for c in endBoard:
        move_dict[move_dict_indexes[i]] = c
        i += 1
    move_dict[move_dict_indexes[i]] = correctMove
    return move_dict


def dict_to_csv_str_format(data):
    string = ''
    for i in data:
        string += str(i)
        for c in data[i]:
            string += ',' + str(data[i][c])
        string += '\n'
    return string


def create_model():
    df_iterator = pd.read_csv('chess_games_modified_data.csv', chunksize=1000000)
    index = 0
    for i in df_iterator:
        if index < 2:
            line = i.sample(1)
            print(type(i))
            print(type(line))
            print(line)
            index += 1


def create_train_test():
    chunksize = 500000
    df_iterator = pd.read_csv('chess_games_modified_data.csv', chunksize=chunksize)
    open('final_modified_data/train_modified.csv', 'w').close()
    open('final_modified_data/test_modified.csv', 'w').close()
    train_data = open('final_modified_data/train_modified.csv', 'a')
    test_data = open('final_modified_data/test_modified.csv', 'a')
    index = 0
    for data in df_iterator:
        #Y = pd.factorize(i['0.65'])[0]
        #X = i.drop(['0.65'], axis=1)
        #print(type(Y))
        #print(X)

        Y = np.zeros((chunksize))
        train, test, g, h = train_test_split(data, Y, test_size=0.1, random_state=42)

        #print('X_train  ' + str(len(train)))
        #print('X_test  ' + str(len(test)))
        if index == 0:
            train.to_csv('final_modified_data/train_modified.csv')
            test.to_csv('final_modified_data/test_modified.csv')
        else:
            train = train.to_dict(orient='index')
            test = test.to_dict(orient='index')

            train_data.write(dict_to_csv_str_format(train))
            test_data.write(dict_to_csv_str_format(test))
        index += 1
        print(index)
        if index == None:
            break
    train_data.close()
    test_data.close()


def create_passive_aggressive_classifier_model():
    chunksize = 500000
    df_iterator = pd.read_csv('final_modified_data/train_modified.csv', chunksize=chunksize)
    model = PassiveAggressiveClassifier(verbose=2)
    index = 0
    for data in df_iterator:
        y = data['correct_move']
        y = y.to_numpy()
        del data['correct_move']
        del data['Unnamed: 0']
        del data['Unnamed: 0.1']
        # print(data.head(5))

        model.partial_fit(data, y, classes=np.unique(y))
        index += chunksize
        print(index)

    f = open('passive_aggressive_classifier_model', 'wb')
    p.dump(model, f)
    f.close()


def create_SGD_classifier_model():
    chunksize = 500000
    df_iterator = pd.read_csv('final_modified_data/train_modified.csv', chunksize=chunksize)
    model = SGDClassifier(verbose=2)
    index = 0
    for data in df_iterator:
        y = data['correct_move']
        y = y.to_numpy()
        del data['correct_move']
        del data['Unnamed: 0']
        del data['Unnamed: 0.1']
        #print(data.head(5))

        model.partial_fit(data, y, classes=np.unique(y))
        index += chunksize
        print(index)

    f = open('SGD_classifier_model', 'wb')
    p.dump(model, f)
    f.close()


def create_RandomForestClassifier_model():
    data = pd.read_csv('final_modified_data/train_modified.csv')
    model = RandomForestClassifier(verbose=2)

    print("here 1")
    print(data.head(5))

    y = data['correct_move']
    y = y.to_numpy()
    del data['correct_move']
    del data['Unnamed: 0']
    del data['Unnamed: 0.1']

    print("here 2")
    print(data.head(5))
    print(data.shape)

    model.fit(data, y)
    data = 0

    f = open('RandomForestClassifier_model', 'wb')
    p.dump(model, f)
    f.close()


def learningCurve():
    data = pd.read_csv('final_modified_data/train_modified.csv')
    model = RandomForestClassifier()
    y = data['correct_move']
    y = y.to_numpy()
    del data['correct_move']

    train_sizes = [50000, 500000, 5000000, 15000000, 19000000]
    cv = 5

    train_sizes, train_scores, validation_scores = learning_curve(
        estimator=model,
        X=data, y=y,
        train_sizes=train_sizes, cv=cv,
        scoring='neg_mean_squared_error')

    train_scores_mean = -train_scores.mean(axis=1)
    validation_scores_mean = -validation_scores.mean(axis=1)

    plt.style.use('seaborn')
    plt.plot(train_sizes, train_scores_mean, label='Training error')
    plt.plot(train_sizes, validation_scores_mean, label='Validation error')
    plt.ylabel('MSE', fontsize=14)
    plt.xlabel('Training set size', fontsize=14)
    plt.title('Learning curves', fontsize=18, y=1.03)
    plt.legend()
    plt.ylim(0, 40)


def test_model(file_name= 'SGD_classifier_model'):
    f = open(file_name, 'rb')
    model = p.load(f)
    data = pd.read_csv('final_modified_data/test_modified.csv')

    y = data['correct_move']
    y = y.to_numpy()
    del data['correct_move']
    del data['Unnamed: 0']
    del data['Unnamed: 0.1']

    score = model.score(data, y)

    predictions = model.predict(data)

    f1 = metrics.f1_score(y_true=y, y_pred=predictions)

    print('Score = ' + str(score))
    print('F1 Score = ' + str(f1))
    f.close()


def create_train_test2():
    df = pd.read_csv('chess_games_modified_data.csv')
    open('final_modified_data/train_modified.csv', 'w').close()
    open('final_modified_data/test_modified.csv', 'w').close()

    Y = np.zeros(df.shape[0])
    train, test, g, h = train_test_split(df, Y, test_size=0.1, random_state=42)
    df = 0

    print('X_train  ' + str(len(train)))
    print('X_test  ' + str(len(test)))

    train.to_csv('final_modified_data/train_modified.csv')
    test.to_csv('final_modified_data/test_modified.csv')


if __name__ == '__main__':
    # create_balanced_num_dataset()
    # create_train_test2()
    # create_passive_aggressive_classifier_model()
    test_model('passive_aggressive_classifier_model')
