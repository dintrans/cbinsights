def positive_int_validator(x):
    try:
        if int(x) >= 0:
            return int(x)
    except:
        raise ValueError


def str_in_array_validator(x, arr):
    if x in arr:
        return x
    else:
        raise ValueError
