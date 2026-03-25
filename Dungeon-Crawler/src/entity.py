"""
Entity class module.

All objects within the game that require hitpoints, movement, and interactions
should inherit entity.

Good examples:
    Player - requires health, movement, environment interaction
    Enemies - same as Player
    Bubble - Bounces around the screen checking interactions,
            and is popped (hence the need for hitpoints)

Objects that inherit entity should override entity methods and call super()
at the end of each overridden method.
"""
from typing import Any, Callable
from pathlib import Path

import pygame
from pygame import Vector2, sprite, Surface, Rect

# from pygame import locals


class Entity(sprite.Sprite):
    """
    Base class for all entity types.
    """

    _SCALE: int = 4

    __slots__: list[str] = ["_world"  # Any (World this entity belongs to)
                            "_sheet",  # Surface
                            "_assets",  # dict[Surface]
                            "_position",  # Vector2
                            "_velocity",  # Vector2
                            "_speed",  # float
                            "_max_speed",  # float
                            "_friction",  # float
                            "_sounds",  # list[int]
                            "_HP",  # int
                            "_rect",  # Rect
                            "_image"]  # Surface

    def __init__(self, world: Any,
                 position: Vector2 = Vector2(0, 0),
                 speed: float = 5.0,
                 max_speed: float = 5.0,
                 friction: float = .75,
                 HP: int | None = None,
                 img: Surface | None = None) -> None:
        """
        Entities are game objects with some "living" attributes.
        Entities collide, can die and disappear, and can perform actions.

        Args:
            world (Any): World containing this entity
            position (Vector2, optional): World position. Defaults to Vector2(0, 0).
            speed (float, optional): entity speed. Defaults to 5.0.
            max_speed (float, optional): clamp speed. Defaults to 5.0.
            friction (float, optional): rate of slowdown. Defaults to .75.
            HP (int | None, optional): Hit points. Defaults to None.
            img (Surface | None, optional): base Surface. Defaults to None.
        """
        super().__init__()
        from world import World
        self._world: World = world

        self._position: Vector2 = position

        self.speed = speed
        self._max_speed: float = max_speed
        self.HP = HP if HP else 100

        self._velocity: Vector2 = Vector2()
        self._friction: float = friction
        self._sounds: list[int] = list[int]()

        self._assets: dict[str, Surface] = dict[str, Surface]()
        sheet_path = Path(__file__).parent / "../assets/visual/sprites/player/Fish-Sheet.png"
        self._sheet: Surface = pygame.image.load(sheet_path)
        self.assets_init(16, 16, 3, "ESN", "move", self._sheet)

    def assets_init(self, width: int,
                    height: int,
                    group_size: int,
                    pattern: str,
                    name: str,
                    sheet: Surface,
                    func: Callable[..., Any] | None = None,
                    *args) -> None:
        """
        Create assets from a sprite sheet.

        Each individual sprite is as wide as width, and as long as height.
        """
        def get_img(sheet_pos: list[int]) -> Surface:
            new_img: Surface = Surface((width, height)).convert_alpha()
            new_img.blit(sheet, (0, 0), (sheet_pos[0], sheet_pos[1], width, height))
            new_img = pygame.transform.scale(new_img,
                                             (width * self._SCALE, height * self._SCALE))
            return new_img

        def regular() -> None:
            """regular function for creating scripts"""
            sheet_pos: list[int] = [0, 0]
            for p_i in range(len(pattern)):
                for i in range(group_size):
                    img_name: str = f"{pattern[p_i]}{name}{i}"
                    self._assets[img_name] = get_img(sheet_pos)

                    sheet_pos[0] += width
                    if sheet_pos[0] >= sheet.get_width():
                        sheet_pos[0] = 0
                        sheet_pos[1] += height

        if not func:
            regular()
        else:
            func(*args)

        self._rect: Rect = Rect(0, 0, width * self._SCALE, height * self._SCALE)

# ----- properties -----

    @property
    def image(self) -> Surface:
        """current image display"""
        return self._image

    @image.setter
    def image(self, other: Surface) -> None:
        self._image: Surface = other

    @property
    def rect(self) -> Rect:
        """entity rect for collision and blitting"""
        return self._rect

    def set_rect(self) -> None:
        """Set rect value to position"""
        self._rect.center = (int(self._position.x), int(self._position.y))

    @property
    def HP(self) -> int:
        """Entity hit points"""
        return self._HP

    @HP.setter
    def HP(self, other: int) -> None:
        self._HP: int = other

    @property
    def speed(self) -> float:
        """the speed to increment velocity"""
        return self._speed

    @speed.setter
    def speed(self, other: float) -> None:
        self._speed: float = other

    @property
    def move_speed(self) -> float:
        """Speed entity is moving at. Measured pixles/second"""
        return self._velocity.magnitude()

# ----- base methods -----

    def loop(self, delta: float) -> None:
        """
        Entity loop. Run once every frame per entity.

        The base method will call move() and collide() for updating position.
        """
        direction: Vector2 = Vector2()

        key: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        value = "Emove0"
        if key[pygame.K_a]:
            direction.x += -1
            value = "Emove2"
        if key[pygame.K_d]:
            direction.x += 1
            value = "Smove0"

        if key[pygame.K_w]:
            direction.y += -1
            value = "Smove1"
        if key[pygame.K_s]:
            direction.y += 1
            value = "Nmove0"
        
        self.image = self._assets.get(value)

        self.move(delta, direction)
        self.collide()
        key = pygame.key.get_pressed()

    def render(self) -> tuple[Surface, Rect]:
        """
        Returns the current image and rect of an entity.
        """
        return (self.image, self.rect)

# ----- entity methods -----

    def move(self,  delta: float, dir: Vector2 | None = None) -> None:
        """
        Movement for an Entity object.

        Entities move in accordance to direction

        Args:
            dir (Vector2 | None, optional): Direction of acceleration.
        """
        # add direction
        if not dir:
            dir = Vector2()

        self._velocity += Vector2(dir.x * self.speed, dir.y * self.speed)

        # handle x
        try:
            self._velocity.x += -(self._velocity.x / abs(self._velocity.x)) * self._friction
            if abs(self._velocity.x) <= self._friction/2:
                self._velocity.x = 0
        except ZeroDivisionError:
            pass

        try:
            self._velocity.y += -(self._velocity.y / abs(self._velocity.y)) * self._friction
            if abs(self._velocity.y) <= self._friction/2:
                self._velocity.y = 0
        except ZeroDivisionError:
            pass

        # velocity clamping (check x and y of velocity)
        try:
            norm = self._velocity.normalize()
            xclamp = abs(norm.x) * self._max_speed if norm.x else self._max_speed
            yclamp = abs(norm.y) * self._max_speed if norm.y else self._max_speed
            self._velocity.x = pygame.math.clamp(self._velocity.x, -xclamp, xclamp)
            self._velocity.y = pygame.math.clamp(self._velocity.y, -yclamp, yclamp)
        except ValueError:
            pass

        self._position += (self._velocity * delta)
        # print(self._position)
        self.set_rect()

    def collide(self) -> None:
        """FIXME"""
        self._world.entity_action(self, "collision")

    def play_sound(self, indx: int) -> None:
        """FIXME"""
        pass
