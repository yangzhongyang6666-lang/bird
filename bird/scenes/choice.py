import pygame

class ChoiceScene:
    """全 12 关展示大厅"""
    def __init__(self, surface, res_manager):
        self.surface = surface
        self.res_manager = res_manager
        
        self.level_buttons = []
        
        # 布局参数：将 12 个球排成 2 行 6 列
        start_x = 60   # 最左侧起点的 X 坐标
        start_y = 100  # 第一行的 Y 坐标
        x_gap = 90     # 水平间距
        y_gap = 100    # 垂直间距
        
        for i in range(1, 13):
            # 计算当前关卡应该在第几行、第几列 (0-indexed)
            row = (i - 1) // 6
            col = (i - 1) % 6
            
            x = start_x + col * x_gap
            y = start_y + row * y_gap
            
            # 为每个关卡创建一个 60x60 的碰撞检测框
            rect = pygame.Rect(x, y, 60, 60)
            self.level_buttons.append({
                'level': i,
                'rect': rect
            })
            # 【新增】：最大解锁关卡权限（默认是1，GameManager 启动时会用存档覆盖它）
        self.unlocked_max = 1
            
    def handle_event(self, event):
        """【升级版】：智能权限校验点击事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for btn in self.level_buttons:
                if btn['rect'].collidepoint(mouse_pos):
                    level = btn['level']
                    
                    # 🌟 核心闸机：不管点第几关，统一向最高权限 unlocked_max 请示！
                    if level <= self.unlocked_max:
                        print(f"✅ 玩家成功进入 关卡 {level}！")
                        return f"level_{level}" 
                    else:
                        print(f"🔒 关卡 {level} 尚未解锁，请先通关前置关卡！")
                        return None 
        return None

    def run(self):
        """【升级版】：智能渲染 12 宫格界面与动态枷锁"""
        # 1. 画大背景
        bg = self.res_manager.get_image('welcome_bg')
        if bg:
            self.surface.blit(bg, (0, 0))
        
        # 2. 画提亮遮罩
        overlay = pygame.Surface((self.surface.get_width(), self.surface.get_height()), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 80)) 
        self.surface.blit(overlay, (0, 0))
        
        # 3. 遍历渲染 12 个关卡球
        for btn in self.level_buttons:
            level = btn['level']
            rect = btn['rect']
            icon = self.res_manager.get_image(f'level_{level}_icon')
            
            if icon:
                self.surface.blit(icon, rect)
            
            # =========================================================
            # 🌟【动态视觉枷锁】：一切听从 unlocked_max 的调遣！
            # =========================================================
            if level > self.unlocked_max:
                # 创世玻璃：创建一个和碰撞框一样大的透明图层
                lock_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                
                # 画上你最爱的半透明黑色圆圈遮罩 (180透明度)
                pygame.draw.circle(lock_surface, (0, 0, 0, 180), (rect.width // 2, rect.height // 2), rect.width // 2)
                self.surface.blit(lock_surface, rect.topleft)
                
                # 贴上极其带感的纯英文封条 "LOCK"
                pygame.font.init()
                lock_font = pygame.font.Font(None, 24) # 字号24刚好能塞进你的 60x60 球里
                lock_text = lock_font.render("LOCK", True, (200, 200, 200))
                self.surface.blit(lock_text, (rect.centerx - lock_text.get_width()//2, rect.centery - lock_text.get_height()//2))