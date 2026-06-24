import pygame
import sys
from core.resource_manager import ResourceManager
from scenes.welcome import WelcomeScene
from scenes.choice import ChoiceScene
from scenes.level import LevelScene

class GameManager:
    """游戏总控：负责主循环和场景状态切换 (有限状态机 FSM)"""
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()
        
        # 1. 启动管家，加载所有全局资源
        self.res_manager = ResourceManager()
        self.res_manager.load_all()
        
        # 2. 初始化所有场景
        self.welcome_scene = WelcomeScene(self.surface, self.res_manager)
        self.choice_scene = ChoiceScene(self.surface, self.res_manager)
        self.level_scene = LevelScene(self.surface, self.res_manager)
        
        # 3. 设置游戏的初始状态
        self.current_state = "welcome"

    def run(self):
        """游戏主循环 (死循环)"""
        while True:
            # A. 全局事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                # 【修改点 3】：欢迎界面点击后，进入 choice (选关) 而不是直接进 level
                if event.type == pygame.MOUSEBUTTONDOWN and self.current_state == "welcome":
                    self.current_state = "choice" 
                    continue 
                    
                # 【修改点 4】：如果当前在选关界面，处理按钮点击
                if self.current_state == "choice":
                    # 接收选关界面传回来的信号
                    action = self.choice_scene.handle_event(event)
                    if action == "level_1":
                        self.current_state = "level" # 点了关卡1，再切到战斗场景！
                    continue
                    
                # 【修改点2】：把鼠标事件移交给关卡处理（为了能拉弹弓）
                if self.current_state == "level":
                    self.level_scene.handle_event(event)

            # B. 状态机路由分发
            if self.current_state == "welcome":
                self.welcome_scene.run()

            # 【修改点 5】：增加渲染选关界面的逻辑
            elif self.current_state == "choice":
                self.choice_scene.run()
                
            # 【修改点3】：运行真正的关卡，而不是画灰屏
            elif self.current_state == "level":
                self.level_scene.run()

            # C. 统一刷新屏幕和控帧
            pygame.display.flip()
            self.clock.tick(40)