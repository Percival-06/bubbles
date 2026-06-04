# Level Detail Card Design

## Goal
Improve the level selection screen by showing a transparent glass detail panel beside the selected level node.

## Behavior
When a level node is hovered or selected with keyboard navigation, the screen shows a detail card near the node. The card contains a miniature map on the left and the level title plus description on the right. Locked levels show the existing locked hint instead of the normal description.

## Visual Design
The detail card uses the same ocean-glass language as existing menu buttons: translucent blue fill, soft highlight, white inner border, and restrained glow. The card is clamped inside the screen so nodes near the right edge do not push it off-screen.

## Mini Map
The mini map is rendered from `world/levels/*.json` data through `Level(level_id)`. Platforms, hazards, start point, end point, energy seeds, and small bubbles are scaled into the thumbnail area.

## Scope
Modify only the level selection menu rendering. Do not add image assets or change gameplay logic.
