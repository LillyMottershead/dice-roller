def ensure_tuple_return(func):
    def wrapper(*args, **kwargs):
        func_return = func(*args, **kwargs)
        if type(func_return) is tuple:
            return func_return
        return func_return,
    return wrapper