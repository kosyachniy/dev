def sort_by_preset(array, order):
    max_value = len(order) + 1
    ordering = lambda i: order.index(i) if i in order else max_value
    return sorted(array, key=ordering)
