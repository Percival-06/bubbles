import json
import os
import pygame
from settings import *
from core.save_manager import LEVEL_ORDER

class Level:
    LEVEL_INFO = [
        {"id": "training", "title": "教学关：火山口", "description": "熟悉体积调节与浮沉。"},
        {"id": "deep_sea", "title": "深海通道", "description": "开始在污染边缘规划路线。"},
        {"id": "mid_sea", "title": "中层海域", "description": "在狭窄空间中权衡资源与风险。"},
    ]

    @classmethod
    def catalog(cls):
        return list(cls.LEVEL_INFO)

    def __init__(self, level_name):
        self.name = level_name
        self.title = level_name
        self.description = ""
        self.next_level = self._next_level(level_name)
        self.platforms = []      # 元组列表
        self.collectibles = []   # 动态列表：[x, y, type]
        self.hazards = []        # (x, y, w, h)
        self.start_pos = (400, 550)
        self.end_pos = (400, 50)
        self.total_energy = 0
        self.collected_energy = 0
        self.collected_bubbles = 0
        self.load_level(level_name)

    def _next_level(self, level_name):
        if level_name not in LEVEL_ORDER:
            return None
        index = LEVEL_ORDER.index(level_name)
        if index + 1 >= len(LEVEL_ORDER):
            return None
        return LEVEL_ORDER[index + 1]

    def load_level(self, level_name):
        path = os.path.join("world", "levels", f"{level_name}.json")
        if not os.path.exists(path):
            self.load_test_level()
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.title = data.get("title", level_name)
            self.description = data.get("description", "")
            self.next_level = data.get("next", self._next_level(level_name))
            self.platforms = data.get("platforms", [])
            self.collectibles = data.get("collectibles", [])
            self.hazards = data.get("hazards", [])
            self.start_pos = tuple(data.get("start", (400, 550)))
            self.end_pos = tuple(data.get("end", (400, 50)))
            self.total_energy = sum(1 for item in self.collectibles if item[2] == "energy")

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
        self.total_energy = sum(1 for item in self.collectibles if item[2] == "energy")

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
        返回本帧收集统计（可用于音效、结算等）
        """
        stats = {"energy": 0, "bubble": 0}
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
                    self.collected_energy += 1
                    stats["energy"] += 1
                elif typ == "bubble":
                    player.absorb(VOLUME_INCREMENT)   # 吸收小泡泡，体积变大，上浮
                    self.collected_bubbles += 1
                    stats["bubble"] += 1
                # 不保留被收集的物品（消失）
            else:
                new_collectibles.append(item)
        self.collectibles = new_collectibles
        return stats

    def apply_hazards(self, player, dt):
        player_rect = pygame.Rect(player.x - player.radius, player.y - player.radius,
                                  player.radius*2, player.radius*2)
        touched = False
        for haz in self.hazards:
            if player_rect.colliderect(pygame.Rect(*haz)):
                player.apply_pollution(dt)
                touched = True
        return touched

    def add_small_bubble(self, x, y):
        """在指定位置生成一个小泡泡（用于玩家释放）"""
        self.collectibles.append([x, y, "bubble"])

    def is_at_end(self, player):
        """检查玩家是否到达终点"""
        player_center = (player.x, player.y)
        # 简单距离判断
        dist = ((player_center[0] - self.end_pos[0])**2 + (player_center[1] - self.end_pos[1])**2)**0.5
        return dist < 60
