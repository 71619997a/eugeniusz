class Player(object):
    def __init__(self, name):
        self.name = name
        self.pos = [0,0]
        self.dir = 0
        self.input = Input()


class Input(object):
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
