from constants import *
from wall import Wall
from random import randint

class Player(object):
    def __init__(self, name, x, y, dir, col):
        self.name = name
        self.x = x
        self.y = y
        self.dir = dir
        self.input = Input()
        self.walls = [Wall(dir, x, y)]
        self.color = col
        self.dead = False


class Input(object):
    def __init__(self):
        self.key = None
