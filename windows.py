import pygame as pg
import pygame_gui

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements import UIPanel, UIDropDownMenu
from pygame_gui.elements.ui_image import UIImage
from pygame_gui.windows import UIMessageWindow

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
    def __init__(self, position, size,  ui_manager, modes, tools, grid, window):
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
        self.options[0].select()

        
        #grid chheckbox
        self.grid = grid
        self.gridCheckbox = pygame_gui.elements.UIButton(relative_rect=pg.Rect((5, self.modesheight+5), (80, 30)), text="grid", manager=ui_manager, container = self)
        self.gridCheckbox.select()

        self.modesheight+=40

        #back/forward
        self.back = pygame_gui.elements.UIButton(relative_rect=pg.Rect((5, self.modesheight + 25), (40, 30)), text="←", manager=ui_manager, container = self)
        self.forward = pygame_gui.elements.UIButton(relative_rect=pg.Rect((45, self.modesheight + 25), (40, 30)), text="→", manager=ui_manager, container = self)

        self.saveAsSvgButton = pygame_gui.elements.UIButton(relative_rect=pg.Rect((5, self.modesheight+60), (80, 30)), text="save", manager=ui_manager, container = self)

        self.helpButton = pygame_gui.elements.UIButton(relative_rect=pg.Rect((5, 680), (80, 30)), text="help", manager=ui_manager, container = self)

        self.helpWindow = None

    def process_event(self, event):
        handled = super().process_event(event)

        if (event.type == pg.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED):
            for b in self.options:
                if event.ui_element == b:
                    for i in self.options: i.unselect()
                    b.select()
                    self.window.changeMode(b.text)
                    
            if event.ui_element == self.back:
                self.window.back()
            if event.ui_element == self.forward:
                self.window.forward()

            if event.ui_element == self.gridCheckbox:
                if self.gridCheckbox.is_selected:
                    self.gridCheckbox.unselect()
                else:
                    self.gridCheckbox.select()
                self.grid.active = self.gridCheckbox.is_selected

            if event.ui_element == self.saveAsSvgButton:
                self.window.saveSvg()
            if event.ui_element == self.helpButton and self.window.canDraw:
                self.helpWindow = HelpPopup(self.window.manager)
                self.window.canDraw = False
        if event.type == pg.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.helpWindow:
                self.window.canDraw = True
                self.helpWindow = None
        #event processes
        return handled

    def update(self, time_delta):
        #pg.draw.rect(self.draw_surface_element.image, (255,255,255), (0,0,self.rect[2],self.rect[3]))
        super().update(time_delta)

class HelpPopup(UIMessageWindow):

    def __init__(self, manager):

        data = [
            {"title":"Controls", "info": "Middle click to move with canvas<br>"},
            {"title":"Point", "info": "Left click to place point<br>Right click to delete point<br>Hold left mouse button to move point"},
            {"title":"Line/Arrow", "info": "Select two points to create line/Arrow"},
            {"title":"Rect", "info": "Select two points to create rectangle<br>rect = Two oposite corners<br>rect2 = center and corner"},
            {"title":"Circle", "info": "Select two points to create circle<br>circle = center and radius<br>circle2 = distance of these two points is diameter"},
            {"title":"Bezier", "info": "Select three points to create quadratic bezier curve"},
            {"title":"Select", "info": "Select points :) (a bit broken rn, will be fixed later)"},
            {"title":"Move", "info": "Use left click to move with selected points"},
        ]

        out = ""
        for i in data:
            out += f"<b>{i['title']}</b><br>"
            out += f"{i['info']}<br><br>"

        super().__init__(rect = pg.Rect(50,50,600,500), manager = manager, html_message=out)



