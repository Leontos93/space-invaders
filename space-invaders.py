import arcade
import random

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
        self.enemy_bullet_list = None
        self.enemy_change_x = 1
        self.game_over = False
        self.score = 0
        self.background = arcade.load_texture("background_space.png")

    def setup(self):
        self.score = 0
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
        for row in range(3):
            for colum in range(10):
                enemy_sprite = arcade.Sprite(
                    ":resources:images/space_shooter/playerShip1_green.png", 0.5
                )
                enemy_sprite.angle = 180
                enemy_sprite.center_x = 70 + colum * 100
                enemy_sprite.top = WINDOW_HEIGHT - 70 - row * 60
                self.enemy_list.append(enemy_sprite)
        # Кулі
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)
        if self.game_over:
            arcade.draw_text(
                "Game Over",
                WINDOW_WIDTH / 2,
                WINDOW_HEIGHT / 2,
                arcade.color.WHITE,
                64,
                anchor_x="center",
                anchor_y="center",
            )

    def on_update(self, delta_time):
        self.player_list.update()
        self.bullet_list.update()
        self.enemy_list.update()
        self.enemy_bullet_list.update()
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > WINDOW_WIDTH:
            self.player_sprite.right = WINDOW_WIDTH
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if hit_list:
                bullet.remove_from_sprite_lists()
                for enemy in hit_list:
                    enemy.remove_from_sprite_lists()
                    self.score += 10
                continue
            if bullet.bottom > self.height:
                bullet.remove_from_sprite_lists()
        move_down = False
        for enemy in self.enemy_list:
            enemy.center_x += self.enemy_change_x
            if enemy.right > WINDOW_WIDTH and self.enemy_change_x > 0:
                move_down = True
            if enemy.left < 0 and self.enemy_change_x < 0:
                move_down = True
        if move_down:
            self.enemy_change_x *= -1
            for enemy in self.enemy_list:
                enemy.center_y -= 20
        if self.enemy_list and random.randrange(200) == 0:
            shooting_enemy = random.choice(self.enemy_list)
            enemy_bullet = arcade.Sprite(
                ":resources:images/space_shooter/laserRed01.png"
            )
            enemy_bullet.center_x = shooting_enemy.center_x
            enemy_bullet.top = shooting_enemy.bottom
            enemy_bullet.angle = 180
            enemy_bullet.change_y = -BULLET_SPEED
            self.enemy_bullet_list.append(enemy_bullet)
        for bullet in self.enemy_bullet_list:
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()
            elif arcade.check_for_collision(bullet, self.player_sprite):
                bullet.remove_from_sprite_lists()
                self.game_over = True
                self.player_sprite.remove_from_sprite_lists()

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
