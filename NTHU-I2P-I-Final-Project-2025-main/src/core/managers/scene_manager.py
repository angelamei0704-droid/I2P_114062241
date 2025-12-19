import pygame as pg
from src.scenes.scene import Scene
from src.utils import Logger


class SceneManager:
    _scenes: dict[str, Scene]
    _current_scene: Scene | None = None
    _next_scene: str | None = None

    def __init__(self):
        Logger.info("Initializing SceneManager")
        self._scenes = {}
        self.game_state = {
            "bag": {
                "monsters": [
                    {
                        "name": "Pikachu",
                        "element": "Electric",
                        "hp": 100,
                        "max_hp": 100,
                        "attack": 30,
                        "defense": 5
                    }
                ]
            }
        }
    def register_scene(self, name: str, scene: Scene) -> None:
        """註冊場景"""
        self._scenes[name] = scene
        Logger.info(f"Registered scene '{name}'")

    def change_scene(self, scene_name: str) -> None:
        """請求切換場景（會延遲到下一個 update）"""
        if scene_name not in self._scenes:
            raise ValueError(f"Scene '{scene_name}' not found")
        Logger.info(f"Scene change requested: '{scene_name}'")
        self._next_scene = scene_name

    # ===== 新增：給 teleport / 新地圖用 =====
    def change_scene_instance(self, scene: Scene) -> None:
        """
        直接切換到一個新的 Scene instance（不需事先 register）
        適合 teleport 到新地圖
        """
        Logger.info(f"Teleporting to new scene instance: {scene.__class__.__name__}")

        # exit 舊場景
        if self._current_scene:
            self._current_scene.exit()

        # 直接換成新 scene
        self._current_scene = scene
        self._current_scene.enter()

        self._next_scene = None
    # =====================================

    def force_change_scene(self, scene_name: str) -> None:
        """立即切換場景，不等待下一個 update"""
        if scene_name not in self._scenes:
            raise ValueError(f"Scene '{scene_name}' not found")
        Logger.info(f"Force changing scene to '{scene_name}'")
        if self._current_scene:
            self._current_scene.exit()
        self._current_scene = self._scenes[scene_name]
        if self._current_scene:
            self._current_scene.enter()
        self._next_scene = None

    def handle_event(self, event: pg.event.EventType):
        """事件分發給當前場景"""
        if self._next_scene is not None:
            return
        if self._current_scene:
            self._current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self._next_scene is not None:
            self._perform_scene_switch()
        if self._current_scene:
            self._current_scene.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        if self._current_scene:
            self._current_scene.draw(screen)

    def _perform_scene_switch(self) -> None:
        if self._next_scene is None:
            return
        if self._current_scene:
            Logger.info(f"Exiting scene")
            self._current_scene.exit()
        self._current_scene = self._scenes[self._next_scene]
        if self._current_scene:
            Logger.info(f"Entering scene '{self._next_scene}'")
            self._current_scene.enter()
        self._next_scene = None


scene_manager = SceneManager()
