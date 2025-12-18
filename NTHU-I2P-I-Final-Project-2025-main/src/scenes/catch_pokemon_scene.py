import pygame as pg
from src.scenes.scene import Scene
from src.utils import Logger
from src.core.services import scene_manager
from src.utils import GameSettings, Position
from src.sprites import Sprite

class CatchPokemonScene(Scene):
    def __init__(self, scene_manager):
        super().__init__()
        self.scene_manager = scene_manager
        self.background = None

        # ===== 玩家精靈 =====
        self.player_sprite = Sprite(
            r"C:\Users\angel\OneDrive\Desktop\NTHU-I2P-I-Final-Project-2025-main\NTHU-I2P-I-Final-Project-2025-main\assets\images\menu_sprites\menusprite16.png",
            (128, 128)
        )
        self.player_pos = Position(GameSettings.SCREEN_WIDTH//2 - 200, GameSettings.SCREEN_HEIGHT//2)

        # ===== 寶可夢精靈 =====
        self.pokemon_sprite = Sprite(
            r"C:\Users\angel\OneDrive\Desktop\NTHU-I2P-I-Final-Project-2025-main\NTHU-I2P-I-Final-Project-2025-main\assets\images\menu_sprites\menusprite6.png",
            (128, 128)
        )
        self.pokemon_pos = Position(GameSettings.SCREEN_WIDTH//2 + 100, GameSettings.SCREEN_HEIGHT//2)

        # ===== 捕捉按鈕 =====
        self.button_rect = pg.Rect(0, 0, 200, 60)
        self.button_rect.center = (GameSettings.SCREEN_WIDTH//2, GameSettings.SCREEN_HEIGHT - 100)
        self.is_hover = False

        self.button_image = pg.Surface(self.button_rect.size, pg.SRCALPHA)
        self.button_image.fill((50, 150, 50))
        font = pg.font.SysFont(None, 36)
        text = font.render("CATCH", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.button_rect.width//2, self.button_rect.height//2))
        self.button_image.blit(text, text_rect)

        self.button_hover_image = pg.Surface(self.button_rect.size, pg.SRCALPHA)
        self.button_hover_image.fill((70, 200, 70))
        self.button_hover_image.blit(text, text_rect)

        # ===== 捕捉動畫狀態 =====
        self.catching = False
        self.catch_timer = 0.0
        self.catch_duration = 1.0
        self.catch_finished = False

        self.pokemon_current_size = self.pokemon_sprite.image.get_size()

        # ===== 回主畫面按鈕 =====
        self.back_button_rect = pg.Rect(0, 0, 200, 60)
        self.back_button_rect.center = (GameSettings.SCREEN_WIDTH//2, GameSettings.SCREEN_HEIGHT//2 + 150)
        self.back_image = pg.Surface(self.back_button_rect.size, pg.SRCALPHA)
        self.back_image.fill((100, 100, 100))
        back_text = font.render("BACK", True, (255, 255, 255))
        self.back_image.blit(back_text, back_text.get_rect(center=(self.back_button_rect.width//2, self.back_button_rect.height//2)))

        self.back_hover_image = pg.Surface(self.back_button_rect.size, pg.SRCALPHA)
        self.back_hover_image.fill((150, 150, 150))
        self.back_hover_image.blit(back_text, back_text.get_rect(center=(self.back_button_rect.width//2, self.back_button_rect.height//2)))

    def enter(self):
        Logger.info("Enter CatchPokemonScene")
        self.background = pg.image.load(
            r"C:\Users\angel\OneDrive\Desktop\NTHU-I2P-I-Final-Project-2025-main\NTHU-I2P-I-Final-Project-2025-main\assets\images\backgrounds\background3.png"
        ).convert()
        w, h = self.background.get_size()
        self.background = pg.transform.smoothscale(self.background, (w*4, h*4))

    def exit(self):
        Logger.info("Exit CatchPokemonScene")

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.scene_manager.change_scene("game")
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if not self.catching and not self.catch_finished:
                if self.button_rect.collidepoint(mx, my):
                    Logger.info("Catch button pressed! Start animation...")
                    self.catching = True
                    self.catch_timer = 0.0
            elif self.catch_finished and self.back_button_rect.collidepoint(mx, my):
                self.scene_manager.change_scene("game")

    def update(self, dt):
        if not self.catching and not self.catch_finished:
            mx, my = pg.mouse.get_pos()
            self.is_hover = self.button_rect.collidepoint(mx, my)
        elif self.catching:
            self.catch_timer += dt
            t = min(self.catch_timer / self.catch_duration, 1.0)

            start_x, start_y = self.pokemon_pos.x, self.pokemon_pos.y
            end_x = self.player_pos.x + self.player_sprite.rect.width//2 - self.pokemon_current_size[0]//2
            end_y = self.player_pos.y + self.player_sprite.rect.height//2 - self.pokemon_current_size[1]//2
            self.pokemon_pos.x = start_x + (end_x - start_x) * t
            self.pokemon_pos.y = start_y + (end_y - start_y) * t

            new_width = max(1, int(self.pokemon_current_size[0] * (1 - 0.8 * t)))
            new_height = max(1, int(self.pokemon_current_size[1] * (1 - 0.8 * t)))
            self.pokemon_sprite.image = pg.transform.smoothscale(
                pg.image.load(
                    r"C:\Users\angel\OneDrive\Desktop\NTHU-I2P-I-Final-Project-2025-main\NTHU-I2P-I-Final-Project-2025-main\assets\images\menu_sprites\menusprite6.png"
                ).convert_alpha(),
                (new_width, new_height)
            )

            if t >= 1.0:
                self.catching = False
                self.catch_finished = True

    def draw(self, screen):
        if self.catch_finished:
            screen.fill((0,0,0))
            font = pg.font.SysFont(None, 72)
            text_surface = font.render("Catch a Pokémon", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(GameSettings.SCREEN_WIDTH//2, GameSettings.SCREEN_HEIGHT//2))
            screen.blit(text_surface, text_rect)

            mx, my = pg.mouse.get_pos()
            if self.back_button_rect.collidepoint(mx, my):
                screen.blit(self.back_hover_image, self.back_button_rect.topleft)
            else:
                screen.blit(self.back_image, self.back_button_rect.topleft)
            return

        if self.background:
            screen.blit(self.background, (0, 0))
        screen.blit(self.player_sprite.image, (self.player_pos.x, self.player_pos.y))
        font = pg.font.SysFont(None, 28)
        player_text = font.render("PLAYER", True, (0,0,0))
        screen.blit(player_text, (self.player_pos.x, self.player_pos.y - 20))
        screen.blit(self.pokemon_sprite.image, (self.pokemon_pos.x, self.pokemon_pos.y))
        pokemon_text = font.render("POKEMON", True, (0,0,0))
        screen.blit(pokemon_text, (self.pokemon_pos.x, self.pokemon_pos.y - 20))

        if not self.catching:
            if self.is_hover:
                screen.blit(self.button_hover_image, self.button_rect.topleft)
            else:
                screen.blit(self.button_image, self.button_rect.topleft)
