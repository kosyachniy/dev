def counting_sort(collection, d_range, digit=-1):
    d_range += 1

    B = list(range(len(collection) + 1))
    C = list(range(d_range))

    for i in range(d_range):
        C[i] = 0

    for j in collection:
        C[j[digit]] += 1

    for i in range(1, d_range):
        C[i] = C[i] + C[i - 1]

    for i in range(len(collection)-1, -1, -1):
        B[C[collection[i][digit]]] = collection[i]
        C[collection[i][digit]] -= 1

    return B[1:]

def radix_sort(collection, radix):
    new_collect = []
    max_len = 0

    for i in collection:
        num = []
        while i >= radix:
            remain = i % radix
            num.append(remain)
            i = i // radix
        num.append(i)
        new_collect.append(num)

        if len(num) > max_len:
            max_len = len(num)

    for i in range(0, len(new_collect)):
        space = max_len - len(new_collect[i])
        patch = [0 for j in range(space)]
        new_collect[i].extend(patch)

        new_collect[i].append(i)
        new_collect[i].reverse()

    for i in range(-1, -1 - max_len, -1):
        new_collect = counting_sort(new_collect, radix - 1, i)

    return_list = list(range(len(collection)))

    for i in range(0, len(collection)):
        return_list[i] = collection[new_collect[i][0]]

    return return_list


if __name__ == '__main__':
	print(radix_sort([1234, 56, 7, 77, 23, 15, 16, 16, 6, 222], 8))