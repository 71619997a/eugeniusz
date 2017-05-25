import time
import eventlet
from player import Player
from constants import *


players = []
def data(json):
    ret = {}
    for player in players:
        ret[player.name] = {'pos': player.pos, 'dir': player.dir}
    return ret

def update(json):
    player = getPlayer(json['username'])
    if json['event'] == 'keyboard':
        player.input.key = json['key']

def addUser(user):
    players.append(Player(user))
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
    while True:
        for player in players:
            if player.input.key is not None:
                ndir = keyDir(player.input.key)
                player.dir += ndir
                player.dir %= 4
                player.input.key = None
            if player.dir == UP:
                player.pos[1] -= 1
            elif player.dir == RIGHT:
                player.pos[0] += 1
            elif player.dir == DOWN:
                player.pos[1] += 1
            elif player.dir == LEFT:
                player.pos[0] -= 1
            #player.pos[0] += 1
            #player.dir -= 1
        eventlet.sleep(1./120)
