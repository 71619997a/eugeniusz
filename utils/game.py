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
        self.timeout = 300  # 5 second timeout before game start
        self.roundEnding = False
        self.gameEnding = False
        self.gameEndsSoon = False
        self.alive = 0
        self.scores = []
        self.starting = False

    def data(self, json):
        ret = {'players': {}, 'timeout': self.timeout}
        for i in xrange(len(self.players)):
            player = self.players[i]
            if player.dead:
                ret['players'][player.name] = {'dead': True}
                continue
            if player.name in json['wallnums']:
                wallIdx = max(json['wallnums'][player.name] - 1, 0)  # 1 buffer zone, 2 wall misses is extremely unlikely
            else:
                wallIdx = 0
            newWalls = [wall.ends() for wall in player.walls[wallIdx:]]
            ret['players'][player.name] = {'x': player.x, 'y': player.y, 'dir': player.dir, 'color': player.color, 'updatedwall': wallIdx, 'nwalls': len(player.walls), 'walls': newWalls, 'score': self.scores[i]}
            
            # newWalls = [wall.ends() for wall in player.walls]
            # ret['players'][player.name] = {'x': player.x, 'y': player.y, 'dir': player.dir, 'color': player.color, 'walls': newWalls, 'score': self.scores[i]}
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
        self.alive += 1
        pidx = len(self.players)
        x, y, dir = self.spawnP(pidx)
        player = Player(user, x/self.speed*self.speed, y/self.speed*self.speed, dir, PCOLORS[pidx])
        print player.x, player.y
        self.players.append(player)
        self.pdict[user] = player
        self.scores.append(0)

    def removeUser(self, user):
        player = self.pdict[user]
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
        if player.dead:
            return
        player.dead = True
        player.walls = []
        self.alive -= 1

    def respawnPlayers(self):
        for i in range(len(self.players)):
            player = self.players[i]
            x, y, dir = self.spawnP(i)
            player.x = x / self.speed * self.speed
            player.y = y / self.speed * self.speed
            player.dir = dir
            player.dead = False
            player.walls = [Wall(dir, x, y)]

    def runFrame(self):
        if self.timeout > 0:
            self.timeout -= 1
            return
        if self.alive <= 1:  # on round end, wait 3 seconds, then respawn
            i = None
            for i in range(len(self.players)):
                if not self.players[i].dead:
                    self.players[i].dead = True
                    break
            if i is not None:  # if it is, we don't update score b/c tie
                self.scores[i] += 1
                if self.scores[i] >= 3:
                    # update player database with new wins/losses
                    self.timeout += 300  # 8 seconds for game end? sure
                    self.gameEndsSoon = True
            self.timeout = 180
            self.roundEnding = True
            self.alive = len(self.players)
            return
        if self.gameEndsSoon:
            self.gameEnding = True
            return
        if self.roundEnding:
            self.roundEnding = False
            self.respawnPlayers()  # now do 1 tick so clients see update
            self.timeout = 180  # wait 3 more seconds until start
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
        # 2. check collisions and inc wall
        for player in self.players:
            if player.dead:
                continue
            if player.x < 0 or player.x > self.size or player.y < 0 or player.y > self.size:
                self.killPlayer(player)
                continue
            if player.x in verticals:
                print 'player crossed vwall'
                s, e = verticals[player.x]
                print s, player.y, e
                if player.y >= s and player.y <= e:
                    self.killPlayer(player)
                    continue
            if player.y in horizontals:
                print 'player crossed hwall'
                s, e = horizontals[player.y]
                print s, player.x, e
                if player.x >= s and player.x <= e:
                    self.killPlayer(player)
                    continue
            skip = False
            for p2 in self.players:
                print 'in it'
                if p2 == player:
                    continue
                if p2.x == player.x and p2.y == player.y:
                    self.killPlayer(p2)
                    self.killPlayer(player)
                    skip = True
            if skip:
                continue
            player.walls[-1].inc(self.speed if player.dir % 3 else -self.speed)

