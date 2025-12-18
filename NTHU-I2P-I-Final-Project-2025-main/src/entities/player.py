from __future__ import annotations 
import pygame as pg
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager
    _is_moving: bool = True  # 添加移動狀態標誌
    rect: pg.Rect  # 新增 rect 屬性

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)
        self._is_moving = True
        # ✅ 初始化 rect，大小和 Tile Size 一樣
        self.rect = pg.Rect(self.position.x, self.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)

    @override
    def update(self, dt: float) -> None:
        if not self._is_moving:
            # 如果玩家不能移動，直接返回
            super().update(dt)
            # 同步 rect 位置
            self.rect.topleft = (self.position.x, self.position.y)
            return

        '''
        [TODO HACKATHON 2]
        Calculate the distance change, and then normalize the distance
        
        [TODO HACKATHON 4]
        Check if there is collision, if so try to make the movement smooth
        Hint #1 : use entity.py _snap_to_grid function or create a similar function
        Hint #2 : Beware of glitchy teleportation, you must do
                    1. Update X
                    2. If collide, snap to grid
                    3. Update Y
                    4. If collide, snap to grid
                  instead of update both x, y, then snap to grid
        
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= ...
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += ...
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= ...
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += ...
        
        self.position = ...
        '''
        
        # Check teleportation
        dis = Position(0, 0)

        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1
        
        if dis.x != 0 or dis.y != 0:
            length = math.sqrt(dis.x * dis.x + dis.y * dis.y)
            dis.x /= length
            dis.y /= length
            dis.x *= self.speed * dt
            dis.y *= self.speed * dt
            
            # 創建玩家碰撞矩形
            player_rect = pg.Rect(
                self.position.x,
                self.position.y,
                GameSettings.TILE_SIZE,
                GameSettings.TILE_SIZE
            )
            
            # 先檢查 X 方向移動是否會與敵人碰撞
            temp_rect_x = pg.Rect(
                self.position.x + dis.x,
                self.position.y,
                GameSettings.TILE_SIZE,
                GameSettings.TILE_SIZE
            )
            
            # 再檢查 Y 方向移動是否會與敵人碰撞
            temp_rect_y = pg.Rect(
                self.position.x,
                self.position.y + dis.y,
                GameSettings.TILE_SIZE,
                GameSettings.TILE_SIZE
            )
            
            # 檢查與敵人的碰撞
            enemy_collision_x = False
            enemy_collision_y = False
            
            for enemy in self.game_manager.current_enemy_trainers:
                enemy_rect = pg.Rect(
                    enemy.position.x,
                    enemy.position.y,
                    GameSettings.TILE_SIZE,
                    GameSettings.TILE_SIZE
                )
                
                # 檢查 X 方向移動是否會與敵人碰撞
                if temp_rect_x.colliderect(enemy_rect):
                    enemy_collision_x = True
                    Logger.debug(f"Player would collide with enemy in X direction")
                
                # 檢查 Y 方向移動是否會與敵人碰撞
                if temp_rect_y.colliderect(enemy_rect):
                    enemy_collision_y = True
                    Logger.debug(f"Player would collide with enemy in Y direction")
            
            # 分別處理 X 和 Y 方向的移動
            if not self.game_manager.current_map.check_collision(temp_rect_x) and not enemy_collision_x:
                self.position.x += dis.x
            else:
                self.position.x = self._snap_to_grid(self.position.x)
            
            temp_rect_y = pg.Rect(
                self.position.x,
                self.position.y + dis.y,
                GameSettings.TILE_SIZE,
                GameSettings.TILE_SIZE
            )
            
            enemy_collision_y = False
            for enemy in self.game_manager.current_enemy_trainers:
                enemy_rect = pg.Rect(
                    enemy.position.x,
                    enemy.position.y,
                    GameSettings.TILE_SIZE,
                    GameSettings.TILE_SIZE
                )
                if temp_rect_y.colliderect(enemy_rect):
                    enemy_collision_y = True
                    Logger.debug(f"Player would collide with enemy in Y direction after X move")
            
            if not self.game_manager.current_map.check_collision(temp_rect_y) and not enemy_collision_y:
                self.position.y += dis.y
            else:
                self.position.y = self._snap_to_grid(self.position.y)
            
            player_rect_after = pg.Rect(
                self.position.x,
                self.position.y,
                GameSettings.TILE_SIZE,
                GameSettings.TILE_SIZE
            )
            
            for enemy in self.game_manager.current_enemy_trainers:
                enemy_rect = pg.Rect(
                    enemy.position.x,
                    enemy.position.y,
                    GameSettings.TILE_SIZE,
                    GameSettings.TILE_SIZE
                )
                if player_rect_after.colliderect(enemy_rect):
                    Logger.debug(f"Player collided with enemy at ({enemy.position.x}, {enemy.position.y})")
        
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            dest = tp.destination
            self.game_manager.switch_map(dest)
                
        # ✅ 同步 rect
        self.rect.topleft = (self.position.x, self.position.y)
        super().update(dt)

    def set_movement_enabled(self, enabled: bool):
        """設置玩家是否可以移動"""
        self._is_moving = enabled

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)
