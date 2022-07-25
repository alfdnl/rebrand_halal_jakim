import time


def timer(func):
    # Decorator wrapper function to time process
    def wrapper(*args, **kwargs):
        before = time.time()
        func(*args, **kwargs)
        print("Process takes {:.2f} seconds".format((time.time() - before)))

    return wrapper
