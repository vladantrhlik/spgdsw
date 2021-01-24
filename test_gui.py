import pygame as pg
import pygame_gui
from pygame_gui.elements import UIWindow, UIImage

pg.init()

screen = pg.display.set_mode((1280,720))
running = True

manager = pygame_gui.UIManager((1280,720))
clock = pg.time.Clock()

window = UIWindow(pg.Rect(50,50,800,500), manager, "test")

drawingSurface = pg.Surface((300,300))
drawingImage = UIImage(pg.Rect(0,0,300,300), drawingSurface, manager, window)

while running:

    screen.fill((50,50,50))
    
    for event in pg.event.get():
        manager.process_events(event)
        if event.type == pg.QUIT:
            running = False

    

    time_delta = clock.tick(60)/1000.0
    
    #drawingImage = UIImage(pg.Rect(0,0,300,300), drawingSurface, manager, window)

    
    manager.update(time_delta)
    drawingImage.update(time_delta)

    drawingImage.image.fill((255,255,255))
    pg.draw.line(drawingImage.image, (0,255,0), (0,0), (50,50), 10)

    manager.draw_ui(screen)

    pg.display.flip()

# Done! Time to quit.
pg.quit()