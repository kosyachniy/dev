import os


LANG = 'ru'


def find_word(
    speech='nouns',
    length=None,
    positions=None,
    exists=None,
    unexists=None,
):
    words = []

    with open(f'{LANG}/{speech}.txt', 'r') as file:
        for word in file:
            word = word.strip().lower()

            if not word:
                continue

            if length and len(word) != length:
                continue

            if positions and any(word[k-1] != v for k, v in positions.items()):
                continue

            if exists and any(symbol not in word for symbol in exists):
                continue

            if unexists and any(symbol in word for symbol in unexists):
                continue

            words.append(word)

    return words


if __name__ == '__main__':
    words = find_word(
        length=5,
        positions={3: 'р'},
        exists={'и', 'с'},
        unexists={'у', 'к', 'н', 'а', 'о', 'ж', 'м'},
    )

    print(len(words))
    print(*words, sep=", ")
