import arcade

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Space invaders"
PLAYER_MOVEMENT_SPEED = 2


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.background = arcade.load_texture("background_space.png")
        self.player_list = None

    def setup(self):
        self.player_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_orange.png", 0.5
        )
        self.player_sprite.center_x = WINDOW_WIDTH / 2
        self.player_sprite.bottom = 10
        self.player_sprite.append(self.player_list)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
