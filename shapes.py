import pygame as pg
import math
import svgwrite
class Point:
    def __init__(self, position):
        self.position = position
        self.sprite = None
        self.moving = False
        self.buffering = False
        self.color = (0,0,255)
        self.selected = False
    def draw(self, screen):
        self.color = (0,255,0) if self.moving else (255,0,0) if self.buffering else (0,255,255) if self.selected else None 
        #outline
        roundedPos = (round(self.position[0]), round(self.position[1]))
        if self.color != None: #outline
            self.sprite = pg.draw.circle(screen, self.color, roundedPos, 12)

        self.sprite = pg.draw.circle(screen, (40,40,40), roundedPos, 10)
        
        self.sprite = pg.draw.circle(screen, (255,255,255), roundedPos, 5)

    def move(self, x,y, snapStep, toSnap):
        self.position = [self.position[0]+x, self.position[1]+y]
        
        if toSnap:
            self.position[0] = round(self.position[0]/snapStep) * snapStep
            self.position[1] = round(self.position[1]/snapStep) * snapStep

    def svg(self):
        return svgwrite.shapes.Circle(center = self.position, r=2)

class Shape:
    def __init__(self, points):
        self.points = points
        self.color = (40,40,40)
        self.sprite = None
        self.width = 5

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
        if self.mode == 0:
            self.sprite = pg.draw.line(screen, self.color, self.point1.position, self.point2.position, self.width)
        elif self.mode == 1:
            self.sprite = pg.draw.line(screen, self.color, self.point1.position, self.point2.position, self.width)
            tricolor = self.color
            start = self.point1.position
            end = self.point2.position

            trirad = 20

            rad = 180/math.pi
            thickness = self.width
            pg.draw.line(screen, tricolor, start, end, thickness)
            rotation = (math.atan2(start[1] - end[1], end[0] - start[0])) + math.pi/2
            pg.draw.polygon(screen, tricolor, ((end[0] + trirad * math.sin(rotation),
                                                end[1] + trirad * math.cos(rotation)),
                                            (end[0] + trirad * math.sin(rotation - 120*rad),
                                                end[1] + trirad * math.cos(rotation - 120*rad)),
                                            (end[0] + trirad * math.sin(rotation + 120*rad),
                                                end[1] + trirad * math.cos(rotation + 120*rad))))

    def svg(self):
        return svgwrite.shapes.Line(start = self.point1.position, end = self.point2.position, stroke=svgwrite.rgb(10, 10, 16, '%'))
    

class Circle(TwoPointShape):

    def __init__(self, points, mode):
        TwoPointShape.__init__(self, points, mode)
        self.center = 0
    def draw(self, screen):
        if self.mode == 0:
            self.radius = self.updateRadius()    
            if self.radius < 3: self.radius = 3
            self.center = self.point1.position
            self.sprite = pg.draw.circle(screen, self.color, self.center, round(self.radius), self.width)
        elif self.mode == 1:
            p1 = self.point1.position
            p2 = self.point2.position
            self.center = (round((p1[0]+p2[0])/2), round((p1[1]+p2[1])/2))
            self.radius = self.updateRadius()/2

            self.sprite = pg.draw.circle(screen, self.color, self.center, round(self.radius), self.width)

    def updateRadius(self):
        x_dist = abs(self.point1.position[0]-self.point2.position[0])
        y_dist = abs(self.point1.position[1]-self.point2.position[1])

        return math.sqrt(x_dist**2 + y_dist**2)

    def svg(self):
        return svgwrite.shapes.Circle(center=self.center, r=self.radius, stroke=svgwrite.rgb(10, 10, 16, '%'), fill = "rgb(255,255,255)", fill_opacity=0)

    def __eq__(self, other):
        if type(self) == type(other):
            if self.mode == 0:
                return self.point1 == other.point1 and self.point2 == other.point2 and self.mode == other.mode
            elif self.mode == 1:
                return ((self.point1 == other.point1 and self.point2 == other.point2) or (self.point1 == other.point2 and self.point2 == other.point1)) and self.mode == other.mode
        return False

class Rectangle(TwoPointShape):
    def __init__(self, points, mode):
        TwoPointShape.__init__(self, points, mode)
        self.rect = self.updateRect()

    def updateRect(self):
        p1 = self.point1.position
        p2 = self.point2.position
        if self.mode == 0:    
            width = abs(p1[0] - p2[0])
            height = abs(p1[1] - p2[1])

            posX = min(p1[0], p2[0])
            posY = min(p1[1], p2[1])

            return (posX, posY, width, height)
        elif self.mode == 1:
            width = abs(p1[0] - p2[0]) * 2
            height = abs(p1[1] - p2[1]) * 2

            posX = p1[0] - abs(p1[0]-p2[0])
            posY = p1[1] - abs(p1[1]-p2[1])

            return (posX, posY, width, height)

    def draw(self, screen):
        self.rect = self.updateRect()
        self.sprite = pg.draw.rect(screen, (0,0,0), self.rect, self.width)

    def __eq__(self, other):
        if type(self) == type(other):
            if self.mode == 0:
                return TwoPointShape.__eq__(self,other)
            elif self.mode == 1:        
                return (self.point1 == other.point1 and self.point2 == other.point2) and self.mode == other.mode
        return False

    def svg(self):
        print("saving rect")
        points = self.rect
        rect = svgwrite.container.Group()

        lines = [ 
                [ (points[0],points[1]),(points[0]+points[2], points[1]) ],
                [ (points[0],points[1]),(points[0], points[1]+points[3]) ],
                [ (points[0] + points[2],points[1]),(points[0]+points[2], points[1]+points[3]) ],
                [ (points[0],points[1] + points[3]),(points[0]+points[2], points[1]+points[3]) ],
                ]

        for l in lines:
            print(l[0],l[1])
            rect.add( svgwrite.shapes.Line(start = l[0], end = l[1], stroke=svgwrite.rgb(10, 10, 16, '%')) )
        return rect

class QuadraticBezier(Shape):
    def draw(self, screen):
        p = self.calcLines()

        for i in range(len(p)-1):
            pg.draw.line(screen, self.color, p[i], p[i+1], self.width)

    def calcLines(self):
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
        return p

    def calcShit(self,a0,a1,a2,t):
        thatShit = (1-t)**2 * a0 + 2*(1-t)*t*a1 + t**2 * a2
        return thatShit

    def __eq__(self, other):
        if type(self) == type(other):
            return self.points == other.points or self.points == other.points[::-1]
        return False

    def svg(self):
        p = self.calcLines()
        curve = svgwrite.container.Group()

        for i in range(len(p)-1):
            curve.add( svgwrite.shapes.Line(start = p[i], end = p[i+1], stroke=svgwrite.rgb(10, 10, 16, '%')) )
            #pg.draw.line(screen, self.color, p[i], p[i+1], self.width)

        return curve