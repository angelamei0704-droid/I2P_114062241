'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''
#架構:玩家的操作 → event → handle_event → 場景內物件的反應
import pygame as pg
from src.utils import GameSettings
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager  # 加入 sound_manager 控制音量

class SettingsScene(Scene):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self._create_ui()
        self.dragging_slider = False  # 拖動狀態

    def _create_ui(self):
        # 返回按鈕
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px, py, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )

        # Checkbox
        self.checkbox_music = True
        self.checkbox_rect = pg.Rect(GameSettings.SCREEN_WIDTH // 2 - 150, 220, 30, 30)

        # Slider
        self.volume = 80
        self.slider_rect = pg.Rect(GameSettings.SCREEN_WIDTH // 2 - 150, 280, 300, 10)
        self.slider_knob_radius = 12

        # 初始化 BGM 音量
        if sound_manager.current_bgm:
            sound_manager.current_bgm.set_volume(self.volume / 100)

    # ===== 這裡改名為 handle_event（你的 Engine 是呼叫 handle_event）=====
    def handle_event(self, event):
        super().handle_event(event)   # 保留 Scene 基礎事件
        mx, my = pg.mouse.get_pos()

        # Back 按鈕事件
        self.back_button.handle_event(event)

        # knob 位置
        knob_x = int(self.slider_rect.x + self.volume / 100 * self.slider_rect.width)
        knob_y = self.slider_rect.centery

        # ===== MOUSE DOWN =====
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Checkbox toggle
            if self.checkbox_rect.collidepoint(mx, my):
                self.checkbox_music = not self.checkbox_music
                # 靜音或恢復音樂
                if self.checkbox_music:
                    if sound_manager.current_bgm:
                        sound_manager.current_bgm.set_volume(self.volume / 100)
                else:
                    if sound_manager.current_bgm:
                        sound_manager.current_bgm.set_volume(0)

            # knob 點擊判定
            distance = ((mx - knob_x)**2 + (my - knob_y)**2) ** 0.5
            if distance <= self.slider_knob_radius:
                self.dragging_slider = True

            # 點擊滑桿軌道 -> 跳到位置 & 可以拖動
            elif self.slider_rect.collidepoint(mx, my):
                relative_x = mx - self.slider_rect.x
                self.volume = max(0, min(100, int(relative_x / self.slider_rect.width * 100)))
                self.dragging_slider = True
                # 調整音量（如果未靜音）
                if self.checkbox_music and sound_manager.current_bgm:
                    sound_manager.current_bgm.set_volume(self.volume / 100)

        # ===== MOUSE UP =====
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.dragging_slider = False

        # ===== MOUSE MOTION =====
        elif event.type == pg.MOUSEMOTION:
            if self.dragging_slider:
                relative_x = mx - self.slider_rect.x
                self.volume = max(0, min(100, int(relative_x / self.slider_rect.width * 100)))
                # 調整音量（如果未靜音）
                if self.checkbox_music and sound_manager.current_bgm:
                    sound_manager.current_bgm.set_volume(self.volume / 100)

    def update(self, dt):
        self.back_button.update(dt)

    def draw(self, screen):
        screen.fill((50, 50, 80))

        # 標題
        font = pg.font.SysFont(None, 48)
        title_text = font.render("Settings", True, (255, 255, 255))
        screen.blit(title_text, title_text.get_rect(center=(GameSettings.SCREEN_WIDTH//2, 150)))

        # ===== Checkbox =====
        pg.draw.rect(screen, (255,255,255), self.checkbox_rect, 2)
        if self.checkbox_music:
            pg.draw.line(screen, (255,255,255), self.checkbox_rect.topleft, self.checkbox_rect.bottomright, 3)
            pg.draw.line(screen, (255,255,255), self.checkbox_rect.bottomleft, self.checkbox_rect.topright, 3)

        option_font = pg.font.SysFont(None, 36)
        text_surface = option_font.render("Music On/Off", True, (200,200,200))
        screen.blit(text_surface, (self.checkbox_rect.right + 10, self.checkbox_rect.y))

        # ===== Slider =====
        pg.draw.rect(screen, (200,200,200), self.slider_rect)

        knob_x = self.slider_rect.x + self.volume / 100 * self.slider_rect.width
        pg.draw.circle(screen, (255,255,255), (int(knob_x), self.slider_rect.centery), self.slider_knob_radius)

        vol_text = option_font.render(f"Volume: {self.volume}%", True, (200,200,200))
        screen.blit(vol_text, (self.slider_rect.right + 20, self.slider_rect.y - 10))

        # ===== Back Button =====
        self.back_button.draw(screen)
