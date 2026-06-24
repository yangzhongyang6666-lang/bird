import pygame
import pymunk as pm
from utils.pm_utils import to_pymunk, to_pygame

class PhysicsBird(pygame.sprite.Sprite):
    """物理小鸟基类 (带有重力和碰撞体积)"""
    def __init__(self, bird_info, pos_x, pos_y, space, surface):
        # 注意：这里严格保持为空，不传任何参数给父类
        super().__init__() 
        
        self.surface = surface
        self.space = space
        
        # 1. 从管家发来的字典里，获取物理参数
        self.radius = bird_info['radius']
        self.mass = bird_info['mass']
        self.images = bird_info['images']
        self.image_index = 0
        self.image_count = len(self.images)
        
        # 2. 创建刚体 (Body)
        inertia = pm.moment_for_circle(self.mass, 0, self.radius, (0, 0))
        self.body = pm.Body(self.mass, inertia)
        self.body.position = to_pymunk(pos_x, pos_y, surface)
        
        # 3. 创建形状 (Shape)
        self.shape = pm.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = bird_info['elasticity']
        self.shape.friction = bird_info['friction']
        self.shape.collision_type = bird_info['collision_type']
        
        # 4. 加入物理空间
        self.space.add(self.body, self.shape)
        self.alive_time = 0.0
        self.is_dead = False

    def run(self):
        """物理运算与绘制"""
        pos_x, pos_y = to_pygame(self.body.position, self.surface)
        draw_x = pos_x - self.radius
        draw_y = pos_y - self.radius

        current_image = self.images[int(self.image_index)]
        self.surface.blit(current_image, (draw_x, draw_y))
        
        # 动画帧轮播
        self.image_index = (self.image_index + 1) % self.image_count
        self.image_index = (self.image_index + 1) % self.image_count

        # =====================================================
        # 【新增：飞鸟寂灭监测】
        # =====================================================
        self.alive_time += 1.0 / 40.0
        current_speed = self.body.velocity.length
        
        # 寂灭法案：1. 在场上活过 5 秒强制超度； 2. 活了超过 1.5 秒且速度已经慢如蜗牛(<8.0)，判定动能耗尽
        if self.alive_time > 5.0 or (self.alive_time > 1.5 and current_speed < 8.0):
            self.is_dead = True


class StandbyBird(pygame.sprite.Sprite):
    """待机小鸟 (只有动画，没有物理重量，跟着鼠标走)"""
    def __init__(self, bird_info, pos_x, pos_y, surface):
        # 注意：这里也严格保持为空
        super().__init__()
        
        self.surface = surface
        self.images = bird_info['images']
        self.image_index = 0
        self.image_count = len(self.images)
        self.radius = bird_info['radius']
        
        # 实际绘制的坐标 (拖拽时会跟着鼠标改变)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def run(self):
        """动画绘制"""
        current_image = self.images[int(self.image_index)]
        draw_x = self.pos_x - self.radius
        draw_y = self.pos_y - self.radius
        self.surface.blit(current_image, (draw_x, draw_y))
        
        # 缓慢播放挥舞翅膀的动画
        self.image_index = (self.image_index + 0.2) % self.image_count