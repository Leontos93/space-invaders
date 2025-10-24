# Space Invaders (Arcade Edition)

A classic Space Invaders-style game created with Python and the [Arcade library](https://arcade.academy/). This project is an adaptation of the "Alien Invasion" game from Eric Matthes' book, "Python Crash Course", but built using the modern and powerful Arcade framework.

The player controls a spaceship at the bottom of the screen and must shoot down an entire fleet of advancing aliens.

 
*(You can replace this placeholder GIF with a real screenshot or GIF of your game)*

## Features

-   Player movement and shooting.
-   A multi-row fleet of enemies that moves horizontally and descends.
-   Randomized enemy shooting.
-   Collision detection for all objects (player bullets, enemy bullets, ships).
-   A scoring system.
-   "Game Over" and "You Win" states.
-   A restart feature to play again after a game ends.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python 3.7+
-   `pip` (Python package installer)

### Installation

1.  **Clone the repository or download the project files.**
    Make sure you have `space_invaders.py` and `background_space.png` in the same directory.
    ```sh
    git clone https://github/Leontos93/space-invaders.git
    cd your-project-folder
    ```

2.  **It is highly recommended to create and activate a virtual environment.**
    -   On Windows:
        ```sh
        python -m venv .venv
        .\.venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```sh
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install the required dependencies.**
    ```sh
    pip install arcade
    ```

### How to Run

Once the setup is complete, run the game with the following command:

```sh
python space_invaders.py
```

## How to Play

-   **Move:** Use the **Arrow Keys** (Left/Right) or **A** / **D** keys to move your spaceship.
-   **Shoot:** Press the **Spacebar** to fire your laser.
-   **Restart:** After the game ends (win or lose), press **Enter** to play again.

## Credits & Assets

-   **Game Logic & Development:** This project was developed as a learning exercise.
-- **Sprites:** All game sprites (player ship, enemy ships, bullets) are from the built-in resource library provided by Arcade.
-   **Background:** The space background image was sourced from [OpenGameArt.org](https://opengameart.org).