import pygame

class ResourceManager:
    """全局资源管理器：负责一次性加载和分发所有图片、音频和物理参数配置"""
    
    def __init__(self):
        # 存储不同资源的字典 (仓库)
        self.images = {}
        self.birds_info = {}
        
    def load_all(self):
        """游戏启动时调用此方法，一次性加载所有需要的资源进内存"""
        print("====== 开始加载全局资源 ======")
        # 1. 加载通用背景
        try:
            self.images['welcome_bg'] = pygame.image.load("./resources/welcome.png").convert()
        except FileNotFoundError:
            print("⚠️ 警告：找不到背景图片")
            self.images['welcome_bg'] = pygame.Surface((658, 370))
            self.images['welcome_bg'].fill((135, 206, 235))
            
        # 2. 加载小鸟数据与切图
        self._load_birds()
        print("====== 全局资源加载完毕 ======")

    def _load_birds(self):
        """内部方法：专门负责加载和切割小鸟"""
        try:
            bird_sheet = pygame.image.load("./resources/angry_birds.png").convert_alpha()
        except FileNotFoundError:
            print("⚠️ 警告：找不到小鸟精灵图")
            return

        # 切割红鸟动画帧 (使用我们之前算好的安全坐标)
        red_bird_images = []
        x, y, w, h = 90, 15, 36, 35
        for i in range(5):
            # 安全检查：防止切出界
            if x + w <= bird_sheet.get_width() and y + h <= bird_sheet.get_height():
                red_bird_images.append(bird_sheet.subsurface((x, y, w, h)))
            x += w
        
        # 如果切图失败保底
        if not red_bird_images:
            red_bird_images.append(bird_sheet)

        # 核心：把红鸟的【物理属性】和【动画图片】打包存进字典
        self.birds_info['redBird'] = {
            'name': 'redBird',
            'shape_name': 'circle',
            'radius': 17,       # 碰撞半径
            'mass': 40,         # 质量
            'elasticity': 0.95, # 弹性 (反弹系数)
            'friction': 1.0,    # 摩擦力
            'collision_type': 0,# 碰撞类别标号：0代表小鸟
            'images': red_bird_images
        }

    def get_bird_info(self, name):
        """对外接口：别的类需要小鸟数据时，直接调用这个方法拿"""
        return self.birds_info.get(name)
        
    def get_image(self, name):
        """对外接口：获取单张图片资源"""
        return self.images.get(name)