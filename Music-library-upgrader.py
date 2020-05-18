import os

from Base import main


def start(test=0):
    main.start(test=test)


if os.path.isfile('Base/test_bit.py'):
    test = 1
else:
    test = 0

start(test=test)

# todo:
