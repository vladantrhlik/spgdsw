import pygame as pg

class Button:

    def __init__(self, rect , value, text, font): #rect = [x,y,w,h]
        self.rect = rect
        self.value = value
        self.text = text
        self.font = font
        self.sprite = None
        self.color = (0,255,255)
    
    def update(self, pos, event):
        if self.sprite.collidepoint(pos):
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                print("button clicked!")
                return True, self.value
            else:
                return False, None
        else:
            return False, None


    def draw(self, screen):
        self.sprite = pg.draw.rect(screen, self.color, self.rect)
        textsurface = self.font.render(self.text, True, (0,0,0))
        screen.blit(textsurface,(self.rect[0]+5, self.rect[1]))


class ToolBar:

    def __init__(self, modes, screen, font):
        self.font = font
        self.options = []
        self.modes = modes
        self.screen = screen

        self.color = (0,255,255)
        self.colorSelected = (0,255,0)

        for b in range(len(modes)):
            a = Button([15,15+60*b,100,50], b, self.modes[b], self.font)
            a.draw(self.screen)
            a.selected = False
            self.options.append(a)
        self.options[0].selected = True

    def update(self, pos, event):
        for b in self.options:
            out = b.update(pos, event)
            if out[0]:
                for i in self.options:
                    i.selected = False
                b.selected = True
                return True,out[1]
        return False, None

    def draw(self):
        for b in self.options:
            if b.selected: 
                b.color = self.colorSelected
            else:
                b.color = self.color
            b.draw(self.screen)