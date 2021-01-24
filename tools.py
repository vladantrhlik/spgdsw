import pygame as pg
import math

class Objects:
    def __init__(self):
        self.containers = {"Point": [], "Line": [], "Circle": [], "Rectangle": [], "QuadraticBezier": []}

        self.objects = []
        self.futureObjects = []

    def __call__(self):
        return self.objects

    def add(self,object):
        self.objects.append(object)
        self.containers[type(object).__name__].append(object)

    def exists(self, object):
        for o in self.objects:
            if object == o:
                return True
        return False

    def listObjects(self, name):
        return self.containers[name]

    def previous(self):
        if len(self.objects)>0:
            self.futureObjects.append(self.objects.pop(len(self.objects)-1))
    
    def backToFuture(self):
        if len(self.futureObjects)>0:
            self.objects.append(self.futureObjects.pop(len(self.futureObjects)-1))

    def removePoint(self, point):
        self.removeShapesWithPoint(point)
        self.objects.remove(point)

    def removeShapesWithPoint(self, point):
        to_remove = []
        for o in self.objects:
            if type(o).__name__ != "Point":
                if point in o.points: to_remove.append(o)
        for r in to_remove: self.objects.remove(r)

class Camera:

    def __init__(self, step):
        self.position = [0,0]

        self.step = step

        self.draging = False
        self.lastPos = [0,0]
        self.movement = [0,0]
    
    def handleInput(self, event, pos):

        if self.draging:
            self.movement[0] = -(self.lastPos[0]-pos[0])
            self.movement[1] = -(self.lastPos[1]-pos[1])

            self.position[0] += self.movement[0]
            self.position[1] += self.movement[1]
            print(self.movement, self.position)

            #step stuff
            self.position[0] = round(self.position[0]/self.step) * self.step
            self.position[1] = round(self.position[1]/self.step) * self.step

            self.lastPos = pos

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 2:
            self.lastPos = pos
            self.dragStart = pos
            self.draging = True
        if event.type == pg.MOUSEBUTTONUP and event.button == 2:
            self.draging = False

class Grid:
    def __init__(self, u, w, h, screen):
        self.unit = 10
        self.step = u/10
        self.w = w
        self.h = h
        self.screen = screen
        self.color = (0,0,0)
        self.width = 1
    
    def draw(self, screen):
        for x in range(math.ceil(self.w/self.unit)):
            self.color = (75,75,75) if x%self.step == 0 else (150,150,150)
            self.width = 2 if x%self.step == 0 else 1
            pg.draw.line(screen, self.color, (x*self.unit,0), (x*self.unit, self.h), self.width)
        for y in range(math.ceil(self.h/self.unit)):
            self.color = (75,75,75) if y%self.step == 0 else (150,150,150)
            self.width = 2 if y%self.step == 0 else 1
            pg.draw.line(screen, self.color, (0,y*self.unit), (self.w, y*self.unit), self.width)

        pg.draw.rect(screen, (0,0,0), (0,0,self.w, self.h), 3)



class SelectionTool:
    def __init__(self, screen):
        self.screen = screen
        self.startPos = [0,0]
        self.endPos = [0,0]
        self.selecting = False

        self.selected = []

        self.rect = []
    
    def update(self, pos, screen):
        width = abs(self.startPos[0] - pos[0])
        height = abs(self.startPos[1] - pos[1])

        posX = min(self.startPos[0], pos[0])
        posY = min(self.startPos[1], pos[1])

        self.rect = (posX, posY, width, height)

        pg.draw.rect(screen, (0,0,255,125), self.rect)

    def selectPoints(self, points):
        for p in points:
            x = p.position[0]
            y = p.position[1]
            if self.rect[0] <= x <= self.rect[0] + self.rect[2] and self.rect[1] <= y <= self.rect[1] + self.rect[3]:
                p.selected = True
                self.selected.append(p)

    def clearSelection(self, points):
        for p in self.selected:
            p.selected = False
        self.selected = []

    def handleInput(self, event, pos, points):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.startPos = pos
            self.selecting = True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.selecting = False
            self.endPos = pos
            self.selectPoints(points)

class MoveTool:
    def __init__(self, screen):
        self.moving = False
        self.startPos = [0,0]
        self.movingObjects = []
        self.lastPos = self.startPos

    def update(self, pos, selected):
        if pos == self.lastPos:
            return

        moveX = pos[0] - self.lastPos[0]
        moveY = pos[1] - self.lastPos[1]

        for s in selected:
            s.move(moveX,moveY)
            
        self.lastPos = pos

    def handleInput(self, event, pos, points):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.startPos = pos
            self.lastPos = pos
            self.moving = True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.moving = False
