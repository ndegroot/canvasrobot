def need_more_values_warning():
    return 1, 2, 3


class AsClass:
    def need_more_values_warning(self):
        return 1, 2, 3


if __name__ == '__main__':
    a, b, c = need_more_values_warning()  # ok

    my_instance = AsClass()

    d, e, f = my_instance.need_more_values_warning()

    print(a)
    print(b)
    print(c)
