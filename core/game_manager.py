import pygame
import sys
from core.resource_manager import ResourceManager
from scenes.welcome import WelcomeScene
from scenes.level import LevelScene

class GameManager:
    """游戏总控：负责主循环和场景状态切换 (有限状态机 FSM)"""
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()
        
        # 1. 启动管家，加载所有全局资源
        self.res_manager = ResourceManager()
        self.res_manager.load_all()
        
        # 2. 初始化所有场景 (目前先装载欢迎界面)
        self.welcome_scene = WelcomeScene(self.surface, self.res_manager)
        self.level_scene = LevelScene(self.surface, self.res_manager)
        
        # 3. 设置游戏的初始状态
        self.current_state = "welcome"

    def run(self):
        """游戏主循环 (死循环)"""
        while True:
            # A. 全局事件处理 (监听鼠标和键盘)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                # 【交互测试】：如果玩家在欢迎界面点击了鼠标，我们就触发场景跳转！
                if event.type == pygame.MOUSEBUTTONDOWN and self.current_state == "welcome":
                    print("➡️ 玩家点击了屏幕！触发状态切换：进入选关界面...")
                    self.current_state = "choice" 

            # B. 状态机路由分发 (根据当前状态，决定运行哪个场景的代码)
            if self.current_state == "welcome":
                self.welcome_scene.run()
                
            elif self.current_state == "choice":
                # TODO: 我们还没写选关界面，先弄个灰色的背景占位
                self.surface.fill((150, 150, 150))
                # 可以在这里写一行字，但为了代码简洁我们先留空

            # C. 统一刷新屏幕和控帧
            pygame.display.flip()
            self.clock.tick(40)