import pygame
import pymunk as pm
from utils.pm_utils import to_pymunk
from entities.bird import PhysicsBird

class WelcomeScene:
    """欢迎界面场景"""
    def __init__(self, surface, res_manager):
        self.surface = surface
        self.res_manager = res_manager
        self.status = "running" # 状态标志：running 代表正在播放，end 代表播放结束
        
        # 1. 为欢迎界面创建专属的物理空间
        self.space = pm.Space()
        self.space.gravity = (0.0, -700.0)
        
        # 2. 从管家处获取背景图
        self.bg_image = self.res_manager.get_image('welcome_bg')
        
        # 3. 创建地面刚体
        x, y = to_pymunk(self.surface.get_width(), self.surface.get_height(), self.surface)
        static_body = self.space.static_body
        ground_line = pm.Segment(static_body, (0.0, y), (x, y), 0.0)
        ground_line.elasticity = 0.95
        ground_line.friction = 1.0
        self.space.add(ground_line)
        
        # 4. 从管家处获取红鸟数据并实例化
        red_bird_info = self.res_manager.get_bird_info('redBird')
        self.bird = PhysicsBird(red_bird_info, 100, 100, self.space, self.surface)

    def run(self):
        """每一帧调用的运行逻辑"""
        # 画背景
        self.surface.blit(self.bg_image, (0, 0))
        # 运行小鸟
        self.bird.run()
        # 推进物理时间
        self.space.step(1.0 / 40.0)