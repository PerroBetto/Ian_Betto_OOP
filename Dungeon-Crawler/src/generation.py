from structures import Room, Dungeon

import random
import pygame
from pygame import locals

class Generation:
    def __init__(self):
        self.rooms: dict = Dungeon.rooms
        self.seed: int = Dungeon.seed()
        self.rng = random.Random(self.seed())
        self.sel_img = ""


    def Apply_textures(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for room in self.rooms.values():
            if room[room.room_type] is not "boss":
                if room[room.x, room.y]

    def Ran_wall(self):
        
        for i in range(3):
            wall_type = self.rng.choice(3)
            if wall_type is 1:
                sel_img += ""
            if wall_type is 2:
                pass
            if wall_type is 3:
                pass
                