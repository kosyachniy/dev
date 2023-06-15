import time
import csv

import numpy as np
import matplotlib.pyplot as plt


def get_data(name='data.csv', skip=1, sign=','):
    with open(name, 'r') as file:
        data = list(csv.reader(file, delimiter=sign, quotechar=' '))[skip:]
        return data

def process_google_search_data(data, col=1):
    x = []
    y = []

    for row in data[::-1]:
        date = time.strptime(row[0], '%Y-%m-%d')
        x.append(int(time.mktime(date)))
        y.append(int(row[col]))

    return x, y

def process_telegram_data(data, col=1):
    x = []
    y = []

    for row in data[::-1]:
        date = time.strptime(row[0], '%d.%m.%y')
        x.append(int(time.mktime(date)))
        y.append(int(row[col]))

    return x, y

def aprox(x, y, level=2):
    # f = interpolate.interp1d(x, y)
    return np.polyfit(x, y, level)

def predict(f, x, period, volume):
    frames = []

    for current in x:
        if len(frames) > period:
            frames = frames[1:]

        y = np.poly1d(f)(current)
        frames.append(y)

        print(sum(frames))
        if sum(frames) >= volume:
            break

    else:
        while True:
            if len(frames) > period:
                frames = frames[1:]

            current += 86400
            x.append(current)

            y = np.poly1d(f)(current)
            frames.append(y)

            print(sum(frames))
            if sum(frames) >= volume:
                break

    return current, x

def get_date(date):
    return time.strftime('%d.%m.%Y', time.localtime(date))

def get_graph_data(f, x):
    return [round(i, 2) for i in np.poly1d(f)(x)]

def graph(x, y, f):
    x = [time.strftime('%d.%m', time.localtime(day)) for day in x]

    plt.grid(True)
    plt.xticks(rotation=90)
    plt.plot(x[:len(y)], y)
    plt.plot(x, f)
    plt.show()

def main(name='data.csv', col=1, volume=1000, period=30, level=3):
    data = get_data(name)
    x, y = process_telegram_data(data, col)
    f = aprox(x, y, level)
    date, x = predict(f, x, period, volume)
    day = get_date(date)
    print(day)
    f = get_graph_data(f, x)
    graph(x, y, f)


if __name__ == '__main__':
    main('data.csv', 1, 30000)
    # main('data.csv', 2, 10000000)
    # main('data2.csv', 1, 250, 1)
