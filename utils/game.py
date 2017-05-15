import time
import eventlet
car = [0,0,0]

def data(json):
    return car


def run():
    while True:
        car[0] += 1
        eventlet.sleep(1./120)
