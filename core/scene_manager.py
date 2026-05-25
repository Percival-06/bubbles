import pygame
import sys
from ui.menus import MainMenu, PauseMenu
from entities.bubble import Bubble
from world.level_parser import Level
from ui.renderer import Renderer
from settings import VOLUME_INCREMENT   # 从 settings 导入（如果没有则定义为 2.0）

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
            # 释放小泡泡（按 X 键）
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                # 只有当玩家成功释放体积时才生成小泡泡
                if self.player and self.player.release(VOLUME_INCREMENT):
                    # 在泡泡身后生成小泡泡（向左偏移一点）
                    self.current_level.add_small_bubble(self.player.x - 30, self.player.y)
            # 其他玩家事件（例如暂时没用）
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
            elif result == "quit":
                self.running = False
    
    def update(self, dt):
        if self.scene == "game":
            if self.player and self.current_level:
                # 1. 玩家更新（物理、移动）
                self.player.update(dt, self.current_level)
                # 2. 关卡更新（目前暂无动态元素，但保留）
                self.current_level.update(dt)
                # 3. 检测收集物碰撞（吸收能量种子和小泡泡）
                self.current_level.handle_collectibles(self.player)
                # 4. 检查胜利条件（到达终点）
                if self.current_level.is_at_end(self.player):
                    self.victory()   # 简单切换场景或显示信息
    
    def render(self, screen):
        if self.scene == "menu":
            self.main_menu.render(screen)
        elif self.scene == "game":
            self.renderer.render(screen, self.player, self.current_level)
        elif self.scene == "pause":
            # 游戏画面 + 暂停菜单覆盖
            self.renderer.render(screen, self.player, self.current_level)
            self.pause_menu.render(screen)
    
    def start_game(self, level_name):
        self.current_level = Level(level_name)
        self.player = Bubble(*self.current_level.start_pos)  # 使用关卡起点坐标
        self.renderer = Renderer()
        self.current_level_name = level_name
        self.scene = "game"
    
    def victory(self):
        # 简单处理：回到菜单，后续可替换为胜利画面
        self.scene = "menu"
        # 这里可以加上音效或过渡效果
    
    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()