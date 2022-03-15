import time


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func_return_val = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'{func.__name__}: {end - start}')
        return func_return_val

    return wrapper


def api_ok(result):
    return {'ok': True, 'result': result}


def api_error(code, name):
    return {'ok': False, 'error': {'code': code, 'name': name}}
