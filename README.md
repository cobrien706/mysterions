# mysterions - An arcade-style action game - collect coins, get around obstacles, avoid monsters, try not to die.

# :robot:  :ghost::ghost::ghost:  :ghost:

This is a demo game for the [final assignment](https://programming-25.mooc.fi/part-14/4-your-own-game) for the  
[University of Helsinki MOOC Center](https://www.mooc.fi/en/) online course [Python Programming MOOC 2025](https://programming-25.mooc.fi/).

The goal of this project was to fulfill the assignment, but also to try to create code that could be readily modified, maintained and improved upon by other developers, to better familiarize myself with better techniques, writing 'pythonic' code, and creating as solid documentation as possible, using resources such as Sphinx and Read the Docs.

# Description

The project is a relatively simple Python game kept to one script using PyGame. At each round the playing field is randomly populated with obstacles to navigate around, coins to be collected for points, monsters to be avoided, and a robot, which is the player.

# Gameplay

<<img width="977" height="852" alt="mysterions_game_board_example" src="https://github.com/user-attachments/assets/2570602c-9c9e-44f3-bfe1-9336c4393e82" />

Gameplay is almost self-explanatory with no intentional surprises. 
- The player starts with a health level of 100% and 3 lives.
- The player gets a momentary head start (three seconds OOTB) before the monsters start moving. This time allows the user to locate their character and get away from monsters in close proximity.
- The player navigates the board by holding down the arrow keys (LEFT ⬅️, RIGHT ➡️, UP ⬆️, DOWN ⬇️) (LRUD) for the corresponding direction. Keys can be combined (e.g. hold down UP and LEFT at the same time) to move diagonally.
- The player navigates through the board to collect coins, earning 100 points a coin, while the monsters on the board pursue the player.
- If the player contacts a monster, the player's health drops 20% and the monster disappears.
- A round ends when either all the coins on the board are collected or health declines to zero.
- If the player collects all the coins, they are awarded an additional life (to a maximum of five.)
- If the player's health reaches zero before all the coins are collected, they lose a life. If the player loses all of their lives, the game ends.
- At the game's end, player has the option of continuing the game (three more lives, start a new round, keep the current score), start a new game, or quit.

As configured OOTB, the player moves twice as fast as the monsters and can move in all directions. Monsters can only move left, right, up, or down for any particular stretch of movement. (They can only move diagonally once they are close to the player.)

That's it. No boss fights, no transition screens, no pausing, no leader board, not even sound effects.

Whether the game is *fun* as-is is of course subjective. But the number of monsters, coins and obstacles, and their placement, randomly changes from round to round, gameplay can go from 'That's easy!' to 'Oh... oh no... 👀' unexpectedly.

# Installation
The game requires [PyGame](https://www.pygame.org).  
Other modules (`random`,`threading`,`time`) should be in the standard library.

    pip install -r requirements.txt 
    python mysterions.py 

# Monster Behavior

![mysterion_strategy_in_a_nutshell](https://github.com/user-attachments/assets/148614d5-3954-4d1a-94e8-d54f097cde79)

All the monsters follow the same set of strategies in pursing the player and navigating the board.

## charge

<img width="430" height="448" alt="monster_charge_sample_edit" src="https://github.com/user-attachments/assets/51ddebf5-a3ad-4a8a-8244-8d85f0c9dda6" />

The initial strategy, and the one they always eventually go back to, is *charge*, where the Monster simply heads toward the Robot's current location.

The difference between the Monster and the Robot's coordinates *(diff<sub>x</sub>, diff<sub>y</sub>) = (r<sub>x</sub> - m<sub>x</sub>, r<sub>y</sub> - m<sub>y</sub>)* are used to determine the direction the Monster must go to get closer to the Robot.

There is a threshold value *(t)* which determines the direction used by the Monster when heading toward the Robot.

*If* the absolute values of *diff<sub>x</sub>* and *diff<sub>y</sub>* are both below *t*, the Monster is very close to the Robot, and the Monster can go diagonally toward the Robot.

*Else if* *abs(diff<sub>x</sub>)* is greater than or equal to *t*, head toward the Robot along the x axis (left or right).

*Else if* *abs(diff<sub>y</sub>)* is greater than or equal to *t* (this should be the case even if we don't confirm it), head toward the Robot along the y axis (up or down).

The direction (x, y) is multiplied by the Monster's velocity to make the change vector, which is the amount the Monster will move on the next screen refresh.

*charge* works fine, until the Monster runs into an obstacle and has to get around it. The next strategy and sub-strategies address this.

## knight_moves

<img width="851" height="538" alt="monster_knight_moves_sample_edit" src="https://github.com/user-attachments/assets/249ccbcd-4958-408c-bf09-7e56f60afc8b" />

If the Monster during a *charge* determines the direction it is going will result in collision with an obstacle *(is_collision)*, the strategy is changed to *knight_moves*.

*knight_moves* has multiple stages. 
0. During *move*, the upcoming change in position results in *is_collision* returning true. We need to change direction.
1. To determine the best way to go, *best_direction* determines which direction (LRUD) has the most clearance, and returns the direction and the distance available.
2. *knight_moves* stage is changed to 'start'.
3. The *straight* maneuver is applied, and the Monster goes in the best direction for part of the distance, currently set for half the available distance. *knight_moves* stage is changed to 'first'.
4. When the *straight* maneuver is completed, *knight_moves* stage is changed to 'next'. *random_turn* calculates a direction and distance perpendicular to the first *straight* maneuver for a random distance.
5. *knight_moves* stage is changed to 'second' and the second *straight* maneuver for the random turn is applied.
6. When the second *straight* maneuver is completed, *knight_moves* stage is changed to 'finish'.
7. The maneuver returns to *charge*.

The second *straight* from the *random_turn* can result in another collision. In this event, a whole new *knight_moves* maneuver begins. This can occur more than once until a *knight_moves* finishes.
