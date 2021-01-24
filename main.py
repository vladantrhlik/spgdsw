# Import and initialize the pygame library
import pygame as pg
import pygame_gui

from pygame_gui.elements import UIWindow, UIImage

import math
from shapes import *
from tools import *
from windows import *
import copy

pg.init()
pg.font.init()


class Window:
    def __init__(self):
        self.screenSize = [1280,720]

        self.screen = pg.display.set_mode(self.screenSize)
        self.manager = pygame_gui.UIManager(self.screenSize, 'data/themes/theme_1.json')
        self.clock = pg.time.Clock()

        self.modes = ["point", "line", "circle", "circle2", "rect","rect2","bezier"]
        self.tools = ["select", "move"]
        self.mode = "point"

        #self.drawingWindow = DrawingPanel((100,0),(1180,720), self.manager)
        self.toolBar = ToolBar((0,0), (100,720), self.manager, self.modes, self.tools, self)
        self.objects = Objects()

        self.running = True

        self.moving = []

        self.pointBuffer = []
        self.font = pg.font.SysFont('Verdana', 20)

        self.canvasSize = [1000,1000]

        self.selectionTool = SelectionTool(self.screen)
        self.moveTool = MoveTool(self.screen)
        
        #step = 10
        self.grid = Grid(50, self.canvasSize[0],self.canvasSize[1], self.screen)
        self.camera = Camera(10)


        self.versions = [self.objects]

    def clearPointBuffer(self):
        for o in self.pointBuffer:
            o.buffering = False

        self.pointBuffer = []

    def changeMode(self, mode):
        self.mode = mode
        self.clearPointBuffer()

    def back(self):
        self.objects.previous() #ctrl+z (zpět)
    def forward(self):
        self.objects.backToFuture() #ctrl+shift+z (vpřed)

    def handleKeyboard(self, event):
        if event.key == pg.K_SPACE:
            if pg.key.get_mods() & pg.KMOD_SHIFT:
                self.forward()
            else:
                self.back()
        if event.key == pg.K_ESCAPE:
            self.clearPointBuffer()
            self.selectionTool.clearSelection(self.objects.listObjects("Point"))

    def bufferPoints(self, event, pos):
        if event.type == pg.MOUSEBUTTONDOWN and self.mode not in ["point", "select", "move"] and event.button == 1:
            for o in self.objects.listObjects("Point"):
                if o.sprite.collidepoint(pos):
                    if o in self.pointBuffer:
                        o.buffering = False
                        self.pointBuffer.remove(o)
                    else:
                        self.pointBuffer.append(o)
                        o.buffering = True

    def handlePoints(self, event, pos):
        #view point on grid
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for o in self.moving:
                o.moving = False
            self.moving = []
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1: #adding points
                #check if collides existing points
                newPoint =True
                for o in self.objects.listObjects("Point"):
                    if o.sprite.collidepoint(pos):
                        newPoint = False
                        o.moving = True
                        self.moving.append(o)    
                if newPoint:
                    p = Point(pos)
                    self.objects.add(p)
            if event.button == 3: #removing points
                for o in self.objects.listObjects("Point"):
                    if o.sprite.collidepoint(pos):
                        self.objects.removePoint(o)
                        break

    def handleShapes(self):
        if self.mode in ["line","circle","rect","circle2","rect2"]:
            if len(self.pointBuffer) > 2:
                self.pointBuffer[0].buffering = False
                self.pointBuffer.pop(0)

            if len(self.pointBuffer) == 2:
                a,b = self.pointBuffer

                if self.mode == "line":
                    line = Line([a,b], 0)
                    if not self.objects.exists(line):
                        self.objects.add(line)

                if self.mode[:len("circle")] == "circle":
                    if self.mode == "circle2":
                        circle = Circle([a,b], 1)
                    else:
                        circle = Circle([a,b], 0)
                    if not self.objects.exists(circle):
                        self.objects.add(circle)

                if self.mode[:len("rect")] == "rect":
                    if self.mode == "rect2":
                        rect = Rectangle([a,b],1)
                    else:
                        rect = Rectangle([a,b],0)
                    if not self.objects.exists(rect):
                        self.objects.add(rect)
        #bezier
        if self.mode == "bezier":
            if len(self.pointBuffer) > 3:
                self.pointBuffer[0].buffering = False
                self.pointBuffer.pop(0)
            if len(self.pointBuffer) == 3:
                a,b,c = self.pointBuffer
                curve = QuadraticBezier([a,b,c])
                if not self.objects.exists(curve):
                    self.objects.add(curve)

    def drawToolOverlays(self, pos):
        s = pg.Surface(self.screenSize, pg.SRCALPHA)  # the size of your rect
        s.set_alpha(128)                # alpha level

        if self.mode == "point":
            pg.draw.circle(s, (0,0,255,125), pos, 8)

        if self.mode == "select" and self.selectionTool.selecting:
            self.selectionTool.update(pos,s)
        self.screen.blit(s, (0,0))    # (0,0) are the top-left coordinates

    def update(self):
        drawingPos = list(pg.mouse.get_pos())
        mousePos = drawingPos.copy()
        drawingPos[0] = round(drawingPos[0]/self.grid.unit) * self.grid.unit
        drawingPos[1] = round(drawingPos[1]/self.grid.unit) * self.grid.unit

        drawingPosNoCam = drawingPos.copy()

        drawingPos[0] -= self.camera.position[0] 
        drawingPos[1] -= self.camera.position[1] 
        
        for event in pg.event.get():
            self.manager.process_events(event)

            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                self.handleKeyboard(event)
            if mousePos[0] > self.toolBar.rect[2]: #jestli je mouse v okně
                self.bufferPoints(event, drawingPos)
                if self.mode == "point": self.handlePoints(event, drawingPos)
                if self.mode == "select": self.selectionTool.handleInput(event, drawingPos, self.objects.listObjects("Point"))
                if self.mode == "move": self.moveTool.handleInput(event, drawingPos, self.objects.listObjects("Point"))

                self.camera.handleInput(event, mousePos)



        self.handleShapes()

        time_delta = self.clock.tick(60)/1000.0
        self.manager.update(time_delta)

        #moving with points
        if len(self.moving) > 0:
            for o in self.moving:
                if type(o).__name__ == "Point":
                    o.position = drawingPos

        if self.moveTool.moving: self.moveTool.update(drawingPos, self.selectionTool.selected)
    
        #drawing stuff
        self.screen.fill((255,255,255))
        

        objectsSurface = pg.Surface(self.canvasSize, pg.SRCALPHA)
        self.grid.draw(objectsSurface)
        for object in self.objects():
            object.draw(objectsSurface)
        self.screen.blit(objectsSurface, self.camera.position)
        self.drawToolOverlays(drawingPosNoCam)
        self.manager.draw_ui(self.screen)


window = Window()
while window.running:
    window.update()
    pg.display.flip()

# Done! Time to quit.
pg.quit()
