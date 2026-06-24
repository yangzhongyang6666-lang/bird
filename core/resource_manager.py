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
            
        # 2. 依次命令管家去干活
        self._load_birds()
        self._load_slings()
        self._load_levels()
        print("====== 全局资源加载完毕 ======")

    def _load_birds(self):
        """内部方法：专门负责加载和切割小鸟"""
        try:
            bird_sheet = pygame.image.load("./resources/angry_birds.png").convert_alpha()
        except FileNotFoundError:
            print("⚠️ 警告：找不到小鸟精灵图")
            return

        red_bird_images = []
        x, y, w, h = 90, 15, 36, 35
        for i in range(5):
            if x + w <= bird_sheet.get_width() and y + h <= bird_sheet.get_height():
                red_bird_images.append(bird_sheet.subsurface((x, y, w, h)))
            x += w
        
        if not red_bird_images:
            red_bird_images.append(bird_sheet)

        self.birds_info['redBird'] = {
            'name': 'redBird',
            'shape_name': 'circle',
            'radius': 17,       
            'mass': 40,         
            'elasticity': 0.95, 
            'friction': 1.0,    
            'collision_type': 1,
            'images': red_bird_images
        }

    def _load_slings(self):
        """内部方法：切割并加载弹弓的左右两半"""
        try:
            sling_image = pygame.image.load("./resources/sling1.png").convert_alpha()
            left = sling_image.subsurface((13, 1, 49, 135))
            right = sling_image.subsurface((97, 1, 44, 210))
            
            self.images['sling_left'] = pygame.transform.scale(left, (24, 67))
            self.images['sling_right'] = pygame.transform.scale(right, (22, 105))
        except FileNotFoundError:
            print("⚠️ 警告：找不到弹弓图片 sling1.png")
            self.images['sling_left'] = None
            self.images['sling_right'] = None

    def _load_levels(self):
        """内部方法：用循环自动切割全部 12 个选关图标"""
        try:
            num_image = pygame.image.load("./resources/number.png").convert_alpha()
            
            # 自动计算：原图被均分为了 4行 3列
            cell_w = num_image.get_width() // 3
            cell_h = num_image.get_height() // 4
            
            level_num = 1
            for row in range(4):
                for col in range(3):
                    icon = num_image.subsurface((col * cell_w, row * cell_h, cell_w, cell_h))
                    self.images[f'level_{level_num}_icon'] = pygame.transform.smoothscale(icon, (60, 60))
                    level_num += 1
                    
        except FileNotFoundError:
            print("⚠️ 警告：找不到选关图片 number.png")

    def get_bird_info(self, name):
        """对外接口：别的类需要小鸟数据时，直接调用这个方法拿"""
        return self.birds_info.get(name)
        
    def get_image(self, name):
        """对外接口：获取单张图片资源"""
        return self.images.get(name)