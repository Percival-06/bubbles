import pygame
import sys
from core.save_manager import SaveManager
from entities.bubble import Bubble
from ui.menus import MainMenu, PauseMenu, LevelSelectMenu, SettingsMenu, ResultMenu
from ui.renderer import Renderer
from world.level_parser import Level
from settings import VOLUME_INCREMENT, MAX_ENERGY


class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.scene = "menu"
        self.running = True
        self.save_manager = SaveManager()
        self.main_menu = MainMenu()
        self.pause_menu = PauseMenu()
        self.level_select_menu = LevelSelectMenu(self.save_manager)
        self.settings_menu = SettingsMenu(self.save_manager)
        self.result_menu = ResultMenu()
        self.current_level = None
        self.current_level_name = None
        self.player = None
        self.renderer = Renderer()
        self.last_result = None
        self.settings_return_scene = "menu"

    def handle_event(self, event):
        if self.scene == "menu":
            self._handle_menu_event(event)
        elif self.scene == "level_select":
            self._handle_level_select_event(event)
        elif self.scene == "settings":
            self._handle_settings_event(event)
        elif self.scene == "game":
            self._handle_game_event(event)
        elif self.scene == "pause":
            self._handle_pause_event(event)
        elif self.scene == "result":
            self._handle_result_event(event)

    def _handle_menu_event(self, event):
        result = self.main_menu.handle_event(event)
        if result == "start":
            self.start_game("training")
        elif result == "continue":
            self.start_game(self.save_manager.data["unlocked_level"])
        elif result == "levels":
            self.level_select_menu.refresh()
            self.scene = "level_select"
        elif result == "settings":
            self.settings_return_scene = "menu"
            self.settings_menu.refresh(self.settings_return_scene)
            self.scene = "settings"
        elif result == "quit":
            self.running = False

    def _handle_level_select_event(self, event):
        result = self.level_select_menu.handle_event(event)
        if isinstance(result, tuple) and result[0] == "level":
            self.start_game(result[1])
        elif result == "back":
            self.scene = "menu"

    def _handle_settings_event(self, event):
        result = self.settings_menu.handle_event(event)
        if isinstance(result, tuple) and result[0] == "toggle":
            self.save_manager.toggle_setting(result[1])
            self.settings_menu.refresh(self.settings_return_scene)
        elif result == "back":
            self.scene = self.settings_return_scene
            self.settings_return_scene = "menu"
        elif result == "menu":
            self.scene = "menu"
            self.settings_return_scene = "menu"

    def _handle_game_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.renderer.is_settings_button_hit(event.pos):
                self.settings_return_scene = "game"
                self.settings_menu.refresh(self.settings_return_scene)
                self.scene = "settings"
                return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.scene = "pause"
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            if self.player and self.player.release(VOLUME_INCREMENT):
                self.current_level.add_small_bubble(self.player.x - self.player.radius - 12, self.player.y)
            return
        if self.player:
            self.player.handle_event(event)

    def _handle_pause_event(self, event):
        result = self.pause_menu.handle_event(event)
        if result == "resume":
            self.scene = "game"
        elif result == "restart":
            self.start_game(self.current_level_name)
        elif result == "levels":
            self.level_select_menu.refresh()
            self.scene = "level_select"
        elif result == "menu":
            self.scene = "menu"
        elif result == "quit":
            self.running = False

    def _handle_result_event(self, event):
        result = self.result_menu.handle_event(event)
        if result == "next" and self.last_result and self.last_result.get("next_level"):
            self.start_game(self.last_result["next_level"])
        elif result == "retry":
            self.start_game(self.current_level_name)
        elif result == "levels":
            self.level_select_menu.refresh()
            self.scene = "level_select"
        elif result == "menu" or result == "back":
            self.scene = "menu"

    def update(self, dt):
        if self.scene != "game" or not self.player or not self.current_level:
            return

        self.player.update(dt, self.current_level)
        self.current_level.update(dt)
        collected = self.current_level.handle_collectibles(self.player)
        if collected["energy"]:
            self.renderer.trigger_energy_collection(self.current_level, collected["energy"])
        touched_hazard = self.current_level.apply_hazards(self.player, dt)
        if touched_hazard and hasattr(self.renderer, "trigger_pollution_warning"):
            self.renderer.trigger_pollution_warning()

        if self.player.has_failed():
            reason = "Life seed energy depleted" if self.player.energy <= 0 else "Pollution level too high"
            self.finish_level(False, reason)
        elif self.current_level.is_at_end(self.player):
            self.finish_level(True)

    def render(self, screen):
        if self.scene == "menu":
            self.main_menu.render(screen, "Guide the life seed from the deep sea to land")
        elif self.scene == "level_select":
            self.level_select_menu.render(screen, "Unlocked levels can be replayed")
        elif self.scene == "settings":
            self._render_settings_scene(screen)
        elif self.scene == "game":
            self.renderer.render(screen, self.player, self.current_level)
        elif self.scene == "pause":
            self.renderer.render(screen, self.player, self.current_level)
            self.pause_menu.render(screen)
        elif self.scene == "result":
            self.result_menu.render(screen)

    def _render_settings_scene(self, screen):
        subtitle = "Basic toggles are available"
        if self.settings_return_scene == "game" and self.player and self.current_level:
            self.renderer.render(screen, self.player, self.current_level)
            mask = pygame.Surface((screen.get_width(), screen.get_height()))
            mask.set_alpha(150)
            mask.fill((0, 0, 0))
            screen.blit(mask, (0, 0))
            self.settings_menu.render(screen, subtitle, fill_background=False)
        else:
            self.settings_menu.render(screen, subtitle)

    def start_game(self, level_name):
        self.current_level = Level(level_name)
        self.player = Bubble(*self.current_level.start_pos)
        self.current_level_name = level_name
        self.renderer.reset_level_stars(self.current_level)
        self.scene = "game"

    def finish_level(self, success, reason=""):
        badge = "none"
        if success:
            badge = self._calculate_badge()
            self.save_manager.unlock_next_after(self.current_level_name)
            self.save_manager.record_result(self.current_level_name, badge)
        self.last_result = {
            "success": success,
            "reason": reason,
            "badge": badge,
            "next_level": self.current_level.next_level if success else None,
            "energy_collected": self.current_level.collected_energy,
            "energy_total": self.current_level.total_energy,
        }
        self.result_menu.set_result(self.last_result)
        self.scene = "result"

    def _calculate_badge(self):
        total = max(1, self.current_level.total_energy)
        collect_ratio = self.current_level.collected_energy / total
        energy_ratio = self.player.energy / MAX_ENERGY
        score = collect_ratio * 0.7 + energy_ratio * 0.3
        if score >= 0.85:
            return "gold"
        if score >= 0.55:
            return "silver"
        return "bronze"

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()
