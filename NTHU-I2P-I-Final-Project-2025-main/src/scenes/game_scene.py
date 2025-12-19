import pygame as pg
from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager
from src.sprites import Sprite
from typing import override
from src.core.services import scene_manager  # 引入全域 scene_manager


class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite

    def __init__(self):
        super().__init__()

        # ===== GAME MANAGER =====
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager

        # ===== ONLINE MANAGER =====
        self.online_manager = OnlineManager() if GameSettings.IS_ONLINE else None

        # ===== ONLINE SPRITE =====
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))

        # ===== UI 按鈕 =====
        self.top_right_image = pg.image.load("assets/images/UI/button_setting.png")
        self.top_right_hover = pg.image.load("assets/images/UI/button_setting_hover.png")
        self.top_right_rect = self.top_right_image.get_rect()
        self.is_top_right_hover = False

        self.backpack_image = pg.image.load("assets/images/UI/button_backpack.png")
        self.backpack_hover = pg.image.load("assets/images/UI/button_backpack_hover.png")
        self.backpack_rect = self.backpack_image.get_rect()
        self.is_backpack_hover = False

        self.back_image = pg.image.load("assets/images/UI/button_back.png")
        self.back_hover = pg.image.load("assets/images/UI/button_back_hover.png")
        self.back_rect = self.back_image.get_rect()
        self.is_back_hover = False

        self.save_image = pg.image.load("assets/images/UI/button_save.png")
        self.save_hover = pg.image.load("assets/images/UI/button_save_hover.png")
        self.save_rect = self.save_image.get_rect()

        self.load_image = pg.image.load("assets/images/UI/button_load.png")
        self.load_hover = pg.image.load("assets/images/UI/button_load_hover.png")
        self.load_rect = self.load_image.get_rect()

        # ===== OVERLAY STATE =====
        self.overlay_open = False
        self.overlay_type = None  # None / "setting" / "backpack"

        # ===== VOLUME SLIDER =====
        self.slider_rect = pg.Rect(0, 0, 300, 10)
        self.slider_knob_radius = 12
        self.slider_dragging = False
        self.volume = 80
        if sound_manager.current_bgm:
            sound_manager.current_bgm.set_volume(self.volume / 100)

        # ===== NPC WARNING ICON =====
        self.warning_icon = pg.image.load("assets/images/exclamation.png")
        self.warning_icon = pg.transform.smoothscale(
            self.warning_icon,
            (self.warning_icon.get_width()*5, self.warning_icon.get_height()*5)
        )

        # ===== OVERLAY IMAGE =====
        self.overlay_image = pg.image.load("assets/images/UI/raw/UI_Flat_FrameMarker03a.png").convert_alpha()

        # ===== 草叢初始化 =====
        self.bushes = []           # 原本 catch_pokemon 草叢
        self.teleport_bushes = []  # 新增：傳送用草叢

        # ===== SHOP NPC =====
        self.shop_npc_image = pg.image.load(
            "assets/images/menu_sprites/menusprite13.png"
        ).convert_alpha()
        self.shop_npc_image = pg.transform.smoothscale(
            self.shop_npc_image,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        self.shop_npc_rect = None
        self.shop_overlay_open = False
        
        # 新增：用於 NPC 頭上文字和商店 UI 的字體
        self.npc_font = pg.font.SysFont(None, 24)
        self.shop_title_font = pg.font.SysFont(None, 48) # 商店標題
        self.shop_item_font = pg.font.SysFont(None, 28) # 商店物品清單字體

        # ===== BUY 按鈕 (程式生成 =====
        # ===== BUY 按鈕 =====
        self.buy_button_size = (120, 30)
        self.buy_button_image = pg.Surface(self.buy_button_size, pg.SRCALPHA)
        self.buy_button_color = (0, 200, 0)
        self.buy_button_hover_color = (0, 255, 0)
        font = pg.font.SysFont(None, 24)
        text = font.render("Buy Pokeball", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.buy_button_size[0]//2, self.buy_button_size[1]//2))
        self.buy_button_image.blit(text, text_rect)
        self.buy_button_rect = self.buy_button_image.get_rect()
        self.is_buy_hover = False

        # ===== SELL 按鈕 =====
        self.sell_button_size = (120, 30)
        self.sell_button_image = pg.Surface(self.sell_button_size, pg.SRCALPHA)
        self.sell_button_color = (200, 0, 0)
        self.sell_button_hover_color = (255, 0, 0)
        text = font.render("Sell Pokeball", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.sell_button_size[0]//2, self.sell_button_size[1]//2))
        self.sell_button_image.blit(text, text_rect)
        self.sell_button_rect = self.sell_button_image.get_rect()
        self.is_sell_hover = False

        # ===== MINIMAP SETTINGS =====
        self.minimap_width = 180
        self.minimap_height = 180
        self.minimap_pos = (10, 10)  # 左上角
        self.minimap_surface = pg.Surface(
            (self.minimap_width, self.minimap_height)
        )

        self.minimap_tile_size = 4  # 每個 tile 縮小成 4x4 像素，可調整
        
        # Shop 分頁狀態
        self.shop_page = "buy"  # 可選 "buy" 或 "sell"
        # Shop tab 按鈕位置
        self.buy_tab_rect = pg.Rect(0, 0, 100, 30)
        self.sell_tab_rect = pg.Rect(0, 0, 100, 30)

        # ===== 讀取寶可夢圖片 =====
        for monster in self.game_manager.bag.monsters:
            path = monster.get("sprite_path")
            if path:
                # 假設你的圖片放在 assets/images/
                monster["sprite_image"] = pg.image.load(f"assets/images/{path}").convert_alpha()


        # ===== 導航目的地 =====
        TS = GameSettings.TILE_SIZE
        self.nav_places = [
            {"name": "House", "pos": (16*TS, 28*TS)},
            {"name": "Garden", "pos": (10*TS, 25*TS)}
        ]
        # 用於按鈕循環導航
        # ===== 導航按鈕 =====
        self.nav_image = pg.image.load("assets/images/UI/button_play.png")
        self.nav_hover = pg.image.load("assets/images/UI/button_play_hover.png")
        self.nav_rect = self.nav_image.get_rect()
        self.is_nav_hover = False

        # ===== Navigation UI State =====
        self.nav_overlay_open = False     # 是否顯示導航選單
        self.nav_target = None            # 目前導航目標 (x, y)
        self.nav_in_progress = False      # 是否正在導航
        self.house_btn = None
        self.garden_btn = None

    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()

        # ===== 在玩家位置生成草叢 =====
        player = self.game_manager.player
        px, py = player.position.x, player.position.y
        TS = GameSettings.TILE_SIZE

        # catch_pokemon 草叢
        self.bushes = [
            pg.Rect(px - 10 * TS, py, TS, TS),
        ]

        # teleport 草叢（你指定位置 px + 10 * TS）
        player = self.game_manager.player
        px, py = player.position.x, player.position.y
        TS = GameSettings.TILE_SIZE
        self.shop_npc_rect = pg.Rect(px + 2 * TS,py - TS,TS,TS)

    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()

    @override
    def update(self, dt: float):
        screen_width = pg.display.get_surface().get_width()
        self.top_right_rect.topright = (screen_width - 20, 20)
        self.backpack_rect.topright = (screen_width - 20, self.top_right_rect.bottom + 10)

        mx, my = pg.mouse.get_pos()
        left_pressed = pg.mouse.get_pressed()[0]

        # ===== Hover 判定 =====
        self.is_top_right_hover = self.top_right_rect.collidepoint(mx, my)
        self.is_backpack_hover = self.backpack_rect.collidepoint(mx, my)
        self.is_back_hover = self.back_rect.collidepoint(mx, my) if self.overlay_open else False

        # ===== Overlay 開關 =====
        if self.overlay_open:
            if left_pressed and self.is_back_hover:
                self.overlay_open = False
                self.overlay_type = None
                self.slider_dragging = False
        else:
            if left_pressed:
                if self.is_top_right_hover:
                    self.overlay_open = True
                    self.overlay_type = "setting"
                elif self.is_backpack_hover:
                    self.overlay_open = True
                    self.overlay_type = "backpack"

        # ===== 更新遊戲物件 =====

        if not self.overlay_open and not self.shop_overlay_open and not self.nav_overlay_open:
            if self.game_manager.player:
                if not self.nav_in_progress:
                    self.game_manager.player.update(dt)
                else:
                    self.update_navigation(dt)


            if self.game_manager.player:
                self.game_manager.try_switch_map()

            if self.game_manager.player and self.online_manager:
                _ = self.online_manager.update(
                    self.game_manager.player.position.x,
                    self.game_manager.player.position.y,
                    self.game_manager.current_map.path_name
                )
        # 玩家碰到 catch_pokemon 草叢 → 進入 CatchPokemonScene
        if self.game_manager.player:
            player_rect = self.game_manager.player.rect
            for bush in self.bushes:
                if player_rect.colliderect(bush):
                    Logger.info("Player touched bush → Switching to catch_pokemon scene")
                    if "catch_pokemon" in scene_manager._scenes:
                        scene_manager.change_scene("catch_pokemon")
                    else:
                        Logger.error("catch_pokemon scene not found!")
                    return


        # ===== Shop NPC Interaction =====
        if self.shop_npc_rect and self.game_manager.player:
            player_rect = self.game_manager.player.rect
            
            # 判斷是否在 NPC 附近 (碰撞或輕微擴大範圍)
            interaction_range = GameSettings.TILE_SIZE * 1.5 
            # 建立一個稍微擴大的 NPC 矩形，用於更寬鬆的互動偵測
            interact_rect = self.shop_npc_rect.inflate(interaction_range, interaction_range)
        screen_width = pg.display.get_surface().get_width()
        self.nav_rect.topright = (screen_width - 20, self.backpack_rect.bottom + 10)

        screen_width = pg.display.get_surface().get_width()
        self.nav_rect.topright = (screen_width - 20, self.backpack_rect.bottom + 10)
        self.update_navigation(dt)
        self.is_nav_hover = self.nav_rect.collidepoint(mx, my)

    # ===== 判斷玩家是否靠近 NPC =====
    def is_warning_active(self) -> bool:
        for enemy in self.game_manager.current_enemy_trainers:
            Logger.info(f"Enemy detected={enemy.detected}")
            if getattr(enemy, "detected", False):
                return True
        return False


    def draw_minimap(self, screen: pg.Surface):
        current_map = self.game_manager.current_map
        player = self.game_manager.player
        if not current_map or not player:
            return

        tiles = current_map.tmxdata.layers[0].data  # 2D list
        map_h = len(tiles)
        map_w = len(tiles[0])

        mini_ts = self.minimap_tile_size

        self.minimap_surface = pg.Surface((map_w * mini_ts, map_h * mini_ts))
        self.minimap_surface.fill((0, 0, 0))  # 背景黑色


        for layer in current_map.tmxdata.visible_layers:
            if hasattr(layer, "data"):  # tile layer
                for y, row in enumerate(layer.data):
                    for x, tile_gid in enumerate(row):
                        if tile_gid != 0:
                            tile_image = current_map.tmxdata.get_tile_image_by_gid(tile_gid)
                            if tile_image:
                                tile_surf = pg.transform.smoothscale(tile_image, (mini_ts, mini_ts))
                                self.minimap_surface.blit(tile_surf, (x * mini_ts, y * mini_ts))


        # 畫玩家位置
        px = int(player.position.x / GameSettings.TILE_SIZE * mini_ts)
        py = int(player.position.y / GameSettings.TILE_SIZE * mini_ts)
        pg.draw.circle(self.minimap_surface, (255, 0, 0), (px, py), 3)

        # 畫邊框
        pg.draw.rect(self.minimap_surface, (255, 255, 255), self.minimap_surface.get_rect(), 1)

        # blit 到畫面
        screen.blit(self.minimap_surface, self.minimap_pos)

        




    @override
    def handle_event(self, event):
        mx, my = pg.mouse.get_pos()
        player_rect = self.game_manager.player.rect if self.game_manager.player else None

        # ===== 鍵盤事件 =====
        if event.type == pg.KEYDOWN:
            # E 鍵：Shop NPC 互動
            if event.key == pg.K_e:
                if self.shop_npc_rect and player_rect:
                    interact_range = GameSettings.TILE_SIZE * 1.5
                    interact_rect = self.shop_npc_rect.inflate(interact_range, interact_range)
                    if player_rect.colliderect(interact_rect):
                        Logger.info("E pressed near NPC → Open Shop")
                        self.shop_overlay_open = True
                        self.overlay_open = False
                        self.overlay_type = None
                        return

            # ESC 鍵：關閉 overlay / shop
            elif event.key == pg.K_ESCAPE:
                if self.shop_overlay_open:
                    self.shop_overlay_open = False
                if self.overlay_open:
                    self.overlay_open = False
                    self.overlay_type = None
                if self.nav_overlay_open:
                    self.nav_overlay_open = False

            # SPACE 鍵：觸發戰鬥
            elif event.key == pg.K_SPACE:
                if any(getattr(enemy, "detected", False) for enemy in self.game_manager.current_enemy_trainers):
                    Logger.info("Player near NPC → Switching to Battle Scene")
                    if "battle" in scene_manager._scenes:
                        scene_manager.change_scene("battle")
                    else:
                        Logger.error("Battle scene not found")


            # 商店操作：B 買、S 賣
            if self.shop_overlay_open:
                if self.shop_page == "buy" and event.key == pg.K_b:
                    price = 300
                    if self.game_manager.bag.money >= price:
                        self.game_manager.bag.money -= price
                        self.game_manager.bag.add_item("potion", 1)
                        Logger.info("Bought Potion")
                    else:
                        Logger.info("Not enough money")
                elif self.shop_page == "sell" and event.key == pg.K_s:
                    sell_price = 150
                    if self.game_manager.bag.has_item("potion"):
                        self.game_manager.bag.remove_item("potion", 1)
                        self.game_manager.bag.money += sell_price
                        Logger.info("Sold Potion")
                    else:
                        Logger.info("No Potion to sell")

        # ===== 滑鼠事件 / Overlay 處理 =====
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Setting Overlay 滑桿 / 按鈕
            if self.overlay_open and self.overlay_type == "setting":
                knob_x = self.slider_rect.x + self.volume / 100 * self.slider_rect.width
                distance = ((mx - knob_x) ** 2 + (my - self.slider_rect.centery) ** 2) ** 0.5
                if distance <= self.slider_knob_radius or self.slider_rect.collidepoint(mx, my):
                    self.slider_dragging = True
                elif self.back_rect.collidepoint(mx, my):
                    self.overlay_open = False
                    self.overlay_type = None
                elif self.save_rect.collidepoint(mx, my):
                    self.game_manager.save("saves/game0.json")
                    Logger.info("Game saved successfully!")
                elif self.load_rect.collidepoint(mx, my):
                    gm = GameManager.load("saves/game0.json")
                    if gm:
                        self.game_manager = gm
                        Logger.info("Game loaded successfully!")

            # Backpack Overlay 返回按鈕
            elif self.overlay_open and self.overlay_type == "backpack":
                if self.back_rect.collidepoint(mx, my):
                    self.overlay_open = False
                    self.overlay_type = None
        if self.shop_overlay_open:
            mx, my = pg.mouse.get_pos()
            self.is_buy_hover = self.buy_button_rect.collidepoint(mx, my)
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.shop_overlay_open:
                mx, my = pg.mouse.get_pos()
                # Buy Pokeball
                # Buy Pokeball
                if self.shop_page == "buy" and self.buy_button_rect.collidepoint(mx, my):
                    price = 200
                    if self.game_manager.bag.money >= price:
                        self.game_manager.bag.money -= price
                        self.game_manager.bag.add_item("pokeball", 1)
                        Logger.info("Bought Pokeball")
                    else:
                        Logger.info("Not enough money")
                # Sell Pokeball
                elif self.shop_page == "sell" and self.sell_button_rect.collidepoint(mx, my):
                    sell_price = 100
                    if self.game_manager.bag.has_item("pokeball"):
                        self.game_manager.bag.remove_item("pokeball", 1)
                        self.game_manager.bag.money += sell_price
                        Logger.info("Sold Pokeball")
                    else:
                        Logger.info("No Pokeball to sell")


                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pg.mouse.get_pos()
                    if self.buy_tab_rect.collidepoint(mx, my):
                        self.shop_page = "buy"
                    elif self.sell_tab_rect.collidepoint(mx, my):
                        self.shop_page = "sell"


        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.slider_dragging:
                self.slider_dragging = False

        elif event.type == pg.MOUSEMOTION and self.slider_dragging:
            relative_x = mx - self.slider_rect.x
            self.volume = max(0, min(100, int(relative_x / self.slider_rect.width * 100)))
            if sound_manager.current_bgm:
                sound_manager.current_bgm.set_volume(self.volume / 100)
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.nav_rect.collidepoint(mx, my):
                Logger.info("Open navigation overlay")
                self.nav_overlay_open = True
                self.overlay_open = False
                self.shop_overlay_open = False
                return

            if self.nav_overlay_open and self.house_btn and self.garden_btn:
                if self.house_btn.collidepoint(mx, my):
                    self.start_navigation(self.nav_places[0]["pos"])
                    self.nav_overlay_open = False

                elif self.garden_btn.collidepoint(mx, my):
                    self.start_navigation(self.nav_places[1]["pos"])
                    self.nav_overlay_open = False


    def start_navigation(self, target_pos):
        self.nav_target = target_pos
        self.nav_in_progress = True

    def update_navigation(self, dt):
        if getattr(self, "nav_in_progress", False) and self.game_manager.player:
            px, py = self.game_manager.player.position.x, self.game_manager.player.position.y
            tx, ty = self.nav_target
            speed = 100 * dt  # 每秒 100 像素
            dx, dy = tx - px, ty - py
            dist = (dx**2 + dy**2)**0.5
            if dist < speed:
                self.game_manager.player.position.x = tx
                self.game_manager.player.position.y = ty
                self.nav_in_progress = False
            else:
                self.game_manager.player.position.x += dx / dist * speed
                self.game_manager.player.position.y += dy / dist * speed

    @override
    def draw(self, screen: pg.Surface):
        camera = self.game_manager.player.camera if self.game_manager.player else PositionCamera(0, 0)
        self.game_manager.current_map.draw(screen, camera)
        
        # ===== Draw Player =====
        if self.game_manager.player:
            self.game_manager.player.draw(screen, camera)

        # ===== Draw Enemy NPCs & Warning Symbol =====
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)
            
        # ===== Draw Bag =====
        self.game_manager.bag.draw(screen)

        # ===== Draw Online Players =====
        if self.online_manager and self.game_manager.player:
            for player in self.online_manager.get_list_players():
                if player["map"] == self.game_manager.current_map.path_name:
                    pos = camera.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)

        # ===== Draw UI Buttons =====
        screen.blit(self.top_right_hover if self.is_top_right_hover else self.top_right_image, self.top_right_rect)
        screen.blit(self.backpack_hover if self.is_backpack_hover else self.backpack_image, self.backpack_rect)
        screen.blit(self.nav_hover if self.is_nav_hover else self.nav_image, self.nav_rect)

        # ===== Draw Extra Hint =====
        TS = GameSettings.TILE_SIZE

        # 固定提示格子的位置 
        hint_tile_x, hint_tile_y = 16, 32
        hint_rect = pg.Rect(hint_tile_x * TS, hint_tile_y * TS, TS, TS)

        # 畫半透明方塊提示
        s = pg.Surface((hint_rect.width, hint_rect.height), pg.SRCALPHA)
        s.fill((0, 0, 255, 100))  # 藍色半透明
        screen.blit(s, (hint_rect.x - camera.x, hint_rect.y - camera.y))

        # 畫文字提示
        font = pg.font.SysFont(None, 24)
        text = font.render("TELEPORT", True, (255, 255, 255))
        text_rect = text.get_rect(center=(hint_rect.centerx - camera.x, hint_rect.centery - camera.y))
        screen.blit(text, text_rect)


        # ===== Draw Overlay if open =====
        # 保留原本 overlay 繪製程式碼，不改動
        if self.overlay_open:
            dim = pg.Surface(screen.get_size())
            dim.set_alpha(150)
            dim.fill((0, 0, 0))
            screen.blit(dim, (0, 0))

            overlay_width = int(self.overlay_image.get_width() * 14)
            overlay_height = int(self.overlay_image.get_height() * 14)
            overlay_scaled = pg.transform.smoothscale(self.overlay_image, (overlay_width, overlay_height))
            overlay_rect = overlay_scaled.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(overlay_scaled, overlay_rect.topleft)

            font = pg.font.SysFont(None, 36)
            small_font = pg.font.SysFont(None, 28)

            # ===== Setting Overlay =====
            if self.overlay_type == "setting":
                text_surface = font.render("Settings", True, (255, 255, 255))
                screen.blit(text_surface, text_surface.get_rect(center=(overlay_rect.centerx, overlay_rect.top - 20)))

                self.slider_rect.topleft = (overlay_rect.x + 20, overlay_rect.y + 120)
                pg.draw.rect(screen, (200,200,200), self.slider_rect)
                knob_x = self.slider_rect.x + self.volume / 100 * self.slider_rect.width
                pg.draw.circle(screen, (255,255,255), (int(knob_x), self.slider_rect.centery), self.slider_knob_radius)
                vol_text = small_font.render(f"Volume: {self.volume}%", True, (255,200,200))
                screen.blit(vol_text, (self.slider_rect.right + 20, self.slider_rect.y - 10))

                btn_y = self.slider_rect.bottom + 30
                spacing = 20
                total_width = self.save_rect.width + self.load_rect.width + self.back_rect.width + spacing*2
                start_x = overlay_rect.centerx - total_width // 2

                self.save_rect.topleft = (start_x, btn_y)
                screen.blit(self.save_hover if self.save_rect.collidepoint(pg.mouse.get_pos()) else self.save_image, self.save_rect)

                self.load_rect.topleft = (start_x + self.save_rect.width + spacing, btn_y)
                screen.blit(self.load_hover if self.load_rect.collidepoint(pg.mouse.get_pos()) else self.load_image, self.load_rect)

                self.back_rect.topleft = (start_x + self.save_rect.width + self.load_rect.width + spacing*2, btn_y)
                screen.blit(self.back_hover if self.is_back_hover else self.back_image, self.back_rect)

            # ===== Backpack Overlay =====
            elif self.overlay_type == "backpack":
                text_surface = font.render("BAG", True, (255, 255, 255))
                screen.blit(text_surface, (overlay_rect.x + 20, overlay_rect.y + 20))

                for i, monster in enumerate(self.game_manager.bag.monsters):
                    name = monster["name"]
                    level = monster.get("level", 1)
                    hp = monster.get("hp", 0)
                    max_hp = monster.get("max_hp", 0)
                    element = monster.get("element", "Unknown")


                    # 畫圖片
                    sprite_img = monster.get("sprite_image")
                    if sprite_img:
                        screen.blit(sprite_img, (overlay_rect.x + 10, overlay_rect.y + 80 + i*50))  # 調整間距和位置

                    # 畫文字
                    m_text = small_font.render(f"{i+1}. {name}  Lv:{level}  HP:{hp}/{max_hp} Element:{element} " , True, (255, 255, 255))
                    screen.blit(m_text, (overlay_rect.x + 80, overlay_rect.y + 80 + i*50))


                for i, item in enumerate(self.game_manager.bag.items):
                    name = item["name"]
                    count = item.get("count", 1)
                    it_text = small_font.render(f"{i+1}. {name} x{count}", True, (255, 255, 255))
                    screen.blit(it_text, (overlay_rect.x + overlay_width//2 + 80, overlay_rect.y + 80 + i*30))

                btn_y = overlay_rect.bottom - 60
                self.back_rect.topleft = (overlay_rect.centerx - self.back_rect.width//2, btn_y)
                screen.blit(self.back_hover if self.is_back_hover else self.back_image, self.back_rect)

            # ===== Draw Shop NPC & NPC 互動提示 =====
        if self.shop_npc_rect and self.game_manager.player:
        # 只有當 overlay 或 shop 未開啟時才畫 NPC
            if not self.overlay_open and not self.shop_overlay_open:
                # 計算 NPC 螢幕位置
                npc_screen_rect = pg.Rect(
                    self.shop_npc_rect.x - camera.x,
                    self.shop_npc_rect.y - camera.y,
                    self.shop_npc_rect.width,
                    self.shop_npc_rect.height
                )
        
                # 繪製 NPC 圖像
                screen.blit(self.shop_npc_image, npc_screen_rect.topleft)
        
                # 繪製 NPC 標籤
                npc_tag = self.npc_font.render("NPC", True, (255, 255, 0))
                npc_tag_rect = npc_tag.get_rect(center=(npc_screen_rect.centerx, npc_screen_rect.top - 20))
                pg.draw.rect(screen, (0, 0, 0), npc_tag_rect.inflate(5, 2)) 
                screen.blit(npc_tag, npc_tag_rect)
    
                # 繪製互動提示
                player_rect = self.game_manager.player.rect
                interact_range = GameSettings.TILE_SIZE * 1.5
                interact_rect = self.shop_npc_rect.inflate(interact_range, interact_range)
                if player_rect.colliderect(interact_rect):
                    interact_text = self.npc_font.render("Press E to Shop", True, (255, 255, 255))
                    text_rect = interact_text.get_rect(center=(npc_screen_rect.centerx, npc_screen_rect.top - 45))
                    bg = pg.Surface((text_rect.width + 10, text_rect.height + 6), pg.SRCALPHA)
                    bg.fill((0, 0, 0, 160))
                    screen.blit(bg, (text_rect.x - 5, text_rect.y - 3))
                    screen.blit(interact_text, text_rect)



        # ===== 繪製 Shop Overlay (可點 Buy 按鈕) =====
        if self.shop_overlay_open:
            # 暗色背景
            dim = pg.Surface(screen.get_size())
            dim.set_alpha(150)
            dim.fill((0, 0, 0))
            screen.blit(dim, (0, 0))

            # Overlay 框
            overlay_width = int(self.overlay_image.get_width() * 10)
            overlay_height = int(self.overlay_image.get_height() * 10)
            overlay_scaled = pg.transform.smoothscale(self.overlay_image, (overlay_width, overlay_height))
            overlay_rect = overlay_scaled.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(overlay_scaled, overlay_rect.topleft)

            font = pg.font.SysFont(None, 36)
            small_font = pg.font.SysFont(None, 28)

            # 標題
            title_text = font.render("NPC SHOP", True, (255, 255, 255))
            screen.blit(title_text, (overlay_rect.x + 40, overlay_rect.y + 30))

            # 鍵盤提示
            keyboard_hint = small_font.render("You can press B to buy Potion, S to sell Potion", True, (255, 255, 255))
            screen.blit(keyboard_hint, (overlay_rect.x + 40, overlay_rect.y + 280))

           
            # 玩家金錢
            money = self.game_manager.bag.money if self.game_manager.player else 0
            money_text = small_font.render(f"Your Money: ${money}", True, (255, 220, 100))
            screen.blit(money_text, (overlay_rect.x + overlay_width//2 + 20, overlay_rect.y + 80))


            # 顯示背包道具
            for i, item in enumerate(self.game_manager.bag.items):
                name = item["name"]
                count = item.get("count", 1)
                it_text = small_font.render(f"{i+1}. {name} x{count}", True, (255, 255, 255))
                screen.blit(it_text, (overlay_rect.x + overlay_width//2 + 20, overlay_rect.y + 120 + i*35))

                # Tab 按鈕位置
                self.buy_tab_rect.topleft = (overlay_rect.x + 40, overlay_rect.y + 30)
                self.sell_tab_rect.topleft = (overlay_rect.x + 160, overlay_rect.y + 30)

                # hover 顏色
                mx, my = pg.mouse.get_pos()
                buy_color = (0, 200, 0) if self.shop_page == "buy" else (100, 100, 100)
                sell_color = (200, 0, 0) if self.shop_page == "sell" else (100, 100, 100)

                pg.draw.rect(screen, buy_color, self.buy_tab_rect)
                pg.draw.rect(screen, sell_color, self.sell_tab_rect)

                font = pg.font.SysFont(None, 24)
                buy_text = font.render("BUY", True, (255,255,255))
                sell_text = font.render("SELL", True, (255,255,255))
                screen.blit(buy_text, buy_text.get_rect(center=self.buy_tab_rect.center))
                screen.blit(sell_text, sell_text.get_rect(center=self.sell_tab_rect.center))

                if self.shop_page == "buy":
                    # 顯示可買道具列表和 Buy 按鈕
                    self.buy_button_rect.topleft = (overlay_rect.x + 40, overlay_rect.y + 80)
                    color = self.buy_button_hover_color if self.is_buy_hover else self.buy_button_color
                    pg.draw.rect(screen, color, self.buy_button_rect)
                    screen.blit(self.buy_button_image, self.buy_button_rect.topleft)
                elif self.shop_page == "sell":
                    # 顯示背包可賣道具列表和 Sell 按鈕
                    self.sell_button_rect.topleft = (overlay_rect.x + 40, overlay_rect.y + 80)
                    color = self.sell_button_hover_color if self.is_sell_hover else self.sell_button_color
                    pg.draw.rect(screen, color, self.sell_button_rect)
                    screen.blit(self.sell_button_image, self.sell_button_rect.topleft)
                    
                    # 顯示可賣道具列表
                    small_font = pg.font.SysFont(None, 28)
                    for i, item in enumerate(self.game_manager.bag.items):
                        name = item["name"]
                        count = item.get("count", 1)
                        it_text = small_font.render(f"{i+1}. {name} x{count}", True, (255, 255, 255))
                        screen.blit(it_text, (overlay_rect.x + 40, overlay_rect.y + 120 + i*35))

                    # ===== Draw Minimap (UI Overlay) =====
        if not self.overlay_open and not self.shop_overlay_open and not self.nav_overlay_open:
            self.draw_minimap(screen)
        # ===== Navigation Overlay =====
        if self.nav_overlay_open:
            # 半透明背景
            dim = pg.Surface(screen.get_size())
            dim.set_alpha(150)
            dim.fill((0, 0, 0))
            screen.blit(dim, (0, 0))

            # 中央框
            box = pg.Rect(
                screen.get_width()//2 - 200,
                screen.get_height()//2 - 150,
                400,
                300
            )
            pg.draw.rect(screen, (40, 40, 40), box, border_radius=12)
            pg.draw.rect(screen, (200, 200, 200), box, 3, border_radius=12)

            font = pg.font.SysFont(None, 36)

            title = font.render("Choose Destination", True, (255, 255, 255))
            screen.blit(title, title.get_rect(center=(box.centerx, box.top + 30)))

            # House 按鈕
            self.house_btn = pg.Rect(box.centerx - 120, box.centery - 20, 240, 40)
            pg.draw.rect(screen, (100, 100, 255), self.house_btn, border_radius=8)
            screen.blit(
                font.render("House", True, (255, 255, 255)),
                font.render("House", True, (255, 255, 255)).get_rect(center=self.house_btn.center)
            )

            # Garden 按鈕
            self.garden_btn = pg.Rect(box.centerx - 120, box.centery + 40, 240, 40)
            pg.draw.rect(screen, (100, 200, 100), self.garden_btn, border_radius=8)
            screen.blit(
                font.render("Garden", True, (255, 255, 255)),
                font.render("Garden", True, (255, 255, 255)).get_rect(center=self.garden_btn.center)
            )
        # ===== Navigation Arrow =====
        if self.nav_in_progress and self.game_manager.player:
            px = self.game_manager.player.position.x - camera.x
            py = self.game_manager.player.position.y - camera.y
            tx = self.nav_target[0] - camera.x
            ty = self.nav_target[1] - camera.y

            pg.draw.line(screen, (255, 255, 0), (px, py), (tx, ty), 4)
            pg.draw.circle(screen, (255, 0, 0), (int(tx), int(ty)), 8)
