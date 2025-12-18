import pygame as pg
import time
from src.scenes.scene import Scene
from src.utils import Logger
import src.core.managers.scene_manager as SM

class BattleScene(Scene):
    def __init__(self, scene_manager):
        super().__init__()
        self.scene_manager = scene_manager

        # ===== 背景 =====
        self.background = pg.image.load("assets/images/backgrounds/background1.png").convert()
        screen_width = pg.display.get_surface().get_width()
        screen_height = pg.display.get_surface().get_height()
        self.background = pg.transform.scale(self.background, (screen_width, screen_height))

        # ===== 角色圖 =====
        self.player_img = pg.image.load("assets/images/menu_sprites/menusprite8.png").convert_alpha()
        self.player_img = pg.transform.scale(self.player_img, (150, 150))
        self.enemy_img = pg.image.load("assets/images/menu_sprites/menusprite2.png").convert_alpha()
        self.enemy_img = pg.transform.scale(self.enemy_img, (150, 150))

        # ===== 攻擊動畫圖片 =====
        self.player_attack_img = pg.image.load("assets/images/ingame_ui/ball.png").convert_alpha()
        self.player_attack_img = pg.transform.scale(self.player_attack_img, (30, 30))
        self.enemy_attack_img = pg.image.load("assets/images/UI/raw/UI_Flat_Handle05a.png").convert_alpha()
        self.enemy_attack_img = pg.transform.scale(self.enemy_attack_img, (30, 30))

        # ===== 血量 =====
        self.max_hp = 100
        self.player_hp = self.max_hp
        self.enemy_hp = self.max_hp

        # ===== 回合控制 =====
        self.turn_count = 1
        self.action_queue = []          # 每回合的動作順序: ("player"/"enemy", "attack"/"run")
        self.current_action = None      # 目前正在進行的攻擊
        self.game_started = False
        self.game_over = False
        self.winner = None

        # ===== 按鈕 =====
        self.buttons = ["Attack", "Attack+Run Away", "Start"]
        self.button_widths = [150, 300, 150]
        self.button_heights = [50, 50, 50]
        self.button_pressed_index = None

        # ===== 攻擊動畫控制 =====
        self.attack_in_progress = False
        self.attack_from_player = True
        self.attack_pos = None
        self.attack_target_pos = None
        self.attack_speed = 500
        self.attack_delay_timer = 0.0

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
        self.over_font = pg.font.SysFont(None, 60)
        self.turn_font = pg.font.SysFont(None, 28)

    def enter(self):
        Logger.info("Entered Battle Scene")

    def exit(self):
        Logger.info("Exiting Battle Scene")

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
                    self.enemy_hp = max(0, self.enemy_hp - 34)
                else:
                    if self.running_away and not self.run_pos_hidden:
                        player_dodged = True
                    else:
                        player_dodged = False
                    if not player_dodged:
                        self.player_hp = max(0, self.player_hp - 34)

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

        # 攻擊動畫
        if self.attack_in_progress and self.attack_pos:
            attack_img = self.player_attack_img if self.attack_from_player else self.enemy_attack_img
            attack_rect = attack_img.get_rect(center=self.attack_pos)
            screen.blit(attack_img, attack_rect)

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

            pg.draw.rect(screen, color, btn_rect)
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=btn_rect.center)
            screen.blit(text_surface, text_rect)
