import pygame as pg
import time
from src.scenes.scene import Scene
from src.utils import Logger
import src.core.managers.scene_manager as SM

ELEMENT_EFFECTIVENESS = {
    "Fire":   {"strong": "Grass", "weak": "Water"},
    "Water":  {"strong": "Fire",  "weak": "Grass"},
    "Grass":  {"strong": "Water", "weak": "Fire"},
    "Electric": {"strong": "Water", "weak": None},
    "Ice": {"strong": "Grass", "weak": "Fire"},
    "Ghost": {"strong": None, "weak": None}
}

class BattleScene(Scene):
    def __init__(self, scene_manager):
        super().__init__()
        self.scene_manager = scene_manager

        # =========================================================
# ===== Player（battle 開始時再初始化）=====
        self.player_name = ""
        self.player_element = ""
        self.max_hp = 100
        self.player_hp = 100
        self.player_attack = 30
        self.player_defense = 5


        # ===== Enemy（合法寫死）=====
        self.enemy_name = "Enemy"
        self.enemy_element = "Water"
        self.enemy_hp = 100
        self.enemy_attack = 28
        self.enemy_defense = 4
        # ===== 背景 =====
        self.background = pg.image.load("assets/images/backgrounds/background1.png").convert()
        screen_width = pg.display.get_surface().get_width()
        screen_height = pg.display.get_surface().get_height()
        self.background = pg.transform.scale(self.background, (screen_width, screen_height))

        # ===== 角色圖 =====
        self.player_img = pg.image.load("assets/images/menu_sprites/menusprite8.png").convert_alpha()
        self.player_img = pg.transform.scale(self.player_img, (200, 200))
        self.enemy_img = pg.image.load("assets/images/menu_sprites/menusprite2.png").convert_alpha()
        self.enemy_img = pg.transform.scale(self.enemy_img, (150, 150))

        # ===== 攻擊動畫圖片 =====
        self.player_attack_img = pg.image.load("assets/images/ingame_ui/ball.png").convert_alpha()
        self.player_attack_img = pg.transform.scale(self.player_attack_img, (30, 30))
        self.enemy_attack_img = pg.image.load("assets/images/UI/raw/UI_Flat_Handle05a.png").convert_alpha()
        self.enemy_attack_img = pg.transform.scale(self.enemy_attack_img, (30, 30))


        # ===== 回合控制 =====
        self.turn_count = 1
        self.action_queue = []          # 每回合的動作順序: ("player"/"enemy", "attack"/"run")
        self.current_action = None      # 目前正在進行的攻擊
        self.game_started = False
        self.game_over = False
        self.winner = None

        # ===== 按鈕 =====
        self.buttons = ["Attack", "Attack+Run Away","Heal Potion","Strength Potion","Defense Potion","Start"]
        self.button_widths = [150, 300, 150,150,150,150]
        self.button_heights = [50, 50, 50,50,50,50]
        self.button_pressed_index = None

        # ===== 攻擊動畫控制 =====
        self.attack_in_progress = False
        self.attack_from_player = True
        self.attack_pos = None
        self.attack_target_pos = None
        self.attack_speed = 500
        self.attack_delay_timer = 0.0
        
        self.damage_texts = []  # 每個元素: {"text": "-34", "pos": [x, y], "timer": 0.0}


        # ===== Run Away動畫控制 =====
        self.running_away = False
        self.run_pos_hidden = False
        self.run_start_pos = None
        self.run_target_pos = None

        # ===== Game Over 返回按鈕 =====
        self.back_image = pg.image.load("assets/images/UI/button_back.png").convert_alpha()
        self.back_hover = pg.image.load("assets/images/UI/button_back_hover.png").convert_alpha()
        self.back_rect = self.back_image.get_rect()

        # ===== 字型 =====
        self.font = pg.font.SysFont(None, 36)
        self.small_font = pg.font.SysFont(None, 20) 
        self.over_font = pg.font.SysFont(None, 60)
        self.turn_font = pg.font.SysFont(None, 28)

        # ===== 攻擊動畫圖片（根據屬性） =====
        self.attack_images = {
            "Electric": pg.image.load(
                r"C:\Users\angel\OneDrive\Desktop\NTHU-I2P-I-Final-Project-2025-main\NTHU-I2P-I-Final-Project-2025-main\assets\images\attack\attack7.png"
            ).convert_alpha()
        }
        self.attack_images["Electric"] = pg.transform.scale(self.attack_images["Electric"], (50, 50))

        # ===== 攻擊屬性背景圖片 =====
        self.attack_bg_images = {
        "Electric": pg.image.load("assets/images/attack/attack7.png").convert_alpha(),
        "Water": pg.image.load("assets/images/attack/attack3.png").convert_alpha()
}


        screen_width = pg.display.get_surface().get_width()
        screen_height = pg.display.get_surface().get_height()
        self.attack_bg_images["Electric"] = pg.transform.scale(self.attack_bg_images["Electric"], (screen_width, screen_height))
        # ===== 攻擊動畫圖片（根據屬性） =====
        self.attack_images = {
    "Electric": pg.image.load("assets/images/attack/attack7.png").convert_alpha(),
    "Water": pg.image.load("assets/images/attack/attack3.png").convert_alpha()
}

        self.attack_images["Electric"] = pg.transform.scale(self.attack_images["Electric"], (50, 50))
        self.attack_images["Water"] = pg.transform.scale(self.attack_images["Water"], (50, 50))
        self.items = {
            "Heal Potion": 2,
            "Strength Potion": 1,
            "Defense Potion": 1
        }

        # ===== 進化動畫 =====
        self.evolving = False           # 是否在進化動畫中
        self.evolve_start_pos = None    # 飛出動畫起始位置
        self.evolve_target_pos = None   # 飛出動畫目標位置
        self.evolve_img = None          # 飛出動畫的圖
        self.evolve_speed = 200         # 飛行速度
        
        # Potion 飛出動畫
        self.potion_animating = False
        self.potion_img = pg.image.load(r"C:\Users\angel\OneDrive\Desktop\NTHU-I2P-I-Final-Project-2025-main\NTHU-I2P-I-Final-Project-2025-main\assets\images\ingame_ui\potion.png").convert_alpha()
        self.potion_img = pg.transform.scale(self.potion_img, (160, 160))
        self.potion_pos = None
        self.potion_target_pos = None
        self.potion_speed = 300
        self.potion_type = None  # 記錄是哪個Potion


    def evolve_player(self):
        game_state = self.scene_manager.game_state
        player_mon = game_state["bag"]["monsters"][0]

        if player_mon.get("evolved", False):
            return  # 已經進化過就不再進化

        Logger.info("Pokemon evolved by potion!")

        # 改名字（可選，但很加分）
        player_mon["name"] = player_mon["name"] + " Evo"

        # 強化數值
        player_mon["max_hp"] += 40
        player_mon["hp"] = player_mon["max_hp"]
        player_mon["attack"] += 15
        player_mon["defense"] += 5

        # 標記進化
        player_mon["evolved"] = True

        # 換圖片（一定要）
        player_mon["image"] = "menusprite16.png"

        # 同步 battle 中的數值
        self.max_hp = player_mon["max_hp"]
        self.player_hp = player_mon["hp"]
        self.player_attack = player_mon["attack"]
        self.player_defense = player_mon["defense"]

        # 立刻換圖
        self.player_img = pg.image.load(
             r"C:\Users\angel\OneDrive\Desktop\NTHU-I2P-I-Final-Project-2025-main\NTHU-I2P-I-Final-Project-2025-main\assets\images\menu_sprites\menusprite16.png"
        ).convert_alpha()
        self.player_img = pg.transform.scale(self.player_img, (200, 200))

        self.evolving = False        # 是否在進化動畫中
        self.evolve_start_pos = None # 起始位置
        self.evolve_target_pos = None # 結束位置（飛出去）
        self.evolve_img = None       # 飛出來的圖
        self.evolve_speed = 200      # 飛行速度

 
    def use_item(self, item_name):
        if self.items.get(item_name, 0) <= 0:
            Logger.info(f"No {item_name} left")
            return

        self.items[item_name] -= 1

        if item_name == "Heal Potion":
            self.player_hp = min(self.max_hp, self.player_hp + 30)

        elif item_name == "Strength Potion":
            self.player_attack += 10

        elif item_name == "Defense Potion":
            self.player_defense += 5

        Logger.info(f"Used {item_name}")

        if item_name in ["Heal Potion", "Strength Potion", "Defense Potion"]:
            original_img = self.player_img   # 1️⃣ 先存原圖給飛出動畫
            self.evolve_player()  # 進化，這裡已經換成進化後圖
            self.potion_animating = True
            screen_width, screen_height = pg.display.get_surface().get_size()
            self.potion_pos = [screen_width // 4, screen_height // 2 - 120]  # 角色頭上
            self.potion_target_pos = [self.potion_pos[0], self.potion_pos[1] + 50]  # 飛到角色上方傾倒
            self.potion_type = item_name
            
            # 設置飛出動畫
            self.evolving = True
            screen_width, screen_height = pg.display.get_surface().get_size()
            self.evolve_start_pos = [screen_width // 4 - 75, screen_height // 2 - 75]
            self.evolve_target_pos = [screen_width // 2, -200]  # 往上飛出畫面
            self.evolve_img = original_img  # 使用進化前圖

    def enter(self):
        Logger.info("Entered Battle Scene")

        game_state = self.scene_manager.game_state
        player_mon = game_state["bag"]["monsters"][0]   # 永遠用第一隻

        self.player_name = player_mon["name"]
        self.player_element = player_mon["element"]
        self.max_hp = player_mon["max_hp"]
        self.player_hp = player_mon["hp"]

        self.player_attack = player_mon.get("attack", 30)
        self.player_defense = player_mon.get("defense", 5)


    def exit(self):
        Logger.info("Exiting Battle Scene")

    def calculate_damage(self, attacker):
        if attacker == "player":
            atk = self.player_attack
            atk_ele = self.player_element
            def_ele = self.enemy_element
            defense = self.enemy_defense
        else:
            atk = self.enemy_attack
            atk_ele = self.enemy_element
            def_ele = self.player_element
            defense = self.player_defense

        damage = atk
        effect = ELEMENT_EFFECTIVENESS.get(atk_ele, {})

        if effect.get("strong") == def_ele:
            damage *= 1.5
        elif effect.get("weak") == def_ele:
            damage *= 0.7

        return max(1, int(damage - defense))
    # ============================================================
    # ================= 玩家按鈕操作 ===========================
    # ============================================================
    def handle_event(self, event):
        if self.game_over:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_rect.collidepoint(event.pos):
                    self.scene_manager.force_change_scene("game")
            return

        if self.attack_in_progress:
            return

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            screen_width, screen_height = pg.display.get_surface().get_size()
            num_buttons = len(self.buttons)
            spacing = 50
            start_x = (screen_width - (sum(self.button_widths) + spacing * (num_buttons - 1))) // 2
            button_y = screen_height - 80

            for i, btn in enumerate(self.buttons):
                btn_rect = pg.Rect(start_x + sum(self.button_widths[:i]) + spacing * i,
                                   button_y,
                                   self.button_widths[i],
                                   self.button_heights[i])
                if btn_rect.collidepoint(mx, my):
                    self.button_pressed_index = i
                    if btn == "Start":
                        self.game_started = True
                        Logger.info("Battle Started")
                    elif self.game_started and not self.game_over:
                        if btn in ["Heal Potion", "Strength Potion", "Defense Potion"]:
                            self.use_item(btn)
                            return
                        if self.turn_count % 2 == 1:  # 奇數輪: player先攻
                            if btn == "Attack":
                                self.action_queue = [("player", "attack"), ("enemy", "attack")]
                            elif btn == "Attack+Run Away":
                                self.action_queue = [("player", "run"), ("enemy", "attack")]
                        else:  # 偶數輪: enemy先攻
                            if btn == "Attack":
                                self.action_queue = [("enemy", "attack"), ("player", "attack")]
                            elif btn == "Attack+Run Away":
                                # 先標記玩家閃避
                                self.running_away = True
                                self.run_pos_hidden = False
                                self.run_start_pos = None
                                self.run_target_pos = None
                                self.action_queue = [("enemy", "attack"), ("player", "run")]
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.button_pressed_index = None

    # ================= 攻擊動畫啟動 ============================
    # ============================================================
    def start_action(self, actor, action_type):
        screen_width, screen_height = pg.display.get_surface().get_size()
        player_pos = (screen_width // 4, screen_height // 2)
        enemy_pos = (screen_width * 3 // 4, screen_height // 2)

        if action_type == "attack":
            self.attack_in_progress = True
            self.attack_from_player = (actor == "player")
            self.attack_pos = list(player_pos if actor == "player" else enemy_pos)
            self.attack_target_pos = enemy_pos if actor == "player" else player_pos
            self.attack_delay_timer = 0.0
        elif action_type == "run":
            self.attack_in_progress = True
            self.attack_from_player = True
            self.attack_pos = list(player_pos)
            self.attack_target_pos = enemy_pos
            self.attack_delay_timer = 0.0

            # 動畫起點
            if self.run_start_pos is None:
                self.run_start_pos = list(player_pos)
            self.run_target_pos = [self.run_start_pos[0], self.run_start_pos[1] - 180]
            self.running_away = True
            self.run_pos_hidden = False
        # 根據屬性選擇動畫
        if actor == "player":
            ele = self.player_element
        else:
            ele = self.enemy_element
        self.current_attack_img = self.attack_images.get(ele, self.player_attack_img)
    # ============================================================
    # ========================== Update ==========================
    # ============================================================
    def update(self, dt: float):
        if not self.game_started or self.game_over:
            return

        screen_width, screen_height = pg.display.get_surface().get_size()
        player_pos = (screen_width // 4, screen_height // 2)
        enemy_pos = (screen_width * 3 // 4, screen_height // 2)

        if not self.current_action and self.action_queue:
            self.current_action = self.action_queue.pop(0)
            self.start_action(*self.current_action)

        # ===== 攻擊動畫 =====
        if self.attack_in_progress and self.attack_pos:
            self.attack_delay_timer += dt
            if self.attack_delay_timer < 1.0:
                return

            pos = self.attack_pos
            target = self.attack_target_pos
            dx = target[0] - pos[0]
            dy = target[1] - pos[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < self.attack_speed * dt:
                if self.attack_from_player:
                    damage = self.calculate_damage("player")
                    self.enemy_hp = max(0, self.enemy_hp - damage)
                    # 加入浮動文字
                    self.damage_texts.append({
                        "text": f"-{damage}",
                        "pos": [self.attack_target_pos[0], self.attack_target_pos[1] - 50],
                        "timer": 0.0
                    })
                else:
                    player_dodged = self.running_away and not self.run_pos_hidden
                    if not player_dodged:
                        damage = self.calculate_damage("enemy")
                        self.player_hp = max(0, self.player_hp - damage)
                        self.damage_texts.append({
                            "text": f"-{damage}",
                            "pos": [player_pos[0], player_pos[1] - 50],
                            "timer": 0.0
                        })


                self.attack_in_progress = False
                self.attack_pos = None
                self.attack_target_pos = None
                self.attack_delay_timer = 0.0
                self.current_action = None

                if not self.action_queue:
                    self.turn_count += 1
                    self.running_away = False
                    self.run_pos_hidden = False
                    self.run_start_pos = None
                    self.run_target_pos = None
            else:
                move_x = dx / dist * self.attack_speed * dt
                move_y = dy / dist * self.attack_speed * dt
                pos[0] += move_x
                pos[1] += move_y
                return
        # Potion 飛行動畫
        if self.potion_animating and self.potion_pos:
            dx = self.potion_target_pos[0] - self.potion_pos[0]
            dy = self.potion_target_pos[1] - self.potion_pos[1]
            dist = (dx**2 + dy**2)**0.5
            step = self.potion_speed * dt
            if dist <= step:
                self.potion_animating = False  # 飛到目標，結束動畫
                # 可以在這裡加一個小傾倒效果或閃光
            else:
                self.potion_pos[0] += dx / dist * step
                self.potion_pos[1] += dy / dist * step



        # ===== Run Away動畫 =====
        if self.running_away and self.run_start_pos is not None and not self.run_pos_hidden:
            step = 600 * dt
            if (self.run_start_pos[1] - self.run_target_pos[1]) >= step:
                self.run_start_pos[1] -= step
            else:
                self.run_pos_hidden = True

        # ===== 安全檢查死亡 =====
        if self.player_hp <= 0:
            self.game_over = True
            self.winner = "enemy"
        elif self.enemy_hp <= 0:
            self.game_over = True
            self.winner = "player"
        # 進化飛出動畫
        if self.evolving and self.evolve_img:
            dx = self.evolve_target_pos[0] - self.evolve_start_pos[0]
            dy = self.evolve_target_pos[1] - self.evolve_start_pos[1]
            dist = (dx**2 + dy**2)**0.5
            step = self.evolve_speed * dt
            if dist <= step:
                self.evolving = False  # 飛出去完成
                
            else:
                self.evolve_start_pos[0] += dx / dist * step
                self.evolve_start_pos[1] += dy / dist * step
        for dmg in self.damage_texts[:]:
            dmg["timer"] += dt
            dmg["pos"][1] -= 30 * dt  # 往上飄
            if dmg["timer"] > 1.0:
                self.damage_texts.remove(dmg)

    # ========================== Draw ============================
    # ============================================================
    def draw(self, screen: pg.Surface):
        screen_width, screen_height = screen.get_size()

        if self.game_over:
            screen.fill((0, 0, 0))
            text_surface = self.over_font.render("GAME OVER!!!", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            screen.blit(text_surface, text_rect)

            result_text = "YOU WIN!" if self.winner == "player" else "YOU LOSE!"
            result_surface = self.over_font.render(result_text, True, (255, 255, 255))
            result_rect = result_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            screen.blit(result_surface, result_rect)

            self.back_rect.center = (screen_width // 2, screen_height // 2 + 150)
            mx, my = pg.mouse.get_pos()
            if self.back_rect.collidepoint((mx, my)):
                screen.blit(self.back_hover, self.back_rect)
            else:
                screen.blit(self.back_image, self.back_rect)
            return

        # ===== 戰鬥畫面 =====
        screen.blit(self.background, (0, 0))
        player_pos_draw = (screen_width // 4 - 75, screen_height // 2 - 75)
        enemy_pos_draw = (screen_width * 3 // 4 - 75, screen_height // 2 - 75)

        # ===== 安全處理玩家座標 =====
        player_draw_pos = player_pos_draw
        if self.running_away and self.run_start_pos is not None:
            player_draw_pos = self.run_start_pos
        screen.blit(self.player_img, player_draw_pos)

        screen.blit(self.enemy_img, enemy_pos_draw)
 
        # ===== 戰鬥畫面背景 =====
        if self.attack_in_progress:
            if self.attack_from_player:
                # 玩家攻擊背景  
                screen.blit(self.attack_bg_images.get(self.player_element, self.background), (0, 0))
            else:
                # 敵人攻擊背景（固定水屬性）
                screen.blit(self.attack_bg_images["Water"], (0, 0))
        else:
        # 正常背景
            screen.blit(self.background, (0, 0))


        # ===== 攻擊動畫 =====
        if self.attack_in_progress and self.attack_pos:
            attack_img = self.current_attack_img
            offset_y = -50 if self.attack_from_player else 0
            attack_rect = attack_img.get_rect(center=(self.attack_pos[0], self.attack_pos[1] + offset_y))
            screen.blit(attack_img, attack_rect)

        # 血條
        bar_width = 150
        bar_height = 15
        pg.draw.rect(screen, (0, 100, 0), (player_pos_draw[0], player_pos_draw[1] - 20, bar_width, bar_height))
        pg.draw.rect(screen, (255, 0, 0), (player_pos_draw[0], player_pos_draw[1] - 20, bar_width * self.player_hp / self.max_hp, bar_height))
        pg.draw.rect(screen, (0, 100, 0), (enemy_pos_draw[0], enemy_pos_draw[1] - 20, bar_width, bar_height))
        pg.draw.rect(screen, (255, 0, 0), (enemy_pos_draw[0], enemy_pos_draw[1] - 20, bar_width * self.enemy_hp / self.max_hp, bar_height))

        # 名稱
        player_name = self.font.render("Player", True, (255, 255, 255))
        enemy_name = self.font.render("Enemy", True, (255, 255, 255))
        screen.blit(player_name, (player_pos_draw[0], player_pos_draw[1] - 50))
        screen.blit(enemy_name, (enemy_pos_draw[0], enemy_pos_draw[1] - 50))

        # Turn
        turn_text = self.turn_font.render(f"Turn {self.turn_count}", True, (255, 255, 0))
        screen.blit(turn_text, (screen_width // 2 - 50, 20))



        # 按鈕
        num_buttons = len(self.buttons)
        spacing = 50
        start_x = (screen_width - (sum(self.button_widths) + spacing * (num_buttons - 1))) // 2
        button_y = screen_height - 80

        for i, text in enumerate(self.buttons):
            btn_rect = pg.Rect(start_x + sum(self.button_widths[:i]) + spacing * i,
                               button_y,
                               self.button_widths[i],
                               self.button_heights[i])

            mx, my = pg.mouse.get_pos()
            if btn_rect.collidepoint((mx, my)):
                color = (200, 200, 200) if self.button_pressed_index == i else (150, 150, 150)
            else:
                color = (100, 100, 100)
            if text in self.items and self.items[text] == 0:
                color = (80, 80, 80)

            pg.draw.rect(screen, color, btn_rect)
            display_text = text
            if text in self.items:
                display_text = f"{text} ({self.items[text]})"
            text_surface = self.small_font.render(display_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=btn_rect.center)
            screen.blit(text_surface, text_rect)

        # ===== 角色圖 =====
        player_draw_pos = player_pos_draw
        if self.running_away and self.run_start_pos is not None:
            player_draw_pos = self.run_start_pos
        screen.blit(self.player_img, player_draw_pos)
        screen.blit(self.enemy_img, enemy_pos_draw)

        # ===== 屬性克制表 (右上角) =====
        x_offset = screen_width - 800  # 右邊距離
        y_offset = 20                  # 上方距離
        line_height = 20               # 行高

        title_surface = self.font.render("Element Effectiveness", True, (255, 255, 0))
        screen.blit(title_surface, (x_offset, y_offset))
        y_offset += line_height

        for ele, eff in ELEMENT_EFFECTIVENESS.items():
            strong = eff.get("strong") or "None"
            weak = eff.get("weak") or "None"
            line_text = f"{ele}: strong → {strong}, weak → {weak}"
            line_surface = self.font.render(line_text, True, (255, 255, 255))
            screen.blit(line_surface, (x_offset, y_offset))
            y_offset += line_height

        # 元素顯示（在角色下方）
        player_element_text = self.font.render(f"Element: {self.player_element}", True, (0, 255, 255))
        enemy_element_text = self.font.render(f"Element: {self.enemy_element}", True, (0, 255, 255))
        screen.blit(player_element_text, (player_pos_draw[0], player_pos_draw[1] + 160))  # 150圖高 + 10間距
      
        screen.blit(enemy_element_text, (enemy_pos_draw[0], enemy_pos_draw[1] + 160))
       

        if self.evolving and self.evolve_img:
            screen.blit(self.evolve_img, self.evolve_start_pos)
        else:
            # 正常畫玩家
            screen.blit(self.player_img, player_draw_pos)  # 正常畫玩家圖（已經是進化後）
        for dmg in self.damage_texts:
            dmg_surface = self.font.render(dmg["text"], True, (255, 0, 0))
            dmg_rect = dmg_surface.get_rect(center=dmg["pos"])
            screen.blit(dmg_surface, dmg_rect)

        if self.potion_animating and self.potion_pos:
            screen.blit(self.potion_img, self.potion_pos)
