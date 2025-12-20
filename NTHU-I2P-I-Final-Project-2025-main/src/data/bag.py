import pygame as pg
from src.utils.definition import Monster, Item


# 用怪獸名字對應元素的字典
NAME_TO_ELEMENT = {
    "Pikachu": "Electric",
    "Charizard": "Fire",
    "Blastoise": "Water",
    "Venusaur": "Grass",
    "Gengar": "Ghost",
    "Dragonite": "Ice"
}


class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(
        self,
        monsters_data: list[Monster] | None = None,
        items_data: list[Item] | None = None,
        money: int = 1000
    ):
        # 寶可夢 / 角色
        self._monsters_data = monsters_data if monsters_data else []

        # 物品
        self._items_data = items_data if items_data else []

        # 金錢（商店同步用）
        self.money = money

    # ===== 基本存取 =====
    @property
    def monsters(self) -> list[Monster]:
        return self._monsters_data

    @property
    def items(self) -> list[Item]:
        return self._items_data

    # ===== 更新 / 繪製（保留給之後擴充）=====
    def update(self, dt: float):
        pass

    def draw(self, screen: pg.Surface):
        pass

    # ===== Item 操作（商店同步核心）=====
    def get_item(self, name: str) -> Item | None:
        for item in self._items_data:
            if item.get("name") == name:
                return item
        return None

    def has_item(self, name: str, count: int = 1) -> bool:
        item = self.get_item(name)
        return item is not None and item.get("count", 0) >= count

    def add_item(self, name: str, count: int = 1, sprite_path: str = ""):
        item = self.get_item(name)
        if item:
            item["count"] += count
        else:
            self._items_data.append({
                "name": name,
                "count": count,
                "sprite_path": sprite_path
            })

    def remove_item(self, name: str, count: int = 1) -> bool:
        item = self.get_item(name)
        if not item or item["count"] < count:
            return False

        item["count"] -= count
        if item["count"] <= 0:
            self._items_data.remove(item)
        return True

    # ===== 存檔用 =====
    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": [
                {
                    "name": m.get("name", "Unknown"),
                    "level": m.get("level", 1),
                    "hp": m.get("hp", 0),
                    "max_hp": m.get("max_hp", 0),
                    "element": m.get("element", NAME_TO_ELEMENT.get(m.get("name"), "Unknown")),
                    "sprite_path": m.get("sprite_path", ""),
                    "evolves_to": m.get("evolves_to")
                } for m in self._monsters_data
            ],
            "items": [
                {
                    "name": i.get("name", "Unknown"),
                    "count": i.get("count", 1),
                    "sprite_path": i.get("sprite_path", "")
                } for i in self._items_data
            ],
            "money": self.money
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        # ===== Monsters =====
        raw_monsters = data.get("monsters") or []
        monsters: list[Monster] = []
        for m in raw_monsters:
            if isinstance(m, dict):
                monsters.append({
                    "name": m.get("name", "Unknown"),
                    "level": m.get("level", 1),
                    "hp": m.get("hp", 0),
                    "max_hp": m.get("max_hp", 0),
                    "element": m.get("element") or NAME_TO_ELEMENT.get(m.get("name"), "Unknown"),
                    "sprite_path": m.get("sprite_path", ""),
                    "evolves_to": m.get("evolves_to")
                })
            else:
                monsters.append(m)

        # ===== Items =====
        raw_items = data.get("items") or []
        items: list[Item] = []
        for i in raw_items:
            if isinstance(i, dict):
                items.append({
                    "name": i.get("name", "Unknown"),
                    "count": i.get("count", 1),
                    "sprite_path": i.get("sprite_path", "")
                })
            else:
                items.append(i)

        # ===== Money =====
        money = data.get("money", 1000)

        return cls(monsters, items, money)
    def add_monster(self, monster: Monster):
        self._monsters_data.append(monster)