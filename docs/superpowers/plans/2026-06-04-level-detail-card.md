# Level Detail Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a glass detail card with a generated mini map to the level selection screen.

**Architecture:** Keep the feature inside `ui/menus.py` because level selection rendering already lives there. Cache loaded `Level` objects per level id so drawing a thumbnail does not repeatedly parse JSON every frame.

**Tech Stack:** Python, Pygame, existing `Level` JSON parser.

---

### Task 1: Add Detail Card Rendering

**Files:**
- Modify: `ui/menus.py`

- [ ] Add a level preview cache to `LevelSelectMenu.__init__`.
- [ ] Add helpers for text wrapping, glass panel drawing, mini-map drawing, and detail-card positioning.
- [ ] Replace the bottom description render with the new node-side detail card.
- [ ] Run `python -m unittest tests.test_game_logic`.
