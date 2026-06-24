import pygame
import pymunk as pm
from utils.pm_utils import to_pymunk, to_pygame

class PhysicsBird(pygame.sprite.Sprite):
    """物理小鸟基类 (彻底与资源路径解耦)"""
    
    def __init__(self, bird_info, pos_x, pos_y, space, surface):
        super().__init__()
        self.surface = surface
        self.space = space
        
        # 1. 从管家发来的字典里，直接获取物理参数
        self.radius = bird_info['radius']
        self.mass = bird_info['mass']
        
        # 2. 从管家发来的字典里，获取已经切好的动画图片列表
        self.images = bird_info['images']
        self.image_index = 0
        self.image_count = len(self.images)
        
        # 3. 创建刚体 (Body - 负责算质量和位置)
        inertia = pm.moment_for_circle(self.mass, 0, self.radius, (0, 0))
        self.body = pm.Body(self.mass, inertia)
        self.body.position = to_pymunk(pos_x, pos_y, surface)
        
        # 4. 创建形状 (Shape - 负责算碰撞体积)
        self.shape = pm.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = bird_info['elasticity']
        self.shape.friction = bird_info['friction']
        self.shape.collision_type = bird_info['collision_type']
        
        # 5. 加入物理空间
        self.space.add(self.body, self.shape)

    def run(self):
        """物理运算与绘制"""
        # 物理坐标转屏幕坐标
        pos_x, pos_y = to_pygame(self.body.position, self.surface)
        draw_x = pos_x - self.radius
        draw_y = pos_y - self.radius

        # 动画帧轮播 (像放电影一样连续切换列表里的图片)
        current_image = self.images[self.image_index]
        self.surface.blit(current_image, (draw_x, draw_y))
        
        # 简单控制帧切换
        self.image_index = (self.image_index + 1) % self.image_count
        
        # 画一个蓝色的辅助线圆圈，方便我们看清它的物理碰撞体积
        pygame.draw.circle(self.surface, (0, 0, 255), (int(pos_x), int(pos_y)), self.radius, 2)