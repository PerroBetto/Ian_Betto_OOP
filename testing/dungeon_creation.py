import random
from collections import deque
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "Dungeon-Crawler" / "src"))
from generation import Generation # type: ignore

class Room:
    def __init__(self, x, y, room_type="empty"):
        self.x = x
        self.y = y
        self.room_type = room_type
        self.connections = []

    def connect(self, other_room):
        """Creates a bidirectional connection."""
        if other_room not in self.connections:
            self.connections.append(other_room)
        if self not in other_room.connections:
            other_room.connections.append(self)

    def __repr__(self):
        return f"Room({self.x}, {self.y}, {self.room_type})"


class Dungeon:
    def __init__(self, seed, total_rooms=12, min_puzzle_rooms=4):
        self.seed = seed
        self.total_rooms = total_rooms
        self.min_puzzle_rooms = min_puzzle_rooms
        self.rooms = {}  # {(x, y): Room}
        self.rng = random.Random(seed)  # Independent RNG
        self.generate()

    def generate(self):  # Call this function to generate dungeon
        self._generate_layout()
        self._assign_room_types()

    def _generate_layout(self):
        start = Room(0, 0, "start")
        self.rooms[(0, 0)] = start
        active_rooms = [start]

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while len(self.rooms) < self.total_rooms:
            current = self.rng.choice(active_rooms)
            dx, dy = self.rng.choice(directions)

            new_x = current.x + dx
            new_y = current.y + dy

            if (new_x, new_y) not in self.rooms:
                new_room = Room(new_x, new_y)
                self.rooms[(new_x, new_y)] = new_room
                current.connect(new_room)
                active_rooms.append(new_room)

    def _find_farthest_room(self, start):
        visited = set()
        queue = deque([(start, 0)])
        farthest = (start, 0)

        while queue:
            room, dist = queue.popleft()
            visited.add(room)

            if dist > farthest[1]:
                farthest = (room, dist)

            for neighbor in room.connections:
                if neighbor not in visited:
                    queue.append((neighbor, dist + 1))

        return farthest[0]

    def _assign_room_types(self):
        all_rooms = list(self.rooms.values())

        start_room = self.rooms[(0, 0)]

        # Find farthest room for boss
        boss_room = self._find_farthest_room(start_room)
        boss_room.room_type = "boss"

        remaining = [
            r for r in all_rooms
            if r != start_room and r != boss_room
        ]

        # Assign puzzle rooms
        puzzle_rooms = self.rng.sample(
            remaining,
            min(self.min_puzzle_rooms, len(remaining))
        )

        for room in puzzle_rooms:
            room.room_type = "puzzle"

        # Assign enemy rooms to remaining empty rooms
        for room in remaining:
            if room.room_type == "empty":
                room.room_type = "enemy"

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else random.randint(0, 1000000)
    dungeon: Dungeon = Dungeon(seed=seed)
    generation = Generation(dungeon)
    generation.Apply_textures()

    print(f"Seed: {seed}")
    print(f"Rooms generated: {len(dungeon.rooms)}")
    print(f"Wall records generated: {len(generation.room_walls)}")

    for (x, y), room in sorted(dungeon.rooms.items()):
        print(f"Room ({x}, {y}): type={room.room_type}, connections={[f'({r.x}, {r.y})' for r in room.connections]}")
    directions = {
        "W": (-1, 0),
        "N": (0, 1),
        "E": (1, 0),
        "S": (0, -1),
    }

    errors = []

    for (x, y), room in sorted(dungeon.rooms.items()):
        print(f"\nRoom ({x}, {y}) type={room.room_type}")
        for orientation in ["W", "N", "E", "S"]:
            key = (x, y, orientation)
            wall_data = generation.room_walls.get(key)
            if wall_data is None:
                errors.append(f"Missing wall data for {key}")
                continue

            dx, dy = directions[orientation]
            neighbor_exists = (x + dx, y + dy) in dungeon.rooms

            # Match generation.py behavior exactly:
            # boss south side is always forced to closed boss door texture.
            expected_hasdoor = neighbor_exists
            if room.room_type == "boss" and orientation == "S":
                expected_hasdoor = True

            if wall_data["hasdoor"] != expected_hasdoor:
                errors.append(
                    f"{key}: hasdoor={wall_data['hasdoor']} expected={expected_hasdoor}"
                )

            expected_open = expected_hasdoor and orientation == "S" and room.room_type != "boss"
            if wall_data["isopen"] != expected_open:
                errors.append(
                    f"{key}: isopen={wall_data['isopen']} expected={expected_open}"
                )

            wall_path = wall_data["sel_img"]
            if not isinstance(wall_path, Path):
                errors.append(f"{key}: sel_img is not a pathlib.Path ({type(wall_path)})")

            print(
                f"  {orientation}: hasdoor={wall_data['hasdoor']}, "
                f"isopen={wall_data['isopen']}, path={wall_path}"
            )

    print("\nVerification Summary")
    if errors:
        print(f"FAIL ({len(errors)} issues)")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print("PASS (all wall records match expected room-surroundings logic)")


if __name__ == "__main__":
    main()
    
