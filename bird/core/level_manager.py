import pygame
from pytmx.util_pygame import load_pygame
from entities.obstacle import Obstacle

class LevelManager:
    """关卡解析器：具备高度自愈能力的 Tiled 地图加载器"""
    def __init__(self, tmx_path):
        print(f"\n====== 正在解析 TMX 文件：{tmx_path} ======")
        self.tmx_data = load_pygame(tmx_path)
        
        self.backup_textures = {}
        
        # --- 🎒 1. 独立尝试揣上【小猪】衣服 ---
        try:
            pig_sheet = pygame.image.load("./resources/level/pig.png").convert_alpha()
            
            crop_x, crop_y = 20, 0 
            crop_w, crop_h = 67, 74
            
            # 1. 抠出原始图像
            raw_pig = pig_sheet.subsurface((crop_x, crop_y, crop_w, crop_h))
            
            # 2. 【净化魔法】：创建一张真正带 Alpha 通道的画布
            clean_pig = pygame.Surface((crop_w, crop_h), pygame.SRCALPHA)
            clean_pig.fill((0,0,0,0)) # 填充完全透明
            
            # 3. 逐像素复制：将非黑色像素画上去，黑色像素自动忽略
            for x in range(crop_w):
                for y in range(crop_h):
                    color = raw_pig.get_at((x, y))
                    # 如果不是黑色 (0,0,0)，才画上去
                    if color[:3] != (0, 0, 0):
                        clean_pig.set_at((x, y), color)
            
            self.backup_textures['pig'] = clean_pig
            print("🎒 成功抠出并净化了第一只猪！")
            
        except Exception as e:
            print(f"❌ 猪猪抠图失败！原因：{e}")
        # 2. 加载木头 (用 wood3.png 作为兜底)
        try:
            wood_img = pygame.image.load("./resources/level/wood3.png").convert_alpha()
            self.backup_textures['wood'] = wood_img # 存整张图
            print("🎒 成功揣上了兜底 木头 贴图！")
        except:
            print("❌ 木头图片加载失败")

    def build_level(self, space, surface):
        obstacles = []
        for obj in self.tmx_data.objects:
            name = obj.name
            if not name or "bird" in name.lower() or "sling" in name.lower():
                continue
                
            image = obj.image
            
            # 【终极自愈逻辑】
            if image is None:
                if "pig" in name.lower():
                    image = self.backup_textures.get('pig')
                elif "wood" in name.lower():
                    # 把整张木头图切一小块给它用
                    base_wood = self.backup_textures.get('wood')
                    if base_wood:
                        # 尝试切一块，如果越界就用整张
                        try:
                            image = base_wood.subsurface((0, 0, min(40, base_wood.get_width()), min(40, base_wood.get_height())))
                        except:
                            image = base_wood
            
            if image is None:
                continue
                
            # 召唤实体
            w = obj.width if obj.width > 0 else 40
            h = obj.height if obj.height > 0 else 40
            new_obs = Obstacle(name, image, obj.x, obj.y, w, h, space, surface)
            obstacles.append(new_obs)
                
        return obstacles