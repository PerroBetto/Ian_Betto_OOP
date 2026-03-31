from structures import Dungeon
from pathlib import Path
import random


class Generation:
    def __init__(self, dungeon: Dungeon | None = None):
        self.dungeon = dungeon
        seed_value = self.dungeon.seed if self.dungeon is not None else None
        self.rng = random.Random(seed_value)
        self.sel_img: str = "../assets/visual/textures/walls"
        self.room_walls: dict[tuple[int, int, str], dict[str, object]] = {}
        # room_walls information in tuple order:
        # x: X cordinate on map
        # y: y cordinate on map
        # ori: orientation (West, North, East, or South) to know which rectangle to apply the texture to, may not need this!
        # hasdoor: know if we have a wall or door
        # isopen, if hasdoor is true, then isopen will state if our texture should use the open or closed state
        # sel_img, our path to get to the right texture (no need to specify boss texture or not, should be fine either way)

    def Apply_textures(self):
        if self.dungeon is None:
            raise ValueError("Generation requires a Dungeon instance to apply textures.")

        directions = [
            ("W", (-1, 0)),
            ("N", (0, 1)),
            ("E", (1, 0)),
            ("S", (0, -1)),
        ]

        self.room_walls.clear()

        for cur_room in self.dungeon.rooms.values():
            for orientation, (dx, dy) in directions:
                neighbor_xy = (cur_room.x + dx, cur_room.y + dy)
                has_door = neighbor_xy in self.dungeon.rooms

                if cur_room.room_type == "boss" and orientation == "S":
                    rel_path = f"{self.sel_img}/boss/{orientation}_x_boss.png"
                    self._store_wall(cur_room.x, cur_room.y, self.Sel_ori(orientation), True, False, rel_path)
                    continue

                if has_door:
                    is_open = orientation == "S"
                    if orientation == "S":
                        file_name = f"{orientation}_o.png"
                    else:
                        wall_variant = self.Ran_wall()
                        file_name = f"{orientation}_o_{wall_variant}.png"
                    rel_path = f"{self.sel_img}/door/{file_name}"
                    self._store_wall(cur_room.x, cur_room.y, self.Sel_ori(orientation), True, is_open, rel_path)
                else:
                    wall_variant = self.Ran_wall()
                    file_name = f"{orientation}_{wall_variant}.png"
                    rel_path = f"{self.sel_img}/empty/{file_name}"
                    self._store_wall(cur_room.x, cur_room.y, self.Sel_ori(orientation), False, False, rel_path)

    def Sel_ori(self, wall_ori: int):
        if wall_ori == 1:
            return "W"
        if wall_ori == 2:
            return "N"
        if wall_ori == 3:
            return "E"
        if wall_ori == 4:
            return "S"
        raise ValueError(f"Invalid wall orientation id: {wall_ori}")

    def Ran_wall(self):
        return self.rng.choice([1, 2, 3, 4])

    def whole_filepath(self, rel_path: str):
        return (Path(__file__).parent / rel_path).resolve()

    def _store_wall(
        self,
        x: int,
        y: int,
        orientation: str,
        hasdoor: bool,
        isopen: bool,
        rel_path: str,
    ):
        self.room_walls[(x, y, orientation)] = {
            "x": x,
            "y": y,
            "ori": orientation,
            "hasdoor": hasdoor,
            "isopen": isopen,
            "sel_img": self.whole_filepath(rel_path),
        }
