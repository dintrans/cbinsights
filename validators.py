def positive_int_validator(x):
    if int(x)>=0:
        return int(x)
    else:
        raise ValueError

def string_in_array_validator(x,arr):
    if x in arr:
        return x
    else:
        raise ValueError