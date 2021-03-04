import random
import time


if __name__ == '__main__':
    while True:
        with open('app/index.html', 'w') as fh:
            fh.write(str(random.random()))
        time.sleep(random.random() * 10 + 1)
