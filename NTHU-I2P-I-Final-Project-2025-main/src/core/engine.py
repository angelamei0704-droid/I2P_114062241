import pygame as pg
from src.utils import GameSettings, Logger
from .services import scene_manager, input_manager
from src.scenes.menu_scene import MenuScene
from src.scenes.game_scene import GameScene
from src.scenes.setting_scene import SettingsScene  # 導入設置場景
from src.scenes.battle_scene import BattleScene  # 新增
from src.scenes.catch_pokemon_scene import CatchPokemonScene
from src.scenes.new_map import NewMapScene  # 新增：新地圖場景

class Engine:
    screen: pg.Surface  # 遊戲螢幕
    clock: pg.time.Clock  # FPS 控制
    running: bool  # 遊戲運行狀態

    def __init__(self):
        Logger.info("Initializing Engine")
        pg.init()
        self.screen = pg.display.set_mode(
            (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT)
        )
        self.clock = pg.time.Clock()
        self.running = True
        pg.display.set_caption(GameSettings.TITLE)

        # ===== 註冊場景 =====
        scene_manager.register_scene("menu", MenuScene())
        scene_manager.register_scene("game", GameScene())
        scene_manager.register_scene("settings", SettingsScene())  
        scene_manager.register_scene("battle", BattleScene(scene_manager)) 
        scene_manager.register_scene("catch_pokemon", CatchPokemonScene(scene_manager))
        scene_manager.register_scene("new_map", NewMapScene(self))  # 註冊 NewMapScene

        # 預設進入主選單
        scene_manager.change_scene("menu")

    def run(self):
        Logger.info("Running the Game Loop ...")
        while self.running:
            dt = self.clock.tick(GameSettings.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

    def handle_events(self):
        input_manager.reset()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            # ===== 傳給你的 input_manager =====
            input_manager.handle_events(event)

            # ===== 傳給目前場景 =====
            scene_manager.handle_event(event)

            # ===== Debug log: 打印事件 =====
            # Logger.info(f"Event: {event}")  # 可開啟查看所有事件

    def update(self, dt: float):
        # ===== 更新當前場景 =====
        scene_manager.update(dt)

    def render(self):
        # ===== 清空畫面 =====
        self.screen.fill((0, 0, 0))

        # ===== 畫當前場景 =====
        scene_manager.draw(self.screen)

        # ===== 更新螢幕 =====
        pg.display.flip()
