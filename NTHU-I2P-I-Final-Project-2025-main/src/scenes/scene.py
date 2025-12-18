from __future__ import annotations
import pygame as pg

class Scene:
    def __init__(self) -> None:
        ...

    def enter(self) -> None:
        ...

    def exit(self) -> None:
        ...

    def update(self, dt: float) -> None:
        ...

    def draw(self, screen: pg.Surface) -> None:
        ...

    # ===== 新增 handle_event =====
    def handle_event(self, event: pg.event.Event) -> None:
        """處理事件，預設為空，可由子類別 override"""
        pass
