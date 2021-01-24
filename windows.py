import pygame as pg
import pygame_gui

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements import UIPanel, UIDropDownMenu
from pygame_gui.elements.ui_image import UIImage

class DrawingPanel(UIPanel):
    def __init__(self, position, size,  ui_manager):
        super().__init__(pg.Rect(position, size), manager = ui_manager, object_id='#drawing_window', starting_layer_height=5)


        draw_surface_size = self.get_container().get_size()
        self.draw_surface_element = UIImage(pg.Rect((0, 0), draw_surface_size), pg.Surface(draw_surface_size).convert(), manager=ui_manager, container=self, parent_element=self)

        self.is_active = True

    def process_event(self, event):
        handled = super().process_event(event)
        #event processes
        return handled

    def update(self, time_delta):
        pg.draw.rect(self.draw_surface_element.image, (255,255,255), (0,0,self.rect[2],self.rect[3]))
        super().update(time_delta)

    def calcPos(self, pos, unit):
        pos = list(pos)
        pos[0] -= self.rect.x
        pos[1] -= self.rect.y
        return pos

class ToolBar(UIPanel):
    def __init__(self, position, size,  ui_manager, modes, tools, window):
        super().__init__(pg.Rect(position, size), manager = ui_manager, object_id='#toobar', starting_layer_height = 5)
        self.modes = modes
        self.tools = tools
        self.options = []
        self.window = window
        
        self.modesheight = 0
        for i in range(len(modes) + len(tools)):
            if i < len(modes):
                but = pygame_gui.elements.UIButton(relative_rect=pg.Rect((5, 35*i+5), (80, 30)), text=modes[i], manager=ui_manager, container = self)
            else:
                but = pygame_gui.elements.UIButton(relative_rect=pg.Rect((5, 35*i+40), (80, 30)), text=tools[i-len(modes)], manager=ui_manager, container = self)
                self.modesheight = 35*i+40 + 30

            self.options.append(but)

        self.selected = pygame_gui.elements.UIButton(relative_rect=pg.Rect((85, 8), (10,30)), text="", manager=ui_manager, container = self)
        self.selected.rect = pg.Rect((85, 0 * 35 + 8), (10,30))
        self.is_active = True

        #back/forward
        self.back = pygame_gui.elements.UIButton(relative_rect=pg.Rect((5, self.modesheight + 25), (40, 30)), text="←", manager=ui_manager, container = self)
        self.forward = pygame_gui.elements.UIButton(relative_rect=pg.Rect((45, self.modesheight + 25), (40, 30)), text="→", manager=ui_manager, container = self)

    def process_event(self, event):
        handled = super().process_event(event)

        if (event.type == pg.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED):
            for b in self.options:
                if event.ui_element == b:
                    print(b.text)
                    self.window.changeMode(b.text)
                    a = 8
                    if b.text in self.tools: a = 43
                    self.selected.rect = pg.Rect((85, self.options.index(b) * 35 + a), (10,30))
            if event.ui_element == self.back:
                self.window.back()
            if event.ui_element == self.forward:
                self.window.forward()
        #event processes
        return handled

    def update(self, time_delta):
        #pg.draw.rect(self.draw_surface_element.image, (255,255,255), (0,0,self.rect[2],self.rect[3]))
        super().update(time_delta)

