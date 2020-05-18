import os

from Base import main


def start(test=0):
    # todo: print that all new songs will be downloaded in which folder
    main.start(test=test)


if os.path.isfile('Base/test_bit.py'):
    test = 1
else:
    test = 0

start(test=test)

# todo: add logs
