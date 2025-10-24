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

        # --- Sprite lists will be created in setup() ---
        self.player_list = None
        self.player_sprite = None
        self.enemy_list = None
        self.bullet_list = None
        self.enemy_bullet_list = None

        # --- Game state attributes ---
        self.enemy_change_x = 1
        self.game_over = False
        self.score = 0

        # --- Pre-load the background texture ---
        self.background = arcade.load_texture("background_space.png")

    def setup(self):
        # Reset the score for a new game
        self.score = 0

        # --- Set up the Player ---
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_orange.png", 0.5
        )
        self.player_sprite.center_x = WINDOW_WIDTH / 2
        self.player_sprite.bottom = 10
        self.player_list.append(self.player_sprite)

        # --- Set up the Enemies ---
        self.enemy_list = arcade.SpriteList()
        # Create a grid of enemies using nested loops
        for row in range(3):
            for colum in range(10):
                enemy_sprite = arcade.Sprite(
                    ":resources:images/space_shooter/playerShip1_green.png", 0.5
                )
                enemy_sprite.angle = 180  # Rotate enemy to face down
                # Position enemies in a grid
                enemy_sprite.center_x = 70 + colum * 100
                enemy_sprite.top = WINDOW_HEIGHT - 70 - row * 60
                self.enemy_list.append(enemy_sprite)

        # --- Set up Bullet lists ---
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()

    def on_draw(self):
        self.clear()

        # Draw the background texture
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        # Draw all the sprite lists
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()

        # Draw the current score on the screen
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

        # If the game is over, draw the appropriate message
        if self.game_over:
            # Check if all enemies are defeated to show "YOU WIN!"
            message = "YOU WIN!" if not self.enemy_list else "GAME OVER"
            arcade.draw_text(
                message,
                WINDOW_WIDTH / 2,
                WINDOW_HEIGHT / 2,
                arcade.color.WHITE,
                64,
                anchor_x="center",
                anchor_y="center",
            )

    def on_update(self, delta_time):
        # Update all sprite lists. This moves the sprites.
        self.player_list.update()
        self.bullet_list.update()
        self.enemy_list.update()
        self.enemy_bullet_list.update()

        # Prevent the player from moving off-screen
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        elif self.player_sprite.right > WINDOW_WIDTH:
            self.player_sprite.right = WINDOW_WIDTH

        # --- Player's bullets logic ---
        for bullet in self.bullet_list:
            # Check for collision between a bullet and the enemy list
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if hit_list:
                bullet.remove_from_sprite_lists()
                for enemy in hit_list:
                    enemy.remove_from_sprite_lists()
                    self.score += 10
                continue  # Move to the next bullet, since this one is gone

            # Remove bullet if it goes off the top of the screen
            if bullet.bottom > self.height:
                bullet.remove_from_sprite_lists()

        # --- Enemy fleet movement logic ---
        move_down = False
        # Manually update each enemy's horizontal position
        for enemy in self.enemy_list:
            enemy.center_x += self.enemy_change_x
            # Check if any enemy has hit the screen boundary
            if (enemy.right > WINDOW_WIDTH and self.enemy_change_x > 0) or (
                enemy.left < 0 and self.enemy_change_x < 0
            ):
                move_down = True

        # If a boundary was hit, reverse direction and move the whole fleet down
        if move_down:
            self.enemy_change_x *= -1
            for enemy in self.enemy_list:
                enemy.center_y -= 20

        # --- Enemy shooting logic ---
        # Only shoot if there are enemies left
        if self.enemy_list and random.randrange(200) == 0:
            # Pick a random enemy from the list to shoot
            shooting_enemy = random.choice(self.enemy_list)
            enemy_bullet = arcade.Sprite(
                ":resources:images/space_shooter/laserRed01.png"
            )
            enemy_bullet.center_x = shooting_enemy.center_x
            enemy_bullet.top = shooting_enemy.bottom
            enemy_bullet.angle = 180
            enemy_bullet.change_y = -BULLET_SPEED
            self.enemy_bullet_list.append(enemy_bullet)

        # --- Enemy bullets logic ---
        for bullet in self.enemy_bullet_list:
            # Remove bullet if it goes off the bottom of the screen
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()
            # Check if an enemy bullet hits the player
            elif arcade.check_for_collision(bullet, self.player_sprite):
                bullet.remove_from_sprite_lists()
                self.game_over = True
                self.player_sprite.remove_from_sprite_lists()

        # --- Win condition ---
        # If the enemy list is empty, the player wins
        if not self.enemy_list:
            self.game_over = True

    def on_key_press(self, key, modifiers):
        # --- Game Restart Logic ---
        # If the game is over, check for the ENTER key to restart
        if self.game_over and key == arcade.key.ENTER:
            self.setup()  # Reset the game
            self.game_over = False  # Set the game state to active

        # --- Player Controls ---
        # Horizontal movement
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        # Shooting
        elif key == arcade.key.SPACE:
            bullet = arcade.Sprite(
                ":resources:images/space_shooter/laserBlue01.png", 0.8
            )
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top
            bullet.angle = (
                -90
            )  # This rotation is optional as the sprite is already oriented up
            bullet.change_y = BULLET_SPEED
            self.bullet_list.append(bullet)

    def on_key_release(self, key, modifiers):
        # Stop player movement when the key is released
        if (
            key == arcade.key.LEFT
            or key == arcade.key.A
            or key == arcade.key.RIGHT
            or key == arcade.key.D
        ):
            self.player_sprite.change_x = 0


def main():
    """Main function to set up and run the game."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
