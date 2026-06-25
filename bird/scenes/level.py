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
    def __init__(self, surface, res_manager, level_id=1):
        self.surface = surface
        self.res_manager = res_manager
        self.level_id = level_id    # 🌟【补漏手术 2】：把传进来的关卡号存进肚子里
        
        # ... (中间那些 mouse_pressed, standby_bird 等代码保持原样) ...
        
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
            # 🌟【补漏手术 3】：把写死的 level-1.tmx 改成动态拼接的 f-string！
            tmx_path = f"./resources/level/level-{self.level_id}.tmx"
            self.level_manager = LevelManager(tmx_path)
            self.obstacles = self.level_manager.build_level(self.space, self.surface)
        except Exception as e:
            print(f"❌ 读取地图 {self.level_id} 失败！错误信息：{e}")
        # 【全盘替换】：把原来 44、45 行的野代码删光，全场唯此一句仲裁注册！
        self.space.on_collision(1, 2, begin=self.bird_hit_pig_handler)
        # 1号(鸟) vs 2号(猪)：首帧接触即死 (begin)
        self.space.on_collision(1, 2, begin=self.bird_hit_pig_handler)

        # 1号(鸟) vs 3号(木头)：力学求解完毕后，按力道扣血 (post_solve)
        self.space.on_collision(1, 3, post_solve=self.bird_hit_wood_handler)
        # =========================================================
        # 【新增：游戏状态机与 UI 基建】
        # =========================================================
        # =========================================================
        # 【修改：换上 Pygame 内置防弹字体，彻底绕过 Windows 注册表崩溃】
        # =========================================================
        self.game_state = "PLAYING" 
        
        pygame.font.init()
        # 放弃 SysFont，使用自带的纯英文免扫描字体 (None)
        self.ui_font = pygame.font.Font(None, 60)       # 标题大字
        self.ui_font_small = pygame.font.Font(None, 36) # 按钮小字
        
        # 按钮位置保持不变
        screen_w, screen_h = self.surface.get_width(), self.surface.get_height()
        self.btn_left = pygame.Rect(screen_w // 2 - 160, screen_h // 2 + 30, 140, 50)
        self.btn_right = pygame.Rect(screen_w // 2 + 20, screen_h // 2 + 30, 140, 50)
        # 预设两个按钮的隐形点击区域 (Rect)
        # ... (保持原样)
        self.btn_right = pygame.Rect(screen_w // 2 + 20, screen_h // 2 + 30, 140, 50)
        
        # 【新增】：专门用来向大管家发报的“信号枪”
        self.scene_signal = None
        self.btn_left = pygame.Rect(screen_w // 2 - 160, screen_h // 2 + 30, 140, 50)
        self.btn_right = pygame.Rect(screen_w // 2 + 20, screen_h // 2 + 30, 140, 50)
        self.scene_signal = None 

        # =========================================================
        # 【新增：计分系统基建】
        # =========================================================
        self.score = 0
        self.font_score = pygame.font.Font(None, 48) # 右上角大号计分板字体
        
    def handle_event(self, event):
        """接管玩家鼠标操作"""
        if self.game_state != "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_left.collidepoint(event.pos):
                    if self.game_state == "VICTORY":
                        self.scene_signal = "NEXT_LEVEL"  # 挂载：下一关信号！
                    else:
                        self.scene_signal = "RESTART"     # 挂载：重开信号！
                
                elif self.btn_right.collidepoint(event.pos):
                    self.scene_signal = "MENU"            # 挂载：退回大厅信号！
            return 
            
                
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
        # =========================================================
        # 🌟【新增：清屏与铺设专属战斗背景】
        # 必须放在 run 的第一行，用来盖住大厅残留的画面！
        # =========================================================
        # 假设你在资源管家 (resource_manager.py) 里加载了一张战斗背景，叫 'battle_bg'
        # 如果你没有切出单独的战斗背景图，这里就会兜底变成清爽的物理引擎天蓝色！
        bg = self.res_manager.get_image('battle_bg') 
        if bg:
            # 尝试添加偏移量：比如 X 向左移 50 像素，Y 向上移 20 像素
            # 如果此时弹弓位置没动，这就会让背景图“向后退”，从而视觉上拉近弹弓与地面的距离
            self.surface.blit(bg, (0, 10)) 
        else:
            self.surface.fill((135, 206, 235))
        
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

        # 4. 如果正在拖拽，画出两根皮筋分别连在鸟的身上
        if self.mouse_pressed and self.standby_bird:
            pygame.draw.line(self.surface, (48, 22, 8), (self.sling_x - 16, self.sling_y - 10), 
                             (self.standby_bird.pos_x, self.standby_bird.pos_y), 4)
            pygame.draw.line(self.surface, (48, 22, 8), (self.sling_x + 5, self.sling_y - 10), 
                             (self.standby_bird.pos_x, self.standby_bird.pos_y), 4)

            # =========================================================
            # 🌟【新增】：雷达级抛物线预测系统 (Trajectory Prediction)
            # =========================================================
            # 根据刚才拖拽的向量，逆推出发射初始速度 (冲量500 / 鸟质量40 = 12.5)
            vx = (self.sling_x - self.standby_bird.pos_x) * 12.5
            vy = (self.sling_y - self.standby_bird.pos_y) * 12.5
            
            # 向前推演 8 个时间点的位置，画出虚线圆点
            for i in range(1, 9):
                time_step = i * 0.08  # 每个点间隔 0.08 秒
                # 运动学方程：X = v*t, Y = v*t + 0.5*g*t^2 (重力700)
                pred_x = self.sling_x + vx * time_step
                pred_y = self.sling_y + vy * time_step + 0.5 * 700 * (time_step ** 2)
                
                # 点越远，半径越小，颜色越透明（产生渐隐效果）
                radius = max(1, 6 - i)
                pygame.draw.circle(self.surface, (255, 255, 255), (int(pred_x), int(pred_y)), radius)
            
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
           # =====================================================
        # 3. 终极胜负审判庭 (带状态锁)
        # =====================================================
        # 只有在“游玩中”状态，才进行胜负评判，防止控制台无限刷屏！
        if self.game_state == "PLAYING":
            alive_pigs = [obs for obs in self.obstacles if "pig" in obs.name.lower() and not obs.is_dead]
            
            # 【胜利条件】
            if len(alive_pigs) == 0:
                self.game_state = "VICTORY"
                # 【新增】：结账时，弹匣里每省下一只鸟，加 10000 分！
                bonus = len(self.bird_queue) * 10000
                self.score += bonus
                print(f"🏆 状态切换：VICTORY！节省弹药 {len(self.bird_queue)}发，奖励 +{bonus}")
                
            # 【失败条件】
            elif len(self.bird_queue) == 0 and (self.standby_bird is None) and len(self.birds) == 0:
                is_world_sleeping = True
                for obs in self.obstacles:
                    if ("box" in obs.name.lower() or "wood" in obs.name.lower()) and not obs.is_dead:
                        if obs.body.velocity.length > 5.0:
                            is_world_sleeping = False
                            break
                if is_world_sleeping:
                    self.game_state = "DEFEAT" # 啪！锁死状态！
                    print("💀 状态切换：DEFEAT！")
        
                    # =====================================================
        # 【新增】：在屏幕右上角绘制实时 HUD 计分板
        # =====================================================
        if self.game_state == "PLAYING":
            score_text = self.font_score.render(f"SCORE: {int(self.score)}", True, (255, 255, 255))
            # 画一个带一点黑色阴影的分数，看起来更立体
            shadow_text = self.font_score.render(f"SCORE: {int(self.score)}", True, (0, 0, 0))
            self.surface.blit(shadow_text, (self.surface.get_width() - 248, 22))
            self.surface.blit(score_text, (self.surface.get_width() - 250, 20))

        # =====================================================
        # 4. 后台重力坍塌与 UI 渲染
        # =====================================================
        # 注意：这里我们故意没有 return，也没有停止 space.step()，
        # 所以堡垒依然会在 UI 背后继续倒塌！
        if self.game_state != "PLAYING":
            self.draw_settlement_ui()
        
    def bird_hit_pig_handler(self, arbiter, space, data):
        """Pymunk 7.x 碰撞首帧回调：小猪湮灭"""
        bird_shape, pig_shape = arbiter.shapes
        pig_instance = pig_shape.entity  # 拿到小猪的 Python 实例
        
        # 宣判阵亡！
        pig_instance.is_dead = True
        print(f"💥 爆头！小猪 [{pig_instance.name}] 被宣判阵亡！")
        pig_instance.is_dead = True
        self.score += 5000  # 【新增】：爆头一只猪，重赏 5000 分！
        print(f"💥 爆头！小猪 [{pig_instance.name}] 阵亡！得分 +5000")

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
                self.score += 500   # 【新增】：彻底粉碎一块木头，赏 500 分！
                print(f"💨 轰隆！木头 [{wood_instance.name}] 化为碎片！得分 +500")

    def draw_settlement_ui(self):
        """绘制带有半透明毛玻璃质感的结算面板 (国际化街机版)"""
        screen_w, screen_h = self.surface.get_width(), self.surface.get_height()
        
        # 1. 盖一层半透明黑色遮罩
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.surface.blit(overlay, (0, 0))
        
        # 2. 绘制标题 (STAGE CLEAR / MISSION FAILED)
        title_text = "STAGE CLEAR!" if self.game_state == "VICTORY" else "MISSION FAILED"
        title_color = (255, 215, 0) if self.game_state == "VICTORY" else (200, 200, 200)
        title_render = self.ui_font.render(title_text, True, title_color)
        self.surface.blit(title_render, (screen_w//2 - title_render.get_width()//2, screen_h//2 - 80))
        
        # 3. 绘制左侧按钮 (NEXT LEVEL / RESTART)
        pygame.draw.rect(self.surface, (70, 130, 180), self.btn_left, border_radius=10)
        left_str = "NEXT" if self.game_state == "VICTORY" else "RETRY"
        left_render = self.ui_font_small.render(left_str, True, (255, 255, 255))
        self.surface.blit(left_render, (self.btn_left.centerx - left_render.get_width()//2, self.btn_left.centery - left_render.get_height()//2))

        # 4. 绘制右侧按钮 (MENU)
        pygame.draw.rect(self.surface, (180, 70, 70), self.btn_right, border_radius=10)
        right_render = self.ui_font_small.render("MENU", True, (255, 255, 255))
        self.surface.blit(right_render, (self.btn_right.centerx - right_render.get_width()//2, self.btn_right.centery - right_render.get_height()//2))


    def handle_event(self, event):
        """接管玩家鼠标操作"""
        # 如果游戏结束了，拦截物理拖拽，只允许点击 UI 按钮！
        if self.game_state != "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                if self.btn_left.collidepoint(event.pos):
                    # 【核心修改】：把原来的 print 删掉！换成发射真实的信号！
                    if self.game_state == "VICTORY":
                        self.scene_signal = "NEXT_LEVEL"  # 挂载：下一关信号！
                    else:
                        self.scene_signal = "RESTART"     # 挂载：重开信号！
                
                elif self.btn_right.collidepoint(event.pos):
                    # 【核心修改】：把原来的 print 删掉！换成发射真实的信号！
                    self.scene_signal = "MENU"            # 挂载：退回大厅信号！
            
            return # 游戏结束时，代码执行到这里就强制退出，底下不执行！
            
        # --- 下面是你原本写好的拉弹弓逻辑（必须原样保留！） ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.standby_bird:
                mouse_x, mouse_y = event.pos
                if math.hypot(mouse_x - self.standby_bird.pos_x, mouse_y - self.standby_bird.pos_y) < 30:
                    self.mouse_pressed = True
                    
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mouse_pressed:
                self.mouse_pressed = False
                self.shoot_bird()
        
        