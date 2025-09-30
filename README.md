# mysterions - An arcade-style action game - collect coins, get around obstacles, avoid monsters, try not to die.

# :robot:  :ghost::ghost::ghost:  :ghost:

This is a demo game for the [final assignment](https://programming-25.mooc.fi/part-14/4-your-own-game) for the  
[University of Helsinki MOOC Center](https://www.mooc.fi/en/) online course [Python Programming MOOC 2025](https://programming-25.mooc.fi/).

The goal of this project was to fulfill the assignment, but also to try to create code that could be readily modified, maintained and improved upon by other developers, to better familiarize myself with better techniques, writing 'pythonic' code, and creating as solid documentation as possible, using resources such as Sphinx and Read the Docs.

# Description

The project is a relatively simple Python game kept to once script file based on PyGame. At each round the playing field is randomly populated with obstacles to navigate around ('Doors', although in this case they don't open), coins to be collected for points, monsters to be avoided, and a robot, which is the player.

Game play is almost self-explanitory with no surprises. 
- The player starts with a health level of 100% and 3 lives.
- Player navigates on the board holding down the arrow keys (⬆️⬇️⬅️➡️) for the correspoding direction. Keys can be combined (e.g. hold down UP and LEFT at the same time) to move diagonally.
- The player navigates through the board to collect coins, earing 100 points a coin, while the monsters on the board pursue the player.
- If the player contacts a monster, the player's health drops 20% and the monster disappears.
- A round ends when either all the coins are collected or health declines to zero.
- If the player collects all the coins, they are awarded an additional life (to a maximum of five.)
- If the player's health reaches zero before all the coins are collected, they lose a life. If the player loses all their lives, the game ends.
- At game end, player has the option of continuing the game (essentialy they start a new game but continue adding to their score), start a new game, or quit.

As configured OOTB, the player moves twice as fast as the monsters and can move in all directions. Monsters can only move left, right, up, or down for any particular stretch of movement. (They can only move diagonally once they are close to the player.)

That's it. No boss fights, no transition screens, no pausing, no leader board, not even sound effects.

Whether the game is *fun* as-s is of course subjective. But the number of monsters, coins and obstacles, and their placement, randomly changes from round to round, gameplay can go from 'That's easy!' to 'Oh dear lord, no.' unexpectedly.





