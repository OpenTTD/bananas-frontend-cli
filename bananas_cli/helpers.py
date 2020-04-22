import asyncio


def task(func):
    def decorator(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func(*args, **kwargs))

    decorator.__name__ = func.__name__
    decorator.__doc__ = func.__doc__
    return decorator
