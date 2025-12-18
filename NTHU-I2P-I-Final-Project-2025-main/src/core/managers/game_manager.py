from __future__ import annotations
from src.utils import Logger, GameSettings, Position, Teleport
import json, os
import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maps.map import Map
    from src.entities.player import Player
    from src.entities.enemy_trainer import EnemyTrainer
    from src.data.bag import Bag

class GameManager:
    player: Player | None
    enemy_trainers: dict[str, list[EnemyTrainer]]
    bag: "Bag"
    current_map_key: str
    maps: dict[str, Map]
    should_change_scene: bool
    next_map: str
    player_spawns: dict[str, Position]

    def __init__(self, maps: dict[str, Map], start_map: str, 
                 player: Player | None,
                 enemy_trainers: dict[str, list[EnemyTrainer]], 
                 bag: Bag | None = None):
        from src.data.bag import Bag
        self.maps = maps
        self.current_map_key = start_map
        self.player = player
        # ✅ 保證每個 map 都有 enemy_trainers list，即使沒有 NPC
        self.enemy_trainers = {k: enemy_trainers.get(k, []) for k in maps.keys()}
        self.bag = bag if bag else Bag([], [])
        self.should_change_scene = False
        self.next_map = ""
        self.player_spawns = {k: m.spawn for k, m in maps.items()}
        # Debug: print loaded maps
        print("Loaded maps:", list(self.maps.keys()))
        print("Start map:", self.current_map_key)

    @property
    def current_map(self) -> Map:
        return self.maps[self.current_map_key]
        
    @property
    def current_enemy_trainers(self) -> list[EnemyTrainer]:
        return self.enemy_trainers.get(self.current_map_key, [])
        
    @property
    def current_teleporter(self) -> list[Teleport]:
        return self.maps[self.current_map_key].teleporters

    def switch_map(self, target: str) -> None:
        if target not in self.maps:
            Logger.warning(f"Map '{target}' not loaded; cannot switch.")
            return
        self.next_map = target
        self.should_change_scene = True

    def try_switch_map(self) -> None:
        if not self.should_change_scene:
            return
        self.current_map_key = self.next_map
        self.next_map = ""
        self.should_change_scene = False

        # 切換地圖後設定玩家出生點
        if self.player:
            spawn = self.maps[self.current_map_key].spawn
            self.player.position = Position(spawn.x, spawn.y)
        Logger.info(f"Switched map to {self.current_map_key}")
    
    def check_teleport(self) -> None:
        if not self.player:
            return
            # 玩家目前的 tile（格子座標）
        px = self.player.position.x // GameSettings.TILE_SIZE
        py = self.player.position.y // GameSettings.TILE_SIZE
        # 目前地圖的 teleport 列表
        tps = getattr(self.current_map, "teleporters", [])
        for tp in tps:
            if tp.x == px and tp.y == py:
                Logger.info(f"Teleport triggered at ({px}, {py}) → {tp.destination}")
                # 切換地圖
                self.switch_map(tp.destination)
                # 若 teleport JSON 有 spawn_x / spawn_y
                spawn_x = getattr(tp, "spawn_x", None)
                spawn_y = getattr(tp, "spawn_y", None)
                if spawn_x is None or spawn_y is None:
                    target_spawn = self.maps[tp.destination].spawn
                    spawn_x = target_spawn.x // GameSettings.TILE_SIZE
                    spawn_y = target_spawn.y // GameSettings.TILE_SIZE
                self.player.position = Position(
                spawn_x * GameSettings.TILE_SIZE,
                spawn_y * GameSettings.TILE_SIZE
                )
                return


    def check_collision(self, rect: pg.Rect) -> bool:
        if self.maps[self.current_map_key].check_collision(rect):
            return True
        for entity in self.enemy_trainers.get(self.current_map_key, []):
            if rect.colliderect(entity.animation.rect):
                return True
        return False

    def save(self, path: str) -> None:
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            Logger.info(f"Game saved to {path}")
        except Exception as e:
            Logger.warning(f"Failed to save game: {e}")

    @classmethod
    def load(cls, path: str) -> "GameManager | None":
        if not os.path.exists(path):
            Logger.error(f"No file found: {path}")
            return None
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, object]:
        map_blocks: list[dict[str, object]] = []
        for key, m in self.maps.items():
            block = m.to_dict()
            block["enemy_trainers"] = [t.to_dict() for t in self.enemy_trainers.get(key, [])]
            map_blocks.append(block)
        return {
            "map": map_blocks,
            "current_map": self.current_map_key,
            "player": self.player.to_dict() if self.player else None,
            "bag": self.bag.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "GameManager":
        from src.maps.map import Map
        from src.entities.player import Player
        from src.entities.enemy_trainer import EnemyTrainer
        from src.data.bag import Bag

        maps_data = data["map"]
        maps: dict[str, Map] = {}
        trainers: dict[str, list[EnemyTrainer]] = {}

        for entry in maps_data:
            path = entry["path"]
            maps[path] = Map.from_dict(entry)

        current_map = data["current_map"]
        gm = cls(maps, current_map, None, trainers, bag=None)

        for m in data["map"]:
            raw_data = m["enemy_trainers"]
            gm.enemy_trainers[m["path"]] = [EnemyTrainer.from_dict(t, gm) for t in raw_data]

        if data.get("player"):
            gm.player = Player.from_dict(data["player"], gm)

        gm.bag = Bag.from_dict(data.get("bag", {})) if data.get("bag") else Bag([], [])
        gm.player_spawns = {k: maps[k].spawn for k in maps}
        return gm
