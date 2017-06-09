#!/usr/bin/python
import sys
sys.path.insert(0,"/var/www/tron/")
from tron import app
from tron import socketio


class FakeApp(object):
    def __init__(self, si, a):
        object.__setattr__(self, 'si', si)
        object.__setattr__(self, 'a', a)

    def __getattr__(self, atname):
        if atname == 'run':
            print 'its run'
            def runfunc(**kwargs):
                return self.si.run(self.a, **kwargs)
            return runfunc
        return object.__getattr__(self.a, atname)

    def __setattr__(self, atname, v):
        return object.__setattr__(self.a, atname, v)


    def __call__(self, *args, **kwargs):
        return self.a(*args, **kwargs)

application = FakeApp(socketio, app)
application = app
