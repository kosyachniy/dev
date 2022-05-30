import os
from collections import defaultdict


LANG = 'ru'


def combine_files(
    speech,
    notify=True,
    count_letters=None,
    replace=None,
    frequency=1,
):
    words_files = {}
    words_counter = defaultdict(int)

    for file_name in sorted(os.listdir(f'{LANG}/{speech}/')):
        with open(f'{LANG}/{speech}/{file_name}', 'r') as file:
            words_files[file_name] = set()

            for row in file:
                word = row.strip().lower()

                if not word or word[0] == '#':
                    continue

                if count_letters and len(word) != count_letters:
                    continue

                if replace:
                    for letter_from, letter_to in replace.items():
                        word = word.replace(letter_from, letter_to)

                if word not in words_files[file_name]:
                    words_files[file_name].add(word)
                    words_counter[word] += 1

    words_once = {i for i in words_counter if words_counter[i] == 1}

    if notify:
        print(f"BASE:  {len(words_counter) - len(words_once)} words")

        for file_name, words_file in words_files.items():
            words_included = words_file & words_once
            print(f"{file_name}:  +{len(words_included)} words")
            print(*words_included, sep=", ")

    return {word for word, count in words_counter.items() if count >= frequency}

def select_words(
    speech='nouns',
    notify=True,
    count_letters=None,
    replace=None,
    frequency=1,
    exclude=False,
):
    words = combine_files(
        speech,
        notify=notify,
        count_letters=count_letters,
        replace=replace,
        frequency=frequency,
    )

    if exclude:
        exclude = combine_files(
            'exclude',
            notify=False,
            count_letters=count_letters,
            replace=replace,
        )

        count = len(words)
        excluded = set()

        for word in exclude:
            if word in words:
                excluded.add(word)
                words.remove(word)

        print(f"-{count - len(words)} words")
        print(*excluded, sep=", ")

    return words


if __name__ == '__main__':
    words = select_words(notify=False)
    print(f"All: {len(words)}")

    words = select_words(
        count_letters=5,
        replace={'ё': 'е'},
        frequency=1,
        exclude=True,
    )
    print(f"5 letters: {len(words)}")
    print(*words, sep=", ")
