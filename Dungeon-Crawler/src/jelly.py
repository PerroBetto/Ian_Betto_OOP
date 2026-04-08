"""FIXME"""
from pathlib import Path
from typing import Any

import pygame
from pygame import Vector2, Surface

from entity import Entity


class Jelly(Entity):
    """
    Simple enemy:
    * detect the distance to the player
    * if player is within distance, move towards them
    * else, don't move, just stay in place
    """
    _DIST_DETECT: float = 350.0
    _MOVE_INTERVAL: float = 2  # measured in seconds

    __slots__: list[str] = ["_move_timer"]  # float

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(0, 0),
                 speed: float = 100,
                 clamp_speed: float = 300,
                 friction: float = 5,
                 HP: int | None = None,
                 assets: dict[str, Surface] | None = None,
                 image: Surface | None = None,
                 anim_timer: float = 100) -> None:

        self._move_timer: float = self._MOVE_INTERVAL

        super().__init__(world, friction=friction)

# ---- base ----

    def loop(self, delta: float, move: Vector2 | None = None) -> None:
        return super().loop(delta, self.jelly_move(delta))

# ---- search for player ----

    def jelly_move(self, delta: float) -> Vector2:
        """
        1. Search for player position
            * if found, move to player
            * else, stay in place

        2. touching player?
            * deal damage
        """
        player: Vector2 = self._world.entity_action(self, "get_player")
        diff: Vector2 = Vector2(player.x - self._position.x, player.y - self._position.y)

        # use the magnitude of the difference to get the distance.
        # check using distance detect constant
        distance: float = diff.magnitude()
        if distance == 0:
            distance = 0.00001
        direction: Vector2 = diff / distance

        if distance <= self._DIST_DETECT:
            # Move towards the player once timer
            # reached zero.
            self._move_timer -= delta
            if self._move_timer <= 0.0:
                self._move_timer = self._MOVE_INTERVAL
                return Vector2(direction.x * self.speed, direction.y * self.speed)

        return Vector2()
