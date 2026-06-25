import pygame
import math
import pymunk as pm
from utils.pm_utils import to_pymunk, to_pygame

class Obstacle(pygame.sprite.Sprite):
    """通用的物理障碍物类（自动兼容小猪和各种建筑材料）"""
    def __init__(self, name, image, x, y, width, height, space, surface):
        super().__init__()
        self.name = name
        self.surface = surface
        # pytmx 传过来的 image 已经切好了，我们确保它缩放到 Tiled 里的尺寸
        self.image = pygame.transform.scale(image, (int(width), int(height)))
        self.width = width
        self.height = height
        self.space = space

        # Pygame 和 Tiled 的坐标系通常以左上角为基准，而物理引擎需要物体的重心(中心点)
        center_x = x + width / 2
        center_y = y + height / 2

        # 🌟 多态魔法：根据你在 Tiled 里起的名字，自动分配物理属性！
        if name and "pig" in name.lower():
            mass = 15
            radius = width / 2
            inertia = pm.moment_for_circle(mass, 0, radius, (0, 0))
            self.body = pm.Body(mass, inertia)
            self.shape = pm.Circle(self.body, radius, (0, 0))
            self.shape.collision_type = 2 # 2 代表小猪，以后用来算分
        else:
            # 默认当作方形的木头/石头建筑
            mass = 20
            inertia = pm.moment_for_box(mass, (width, height))
            self.body = pm.Body(mass, inertia)
            self.shape = pm.Poly.create_box(self.body, (width, height))
            self.shape.collision_type = 3 # 3 代表建筑材料
            
        # 设置物理材质
        self.shape.elasticity = 0.4 # 弹性适中
        self.shape.friction = 0.8   # 摩擦力大一点，防止木头自己滑倒
        
        # 将它放入物理世界
        self.body.position = to_pymunk(center_x, center_y, surface)
        self.space.add(self.body, self.shape)
        
        # 【新增绑定】：在物理刚体上挂载 Python 实例的指针，并盖上“未死亡”印记
        self.shape.entity = self 
        self.is_dead = False
        if "pig" in name.lower():
            self.shape.collision_type = 2  # 2号身份证：小猪
            self.hp = 1.0                  # 一碰就碎
        else:
            self.shape.collision_type = 3  # 3号身份证：可破坏建材
            # 按建材的大小/种类分配血量（大木框100血，长条木板60血）
            self.max_hp = 100.0 if "box" in name.lower() else 60.0
            self.hp = self.max_hp

    def run(self):
        """实时渲染"""
        pos_x, pos_y = to_pygame(self.body.position, self.surface)
        angle_degrees = math.degrees(self.body.angle)
        
        rotated_image = pygame.transform.rotate(self.image, angle_degrees)
        new_rect = rotated_image.get_rect(center=(pos_x, pos_y))
        self.surface.blit(rotated_image, new_rect.topleft)