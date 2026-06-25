import pygame
import sys
import json  # 【新增】：用于读写本地存档
import os    # 【新增】：用于检查存档文件是否存在
from core.resource_manager import ResourceManager
from scenes.welcome import WelcomeScene
from scenes.choice import ChoiceScene
from scenes.level import LevelScene

class GameManager:
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()
        
        # 1. 启动管家加载资源
        self.res_manager = ResourceManager()
        self.res_manager.load_all()
        
        # =========================================================
        # 🌟【新增：本地存档系统 (Save System)】
        # =========================================================
        self.save_file = "save_data.json"
        self.unlocked_level = self.load_progress() # 读取硬盘，看看解锁到了第几关
        self.current_level_id = 1                  # 玩家当前正在玩的关卡编号
        
        # 2. 初始化所有场景 (把解锁进度传给选关大厅)
        self.welcome_scene = WelcomeScene(self.surface, self.res_manager)
        self.choice_scene = ChoiceScene(self.surface, self.res_manager)
        self.choice_scene.unlocked_max = self.unlocked_level # 告诉大厅该给哪些关卡上锁！
        
        self.level_scene = None # 初始不加载战场，省内存
        self.current_state = "welcome"

    def load_progress(self):
        """读取硬盘存档"""
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("unlocked_level", 1)
        return 1 # 没存档，默认只解锁第 1 关

    def save_progress(self, level_num):
        """写入硬盘存档"""
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump({"unlocked_level": level_num}, f)
        print(f"💾 进度已保存：当前解锁至第 {level_num} 关！")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and self.current_state == "welcome":
                    self.current_state = "choice" 
                    continue 
                    
                if self.current_state == "choice":
                    action = self.choice_scene.handle_event(event)
                    if action and action.startswith("level_"):
                        target_lvl = int(action.split("_")[1])
                        # 【安全锁】：如果点击的关卡被锁着，直接拦截！
                        if target_lvl <= self.unlocked_level:
                            self.current_level_id = target_lvl
                            # 传入关卡号，动态生成战场！
                            self.level_scene = LevelScene(self.surface, self.res_manager, self.current_level_id)
                            self.current_state = "level"
                        else:
                            print(f"🔒 第 {target_lvl} 关未解锁，请先通关前面的关卡！")
                    continue
                    
                if self.current_state == "level":
                    self.level_scene.handle_event(event)

            # =========================================================
            # 🌟【跨部门信号监听与动态升级】
            # =========================================================
            if self.current_state == "level" and getattr(self.level_scene, 'scene_signal', None):
                signal = self.level_scene.scene_signal
                
                if signal == "NEXT_LEVEL":
                    # 通关啦！判断要不要解锁新关卡
                    next_lvl = self.current_level_id + 1
                    if next_lvl > self.unlocked_level:
                        self.unlocked_level = next_lvl
                        self.save_progress(self.unlocked_level) # 写入硬盘！
                        self.choice_scene.unlocked_max = self.unlocked_level # 同步给大厅UI
                        
                    # 动态加载下一关的 TMX
                    self.current_level_id = next_lvl
                    self.level_scene = LevelScene(self.surface, self.res_manager, self.current_level_id)
                    
                elif signal == "RESTART":
                    self.level_scene = LevelScene(self.surface, self.res_manager, self.current_level_id)
                    
                elif signal == "MENU":
                    self.current_state = "choice"

            # 状态机路由分发
            if self.current_state == "welcome":
                self.welcome_scene.run()
            elif self.current_state == "choice":
                self.choice_scene.run()
            elif self.current_state == "level":
                self.level_scene.run()

            pygame.display.flip()
            self.clock.tick(40)