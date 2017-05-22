import time
import eventlet
from player import Player

players = []
def data(json):
    for player in players:
        if player.name == json['username']:
            print 'player %s found'
            return {'pos': player.pos, 'dir': player.dir}
    print 'player %s not found' % (json['username'])
    return {}

def update(json):
    player = getPlayer(name)
    if json['event'] == 'keyboard':
        val = json['type'] == 'down'
        if json['key'] == 'W':
            player.input.up = val
        if json['key'] == 'A':
            player.input.left = val
        if json['key'] == 'S':
            player.input.down = val
        if json['key'] == 'D':
            player.input.right = val

def addUser(user):
    players.append(Player(user))

def getPlayer(name):
    for player in players:
        if player.name == name:
            return player

def run():
    while True:
        for player in players:
            if player.input.up:
                player.pos[1] -= 1
            if player.input.down:
                player.pos[1] += 1
            if player.input.left:
                player.pos[0] -= 1
            if player.input.right:
                player.pos[0] += 1
            #player.pos[0] += 1
            #player.dir -= 1
        eventlet.sleep(1./120)
