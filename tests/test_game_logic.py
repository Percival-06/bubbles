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
from entities.bubble import Bubble
from settings import MAX_ENERGY, POLLUTION_LIMIT
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


if __name__ == "__main__":
    unittest.main()
