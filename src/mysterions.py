"""
mysterions.py

A demo game for the final assignment for the
University of Helsinki MOOC Center (https://www.mooc.fi/en/)
online course Python Programming MOOC 2025 (https://programming-25.mooc.fi/).

https://programming-25.mooc.fi/part-14/4-your-own-game

The game requirements include:
    - The game has a sprite the player can move in some way
    - The game has some collectable items and/or enemies
    - The player needs to be set a clear task in the game
    - The game contains a counter which tells the player how they are doing in the game
    - The source code for the game is divided into functions like in the Sokoban example (https://github.com/moocfi/sokoban)
"""

from __future__ import annotations
import pygame
from random import randint, randrange, sample
import threading
import time

class Mysterions:
    def __init__(self):
        """
        Initializes pygame and the window,
        initializes the Game, begins the loop
        of setting the board and playing the game.
        """
        pygame.init()
        window = pygame.Surface((0, 0))
        newgame = Game(window)
        while newgame.status["run"]:
            newgame.set_board()
            newgame.play_game()

class ConstantsNamespace:
    """
    Collects the qualitative values that effect gameplay.

    ___slots___ attribute: See https://realpython.com/python-constants/#the-__slots__-attribute
    """
    __slots__ = ()

    BLACK = (0, 0, 0)               #: color
    WHITE = (255, 255, 255)         #: color
    GREY = (128, 128, 128)          #: color
    DARK_GREY = (80, 80, 80)        #: color

    #: Font used by :class:`Button`.
    #: Font file name and size.
    BUTTON_FONT = ("ARCADE_N.TTF", 16)
    
    #: The number of coins that can be randomly added to the board
    COIN_RANDRANGE = (10, 20)
    #: The value for each coin applied to the score
    COIN_SCORE = 100

    #: The number of doors (blocks, really) that can be randomly added.
    DOOR_RANDRANGE = (10, 30)

    GAME_BOARD_X_DEFAULT = 640      #: Game board default x dimension, not normally used.
    GAME_BOARD_Y_DEFAULT = 480      #: Game board default y dimension, not normally used.

    #: The title at the top of the window.
    GAME_DISPLAY_CAPTION = "ATTACK OF THE MYSTERIONS!!!"

    #: The time between rounds in seconds.
    GAME_DRAMATIC_PAUSE = 3

    #: The font used by :class:`Game` for life, score, etc.
    #: (file name and size.)
    GAME_FONT = ("ARCADE_N.TTF", 16)

    #: :class:`Player` health - maximum starting value
    GAME_PLAYER_HEALTH_MAX = 100

    #: :class:`Player` health - the amound subtracted with each :class:`Robot` / :class:`Monster` collision.
    GAME_PLAYER_HEALTH_SUBTRACT = 20

    #: The starting amount of lives per game 
    GAME_PLAYER_LIFE_COUNT_START = 3
    #: The maximum lives a player can have
    GAME_PLAYER_LIFE_COUNT_MAX = 5

    #: The x dimension of the grid on which objects are placed (like a chess board)
    GAME_START_GRID_SIZE_X = 15    
    #: The y dimension of the grid on which objects are placed (like a chess board) 
    GAME_START_GRID_SIZE_Y = 8     

    #: The framerate of the game (higher = faster game)
    GAME_TICK = 90

    #: When using the Charge maneuver,
    #: the distance in pixels from the robot
    #: the monster can be before it can go
    #: diagnolly. (Otherwise it can only go LRUD)
    MONSTER_CHARGE_DIRECT_THRESHOLD = 40

    #: The number of monsters that can be randomly added to the board.
    MONSTER_RANDRANGE = (5, 15)

    #: Adjusts the wobble factor of the monsters
    #: Lower value  = more wobbly
    #: Min value = 200
    MONSTER_WOBBLE_RNG = 1000

    #: The speed of the monsters (pixels per refresh)
    MONSTER_VELOCITY = 1.0

    #: The amount of space needed to be around
    #: a monster to be considered free of obstacles 
    #: and it can begin Charging toward the robot (Charge maneuver)
    MONSTER_CLEAR_THRESHOLD = 50

    #: When peforming the Random Turn on the Knight Move maneuver,
    #: the range of paces (distance in pixels) the monster can go
    #: after the turn. (Basically minimum and maximum distance.)
    MONSTER_RANDOM_TURN_PACES_RANDRANGE = (100, 250)

    #: Used by is_overlap, the amount of pixels (x, y) that two objects need 
    #: to be sharing to be considered overlapping i.e. have collided.
    MOVING_OVERLAP_FACTOR = 20

    #: When the robot is added to the board
    #: we avoid placing it near the border of the screen.
    #: This is the amount of spaces away from the border
    #: the robot should be placed.
    ROBOT_BOARD_BORDER_BUFFER = 2

    #: The amount of time in seconds
    #: the robot gets a head start
    #: before the monsters attack.
    ROBOT_HEAD_START = 3

    #: The speed of the robot (pixels per refresh.)
    ROBOT_VELOCITY = 2.0

    #: The keys for moving the robot.
    LRUD_KEYS = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "up": pygame.K_UP,
        "down": pygame.K_DOWN
    }

constants = ConstantsNamespace()

class Stationary(pygame.sprite.Sprite):
    """
    The base class for non-moving objects (:class:`Door`, :class:`Coin`).
    
    x, y -- top-left positon of object
    image -- the pygame.image graphic
    """
    def __init__(self, x: int, y: int, image: pygame.image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Door(Stationary):
    pass

class Coin(Stationary):
    pass

class Moving(pygame.sprite.Sprite):
    """
    The base class for moving objects (:class:`Robot`, :class:`Monster`).
    """
    def __init__(self,
                 finex: float,
                 finey: float,
                 image: pygame.image,
                 velocity: float = 1.0):
        """
        Position (finex, finey), velocity, and image

        finex, finey, and velocity -- floats
        which allow for fractional velocities for finer
        movements. Positions are converted to int values
        and assigned to object's rect.topleft.
        
        image -- the pygame.image graphic
        """
        # Fine positioning.
        self.finex, self.finey = finex, finey
        # The object's graphic, containing rectangle, and its position.
        self.image = image
        self.rect = self.image.get_rect()  # image rectangle
        self.rect.topleft = (int(self.finex), int(self.finey))
        # Velocity less than 1 results in no change in position due to rounding.
        if velocity < 1.0:
            raise ValueError(f"{__class__}: velocity must be 1.0 or greater")
        # How fast to move.
        self.velocity = velocity  

    def is_collision(self, things: dict[str, list], change: list[float, float],
                     window: pygame.Rect) -> bool:
        """
        Determines if object's planned position change will result in
        a collision with a stationary object that prevents movement
        (e.g. a :class:`Door`) or with the edge of the window.
        """
        # The value returned. 
        collision = False

        # Where this change is going.
        new_location = self.rect.copy()
        new_location.move_ip(change)

        # Check the new location against the Doors and see if any overlap (collide).
        for item in things['doors']:
            if self.is_overlap(new_location, item):
                collision = True
                break
        # Or do we hit the edge of the window?
        window_rect = window
        if not window_rect.contains(new_location):
            collision = True
        return collision

    def is_overlap(self, location: pygame.rect, item: object) -> bool:
        """
        | Process similar to pygame.Rect.colliderect(new_location, item)
        | input: two Rect objects - location of bot, item (:class:`Monster`, :class:`Coin`, :class:`Door`)
        | check if they overlap by x amount
        | return True or False
        """
        a = location
        b = item.rect
        x_match = len(
            list(range(max(a.left, b.left),
                       min(a.right, b.right) + 1)))
        y_match = len(
            list(range(max(a.top, b.top),
                       min(a.bottom, b.bottom) + 1)))
        return (x_match > constants.MOVING_OVERLAP_FACTOR and y_match > constants.MOVING_OVERLAP_FACTOR)

# Remember to use finex, finey for positioning, x and y for determining location.
class Monster(Moving):
    """
    Monster object, including methods for autonomous navigation.
    """
    def __init__(self,
                 finex: float,
                 finey: float,
                 image: pygame.image,
                 velocity: float = constants.MONSTER_VELOCITY):
        """
        Inherits position and velocity from :class:`Moving` parent object.
        Sets initial maneuver method and creates :class:`Straight` maneuver object.
        """
        super().__init__(finex, finey, image, velocity)
        # Maneuver strategy that's in use.
        self.maneuver = "charge"
        # Object for the Straight maneuver.
        self.straight = self.Straight(self)

    class Straight:
        """
        Collects the methods and variables for maneuvering around
        fixed stationary objects (i.e. :class:`Door`)
        """
        def __init__(self, this_monster: Monster):
            """
            | direction - x, y multiplied against velocity to create vector  
            | paces - how far to travel in this direction?  
            | move_count - how far have we gone in this direction?  
            | completed - have we completed going in this direction?  
            | knight_moves_stage - for a :func:`knight_moves` maneuver, at what stage are we?  
            """
            self.direction = [0.0, 0.0]
            self.paces = 0.0
            self.move_count = 0.0
            self.completed = False
            self.knight_moves_stage = "none"
            self.this_monster = this_monster

        def straight(self) -> list[float, float]:
            """
            Checks if a :class:`Monster` currently following a straight path
            (as part of a larger maneuver) has completed the path,
            and if not, keep going by returning the change it needs to make
            to continue.
            """
            # Where we're going.
            change = [0.0, 0.0]
            # Are we done going this way?
            if self.move_count >= self.paces and self.paces != 0.0:  
                # if so reset
                self.move_count = 0.0
                self.paces = 0.0
                self.completed = True
                change = [0.0, 0.0]
            # Else keep going that way.
            else:
                change = [(self.this_monster.velocity * self.direction[0]),
                          (self.this_monster.velocity * self.direction[1])]
            return change

        def random_turn(self) -> list[list[float, float], int]:
            """
            Used as part of the :func:`knight_moves` maneuver,
            creates a new straight path that is perpendicular to the
            previous one (either turn left or right) for a random number of paces.
            """
            # The direction (x, y) and the number of paces to go
            rand_turn = [[0.0, 0, 0], 0]
            # Make the direction left or right turn of the current direction.
            if self.direction[0] == 0.0:
                rand_turn[0][0] = [-1.0, 1.0][randrange(2)]
            else:
                rand_turn[0][0] = 0.0
            if self.direction[1] == 0.0:
                rand_turn[0][1] = [-1.0, 1.0][randrange(2)]
            else:
                rand_turn[0][1] = 0.0
            # Paces is a random value within a range
            paces = randint(constants.MONSTER_RANDOM_TURN_PACES_RANDRANGE[0], constants.MONSTER_RANDOM_TURN_PACES_RANDRANGE[1])
            rand_turn[1] = paces
            return rand_turn

        def knight_moves(self,
                         cmd: str = None,
                         best: list[list[int, int], float] = None) -> str:
            """
            Called by the :func:`move` function, it sets up and manages a set of maneuvers for
            moving around obstacles. An L-shaped maneuver is taken, first following
            the clearest path (see :func:`best_direction`) for a fraction of the total available distance
            (currently one-half), followed by a random left or right perpendicular turn
            for another random distance. If this results in another possible collision,
            the maneuver is repeated. If the maneuver completes and the way is clear,
            the maneuver is changed to :func:`charge`.
            """
            # print(cmd, self.this_monster.finex, self.this_monster.finey)
            # If there's a collision, start a new knight move at the first stage.
            if cmd == "start":
                self.knight_moves_stage = "first"
                # Change to straight.
                self.this_monster.maneuver = "straight"
                # Go in the best direction.
                self.direction = best[0]
                # Go half the distance available.
                self.paces = best[1] / 2
                # Reset the move count going straight.
                self.move_count = 0.0
                # And reset the completed check
                self.completed = False  

            # "next" should only apply when in first stage - then go to second stage (random_turn)
            elif cmd == "next":
                self.knight_moves_stage = "second"
                # Set the direction and the number of paces to go.
                self.direction, self.paces = self.random_turn()
                # Reset the move count going straight.
                self.move_count = 0.0
                # And reset the completed check
                self.completed = False  

            # If the knight move is finished, set status to none.
            elif cmd == "finish":
                self.knight_moves_stage = "none"

            return self.knight_moves_stage

    def best_direction(
            self, things: dict[str, list],
            window: pygame.rect) -> set[list[list[int, int], float], bool]:
        """
        Determines the direction (LRUD) the :class:`Monster` can travel the
        greatest distance, and also if the :class:`Monster` is clear of obstacles
        (nothing in its way LRUD for a minimum set distance.)

        Returns the direction and distance, and boolean value clear.
        """
        # The four directions to check (x,y) and the distance you can go that way,
        # and are we clear in this direction? (true until found false).
        clear = True  
        # Down, right, up, left
        paths = [
            [[0.0, 1.0], 0, True], [[1.0, 0.0], 0, True], [[0.0, -1.0], 0, True], [[-1.0, 0.0], 0, True]
        ]  

        # For each direction...
        for path in paths:  
            # Stays false until the collision point is determined.
            collision = False
            # How far where we've stepped during the check.
            step = 0.5  
            # Until we've collided...
            while not collision:  

                # 1) Do we collide into any objects?
                # Where we're checking - note one of these (move_x, move_y) is always zero.
                move_x = path[0][0] * (self.rect.width * step)
                move_y = path[0][1] * (self.rect.width * step)
                # Rectangle position to be tested.
                test_rect = self.rect.move(move_x, move_y)
                # Test if it collides with an object.
                # For all the doors...
                for item in things['doors']:
                    # Do we hit anything?
                    if pygame.Rect.colliderect(test_rect, item):
                        collision = True
                        # This is where we collide in this direction
                        path[1] = abs(move_x + move_y)
                        if path[1] <= constants.MONSTER_CLEAR_THRESHOLD:
                            path[2] = False
                        break

                # 2) Do we collide into the edge of the window?
                window_rect = window
                if not window_rect.contains(test_rect):
                    collision = True
                    # This is where we collide in this direction.
                    path[1] = abs(move_x + move_y)

                # Did we hit anything?
                if not collision:
                    # Go another step in that direction.
                    step += 0.5  

        # Are we free of objects in the immediate area?
        clear = all(p[2] == True for p in paths)

        # Which is the best direction to go?
        # Best - direction (x, y) and distance, clear - true/false.
        best = max(paths, key=lambda b: b[1])

        # A literal edge case and a fix:
        # A low value for best distance occurs when colliderect is true only
        # half a width away in all directions, like when the Monster is adjacent to
        # two or more Doors. Also, since the best distance in each direction is a four-way tie,
        # the resulting default direction may be blocked.
        # To bust out of this, we try randomly going in one direction a full width.
        # You may wind back here more than once but it will work after a few tries.
        if best[1] < self.rect.width:
        # pick a random direction and distance for best
            best = paths[randrange(4)]
            best[1] = self.rect.width
            clear = False
        return (best, clear)

    # The Monster heads toward the Robot, left/right/up/down (LRUD) until very close, then can go diagonally.
    def charge(self, target: Robot) -> list[float, float]:
        """
        Returns the vector (direction * velocity) for the :class:`Monster`
        to head toward the :class:`Robot`. As a limitation, it can only go LRUD
        until it is a specific distance from the :class:`Robot`, at which point
        the direction can be diagonal.
        """
        # The direction the Monster is headed.
        direction = [0.0, 0.0]
        # Where the Monster is going
        change = [0.0, 0.0]  

        # How far apart is the Monster from the robot?
        difference = [(target.finex - self.finex), (target.finey - self.finey)]

        # What direction should the Monster go?
        if abs(difference[0]) > 0:
            direction[0] = int(difference[0] / abs(difference[0]))
        if abs(difference[1]) > 0:
            direction[1] = int(difference[1] / abs(difference[1]))

        # If nearby, go directly toward the Robot.
        if (abs(difference[0]) < constants.MONSTER_CHARGE_DIRECT_THRESHOLD and abs(difference[1]) < constants.MONSTER_CHARGE_DIRECT_THRESHOLD):
            change = [(self.velocity * direction[0]),
                      (self.velocity * direction[1])]

        # Otherwise go in a straight direction, either left/right or up/down.

        # If both abs(diff[0]) and abs(diff[1]) are above threshhold, Monster goes L/R before going U/D

        elif abs(difference[0]) >= constants.MONSTER_CHARGE_DIRECT_THRESHOLD:
            change = [(self.velocity * direction[0]), 0]

        elif abs(difference[1]) >= constants.MONSTER_CHARGE_DIRECT_THRESHOLD:
            change = [0, (self.velocity * direction[1])]

        return change

    def wobble(self, change: list[float, float], velocity: float,
                drink_rng: int) -> list[float, float]:
        """
        Adds a random additional vector to an existing change
        to give the aesthetic effect of a wobble to the :class:`Monster`.
        (This was originally intended as a way of getting around obstacles.)
        """
        direction = [0.0, 0.0]

        drink = randint(0, drink_rng)
        if is_between(drink, (0, 99)):
            direction[0] = -1
        elif is_between(drink, (100, 199)):
            direction[0] = 1

        drink = randint(0, drink_rng)
        if is_between(drink, (0, 99)):
            direction[1] = -1
        elif is_between(drink, (100, 199)):
            direction[1] = 1

        change[0] += direction[0] * velocity
        change[1] += direction[1] * velocity

        return change

    def move(self, target: Robot, things: dict[str, list],
             window: pygame.rect, monsters_are_go: bool) -> None:
        """
        Primary function for moving The :class:`Monster`.
        Applies a maneuver and determines if it would result in
        a collision (and revises the strategy accordingly),
        and checks if the applied maneuver is continuing or
        completed. Finally applies the vector change to the :class:`Monster`.
        """
        print("move - maneeuver is", self.maneuver)
        change = [0.0, 0.0]
        if monsters_are_go:
            if self.maneuver == "charge":
                change = self.charge(target)
            elif self.maneuver == "straight":
                change = self.straight.straight()

        # Adds wobble effect to the Monster's movement
        # Adjust the velocity value, rng value to change the effect.
        # Just comment this out to remove the effect.
        # change = self.wobble(change, self.velocity, constants.MONSTER_WOBBLE_RNG)

        # With this change does the Monster collide with anything?
        collision = self.is_collision(things, change, window)

        if collision:
            # What's the clearest way to go and how far? Anything in the way?
            (best, clear) = self.best_direction(things, window)

            # Start a new knight move (even if currently in one)
            self.straight.knight_moves("start", best)
            # Erase the change.
            change = [0.0, 0.0]

        else:
            # Check where the Monster is at.
            # If in a knight_moves, has the Monster completed the two straight segments?
            # If the Monster is going straight...
            if self.maneuver == "straight":  
                # ... and we've completed the run...
                if self.straight.completed:
                    # If the Monster has finished going the best direction...
                    if self.straight.knight_moves() == "first":
                        # Then move on to the next direction.
                        self.straight.knight_moves("next")
                    # Else if we've completed going the second direction.
                    elif self.straight.knight_moves() == "second":
                        # Find what's the clearest way to go and how far, and is there anything in the way?
#                        (best, clear) = self.best_direction(things, window)
                        # If nothing's in the way, charge after the robot.
#                        if clear:
                            self.straight.knight_moves("finish")
                            self.maneuver = "charge"
#                            print("knight_moves finished, switch to charge")
                        # else:
                        #     self.straight.knight_moves("start", best)
                        #     # Erase the change.
                        #     change = [0.0, 0.0]
                        #     print("not clear, restart knight_moves")
                # But if the run's not completed, keep going.
                else:
                    # Increment the move count by one.
                    self.straight.move_count += self.velocity

        # Set the new fine positions.
        self.finex += change[0]
        self.finey += change[1]
        # Apply the fine positions to the monster's rectangle.
        self.rect.x = int(self.finex)
        self.rect.y = int(self.finey)

class Robot(Moving):
    """
    Robot object, including methods for collisions with
    :class:`Coin` s and :class:`Monster` s.
    """
    def __init__(self,
                 finex: float,
                 finey: float,
                 image,
                 velocity: float = 1.0):
        super().__init__(finex, finey, image, velocity)
        self.to = {"left": False, "right": False, "up": False, "down": False}
        """
        Inherits positing and velocity from :class:`Moving` parent object.
        Plus the variables for the LRUD key events.
        """
    # Which directions to go base on keys up or down
    def keys(self, event: pygame.event) -> None:
        """
        Captures the LRUD and Quit key events.
        Called by :func:`play_game`
        """
        if event.type == pygame.KEYDOWN:
            for k, v in constants.LRUD_KEYS.items():
                if event.key == v:
                    self.to[k] = True

        if event.type == pygame.KEYUP:
            for k, v in constants.LRUD_KEYS.items():
                if event.key == v:
                    self.to[k] = False
        if event.type == pygame.QUIT:
            exit()

    def found_coin(self, things: dict[str, list], player: Player) -> None:
        """
        Determines if the :class:`Robot` has collided with a :class:`Coin` .
        If so, it removes the :class:`Coin` from the collection and updates the score.
        If all the :class:`Coin` s are collected (win the round), increment the life and round values.
        """
        new_location = self.rect.copy()
        items = things['coins']
        for item in items:
            if self.is_overlap(new_location, item):
                items.remove(item)
                player.score += constants.COIN_SCORE
                if len(items) == 0:
                    player.life = min(player.life + 1, constants.GAME_PLAYER_LIFE_COUNT_MAX)
                    player.round += 1

    def monster_mash(self, things: dict[str, list], player: Player) -> None:
        """
        Determines if the :class:`Robot` has collided with a :class:`Monster` .
        If so, it removes the :class:`Monster` from the collection and updates the health value.
        If health goes to zero (lose the round), decrement the life value and increment the round value.
        """
        new_location = self.rect.copy()
        items = things['monsters']
        for item in items:
            if self.is_overlap(new_location, item):
                items.remove(item)
                player.health -= constants.GAME_PLAYER_HEALTH_SUBTRACT
                if player.health == 0:
                    player.life -= 1
                    player.round += 1

    def move(self, things: dict[str, list], window: pygame.rect, player: Player) -> None:
        """
        Translate the values set by the key events to
        change in location. Determines if the change results
        in collision. If not, apply the change. Check if new
        location results in collision with :class:`Coin` s or :class:`Monster` s.
        """
        change = [0.0, 0.0]
        if self.to["right"]:
            change[0] = self.velocity
        if self.to["left"]:
            change[0] = -self.velocity
        if self.to["down"]:
            change[1] = self.velocity
        if self.to["up"]:
            change[1] = -self.velocity

        collision = self.is_collision(things, change, window)
        if collision:
            change = [0.0, 0.0]
        # Set the new fine positions.
        self.finex += change[0]
        self.finey += change[1]
        # Apply them to the monster's rectangle
        self.rect.x = int(self.finex)
        self.rect.y = int(self.finey)

        player.round_sync()

        self.found_coin(things, player)
        self.monster_mash(things, player)


def is_between(i: int, a: set) -> bool:
    """
    Returns true if value is in between values in a two item set.
    """
    return (a[0] <= i <= a[1])


class Button():
    """
    Defines a basic button with text.
    Performs different tasks based on the text value.
    """
    def __init__(self,
                 text: str,
                 x: int = 0,
                 y: int = 0,
                 width: int = 100,
                 height: int = 50,
                 color: set[int, int, int] = constants.DARK_GREY):
        """
        Defines the :class:`Button` text, position and dimensions, and color.
        """
        self.text = text
        self.image = pygame.Surface((width, height))
        self.image.fill(constants.DARK_GREY)
        self.rect = self.image.get_rect()
        font = pygame.font.Font(constants.BUTTON_FONT[0], constants.BUTTON_FONT[1])
        text_image = font.render(text, True, constants.WHITE)
        text_rect = text_image.get_rect(center=self.rect.center)
        self.image.blit(text_image, text_rect)
        self.rect.topleft = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the :class:`Button` on the surface.
        """
        surface.blit(self.image, self.rect)

    def handle_event(self, event: pygame.event,
                     status: dict[str, bool],
                     player: Player) -> None:
        """
        Detects the mouse button clicks.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.run_command(player, status)

    def run_command(self, 
                    player: Player,
                    status: dict[str, bool]) -> None:
        """
        Changes :class:`Player` properties and game status based on the string from the chosen :class:`Button`.
        """
        status["choice_made"] = True

        if self.text == "New Game":
            # Reset the player.
            player.score = 0
            player.round = 1
            player.life = constants.GAME_PLAYER_LIFE_COUNT_START
            player.health = constants.GAME_PLAYER_HEALTH_MAX
            player.round_sync()
            status["run"] = True

        elif self.text == "Continue":
            status["run"] = True
            # player.round = 1
            player.life = constants.GAME_PLAYER_LIFE_COUNT_START
            player.health = constants.GAME_PLAYER_HEALTH_MAX
            player.round_sync()

        elif self.text == "Quit":
            status["run"] = False

class Player:
    """
    Object that holds the player's state. It is separate from the :class:`Robot` object.

    Where the player's score, round, life, and health are tracked.
    """
    def __init__(self):
        self.score = 0
        self.round = 1
        # State to check for round updates and for text updates.
        self.round_current = 1
        self.life = constants.GAME_PLAYER_LIFE_COUNT_START
        self.health = constants.GAME_PLAYER_HEALTH_MAX

    def round_sync(self) -> None:
        """
        | A simple function, but it needs explaining.
        | The round_current value is set equal to round at the start of each round.
        | During :func:`play_game` the two values are compared.
        | As long as the two values are equal, the current game remains active.
        | When the player collects all the coins or player loses a life (but not all the lives),
        | a new round can start, and the value of round is incremented by one.
        | When round_current and round are no longer equal, a new board is set and a new round starts.
        | This just sets round_current equal to round again.
        """
        self.round_current = self.round

class Game:
    """
    Object for the :class:`Game` itself, within which all other objects are used.
    """
    def __init__(self, window: pygame.Surface):
        """Creates a new game and sets the initial values."""
        self.status = {
            "run": True,
            "choice_made": False
        }
        # The window the Game runs in.
        self.window = window
        # The time between refreshes (higher is faster).
        self.tick = constants.GAME_TICK 
        self.player = Player()
        self.board = pygame.rect
        # Set the size of the game board, values are defaults.
        self.board_x = constants.GAME_BOARD_X_DEFAULT
        self.board_y = constants.GAME_BOARD_Y_DEFAULT
        # Set a grid for placement of the objects at start.
        self.start_grid_size_x = constants.GAME_START_GRID_SIZE_X
        self.start_grid_size_y = constants.GAME_START_GRID_SIZE_Y
        # Object images
        self.images = {}
        for name in ["robot", "coin", "door", "monster"]:
            self.images[name] = pygame.image.load(name + ".png")
        # Object for traking time.
        self.clock = pygame.time.Clock()
        # The Robot object to be built.
        self.robot1 = pygame.sprite.Sprite
        # Containers for objects to be made.
        self.monsters = []
        self.doors = []
        self.coins = []
        # Dictionary contains monsters, doors, and coins.
        self.things = {}
        # Contains the round, scores, lifes to be displayed.
        self.text = ""
        # How far from the window border in grid space should the robot be randomly placed?
        self.robot_buffer = constants.ROBOT_BOARD_BORDER_BUFFER
        # How many seconds head start to give the robot before the monsters start moving?
        self.headstart = constants.ROBOT_HEAD_START
        # Release the monsters? (see headstart).
        self.monsters_are_go = False
        # Time in seconds to wait before screen reloads for next round, etc.
        self.dramatic_pause = constants.GAME_DRAMATIC_PAUSE
        # The buttons for the end of the game.
        self.btn1 = Button('Continue', 150, 300, 200, 50, constants.DARK_GREY)
        self.btn2 = Button('New Game', 400, 300, 200, 50, constants.DARK_GREY)
        self.btn3 = Button('Quit', 650, 300, 200, 50, constants.DARK_GREY)
        # Font for the score text.
        self.game_font = pygame.font.Font(constants.GAME_FONT[0], constants.GAME_FONT[1])

    def set_board(self) -> None:
        """
        Creates a representation of the :class:`Game` board and
        populates it with objects [:class:`Door`, :class:`Monster`, :class:`Coin`, :class:`Robot`]
        """
        # Make a grid of empty values.
        start_grid = [["" for _ in range(self.start_grid_size_x)]
                      for _ in range(self.start_grid_size_y)
                      ]
        # The size of each square on the grid.
        self.start_grid_square_x = int(self.images["door"].get_width() + 15)
        self.start_grid_square_y = int(self.images["door"].get_height() + 20)
        # The size of the board from multiplying the squares.
        self.board_x = self.start_grid_size_x * self.start_grid_square_x
        self.board_y = self.start_grid_size_y * self.start_grid_square_y
        # The rectangle of the board.
        self.board = pygame.Rect(0, self.start_grid_square_y, self.board_x,
                                 self.board_y)
        # Set/activate the window if it's not active already.
        if not pygame.display.get_active():
            self.window = pygame.display.set_mode(
                (self.board_x, (self.board_y + self.start_grid_square_y)))
            pygame.display.set_caption(constants.GAME_DISPLAY_CAPTION)

        # Set the number of objects to be randomly created.
        objcount = {}
        objcount["coin"] = randrange(constants.COIN_RANDRANGE[0], constants.COIN_RANDRANGE[1])
        objcount["door"] = randrange(constants.DOOR_RANDRANGE[0], constants.DOOR_RANDRANGE[1])
        objcount["monster"] = randrange(constants.MONSTER_RANDRANGE[0], constants.MONSTER_RANDRANGE[1])
        # objcount["monster"] = 1
        # Get the size of the grid.
        grid_size = self.start_grid_size_x * self.start_grid_size_y
        # Create a list of sequential digits that's randomized
        # representing places on the board.
        li = sample(range(0, grid_size), grid_size)
        # Create a list of playing field objects to be placed on the board.
        tmplist = []
        tmplist += ["coin"] * objcount["coin"]
        tmplist += ["door"] * objcount["door"]
        tmplist += ["monster"] * objcount["monster"]
        # The number of objects.
        objlist_len = len(tmplist)
        # Fill out the object list with blanks.
        tmplist += [""] * (grid_size - objlist_len)

        # Zip together the list of random board positions to
        # the list of objects and put in a dictionary.
        # This assigns each object or blank to a position on the board.
        objdict = dict(zip(li, tmplist))

        # Populate the initial grid with the objects.
        start_grid = [["" for _ in range(self.start_grid_size_x)]
                      for _ in range(self.start_grid_size_y)]
        for b, row in enumerate(start_grid):
            for a, item in enumerate(row):
                index = (b * self.start_grid_size_x) + a
                start_grid[b][a] = objdict[index]

        # Create/clear the object lists for the board.
        self.monsters = []
        self.doors = []
        self.coins = []

        # Position the Robot randomly on the grid,
        # a certain distance away from the border.
        robot_grid_x = randint(
            self.robot_buffer,
            self.start_grid_size_x - (self.robot_buffer + 1))
        robot_grid_y = randint(
            self.robot_buffer,
            self.start_grid_size_y - (self.robot_buffer + 1))
        robot_x = (robot_grid_x * self.start_grid_square_x) + self.board.left
        robot_y = (robot_grid_y * self.start_grid_square_y) + self.board.top

        # Creating the Robot object proper, with positon.
        self.robot1 = Robot(robot_x, robot_y, self.images["robot"], constants.ROBOT_VELOCITY)

        # Creating the other objects based on the values for the grid.
        for y in range(len(start_grid)):
            for x in range(len(start_grid[y])):
                # Don't position an object where the Robot will be
                if not (x == robot_grid_x and y == robot_grid_y):
                    if start_grid[y][x] == "monster":
                        self.monsters.append(
                            Monster((x * self.start_grid_square_x) +
                                    self.board.left,
                                    (y * self.start_grid_square_y) +
                                    self.board.top, self.images["monster"]))
                    elif start_grid[y][x] == "door":
                        self.doors.append(
                            Door((x * self.start_grid_square_x) +
                                 self.board.left,
                                 (y * self.start_grid_square_y) +
                                 self.board.top, self.images["door"]))
                    elif start_grid[y][x] == "coin":
                        self.coins.append(
                            Coin((x * self.start_grid_square_x) +
                                 self.board.left,
                                 (y * self.start_grid_square_y) +
                                 self.board.top, self.images["coin"]))
        # Collect all the objects into a dictionary.
        self.things = {
            'monsters': self.monsters,
            'doors': self.doors,
            'coins': self.coins
        }
        # Hold the Monsters to give the Robot a head start.
        self.monsters_are_go = False

        # Reset the trigger for waiting for the Button choice being made.
        self.status["choice_made"] = False

    def release_monsters(self) -> None:
        """
        Set by separate thread after a preset time,
        :class:`Monster` s can move once set to true.
        """
        self.monsters_are_go = True

    # Let's go!
    def play_game(self) -> None:
        """
        Where the :class:`Game` runs. A continuous loop checks for key events,
        updates game objects, and refreshes the display.
        """
        # The seconds to wait before screen reloads for next round, etc.
        self.dramatic_pause = constants.GAME_DRAMATIC_PAUSE
        # Count down in a separate thread for the Monsters to be released.
        t = threading.Timer(self.headstart, self.release_monsters)
        t.start()

        # The game runs in this loop.
        while True:
            # Keep the round going until something happens to start a new one.
            if self.player.round_current == self.player.round:
                # Get commands for the Robot and move accordingly.
                for event in pygame.event.get():
                    self.robot1.keys(event)
                self.robot1.move(self.things, self.board, self.player)

                # Update the text showing round, score, etc.
                self.text = self.game_font.render(
                    f"Round:{self.player.round_current:>2} Life:{self.player.life:>2} Health:{self.player.health:>3} Points:{self.player.score:>5}",
                    True, (255, 255, 255))

                # Keep redrawing everthing as events occur.
                self.window.fill((127, 127, 127))
                pygame.draw.rect(
                    self.window, (80, 80, 80),
                    (0, 0, self.board_x, self.start_grid_square_y))
                
                # This draws all the objects, but the Monsters
                # wind up layered under the Coins.
                # for sprites in self.things.values():
                #    for item in sprites:
                #        self.window.blit(item.image, item.rect.topleft)

                # Draw the Monsters last for better layering.
                # (Should look into a more proper way to manage this.)
                for item in self.coins:
                    self.window.blit(item.image, item.rect.topleft)
                for item in self.doors:
                    self.window.blit(item.image, item.rect.topleft)
                for item in self.monsters:
                    self.window.blit(item.image, item.rect.topleft)

                self.window.blit(self.robot1.image, self.robot1.rect.topleft)
                self.window.blit(self.text, (200, 20))
                pygame.display.flip()

                # Move the Monsters.
                for mon in self.monsters:
                    mon.move(self.robot1, self.things, self.board, self.monsters_are_go)

                # Update the clock.
                self.clock.tick(self.tick)

            else:
                # A new round has started.
                self.player.health = 100
                # Update the round state.
                self.player.round_sync()
                # Is the the player is out of lives?
                if self.player.life == 0:
                    self.dramatic_pause = 0
                    # The Game is still running while waiting for the buttons to be clicked.
                    while self.status["choice_made"] == False:
                        self.btn1.draw(self.window)
                        self.btn2.draw(self.window)
                        self.btn3.draw(self.window)
                        # Listen for events - button clicks, closing window...
                        for event in pygame.event.get():
                            # Look for button response, changes player and game status.
                            self.btn1.handle_event(event, self.status, self.player)
                            self.btn2.handle_event(event, self.status, self.player)
                            self.btn3.handle_event(event, self.status, self.player)
                            if event.type == pygame.QUIT:
                                exit()
                        # Update the full display Surface to the screen.
                        pygame.display.flip()
                        # Update the clock.
                        self.clock.tick(self.tick)
                # Wait a moment.
                time.sleep(self.dramatic_pause)
                # Breaking the loop, to either play a new game, continue the game with more lives, or quit.
                break

if __name__ == "__main__":
    Mysterions()

