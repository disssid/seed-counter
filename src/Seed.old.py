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
        self.size = 0
        self.updates = 0
 #       self.R = randint(0,255)
 #       self.G = randint(0,255)
 #       self.B = randint(0,255)
        self.done = False
        self.state = 0
        self.age = 0
        self.max_age = max_age
        self.dir = None
    def getRGB(self):
        #return (self.R,self.G,self.B)
        return (0,255,0) #use green to show the notation of the seeds
    def getTracks(self):
        return self.tracks
    def getId(self):
        return self.i
    def setState(self, s):
        self.state = s
    def getState(self):
        return self.state
    def getDir(self):
        return self.dir
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
    def getSize(self):
        return self.size
    def setSize(self, s):
        self.size = s
    def getUpdates(self):
        return self.updates
    def updateCoords(self, xn, yn):
        self.age = 0
        self.tracks.append([self.x,self.y])
#        print("The coords of the seeds is xn:",xn," yn:",yn)
#        print("seed ",self.i,", x: ", self.x, ", y: ", self.y, ", len: ", len(self.tracks))
#        print("self.tracks[-1][0] ", self.tracks[-1][0], "self.tracks[-1][1] ", self.tracks[-1][1])
#        if len(self.tracks) >= 2:
#            print("self.tracks[-2][0] ", self.tracks[-2][0], "self.tracks[-2][1] ", self.tracks[-2][1])
        self.px = self.x
        self.py = self.y
        self.x = xn
        self.y = yn
        self.updates += 1
    def updatePrediction(self, xn, yn):
        self.tracks.append([self.x,self.y])
        self.px = self.x
        self.py = self.y
        self.x = xn
        self.y = yn
    def setDone(self):
        self.done = True
    def timeOut(self):
        return self.done
    def going_UP(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][1] < mid_end and self.tracks[-2][1] >= mid_end: #pass by the line
                    state = '1'
                    self.dir = 'up'
                    return True
            else:
                return False
        else:
            return False
    def going_DOWN(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
#            print("len(self.tracks) ",len(self.tracks), " x, y ", self.x, self.y, " state ", self.state)
            if self.state == '0':
                if self.tracks[-1][1] > mid_end and self.tracks[-2][1] <= mid_start: #pass by the line
#                    print("self.tracks[-1][1] is ",self.tracks[-1][1], " > mid_end ", mid_end)
#                    print("self.tracks[-2][1] is ",self.tracks[-2][1], " <= mid_start ", mid_start)
#                    print("The self.tracks is ",self.tracks)
                    self.state = '1'
                    self.dir = 'down'
#mln                    self.done = True
                    if (self.tracks[-1][1] - self.tracks[-2][1])>120 :
#                        print("bad seed ", self.i)
                        self.state = '2'
                        return False
                    else:
                        return True
            else:
                return False
        else:
            return False
    def age_one(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True
        return True
#class MultiPerson:
class MultiSeed:
#    def __init__(self, persons, xi, yi):
    def __init__(self, seeds, xi, yi):
        self.persons = persons
        self.seeds = seeds
        self.x = xi
        self.y = yi
        self.px = 0
        self.py = 0
        self.tracks = []
        self.size = 0
        self.updates = 0
#        self.R = randint(0,255)
 #       self.G = randint(0,255)
 #       self.B = randint(0,255)
        self.done = False
        
