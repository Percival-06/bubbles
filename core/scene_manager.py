import pygame
import sys
from ui.menus import MainMenu, PauseMenu
from entities.bubble import Bubble
from world.level_parser import Level
from ui.renderer import Renderer

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.scene = "menu"
        self.running = True
        self.main_menu = MainMenu(screen)
        self.pause_menu = PauseMenu(screen)
        self.current_level = None
        self.player = None
        self.renderer = None
    
    def handle_event(self, event):
        if self.scene == "menu":
            result = self.main_menu.handle_event(event)
            if result == "start":
                self.start_game("test_level")
            elif result == "quit":
                self.running = False
        
        elif self.scene == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.scene = "pause"
            # 暂停菜单会接管事件吗？ 我们让暂停菜单在 update 中处理
            if self.player:
                self.player.handle_event(event)
        
        elif self.scene == "pause":
            result = self.pause_menu.handle_event(event)
            if result == "resume":
                self.scene = "game"
            elif result == "restart":
                self.start_game(self.current_level_name)
            elif result == "menu":
                self.scene = "menu"
    
    def update(self, dt):
        if self.scene == "game":
            if self.player and self.current_level:
                self.player.update(dt, self.current_level)
                # 检查输赢条件（简化：暂不检查）
    
    def render(self, screen):
        if self.scene == "menu":
            self.main_menu.render(screen)
        elif self.scene == "game":
            self.renderer.render(screen, self.player, self.current_level)
        elif self.scene == "pause":
            # 把游戏画面保留，上面覆盖暂停菜单
            self.renderer.render(screen, self.player, self.current_level)
            self.pause_menu.render(screen)
    
    def start_game(self, level_name):
        self.current_level = Level(level_name)
        self.player = Bubble(400, 550)  # 起点坐标可配置
        self.renderer = Renderer()
        self.current_level_name = level_name
        self.scene = "game"
    
    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()