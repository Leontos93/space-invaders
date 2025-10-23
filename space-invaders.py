import arcade

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Space invaders"
PLAYER_MOVEMENT_SPEED = 10
BULLET_SPEED = 5


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.player_list = None
        self.player_sprite = None
        self.enemy_list = None
        self.bullet_list = None
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
        for i in range(10):
            enemy_sprite = arcade.Sprite(
                ":resources:images/space_shooter/playerShip1_green.png", 0.5
            )
            enemy_sprite.angle = 180
            enemy_sprite.center_x = 70 + i * 100
            enemy_sprite.top = WINDOW_HEIGHT - 70
            self.enemy_list.append(enemy_sprite)
        # Кулі
        self.bullet_list = arcade.SpriteList()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()

    def on_update(self, delta_time):
        self.player_list.update()
        self.bullet_list.update()
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > WINDOW_WIDTH:
            self.player_sprite.right = WINDOW_WIDTH
        for bullet in self.bullet_list:
            if bullet.bottom > WINDOW_HEIGHT:
                bullet.remove_from_sprite_lists()
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            bullet = arcade.Sprite(
                ":resources:images/space_shooter/laserBlue01.png", 0.8
            )
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top
            bullet.angle = -90
            bullet.change_y = BULLET_SPEED
            self.bullet_list.append(bullet)

    def on_key_release(self, key, modifiers):
        if (
            key == arcade.key.LEFT
            or key == arcade.key.A
            or key == arcade.key.RIGHT
            or key == arcade.key.D
        ):
            self.player_sprite.change_x = 0


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
