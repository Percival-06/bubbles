import json
import os
import sys
import tempfile
import types
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    import pygame  # noqa: F401
except ModuleNotFoundError:
    pygame_stub = types.ModuleType("pygame")

    class Rect:
        def __init__(self, x, y, w, h):
            self.x = x
            self.y = y
            self.w = w
            self.h = h

        def colliderect(self, other):
            return not (
                self.x + self.w < other.x
                or other.x + other.w < self.x
                or self.y + self.h < other.y
                or other.y + other.h < self.y
            )

        def collidepoint(self, pos):
            return self.x <= pos[0] <= self.x + self.w and self.y <= pos[1] <= self.y + self.h

    pygame_stub.Rect = Rect
    pygame_stub.KEYDOWN = 1
    pygame_stub.MOUSEBUTTONDOWN = 2
    pygame_stub.K_LEFT = 276
    pygame_stub.K_RIGHT = 275
    pygame_stub.K_a = 97
    pygame_stub.K_d = 100
    pygame_stub.K_x = 120
    pygame_stub.key = types.SimpleNamespace(get_pressed=lambda: {})
    pygame_stub.Surface = lambda *args, **kwargs: None
    pygame_stub.SRCALPHA = 1
    pygame_stub.draw = types.SimpleNamespace(circle=lambda *args, **kwargs: None)
    sys.modules["pygame"] = pygame_stub

import pygame

from core.save_manager import SaveManager
from core.scene_manager import SceneManager
from entities.bubble import Bubble
from settings import MAX_ENERGY, POLLUTION_LIMIT
from ui.menus import ButtonMenu, SettingsMenu
from ui import background as background_ui
from ui.renderer import Renderer
from ui.stars import badge_star_count
from world.level_parser import Level


class SaveManagerTests(unittest.TestCase):
    def test_new_save_starts_with_training_unlocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            save = SaveManager(os.path.join(tmp, "save.json"))

            self.assertEqual(save.data["unlocked_level"], "training")
            self.assertTrue(save.is_unlocked("training"))
            self.assertFalse(save.is_unlocked("mid_sea"))

    def test_unlock_and_badge_progress_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            save = SaveManager(path)
            save.unlock_next_after("training")
            save.record_result("training", "gold")

            reloaded = SaveManager(path)

            self.assertTrue(reloaded.is_unlocked("deep_sea"))
            self.assertEqual(reloaded.data["best_badges"]["training"], "gold")


class LevelTests(unittest.TestCase):
    def test_level_catalog_has_three_ordered_stages(self):
        ids = [info["id"] for info in Level.catalog()]

        self.assertEqual(ids[:3], ["training", "deep_sea", "mid_sea"])

    def test_collectibles_track_energy_and_bubble_pickups(self):
        level = Level("training")
        player = Bubble(*level.start_pos)
        level.collectibles = [[player.x, player.y, "energy"], [player.x, player.y, "bubble"]]

        before_volume = player.volume
        stats = level.handle_collectibles(player)

        self.assertEqual(stats["energy"], 1)
        self.assertEqual(stats["bubble"], 1)
        self.assertEqual(level.collected_energy, 1)
        self.assertGreater(player.volume, before_volume)
        self.assertEqual(len(level.collectibles), 0)

    def test_hazard_collision_pollutes_player_until_failure(self):
        level = Level("deep_sea")
        player = Bubble(*level.start_pos)
        level.hazards = [[player.x - 20, player.y - 20, 40, 40]]

        touched = level.apply_hazards(player, 1.0)

        self.assertTrue(touched)
        self.assertGreater(player.contamination, 0)
        player.contamination = POLLUTION_LIMIT
        self.assertTrue(player.has_failed())


class BubbleTests(unittest.TestCase):
    def test_release_bubble_reduces_volume_and_event_is_single_owner(self):
        bubble = Bubble(100, 100)
        before = bubble.volume

        self.assertTrue(bubble.release())
        self.assertLess(bubble.volume, before)
        self.assertFalse(bubble.handle_event(type("Event", (), {"type": -1})()))

    def test_energy_seed_restores_energy_without_exceeding_max(self):
        bubble = Bubble(100, 100)
        bubble.energy = MAX_ENERGY - 1

        bubble.collect_energy(20)

        self.assertEqual(bubble.energy, MAX_ENERGY)

    def test_absorbed_bubble_rises_in_screen_coordinates(self):
        class NoPressedKeys:
            def __getitem__(self, key):
                return False

        bubble = Bubble(100, 100)
        bubble.absorb()
        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: NoPressedKeys()

        try:
            bubble.update(1 / 60, None)
        finally:
            pygame.key.get_pressed = original_get_pressed

        self.assertLess(bubble.y, 100)

    def test_new_bubble_rises_noticeably_without_input(self):
        class NoPressedKeys:
            def __getitem__(self, key):
                return False

        bubble = Bubble(100, 300)
        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: NoPressedKeys()

        try:
            for _ in range(60):
                bubble.update(1 / 60, None)
        finally:
            pygame.key.get_pressed = original_get_pressed

        rise_distance = 300 - bubble.y
        self.assertGreater(rise_distance, 35)
        self.assertLess(rise_distance, 50)

    def test_platform_blocks_bubble_from_below(self):
        class NoPressedKeys:
            def __getitem__(self, key):
                return False

        level = Level("training")
        level.platforms = [[0, 80, 200, 20]]
        bubble = Bubble(100, 150)
        bubble.vy = -300
        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: NoPressedKeys()

        try:
            bubble.update(0.2, level)
        finally:
            pygame.key.get_pressed = original_get_pressed

        self.assertGreaterEqual(bubble.y - bubble.radius, 100)
        self.assertEqual(bubble.vy, 0)

    def test_platform_blocks_bubble_from_side(self):
        class RightPressedKeys:
            def __getitem__(self, key):
                return key in (pygame.K_RIGHT, pygame.K_d)

        level = Level("training")
        level.platforms = [[140, 0, 20, 200]]
        bubble = Bubble(100, 100)
        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: RightPressedKeys()

        try:
            bubble.update(0.5, level)
        finally:
            pygame.key.get_pressed = original_get_pressed

        self.assertLessEqual(bubble.x + bubble.radius, 140)
        self.assertEqual(bubble.vx, 0)


class MenuStyleTests(unittest.TestCase):
    def test_glass_button_draws_translucent_highlight_and_border(self):
        menu = ButtonMenu.__new__(ButtonMenu)
        draw_button = getattr(menu, "_draw_glass_button", None)

        self.assertTrue(callable(draw_button))

        if not hasattr(pygame, "init"):
            return

        pygame.init()
        screen = pygame.Surface((360, 120), pygame.SRCALPHA)
        rect = pygame.Rect(25, 25, 310, 48)

        draw_button(screen, rect, hovered=True, disabled=False)

        center = screen.get_at(rect.center)
        highlight = screen.get_at((rect.centerx, rect.top + 8))
        border = screen.get_at((rect.left + 1, rect.centery))

        self.assertGreater(center.a, 0)
        self.assertGreater(highlight.a, center.a)
        self.assertGreater(border.a, center.a)


class SceneManagerMenuTests(unittest.TestCase):
    def test_energy_seed_collection_triggers_star_animation(self):
        class NoPressedKeys:
            def __getitem__(self, key):
                return False

        manager = SceneManager.__new__(SceneManager)
        manager.scene = "game"
        manager.player = Bubble(100, 100)
        manager.current_level = Level("training")
        manager.current_level.collectibles = [[100, 100, "energy"]]
        manager.current_level.hazards = []
        manager.current_level.end_pos = (700, 50)
        manager.renderer = type("Renderer", (), {
            "triggered": 0,
            "trigger_energy_collection": lambda self, level, count=1: setattr(self, "triggered", count),
        })()
        manager.finish_level = lambda *args, **kwargs: None

        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: NoPressedKeys()
        try:
            manager.update(1 / 60)
        finally:
            pygame.key.get_pressed = original_get_pressed

        self.assertEqual(manager.renderer.triggered, 1)

    def test_game_settings_button_opens_settings_and_returns_to_game(self):
        manager = SceneManager.__new__(SceneManager)
        manager.scene = "game"
        manager.player = object()
        manager.current_level = object()
        manager.settings_return_scene = "menu"
        manager.settings_menu = type("SettingsMenu", (), {
            "refresh": lambda self, return_scene="menu": None,
            "handle_event": lambda self, event: "back",
        })()
        manager.renderer = type("Renderer", (), {
            "is_settings_button_hit": lambda self, pos: True,
        })()

        click = type("Event", (), {
            "type": pygame.MOUSEBUTTONDOWN,
            "button": 1,
            "pos": (780, 24),
        })()
        manager._handle_game_event(click)

        self.assertEqual(manager.scene, "settings")
        self.assertEqual(manager.settings_return_scene, "game")

        manager._handle_settings_event(type("Event", (), {"type": -1})())

        self.assertEqual(manager.scene, "game")

    def test_game_settings_menu_action_returns_to_main_menu(self):
        manager = SceneManager.__new__(SceneManager)
        manager.scene = "settings"
        manager.settings_return_scene = "game"
        manager.settings_menu = type("SettingsMenu", (), {
            "handle_event": lambda self, event: "menu",
        })()

        manager._handle_settings_event(type("Event", (), {"type": -1})())

        self.assertEqual(manager.scene, "menu")
        self.assertEqual(manager.settings_return_scene, "menu")

    def test_game_settings_menu_shows_resume_and_main_menu_actions(self):
        captured = {}
        menu = SettingsMenu.__new__(SettingsMenu)
        menu.save_manager = type("SaveManager", (), {
            "data": {"settings": {"music": True, "sfx": False}},
        })()
        menu.set_options = lambda options: captured.setdefault("options", options)

        menu.refresh(return_scene="game")

        labels = [option["label"] for option in captured["options"]]
        actions = [option["action"] for option in captured["options"]]
        self.assertIn("返回游戏", labels)
        self.assertIn("返回主菜单", labels)
        self.assertIn("back", actions)
        self.assertIn("menu", actions)


class RendererHudTests(unittest.TestCase):
    def test_badges_map_to_star_counts(self):
        self.assertEqual(badge_star_count("gold"), 3)
        self.assertEqual(badge_star_count("silver"), 2)
        self.assertEqual(badge_star_count("bronze"), 1)
        self.assertEqual(badge_star_count("none"), 0)

    def test_settings_button_hit_area_is_top_right_only(self):
        renderer = Renderer.__new__(Renderer)

        self.assertTrue(renderer.is_settings_button_hit((774, 26)))
        self.assertFalse(renderer.is_settings_button_hit((730, 26)))
        self.assertFalse(renderer.is_settings_button_hit((774, 70)))


class BackgroundRenderTests(unittest.TestCase):
    def test_dynamic_background_layers_are_reused_between_frames(self):
        class FakeSurface:
            def __init__(self, size, flags=0):
                self.size = size
                self.flags = flags

            def get_size(self):
                return self.size

            def get_width(self):
                return self.size[0]

            def get_height(self):
                return self.size[1]

            def fill(self, *args, **kwargs):
                return None

            def blit(self, *args, **kwargs):
                return None

        fake_pygame = types.SimpleNamespace(
            SRCALPHA=1,
            Surface=FakeSurface,
            draw=types.SimpleNamespace(
                polygon=lambda *args, **kwargs: None,
                lines=lambda *args, **kwargs: None,
            ),
            time=types.SimpleNamespace(get_ticks=lambda: 1000),
        )
        screen = FakeSurface((240, 180))
        fake_background = FakeSurface((240, 180))
        original_pygame = background_ui.pygame
        original_get_background_image = background_ui._get_background_image
        created_sizes = []

        def tracked_surface(*args, **kwargs):
            created_sizes.append(args[0])
            return FakeSurface(*args, **kwargs)

        if hasattr(background_ui, "_dynamic_layers"):
            background_ui._dynamic_layers.clear()

        fake_pygame.Surface = tracked_surface
        background_ui.pygame = fake_pygame
        background_ui._get_background_image = lambda size: fake_background
        try:
            background_ui.draw_ocean_background(screen, elapsed=1.0)
            first_count = len(created_sizes)
            background_ui.draw_ocean_background(screen, elapsed=1.1)
            second_count = len(created_sizes) - first_count
        finally:
            background_ui.pygame = original_pygame
            background_ui._get_background_image = original_get_background_image
            if hasattr(background_ui, "_dynamic_layers"):
                background_ui._dynamic_layers.clear()

        self.assertGreaterEqual(first_count, 2)
        self.assertEqual(second_count, 0)


if __name__ == "__main__":
    unittest.main()
