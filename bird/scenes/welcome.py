import pygame
import math

class WelcomeScene:
    """极其华丽的商业级欢迎大厅"""
    def __init__(self, surface, res_manager):
        self.surface = surface
        self.res_manager = res_manager
        
        # 【核心引擎】：引入时间轴（帧计数器），用于驱动所有的呼吸与浮动动画！
        self.frame_count = 0 
        
        pygame.font.init()
        self.font_prompt = pygame.font.Font(None, 40)
        self.font_title_fallback = pygame.font.Font(None, 90) # Logo图片的兜底文字

    def run(self):
        self.frame_count += 1
        screen_w, screen_h = self.surface.get_width(), self.surface.get_height()
        
        # 1. 画大背景
        bg = self.res_manager.get_image('welcome_bg')
        if bg:
            self.surface.blit(bg, (0, 0))
        else:
            self.surface.fill((135, 206, 235)) 
            
        # =========================================================
        # 🌟 2. 呼吸般上下浮动的游戏大 Logo
        # =========================================================
        # 检查你的 resources 文件夹下有没有 angry_birds.png 这个标题图
        logo = self.res_manager.get_image('angry_birds') 
        
        # 【数学魔法】：利用高中数学的正弦波 (math.sin) 制造平滑的上下浮动效果 
        # 振幅 15 像素，周期按帧数除以 15
        float_offset_y = math.sin(self.frame_count / 15.0) * 15 
        
        if logo:
            logo_x = screen_w // 2 - logo.get_width() // 2
            logo_y = 60 + float_offset_y
            self.surface.blit(logo, (logo_x, logo_y))
        else:
            # 如果没读取到图片，就用霸气的纯英文文字代替，加上黑色厚重阴影
            title_text = self.font_title_fallback.render("ANGRY BIRDS", True, (255, 215, 0))
            shadow = self.font_title_fallback.render("ANGRY BIRDS", True, (0, 0, 0))
            self.surface.blit(shadow, (screen_w//2 - title_text.get_width()//2 + 4, 104 + float_offset_y))
            self.surface.blit(title_text, (screen_w//2 - title_text.get_width()//2, 100 + float_offset_y))

        # =========================================================
        # 🌟 3. 地面演员微表演 (对峙画面)
        # =========================================================
        bird_img = self.res_manager.get_image('red-bird')
        pig_img = self.res_manager.get_image('pig')
        
        if bird_img and pig_img:
            # 让红鸟在左边原地暴躁地跳跃 (取绝对值 abs 保证只往天上蹦)
            bird_bounce = abs(math.sin(self.frame_count / 8.0)) * 30
            self.surface.blit(bird_img, (150, screen_h - 130 - bird_bounce))
            
            # 让绿皮猪在右边安静地待命
            self.surface.blit(pig_img, (screen_w - 200, screen_h - 110))

        # =========================================================
        # 🌟 4. 街机精髓：Alpha 渐变闪烁的提示语
        # =========================================================
        # 让透明度在 100 到 255 之间平滑渐变
        alpha = int(175 + 80 * math.sin(self.frame_count / 10.0))
        prompt_text = self.font_prompt.render("- CLICK ANYWHERE TO START -", True, (255, 255, 255))
        
        # Pygame 的纯文本不支持直接调透明度，需要盖在一个带 SRCALPHA 的图层上
        alpha_surface = pygame.Surface(prompt_text.get_size(), pygame.SRCALPHA)
        alpha_surface.blit(prompt_text, (0, 0))
        alpha_surface.set_alpha(alpha) # 注入灵魂闪烁！
        
        self.surface.blit(alpha_surface, (screen_w // 2 - prompt_text.get_width() // 2, screen_h - 80))