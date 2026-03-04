"""
World class module.

Manages all items in the game world (rooms, entities, items, etc.)


* Creates the level layout.
  > Includes saving and loading the game.

* Calls the loop of each respective entity.
* Handles requests its aggregates.

Ideally I believe there should only be one world at a time, managing levels, a single player, etc.
(makes sense, let me know)
"""
import typing_extensions
import pygame
from pygame import locals

from rat import Rat
from bubble import Bubble


class World:
    """
    Object that handles the game world itself. Recieves calls and sends back data to entities.
    Singleton?
    """
    __slots__ = ["_player", "_bubbles"]

    def __init__(self) -> None:
        self._player : Rat = Rat()
        self._bubbles : list[Bubble] = list[Bubble]()

    def loop(self) -> None:
        self._player.loop()
        for bubble in self._bubbles:
            bubble.loop()
