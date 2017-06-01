from constants import *

class Wall(object):
    def __init__(self, dir, sx, sy):
        self.dir = dir % 2
        if self.dir == HORIZONTAL:
            self.const = sy
            self.end = self.start = sx
        else:
            self.const = sx
            self.end = self.start = sy

    def inc(self, dist):
        self.end += dist

    def ends(self):
        if self.dir == HORIZONTAL:
            return (self.start, self.const), (self.end, self.const)
        else:
            return (self.const, self.start), (self.const, self.end)