import os


LANG = 'ru'
NOTIFY_LIMIT = None


def combine_files(speech, notify=True, count_letters=None):
    words = set()

    for file_name in sorted(os.listdir(f'{LANG}/{speech}/')):
        count = len(words)

        with open(f'{LANG}/{speech}/{file_name}', 'r') as file:
            included = set()

            for row in file:
                word = row.strip().lower()

                if not word or word[0] == '#':
                    continue

                if count_letters and len(word) != count_letters:
                    continue

                if word not in words:
                    words.add(word)
                    included.add(word)

        if notify:
            print(f"{file_name}:  +{len(words) - count} words")

            if count and (not NOTIFY_LIMIT or count < NOTIFY_LIMIT):
                print(*included, sep=", ")

    return words

def select_words(speech='nouns', count_letters=None):
    words = combine_files(speech, notify=True, count_letters=count_letters)
    exclude = combine_files(
        'exclude', notify=False, count_letters=count_letters,
    )

    count = len(words)
    excluded = set()

    for word in exclude:
        if word in words:
            excluded.add(word)
            words.remove(word)

    print(f"-{count - len(words)} words")
    print(*excluded, sep=", ")


if __name__ == '__main__':
    select_words()
