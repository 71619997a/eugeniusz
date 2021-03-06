from game import Game
import eventlet
from time import time
games = []
gdict = {}
pdict = {}

def createGame(name, **settings):
    game = Game(name, **settings)
    games.append(game)
    gdict[name] = game

def getGame(name):
    return gdict[name]

def removeUser(name):
    pdict[name].removeUser(name)
    pdict.pop(name)

def join(pname, gname):
    game = getGame(gname)
    game.addUser(pname)
    if len(game.players) == game.maxplayers:
        game.starting = True
    pdict[pname] = game

def endGame(name):
    game = getGame(name)
    pnames = game.pdict.keys()
    for pname in pnames:
        removeUser(pname)
    gdict.pop(name, 0)
    games.remove(game)
    del game

def data(json):
    pname = json['username']
    return pdict[pname].data(json)

def update(json):
    pname = json['username']
    return pdict[pname].update(json)

def run():
    while(1):
        t = time()
        i = 0
        l = len(games)
        while i < l:
            game = games[i]
            if not game.starting:
                i += 1
                continue
            game.runFrame()
            if game.gameEnding:
                endGame(game.name)
                i -= 1
                l -= 1
            i += 1
        elapsed = time() - t
        slptime = max(0, 1./120 - elapsed)
        eventlet.sleep(slptime)
