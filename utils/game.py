import time
import eventlet
from player import Player
from wall import Wall
from constants import *
from random import randint

players = []
def data(json):
    ret = {}
    for player in players:
        if player.name in json['wallnums']:
            wallIdx = json['wallnums'][player.name] - 1
        else:
            wallIdx = 0
        newWalls = [wall.ends() for wall in player.walls[wallIdx:]]
        ret[player.name] = {'x': player.x, 'y': player.y, 'dir': player.dir, 'color': player.color, 'updatedwall': wallIdx, 'nwalls': len(player.walls), 'walls': newWalls}
    return ret

def update(json):
    player = getPlayer(json['username'])
    if json['event'] == 'keyboard':
        player.input.key = json['key']

def addUser(user):
    players.append(Player(user, 0, 0, 0))
    print players

def getPlayer(name):
    for player in players:
        if player.name == name:
            return player
        
def keyDir(key):
    if key == 'D':
        return 1
    if key == 'A':
        return -1
    return 0


def run():
    while True:  # multiple passes
        horizontals = {}
        verticals = {}
        # 0. move so that we dont hit just placed walls and
        # 1. build wall dicts
        for player in players:
            for wall in player.walls:
                # print wall.ends()
                wt = (wall.start, wall.end) if wall.start <= wall.end else (wall.end, wall.start)
                if wall.dir == HORIZONTAL:
                    horizontals[wall.const] = wt
                else:
                    verticals[wall.const] = wt
            if player.input.key is not None:
                ndir = keyDir(player.input.key)
                player.dir += ndir
                player.dir %= 4
                player.input.key = None
                player.walls.append(Wall(player.dir, player.x, player.y))
            if player.dir == UP:
                player.y -= PLAYERVEL
            elif player.dir == RIGHT:
                player.x += PLAYERVEL
            elif player.dir == DOWN:
                player.y += PLAYERVEL
            elif player.dir == LEFT:
                player.x -= PLAYERVEL
        # 2. check collisions and inc wall
        for player in players:
            if player.x in verticals:
                s, e = verticals[player.x]
                if player.y >= s and player.y <= e:
                    # insert player death routine
                    print 'player is dead!'
                    continue
            if player.y in horizontals:
                s, e = horizontals[player.y]
                if player.x >= s and player.x <= e:
                    # insert player death routine
                    print 'player is dead!'
                    continue
            player.walls[-1].inc(PLAYERVEL if player.dir % 3 else -PLAYERVEL)

        eventlet.sleep(1./120)
