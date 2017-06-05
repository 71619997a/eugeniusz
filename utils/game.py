import time
import eventlet
from player import Player
from wall import Wall
from constants import *
from random import randint

class Game(object):  # one game
    def __init__(self, name, **settings):
        self.name = name
        self.players = []
        self.pdict = {}
        self.settings = settings
        settings['maxplayers'] = min(settings['maxplayers'], 4)
        self.size = settings['size']
        self.maxplayers = settings['maxplayers']
        self.speed = settings['speed']

    def data(self, json):
        ret = {}
        for player in self.players:
            if player.dead:
                print player.name, 'dead'
                ret[player.name] = {'dead': True}
                continue
            if player.name in json['wallnums']:
                wallIdx = json['wallnums'][player.name] - 1
            else:
                wallIdx = 0
            newWalls = [wall.ends() for wall in player.walls[wallIdx:]]
            ret[player.name] = {'x': player.x, 'y': player.y, 'dir': player.dir, 'color': player.color, 'updatedwall': wallIdx, 'nwalls': len(player.walls), 'walls': newWalls}
        return ret

    def update(self, json):
        player = self.getPlayer(json['username'])
        if json['event'] == 'keyboard':
            player.input.key = json['key']

    def spawnP(self, i):
        dir = i
        c = 100
        m = self.size / 2
        f = self.size - c
        if i == 0:  # sometimes hardcoding is best
            x = m
            y = f
        elif i == 1:
            x = c
            y = m
        elif i == 2:
            x = m
            y = c
        elif i == 3:
            x = f
            y = m
        return x, y, dir

    def addUser(self, user):
        if len(self.players) >= self.maxplayers:
            # send player back to server browser page
            return
        if user in self.pdict:
            return
        pidx = len(self.players)
        x, y, dir = self.spawnP(pidx)
        player = Player(user, x/self.speed*self.speed, y/self.speed*self.speed, dir, PCOLORS[pidx])
        print player.x, player.y
        self.players.append(player)
        self.pdict[user] = player

    def removeUser(self, user):
        player = pdict[user]
        self.pdict.pop(user, 0)
        self.players.remove(player)
        del player

    def getPlayer(self, name):
        return self.pdict[name]
            
    def keyDir(self, key):
        if key == 'D':
            return 1
        if key == 'A':
            return -1
        return 0

    def killPlayer(self, player):
        player.dead = True

    def runFrame(self):
        horizontals = {}
        verticals = {}
        # 0. move so that we dont hit just placed walls and
        # 1. build wall dicts
        for player in self.players:
            if player.dead:
                continue
            for wall in player.walls:
                # print wall.ends()
                wt = (wall.start, wall.end) if wall.start <= wall.end else (wall.end, wall.start)
                if wall.dir == HORIZONTAL:
                    horizontals[wall.const] = wt
                else:
                    verticals[wall.const] = wt
            if player.input.key is not None:
                ndir = self.keyDir(player.input.key)
                player.dir += ndir
                player.dir %= 4
                player.input.key = None
                player.walls.append(Wall(player.dir, player.x, player.y))
            if player.dir == UP:
                player.y -= self.speed
            elif player.dir == RIGHT:
                player.x += self.speed
            elif player.dir == DOWN:
                player.y += self.speed
            elif player.dir == LEFT:
                player.x -= self.speed
            print player.x, player.y
        # 2. check collisions and inc wall
        for player in self.players:
            if player.dead:
                continue
            if player.x < 0 or player.x > self.size or player.y < 0 or player.y > self.size:
                self.killPlayer(player)
                continue
            if player.x in verticals:
                s, e = verticals[player.x]
                if player.y >= s and player.y <= e:
                    self.killPlayer(player)
                    continue
            if player.y in horizontals:
                s, e = horizontals[player.y]
                if player.x >= s and player.x <= e:
                    self.killPlayer(player)
                    print 'player is dead!'
                    continue
            player.walls[-1].inc(self.speed if player.dir % 3 else -self.speed)

