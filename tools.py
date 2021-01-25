import pygame as pg
import math
import svgwrite

class Objects:
    def __init__(self):
        self.containers = {"Line": [], "Circle": [], "Rectangle": [], "QuadraticBezier": [], "Point": []}

        self.objects = []
        self.futureObjects = []

    def __call__(self):
        keys = list(self.containers.keys())
        out = []
        for k in keys:
            out += self.containers[k]
        return out

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
        print("back")
        print(len(self.objects))
        if len(self.objects)>0:
            self.containers[type(self.objects[-1]).__name__].remove(self.objects[-1])
            self.futureObjects.append(self.objects.pop(len(self.objects)-1))
    
    def backToFuture(self):
        print("forward")
        print(len(self.objects))
        if len(self.futureObjects)>0:
            self.containers[type(self.futureObjects[-1]).__name__].append(self.futureObjects[-1])
            self.objects.append(self.futureObjects.pop(len(self.futureObjects)-1))

    def removePoint(self, point):
        self.removeShapesWithPoint(point)
        self.objects.remove(point)
        self.containers["Point"].remove(point)

    def removeShapesWithPoint(self, point):
        to_remove = []
        for o in self.objects:
            if type(o).__name__ != "Point":
                if point in o.points: to_remove.append(o)
        for r in to_remove: 
            self.objects.remove(r)
            self.containers[type(r).__name__].remove(r)

class Camera:

    def __init__(self, step):
        self.position = [0,0]

        self.step = step

        self.draging = False
        self.lastPos = [0,0]
        self.movement = [0,0]

        self.slowMoveBuffer = [0,0]
    
    def handleInput(self, event, pos, grid):

        if self.draging:
            self.movement[0] = -(self.lastPos[0]-pos[0])
            self.movement[1] = -(self.lastPos[1]-pos[1])


            #slow move bug fix
            if abs(self.movement[0]) < self.step/2: self.slowMoveBuffer[0] += self.movement[0]
            if abs(self.movement[1]) < self.step/2: self.slowMoveBuffer[1] += self.movement[1]
            
            while(abs(self.slowMoveBuffer[0])>self.step):
                znamenko = (self.slowMoveBuffer[0]/abs(self.slowMoveBuffer[0]))
                self.position[0] += self.step * znamenko
                self.slowMoveBuffer[0] += self.step *(-znamenko)

            while(abs(self.slowMoveBuffer[1])>self.step):
                znamenko = (self.slowMoveBuffer[1]/abs(self.slowMoveBuffer[1]))
                self.position[1] += self.step * znamenko
                self.slowMoveBuffer[1] += self.step *(-znamenko)

            self.position[0] += self.movement[0]
            self.position[1] += self.movement[1]

            #step stuff
            if grid:
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
    def __init__(self, u, s, w, h, screen):
        self.unit = u
        self.step = s
        self.w = w
        self.h = h
        self.screen = screen
        self.color = (0,0,0)
        self.width = 1

        self.active = True
    
    def draw(self, screen):
        if self.active:
            #lines
            '''
            for x in range(math.ceil(self.w/self.unit)):
                self.color = (75,75,75) if x%self.step == 0 else (150,150,150)
                self.width = 2 if x%self.step == 0 else 1
                pg.draw.line(screen, self.color, (x*self.unit,0), (x*self.unit, self.h), self.width)
            for y in range(math.ceil(self.h/self.unit)):
                self.color = (75,75,75) if y%self.step == 0 else (150,150,150)
                self.width = 2 if y%self.step == 0 else 1
                pg.draw.line(screen, self.color, (0,y*self.unit), (self.w, y*self.unit), self.width)
            '''
            #dots   
            for y in range(math.ceil(self.h/self.step)):
                for x in range(math.ceil(self.w/self.step)):
                    r = 1
                    if x%self.unit == 0 or y%self.unit == 0: r = 2
                    pg.draw.circle(screen, (150,150,150), (x*self.step,y*self.step), r)
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

    def selectPoints(self, points, camPos):
        for p in points:
            x = p.position[0] + camPos[0]
            y = p.position[1] + camPos[1]
            if self.rect[0] <= x <= self.rect[0] + self.rect[2] and self.rect[1] <= y <= self.rect[1] + self.rect[3]:
                p.selected = True
                self.selected.append(p)

    def clearSelection(self, points):
        for p in self.selected:
            p.selected = False
        self.selected = []

    def handleInput(self, event, pos, points, camPos):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.startPos = pos
            self.selecting = True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.selecting = False
            self.endPos = pos

            self.startPos[0] -= camPos[0]
            self.startPos[1] -= camPos[1]
            self.endPos[0] -= camPos[0]
            self.endPos[1] -= camPos[1]

            self.selectPoints(points, camPos)

    def drawSelection(self, screen, pos):
        rect = list(self.rect)
        rect[0] = self.startPos[0] + pos[0]
        rect[1] = self.startPos[1] + pos[1]
        pg.draw.rect(screen, (0,0,255,125), rect, 3)

class MoveTool:
    def __init__(self, screen, grid, selectionTool):
        self.moving = False
        self.startPos = [0,0]
        self.movingObjects = []
        self.lastPos = self.startPos

        self.grid = grid
        self.gridStep = self.grid.step
        self.snap = False

        self.selectionTool = selectionTool

    def update(self, pos, selected):
        if pos == self.lastPos:
            return

        moveX = pos[0] - self.lastPos[0]
        moveY = pos[1] - self.lastPos[1]

        selectPos = list(self.selectionTool.startPos)
        selectSize = list(self.selectionTool.rect[2:])

        selectPos[0] += moveX
        selectPos[1] += moveY

        if selectPos[0]>=0 and selectPos[1] >= 0 and selectPos[0]+selectSize[0] <= self.grid.w and selectPos[0]+selectSize[0] <= self.grid.w:
            self.selectionTool.startPos = selectPos
            self.snap = self.grid.active
            for s in selected:
                s.move(moveX,moveY, self.gridStep, self.snap)            
        self.lastPos = pos

    def handleInput(self, event, pos, points):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.startPos = pos
            self.lastPos = pos
            self.moving = True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.moving = False

class Exporter:

    def save(self, objects, mode):
        points = objects.listObjects("Point")
        if mode == "svg":
            dwg = svgwrite.Drawing('test.svg')
            #points
            for point in points:
                if point.selected:
                    dwg.add(point.svg())
            #objects
            for object in objects():
                if type(object).__name__ in ["Line", "Circle", "Rectangle", "QuadraticBezier"]: #tady budou všechny podporované shapy
                    selectedPoints = list(filter(lambda x: x.selected, object.points))
                    print(len(selectedPoints))
                    if len(selectedPoints)>0:
                        dwg.add( object.svg() )
            
            dwg.save()
            
