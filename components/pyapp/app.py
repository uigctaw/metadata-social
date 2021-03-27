import pathlib
import random
import time


if __name__ == '__main__':
    while True:
        pathlib.Path('data').mkdir(exist_ok=True)
        with open('data/index.html', 'w') as fh:
            fh.write(str(random.random()))
        time.sleep(random.random() * 10 + 1)
