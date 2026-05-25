import pygame
import sys
from settings import *
from core.scene_manager import SceneManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bubbles - 老鼠人")
    clock = pygame.time.Clock()
    
    manager = SceneManager(screen)
    
    while manager.running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                manager.quit()
            manager.handle_event(event)
        
        manager.update(dt)
        manager.render(screen)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()