import json
import os

class Level:
    def __init__(self, level_name):
        self.name = level_name
        self.platforms = []    # (x, y, width, height)
        self.collectibles = [] # (x, y, type)
        self.hazards = []      # (x, y, width, height)
        self.start_pos = (400, 550)
        self.end_pos = (400, 50)
        self.load_level(level_name)
    
    def load_level(self, level_name):
        path = os.path.join("world", "levels", f"{level_name}.json")
        if not os.path.exists(path):
            # 使用硬编码测试关卡
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
        # 一个简单的垂直通道，底部有平台，中间有收集物
        self.platforms = [
            (0, 500, 800, 20),   # 底部平台
            (350, 350, 100, 20), # 中间浮岛
            (500, 200, 100, 20)  # 上方障碍
        ]
        self.collectibles = [
            (400, 450, "energy"),
            (400, 300, "energy"),
            (550, 150, "energy")
        ]
        self.hazards = [
            (0, 100, 800, 30)    # 顶部污染区
        ]
        self.start_pos = (400, 480)
        self.end_pos = (400, 50)