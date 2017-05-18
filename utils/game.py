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

def addUser(user):
    players.append(Player(user))
def run():
    while True:
        for player in players:
            player.pos[0] += 1
            player.dir -= 1
        eventlet.sleep(1./120)
