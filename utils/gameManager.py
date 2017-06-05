from game import Game
import eventlet
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
        for game in games:
            game.runFrame()
        eventlet.sleep(1./120)