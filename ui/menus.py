import pygame
from settings import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "start"
            if event.key == pygame.K_ESCAPE:
                return "quit"
        return None
    
    def render(self, screen):
        screen.fill(MENU_BG)
        title = self.font.render("Bubbles", True, TEXT_COLOR)
        start_text = self.font.render("Press ENTER to Start", True, TEXT_COLOR)
        quit_text = self.font.render("Press ESC to Quit", True, TEXT_COLOR)
        screen.blit(title, (300, 200))
        screen.blit(start_text, (250, 300))
        screen.blit(quit_text, (260, 350))

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume"
            if event.key == pygame.K_r:
                return "restart"
            if event.key == pygame.K_m:
                return "menu"
        return None
    
    def render(self, screen):
        # 半透明遮罩
        mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        mask.set_alpha(128)
        mask.fill((0,0,0))
        screen.blit(mask, (0,0))
        
        resume_text = self.font.render("ESC - Resume", True, TEXT_COLOR)
        restart_text = self.font.render("R - Restart", True, TEXT_COLOR)
        menu_text = self.font.render("M - Main Menu", True, TEXT_COLOR)
        screen.blit(resume_text, (300, 250))
        screen.blit(restart_text, (300, 300))
        screen.blit(menu_text, (300, 350))