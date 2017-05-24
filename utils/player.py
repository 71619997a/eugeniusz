from constants import *


class Player(object):
    def __init__(self, name):
        self.name = name
        self.pos = [0,0]
        self.dir = UP
        self.input = Input()


class Input(object):
    def __init__(self):
        self.key = 'W'
