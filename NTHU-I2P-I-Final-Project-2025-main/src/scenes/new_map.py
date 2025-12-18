import pygame as pg
from src.scenes.scene import Scene  # 如果你用的是 Scene 作為基底

class NewMapScene(Scene):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine  # 保存 Engine 物件

        # 10x10 地圖（最小合法）
        self.tile_size = 32
        self.map_width = 10
        self.map_height = 10

        # 用數字代表 tile
        self.map_data = [
            [0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,0],
            [0,1,0,0,0,0,0,0,1,0],
            [0,1,0,0,0,0,0,0,1,0],
            [0,1,0,0,0,0,0,0,1,0],
            [0,1,0,0,0,0,0,0,1,0],
            [0,1,0,0,0,0,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
        ]

    def update(self, dt):
        # 這裡你可以取得玩家資料，如果 engine 有 player
        player = getattr(self.engine, "game_manager", None)
        if player and getattr(player, "player", None):
            px, py = player.player.position.x, player.player.position.y
            # 可以用 px, py 做碰撞或事件判定
            # 例如碰到傳送點就切換場景
            TS = self.tile_size
            self.teleport_tile = pg.Rect(px + 5*TS, py, TS, TS)  # 傳送格子

    def draw(self, screen):
        screen.fill((50, 50, 50))

        for y in range(self.map_height):
            for x in range(self.map_width):
                color = (200, 200, 200) if self.map_data[y][x] == 0 else (100, 100, 255)
                rect = pg.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pg.draw.rect(screen, color, rect)

        # 畫傳送格子
        if hasattr(self, "teleport_tile"):
            pg.draw.rect(screen, (255, 0, 0), self.teleport_tile)
            font = pg.font.SysFont(None, 24)
            text = font.render("TELEPORT", True, (255, 255, 255))
            screen.blit(text, (self.teleport_tile.x, self.teleport_tile.y))
