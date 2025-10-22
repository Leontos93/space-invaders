import arcade

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Space invaders"
PLAYER_MOVEMENT_SPEED = 2


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.player_list = None
        self.player_sprite = None
        self.enemy_list = None
        self.enemy_sprite = None
        self.background = arcade.load_texture("background_space.png")

    def setup(self):
        # Встановлюємо гравця
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_orange.png", 0.5
        )
        self.player_sprite.center_x = WINDOW_WIDTH / 2
        self.player_sprite.bottom = 10
        self.player_list.append(self.player_sprite)
        # Встановлюємо ворога
        self.enemy_list = arcade.SpriteList()
        self.enemy_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_green.png", 0.5
        )
        self.enemy_sprite.center_x = WINDOW_WIDTH / 2
        self.enemy_sprite.bottom = 10
        self.enemy_list.append(self.enemy_sprite)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        self.player_list.draw()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
