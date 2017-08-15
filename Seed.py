from random import randint
import time

#class MySeed:
class MySeed:
    tracks = []
    def __init__(self, i, xi, yi, max_age, fc):
        self.i = i
        self.x = xi
        self.y = yi
        self.px = 0
        self.py = 0
        self.fc = fc
        self.tracks = []
        self.updates = 0
        self.done = False
        self.state = 0     # 1 = new, 2 = active, 3 = dead
        self.age = 0
        self.max_age = max_age
    def getId(self):
        return self.i
    def setState(self, s):
        self.state = s
    def getState(self):
        return self.state
    def getX(self):
        return self.x
    def setX(self, v):
        self.x = v
    def getY(self):
        return self.y
    def setY(self, v):
        self.y = v
    def setPX(self, x):
        self.px = x
    def getPX(self):
        return self.px
    def setPY(self, y):
        self.py = y
    def getPY(self):
        return self.py
    def getUpdates(self):
        return self.updates
    def updateCoords(self, xn, yn):
        self.age = 0
        self.tracks.append([self.x,self.y])
        self.x = xn
        self.y = yn
        self.updates += 1
    def updatePrediction(self, xn, yn):
        self.tracks.append([self.x,self.y])
        self.x = xn
        self.y = yn
    def setDone(self):
        self.state = 3
        self.done = True
    def age_one(self):
        self.age += 1
#        if ((self.age > self.max_age) and (self.age > self.updates)):
#            self.done = True
        return True
