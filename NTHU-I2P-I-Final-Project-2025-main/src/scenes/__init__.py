from __future__ import annotations
import pygame as pg
from src.scenes.scene import Scene

class BattleScene(Scene):
    def __init__(self, player, enemy, background_path: str):
        super().__init__()
        self.player = player
        self.enemy = enemy

        # ===== 載入背景圖 =====
        self.background = pg.image.load(background_path).convert()
        self.screen_width, self.screen_height = pg.display.get_surface().get_size()
        self.background = pg.transform.smoothscale(self.background, (self.screen_width, self.screen_height))

        # ===== 狀態控制 =====
        self.turn = "player"  # player 或 enemy
        self.font = pg.font.SysFont(None, 36)

    def enter(self) -> None:
        # 可以在進入戰鬥場景時播放戰鬥BGM
        pass

    def exit(self) -> None:
        # 離開戰鬥場景時停止BGM
        pass

    def update(self, dt: float) -> None:
        # 目前先不做回合制
        pass

    def handle_event(self, event: pg.event.Event) -> None:
        # 目前先沒有操作
        pass

    def draw(self, screen: pg.Surface) -> None:
        # ===== 畫背景 =====
        screen.blit(self.background, (0, 0))

        # ===== 畫文字提示 =====
        text_surface = self.font.render("Battle Scene: Player vs Enemy", True, (255, 255, 255))
        screen.blit(text_surface, (50, 50))
