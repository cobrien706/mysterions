# mysterions - An arcade-style action game - collect coins, get around obstacles, avoid monsters, try not to die.

# :robot:  :ghost::ghost::ghost:  :ghost:

This is a demo game for the [final assignment](https://programming-25.mooc.fi/part-14/4-your-own-game) for the  
[University of Helsinki MOOC Center](https://www.mooc.fi/en/) online course [Python Programming MOOC 2025](https://programming-25.mooc.fi/).

The goal of this project was to fulfill the assignment, but also to try to create code that could be readily modified, maintained and improved upon by other developers, to better familiarize myself with better techniques, writing 'pythonic' code, and creating as solid documentation as possible, using resources such as Sphinx and Read the Docs.

# Description

The project is a relatively simple Python game kept to one script using PyGame. At each round the playing field is randomly populated with obstacles to navigate around, coins to be collected for points, monsters to be avoided, and a robot, which is the player.

# Gameplay

<<img width="977" height="852" alt="mysterions_game_board_example" src="https://github.com/user-attachments/assets/2570602c-9c9e-44f3-bfe1-9336c4393e82" />

Gameplay is almost self-explanitory with no intentional surprises. 
- The player starts with a health level of 100% and 3 lives.
- Player gets a momentary head start (three seconds OOTB) before the monsters start moving. This time allows the user to locate their character and get away from monsters in close proximity.
- Player navigates the board by holding down the arrow keys (LEFT ⬅️, RIGHT ➡️, UP ⬆️, DOWN ⬇️) (LRUD) for the corresponding direction. Keys can be combined (e.g. hold down UP and LEFT at the same time) to move diagonally.
- The player navigates through the board to collect coins, earing 100 points a coin, while the monsters on the board pursue the player.
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



All the monsters follow the same basic strategy in pursing the player and navigating the board:

