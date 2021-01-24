import pygame as pg
import math

class Point:
    def __init__(self, position):
        self.position = position
        self.sprite = None
        self.moving = False
        self.buffering = False
        self.color = (0,0,255)
        self.selected = False
    def draw(self, screen):
        self.color = (0,255,0) if self.moving else (255,0,0) if self.buffering else (0,255,255) if self.selected else (0,0,255) 
        self.sprite = pg.draw.circle(screen, self.color, self.position, 8)

    def move(self, x,y):
        self.position = (self.position[0]+x, self.position[1]+y)

class Shape:
    def __init__(self, points):
        self.points = points
        self.color = (0,0,0)
        self.sprite = None

class TwoPointShape(Shape):
    def __init__(self, points, mode):
        Shape.__init__(self, points)
        self.point1 = points[0]
        self.point2 = points[1]
        self.mode = mode #0 == střed + bod, 1 == bod + bod

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.point1 == other.point1 and self.point2 == other.point2) or (self.point1 == other.point2 and self.point2 == other.point1)
        return False


class Line(TwoPointShape):
    def draw(self, screen):
        self.sprite = pg.draw.line(screen, self.color, self.point1.position, self.point2.position, 3)
    

class Circle(TwoPointShape):
    def draw(self, screen):
        if self.mode == 0:
            self.radius = self.updateRadius()    
            if self.radius < 3: self.radius = 3
            self.sprite = pg.draw.circle(screen, self.color, self.point1.position, round(self.radius), 3)
        elif self.mode == 1:
            p1 = self.point1.position
            p2 = self.point2.position
            center = (round((p1[0]+p2[0])/2), round((p1[1]+p2[1])/2))
            self.radius = self.updateRadius()/2

            self.sprite = pg.draw.circle(screen, self.color, center, round(self.radius), 3)

    def updateRadius(self):
        x_dist = abs(self.point1.position[0]-self.point2.position[0])
        y_dist = abs(self.point1.position[1]-self.point2.position[1])

        return math.sqrt(x_dist**2 + y_dist**2)

    def __eq__(self, other):
        if type(self) == type(other):
            if self.mode == 0:
                return self.point1 == other.point1 and self.point2 == other.point2 and self.mode == other.mode
            elif self.mode == 1:
                return ((self.point1 == other.point1 and self.point2 == other.point2) or (self.point1 == other.point2 and self.point2 == other.point1)) and self.mode == other.mode
        return False

class Rectangle(TwoPointShape):

    def draw(self, screen):
        p1 = self.point1.position
        p2 = self.point2.position
        if self.mode == 0:    
            width = abs(p1[0] - p2[0])
            height = abs(p1[1] - p2[1])

            posX = min(p1[0], p2[0])
            posY = min(p1[1], p2[1])

            rect = (posX, posY, width, height)
            self.sprite = pg.draw.rect(screen, (0,0,0), rect, 3)
        elif self.mode == 1:
            width = abs(p1[0] - p2[0]) * 2
            height = abs(p1[1] - p2[1]) * 2

            posX = p1[0] - abs(p1[0]-p2[0])
            posY = p1[1] - abs(p1[1]-p2[1])

            rect = (posX, posY, width, height)
            self.sprite = pg.draw.rect(screen, (0,0,0), rect, 3)

    def __eq__(self, other):
        if type(self) == type(other):
            if self.mode == 0:
                return TwoPointShape.__eq__(self,other)
            elif self.mode == 1:        
                return (self.point1 == other.point1 and self.point2 == other.point2) and self.mode == other.mode
        return False

class QuadraticBezier(Shape):
    def draw(self, screen):
        p = []
        p0,p1,p2 = self.points
        quality = 20
        for i in range(quality):
            t = 1/quality * i
            #Xpos
            x0 = p0.position[0]
            x1 = p1.position[0]
            x2 = p2.position[0]
            #Ypos
            y0 = p0.position[1]
            y1 = p1.position[1]
            y2 = p2.position[1]

            x = self.calcShit(x0,x1,x2,t)
            y = self.calcShit(y0,y1,y2,t)
            p.append((round(x),round(y)))
        #last point
        p.append(self.points[-1].position)

        for i in range(len(p)-1):
            pg.draw.line(screen, self.color, p[i], p[i+1], 3)


    def calcShit(self,a0,a1,a2,t):
        thatShit = (1-t)**2 * a0 + 2*(1-t)*t*a1 + t**2 * a2
        return thatShit

    def __eq__(self, other):
        if type(self) == type(other):
            return self.points == other.points or self.points == other.points[::-1]
        return False