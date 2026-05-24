import json
import os
import pygame
from settings import *

class Level:
    def __init__(self, level_name):
        self.name = level_name
        self.platforms = []      # 元组列表
        self.collectibles = []   # 动态列表：[x, y, type]
        self.hazards = []        # (x, y, w, h)
        self.start_pos = (400, 550)
        self.end_pos = (400, 50)
        self.load_level(level_name)

    def load_level(self, level_name):
        path = os.path.join("world", "levels", f"{level_name}.json")
        if not os.path.exists(path):
            self.load_test_level()
            return
        with open(path, "r") as f:
            data = json.load(f)
            self.platforms = data.get("platforms", [])
            self.collectibles = data.get("collectibles", [])
            self.hazards = data.get("hazards", [])
            self.start_pos = tuple(data.get("start", (400, 550)))
            self.end_pos = tuple(data.get("end", (400, 50)))

    def load_test_level(self):
        # 简单垂直通道，并加入小泡泡供吸收
        self.platforms = [
            (0, 500, 800, 20),
            (350, 350, 100, 20),
            (500, 200, 100, 20)
        ]
        # 类型包含 "energy" 能量种子 和 "bubble" 小泡泡
        self.collectibles = [
            [400, 450, "energy"],
            [400, 300, "energy"],
            [550, 150, "bubble"],   # 小泡泡，吸收后增加体积
            [200, 400, "bubble"]    # 另一个小泡泡
        ]
        self.hazards = [
            (0, 100, 800, 30)    # 顶部污染区
        ]
        self.start_pos = (400, 480)
        self.end_pos = (400, 50)

    # ----- 游戏运行时逻辑 -----
    def update(self, dt):
        """每帧更新（目前仅占位，后续可添加动态障碍等）"""
        pass

    def get_rect(self, obj):
        """根据对象类型返回碰撞矩形"""
        if isinstance(obj, tuple) and len(obj) == 4:
            return pygame.Rect(*obj)
        elif isinstance(obj, list) and len(obj) == 3:
            x, y, _ = obj
            r = COLLECTIBLE_RADIUS
            return pygame.Rect(x - r, y - r, 2*r, 2*r)
        return pygame.Rect(0, 0, 0, 0)

    def handle_collectibles(self, player):
        """
        检测玩家与所有收集物的碰撞，执行吸收或能量收集。
        返回是否收集到了物品（可用于音效等）
        """
        collected = False
        new_collectibles = []
        for item in self.collectibles:
            x, y, typ = item
            # 简单矩形碰撞检测
            item_rect = pygame.Rect(x - COLLECTIBLE_RADIUS, y - COLLECTIBLE_RADIUS,
                                    2*COLLECTIBLE_RADIUS, 2*COLLECTIBLE_RADIUS)
            player_rect = pygame.Rect(player.x - player.radius, player.y - player.radius,
                                      player.radius*2, player.radius*2)
            if player_rect.colliderect(item_rect):
                if typ == "energy":
                    player.collect_energy(ENERGY_GAIN)
                elif typ == "bubble":
                    player.absorb(VOLUME_INCREMENT)   # 吸收小泡泡，体积变大，上浮
                collected = True
                # 不保留被收集的物品（消失）
            else:
                new_collectibles.append(item)
        self.collectibles = new_collectibles
        return collected

    def add_small_bubble(self, x, y):
        """在指定位置生成一个小泡泡（用于玩家释放）"""
        self.collectibles.append([x, y, "bubble"])

    def is_at_end(self, player):
        """检查玩家是否到达终点"""
        player_center = (player.x, player.y)
        # 简单距离判断
        dist = ((player_center[0] - self.end_pos[0])**2 + (player_center[1] - self.end_pos[1])**2)**0.5
        return dist < 60