import pygame
import math
import pymunk as pm
from pymunk import Vec2d
from utils.pm_utils import to_pymunk
# 导入两种鸟
from entities.bird import PhysicsBird, StandbyBird
from core.level_manager import LevelManager
from collections import deque

class LevelScene:
    """真正的游戏战斗关卡"""
    def __init__(self, surface, res_manager):
        self.surface = surface
        self.res_manager = res_manager
        
        self.space = pm.Space()
        self.space.gravity = (0.0, -700.0)
        
        x, y = to_pymunk(self.surface.get_width(), self.surface.get_height(), self.surface)
        static_body = self.space.static_body
        ground_line = pm.Segment(static_body, (0.0, y), (x, y), 0.0)
        ground_line.elasticity = 0.95
        ground_line.friction = 1.0
        self.space.add(ground_line)
        
        # 弹弓的锚点坐标
        self.sling_x, self.sling_y = 150, 250
        self.max_drag_radius = 60 # 弹弓最大拉力半径
        
        self.mouse_pressed = False
        self.birds = [] 
        # =========================================================
        # 【全盘重构弹药库】：用双端队列发配 3 发备用弹药！
        # =========================================================
        # 稍后我们可以改成 [红鸟, 黄鸟, 黑鸟]，今天先用 3 只红鸟把供弹流水线跑通
        self.bird_queue = deque(['redBird', 'redBird', 'redBird']) 
        
        # 咔哒！亲手把弹匣里的第 1 发推上枪膛（弹弓）
        first_bird_name = self.bird_queue.popleft()
        info = self.res_manager.get_bird_info(first_bird_name)
        self.standby_bird = StandbyBird(info, self.sling_x, self.sling_y, self.surface)
        self.obstacles = [] # 存放建筑的列表
        try:
            self.level_manager = LevelManager("./resources/level/level-1.tmx")
            self.obstacles = self.level_manager.build_level(self.space, self.surface)
        except Exception as e:
            print(f"❌ 读取地图失败！错误信息：{e}")
        # 【全盘替换】：把原来 44、45 行的野代码删光，全场唯此一句仲裁注册！
        self.space.on_collision(1, 2, begin=self.bird_hit_pig_handler)
        # 1号(鸟) vs 2号(猪)：首帧接触即死 (begin)
        self.space.on_collision(1, 2, begin=self.bird_hit_pig_handler)

        # 1号(鸟) vs 3号(木头)：力学求解完毕后，按力道扣血 (post_solve)
        self.space.on_collision(1, 3, post_solve=self.bird_hit_wood_handler)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 【新增安全锁】：只有 standby_bird 活在树杈上时，才允许计算拖拽！
            if self.standby_bird:
                mouse_x, mouse_y = event.pos
                if math.hypot(mouse_x - self.standby_bird.pos_x, mouse_y - self.standby_bird.pos_y) < 30:
                    self.mouse_pressed = True
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mouse_pressed:
                self.mouse_pressed = False
                self.shoot_bird()
                
    def shoot_bird(self):
        # 【安全保险】：如果弹弓上根本没有待机鸟，扣动扳机无效！
        if not self.standby_bird:
            return
            
        pm_x, pm_y = to_pymunk(self.standby_bird.pos_x, self.standby_bird.pos_y, self.surface)
        pm_sling_x, pm_sling_y = to_pymunk(self.sling_x, self.sling_y, self.surface)
        impulse = Vec2d(pm_sling_x - pm_x, pm_sling_y - pm_y) * 500 
        
        red_info = self.res_manager.get_bird_info('redBird')
        new_bird = PhysicsBird(red_info, self.standby_bird.pos_x, self.standby_bird.pos_y, self.space, self.surface)
        new_bird.body.apply_impulse_at_local_point(impulse)
        self.birds.append(new_bird)
        
        # =========================================================
        # ！！！ 核心修改 ！！！ 射出后，将树杈上的待机鸟本体彻底气化！
        # 原来那两行 self.standby_bird.pos_x = ... 删掉！
        # =========================================================
        self.standby_bird = None
        
    def run(self):
        # 1. 铺背景
        bg = self.res_manager.get_image('welcome_bg') 
        self.surface.blit(bg, (0, 0))
        
        # 2. 计算拖拽位置并限制最大距离
        if self.mouse_pressed:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.sling_x
            dy = mouse_y - self.sling_y
            angle = math.atan2(dy, dx)
            # 勾股定理算距离，如果不超过最大半径就按真实的来，超了就截断
            dist = min(math.hypot(dx, dy), self.max_drag_radius) 
            
            self.standby_bird.pos_x = self.sling_x + dist * math.cos(angle)
            self.standby_bird.pos_y = self.sling_y + dist * math.sin(angle)
            
       # 3. 绘制立体弹弓和待机鸟
        sling_left = self.res_manager.get_image('sling_left')
        sling_right = self.res_manager.get_image('sling_right')
        
        if sling_left and sling_right:
            self.surface.blit(sling_right, (self.sling_x - 12, self.sling_y - 20))
            if self.standby_bird:   # <--- 必须加 if！
                self.standby_bird.run()
            self.surface.blit(sling_left, (self.sling_x - 28, self.sling_y - 20))
        else:
            if self.standby_bird:   # <--- 必须加 if！
                self.standby_bird.run()

        # 4. 画皮筋也要加安全锁
        if self.mouse_pressed and self.standby_bird:
            # 连着左边(前)树杈的皮筋
            pygame.draw.line(self.surface, (48, 22, 8), (self.sling_x - 16, self.sling_y - 10), 
                             (self.standby_bird.pos_x, self.standby_bird.pos_y), 4)
            # 连着右边(后)树杈的皮筋
            pygame.draw.line(self.surface, (48, 22, 8), (self.sling_x + 5, self.sling_y - 10), 
                             (self.standby_bird.pos_x, self.standby_bird.pos_y), 4)
            
        # 5. 让发射出去的鸟继续飞
        for bird in self.birds:
            bird.run()
        # 【新增】：让所有的猪和木头都显示出来！
        for obs in self.obstacles:
            obs.run()
            
        # 6. 物理引擎步进
        self.space.step(1.0 / 40.0)
        # 【新增收尸队】：物理演算彻底结束后，把盖了死亡戳的实体安全下葬
        for obs in list(self.obstacles):
            if obs.is_dead:
                self.space.remove(obs.body, obs.shape) # 从物理重力场除名
                self.obstacles.remove(obs)             # 从画面渲染列表剔除
                print(f"☠️ 战场已清理阵亡残骸：{obs.name}")
        # =====================================================
        # 1. 飞鸟收尸队：把躺在地上动能耗尽的鸟从重力场摘除
        # =====================================================
        for b in list(self.birds):
            if b.is_dead:
                self.space.remove(b.body, b.shape)
                self.birds.remove(b)
                print("🕊️ 飞鸟动能耗尽，化为天际的一颗流星。")

        # =====================================================
        # 2. 首席检控官认证·全场最帅的【自动上膛流水线】
        # 触发条件：天空干净了(birds==0) 且 树杈空了(standby==None)
        # =====================================================
        if len(self.birds) == 0 and (self.standby_bird is None):
            if len(self.bird_queue) > 0:
                next_bird_name = self.bird_queue.popleft()
                info = self.res_manager.get_bird_info(next_bird_name)
                self.standby_bird = StandbyBird(info, self.sling_x, self.sling_y, self.surface)
                print(f"🔄 咔哒！下一发弹药 [{next_bird_name}] 自动弹上树杈！弹匣剩余: {len(self.bird_queue)}")
            else:
                # 弹匣空了！明天我们就在这里接入“全场静止胜负判定”
                pass
        
    def bird_hit_pig_handler(self, arbiter, space, data):
        """Pymunk 7.x 碰撞首帧回调：小猪湮灭"""
        bird_shape, pig_shape = arbiter.shapes
        pig_instance = pig_shape.entity  # 拿到小猪的 Python 实例
        
        # 宣判阵亡！
        pig_instance.is_dead = True
        print(f"💥 爆头！小猪 [{pig_instance.name}] 被宣判阵亡！")

    def bird_hit_wood_handler(self, arbiter, space, data):
        """Pymunk 7.x 碰撞求解后回调：按冲量扣血"""
        # Pymunk 官方特性：注册 (1, 3) 监听时，shapes[0] 永远是1号鸟，shapes[1] 永远是3号木头！
        wood_instance = arbiter.shapes[1].entity
        
        if wood_instance.is_dead:
            return

        # 【核心物理算子】：提取两体碰撞瞬间，物理引擎为了弹开它们所施加的“冲量向量长度”
        impact_force = arbiter.total_impulse.length
        
        # 设定弹性过滤阈值（力道低于 150.0 视为刚体间正常的重力叠放挤压，忽略不计）
        if impact_force > 150.0:
            # 伤害计算公式：超出阈值的部分，按 35% 的比例转化为扣血量
            damage = (impact_force - 150.0) * 0.35
            wood_instance.hp -= damage
            
            print(f"🪓 咚！木头 [{wood_instance.name}] 遭受冲击({int(impact_force)}) 扣血 -{int(damage)}，剩余HP: {int(wood_instance.hp)}")
            
            # 血量归零，当场宣判报废！
            if wood_instance.hp <= 0:
                wood_instance.is_dead = True
                print(f"💨 轰隆！木头 [{wood_instance.name}] 结构崩溃，化为碎片！")     
        
        