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
            
    def handle_event(self, event):
        """处理全屏 12 个按钮的点击事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for btn in self.level_buttons:
                if btn['rect'].collidepoint(mouse_pos):
                    level = btn['level']
                    if level == 1:
                        print("✅ 玩家选择了 关卡 1！")
                        return "level_1" 
                    elif level == 2:
                        print("🚧 玩家点击了 关卡 2 (目前还在施工中...)")
                        return "level_2"
                    else:
                        print(f"🔒 关卡 {level} 尚未解锁，敬请期待！")
                        return None # 点击未解锁关卡，不触发状态切换
        return None

    def run(self):
        """绘制炫酷的 12 宫格界面"""
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
            
            # 🎨 修复透明度问题：用一个带 SRCALPHA 的专属遮罩层来画半透明圆
            if level > 2:
                # 创建一块和图标一样大的透明玻璃
                lock_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                # 在这块玻璃的中心，画一个半透明的黑圈 (180是透明度)
                pygame.draw.circle(lock_surface, (0, 0, 0, 180), (rect.width // 2, rect.height // 2), rect.width // 2)
                # 把玻璃贴到屏幕对应的图标位置上
                self.surface.blit(lock_surface, rect.topleft)