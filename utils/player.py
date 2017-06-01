from constants import *
from wall import Wall
from random import randint

class Player(object):
    def __init__(self, name, x, y, dir):
        self.name = name
        self.x = (x / PLAYERVEL) * PLAYERVEL
        self.y = (y / PLAYERVEL) * PLAYERVEL
        self.dir = dir
        self.input = Input()
        self.walls = [Wall(dir, x, y)]
        self.color = ['blu', 'red'][randint(0, 1)]


class Input(object):
    def __init__(self):
        self.key = None
