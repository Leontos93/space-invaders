import arcade
import random
import json
import os

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Space Invaders - Modern Edition!!!"
PLAYER_MOVEMENT_SPEED = 10
BULLET_SPEED = 5
INITIAL_LIVES = 3
HIGH_SCORE_FILE = "high_score.json"


class Explosion(arcade.Sprite):
    """Particle effect for explosions"""

    def __init__(self, center_x, center_y):
        # Do NOT call super().__init__()! Sprite base creates its own texture we do not use here
        self.center_x = center_x
        self.center_y = center_y
        self.lifetime = 0.3  # Duration in seconds
        self.age = 0
        self.particles = []

        # Create particles
        for _ in range(15):
            particle = {
                "x": center_x,
                "y": center_y,
                "vx": random.uniform(-5, 5),
                "vy": random.uniform(-5, 5),
                "size": random.randint(2, 6),
                "color": random.choice(
                    [
                        arcade.color.YELLOW,
                        arcade.color.ORANGE,
                        arcade.color.RED,
                        arcade.color.WHITE,
                    ]
                ),
            }
            self.particles.append(particle)

    def update(self, delta_time):
        self.age += delta_time
        if self.age >= self.lifetime:
            # If trying to use SpriteList, you must call this manually
            try:
                self.remove_from_sprite_lists()
            except Exception:
                pass
            return

        # Update particle positions
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] -= 0.5  # Gravity effect

    def draw(self):
        alpha = int(255 * max(0, (1 - self.age / self.lifetime)))
        for particle in self.particles:
            color = particle["color"]
            # Add alpha channel to RGB color
            if isinstance(color, tuple) and len(color) == 3:
                rgba = (*color, alpha)
            elif isinstance(color, tuple) and len(color) == 4:
                # Already RGBA, just update alpha
                rgba = (color[0], color[1], color[2], alpha)
            else:
                rgba = (255, 255, 0, alpha)
            # Use arcade's low-level shape draw to avoid texture/black square issue
            arcade.draw_circle_filled(
                particle["x"], particle["y"], particle["size"], rgba
            )


class PowerUp(arcade.Sprite):
    """Power-up items that drop from enemies"""

    def __init__(self, center_x, center_y, power_type):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.power_type = power_type  # 'rapid_fire' or 'multi_shot'
        self.change_y = -2
        self.lifetime = 10.0  # Disappear after 10 seconds
        self.age = 0

        # Use different colors for different power-ups
        if power_type == "rapid_fire":
            self.color = arcade.color.CYAN
        else:
            self.color = arcade.color.MAGENTA

    def update(self, delta_time):
        self.age += delta_time
        if self.age >= self.lifetime:
            self.remove_from_sprite_lists()
            return
        self.center_y += self.change_y

    def draw(self):
        # Draw a simple colored circle with pulsing effect
        size = 15 + int(3 * abs(arcade.utils.lerp(-1, 1, (self.age * 5) % 1)))
        arcade.draw_circle_filled(self.center_x, self.center_y, size, self.color)
        arcade.draw_circle_outline(
            self.center_x, self.center_y, size, arcade.color.WHITE, 2
        )


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        # --- Sprite lists will be created in setup() ---
        self.player_list = None
        self.player_sprite = None
        self.enemy_list = None
        self.bullet_list = None
        self.enemy_bullet_list = None
        self.explosion_list = None
        self.powerup_list = None

        # --- Game state attributes ---
        self.enemy_change_x = 1
        self.game_over = False
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        self.high_score = self.load_high_score()

        # --- Power-up states ---
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.multi_shot_active = False
        self.multi_shot_timer = 0
        self.shoot_cooldown = 0.3  # Base cooldown between shots
        self.last_shot_time = 0

        # --- Pre-load the background texture ---
        self.background = arcade.load_texture("background_space.png")

        # --- Sound effects (will be loaded in setup if available) ---
        self.shoot_sound = None
        self.explosion_sound = None
        self.powerup_sound = None
        self.background_music = None

    def load_high_score(self):
        """Load high score from file"""
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        """Save high score to file"""
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(HIGH_SCORE_FILE, "w") as f:
                    json.dump({"high_score": self.high_score}, f)
            except:
                pass

    def setup(self):
        # Reset game state
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        self.game_over = False
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.multi_shot_active = False
        self.multi_shot_timer = 0
        self.last_shot_time = 0

        # --- Set up the Player ---
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_orange.png", 0.5
        )
        self.player_sprite.center_x = WINDOW_WIDTH / 2
        self.player_sprite.bottom = 10
        self.player_list.append(self.player_sprite)

        # --- Set up the Enemies ---
        self.setup_enemies()

        # --- Set up Bullet lists ---
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.powerup_list = arcade.SpriteList()

        # --- Try to load sounds (gracefully fail if not available) ---
        try:
            # These are built-in arcade sounds
            self.shoot_sound = arcade.Sound(":resources:sounds/laser1.wav")
            self.explosion_sound = arcade.Sound(":resources:sounds/explosion1.wav")
            self.powerup_sound = arcade.Sound(":resources:sounds/upgrade1.wav")
        except:
            pass  # Sounds are optional

    def setup_enemies(self):
        """Create enemies based on current level"""
        self.enemy_list = arcade.SpriteList()
        # Increase enemy count and speed with level
        rows = 3 + (self.level - 1) // 2  # More rows every 2 levels
        cols = 10 + (self.level - 1) // 3  # More columns every 3 levels
        rows = min(rows, 5)  # Cap at 5 rows
        cols = min(cols, 15)  # Cap at 15 columns

        # Increase enemy speed with level
        self.enemy_change_x = 1 + (self.level - 1) * 0.3

        for row in range(rows):
            for col in range(cols):
                enemy_sprite = arcade.Sprite(
                    ":resources:images/space_shooter/playerShip1_green.png", 0.5
                )
                enemy_sprite.angle = 180
                # Position enemies in a grid, centered
                spacing_x = min(90, WINDOW_WIDTH / (cols + 1))
                spacing_y = 60
                start_x = (WINDOW_WIDTH - (cols - 1) * spacing_x) / 2
                enemy_sprite.center_x = start_x + col * spacing_x
                enemy_sprite.top = WINDOW_HEIGHT - 70 - row * spacing_y
                self.enemy_list.append(enemy_sprite)

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
        self.explosion_list.draw()
        self.powerup_list.draw()

        # Draw UI elements
        self.draw_ui()

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
            arcade.draw_text(
                "Press ENTER to restart",
                WINDOW_WIDTH / 2,
                WINDOW_HEIGHT / 2 - 80,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center",
            )

    def draw_ui(self):
        """Draw all UI elements"""
        # Score
        score_text = f"Score: {self.score:,}"
        arcade.draw_text(
            score_text, 10, WINDOW_HEIGHT - 30, arcade.csscolor.WHITE, 20, bold=True
        )

        # High Score
        high_score_text = f"High Score: {self.high_score:,}"
        arcade.draw_text(
            high_score_text, 10, WINDOW_HEIGHT - 60, arcade.csscolor.YELLOW, 18
        )

        # Level
        level_text = f"Level: {self.level}"
        arcade.draw_text(
            level_text,
            WINDOW_WIDTH - 150,
            WINDOW_HEIGHT - 30,
            arcade.csscolor.WHITE,
            20,
            bold=True,
        )

        # Lives
        lives_text = f"Lives: {self.lives}"
        arcade.draw_text(
            lives_text,
            WINDOW_WIDTH - 150,
            WINDOW_HEIGHT - 60,
            arcade.csscolor.WHITE,
            18,
        )

        # Draw life indicators
        for i in range(self.lives):
            arcade.draw_circle_filled(
                10 + i * 25, WINDOW_HEIGHT - 90, 8, arcade.color.RED
            )

        # Power-up indicators
        y_pos = WINDOW_HEIGHT - 120
        if self.rapid_fire_active:
            time_left = max(0, self.rapid_fire_timer)
            arcade.draw_text(
                f"Rapid Fire: {time_left:.1f}s",
                WINDOW_WIDTH - 200,
                y_pos,
                arcade.color.CYAN,
                16,
            )
            y_pos -= 25

        if self.multi_shot_active:
            time_left = max(0, self.multi_shot_timer)
            arcade.draw_text(
                f"Multi Shot: {time_left:.1f}s",
                WINDOW_WIDTH - 200,
                y_pos,
                arcade.color.MAGENTA,
                16,
            )

    def on_update(self, delta_time):
        if self.game_over:
            return

        # Update all sprite lists. This moves the sprites.
        self.player_list.update()
        self.bullet_list.update()
        self.enemy_list.update()
        self.enemy_bullet_list.update()
        self.explosion_list.update(delta_time)
        self.powerup_list.update(delta_time)

        # Update power-up timers
        if self.rapid_fire_active:
            self.rapid_fire_timer -= delta_time
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_active = False
                self.shoot_cooldown = 0.3

        if self.multi_shot_active:
            self.multi_shot_timer -= delta_time
            if self.multi_shot_timer <= 0:
                self.multi_shot_active = False

        self.last_shot_time += delta_time

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
                    # Create explosion effect
                    explosion = Explosion(enemy.center_x, enemy.center_y)
                    self.explosion_list.append(explosion)

                    # Play explosion sound
                    if self.explosion_sound:
                        arcade.play_sound(self.explosion_sound, volume=0.3)

                    # Random chance to drop power-up (10% chance)
                    if random.random() < 0.1:
                        power_type = random.choice(["rapid_fire", "multi_shot"])
                        powerup = PowerUp(enemy.center_x, enemy.center_y, power_type)
                        self.powerup_list.append(powerup)

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
        # Increase shooting frequency with level
        shoot_chance = 200 - (self.level - 1) * 10
        shoot_chance = max(50, shoot_chance)  # Cap at reasonable frequency
        if self.enemy_list and random.randrange(int(shoot_chance)) == 0:
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
                self.lives -= 1

                # Create explosion effect
                explosion = Explosion(
                    self.player_sprite.center_x, self.player_sprite.center_y
                )
                self.explosion_list.append(explosion)

                if self.explosion_sound:
                    arcade.play_sound(self.explosion_sound, volume=0.3)

                if self.lives <= 0:
                    self.game_over = True
                    self.save_high_score()
                    self.player_sprite.remove_from_sprite_lists()
                else:
                    # Respawn player after a brief moment
                    self.player_sprite.center_x = WINDOW_WIDTH / 2
                    self.player_sprite.bottom = 10

        # --- Power-up collision detection ---
        for powerup in self.powerup_list:
            if powerup.top < 0:
                powerup.remove_from_sprite_lists()
            elif arcade.check_for_collision(powerup, self.player_sprite):
                powerup.remove_from_sprite_lists()
                if self.powerup_sound:
                    arcade.play_sound(self.powerup_sound, volume=0.5)

                if powerup.power_type == "rapid_fire":
                    self.rapid_fire_active = True
                    self.rapid_fire_timer = 10.0  # 10 seconds
                    self.shoot_cooldown = 0.1  # Much faster shooting
                elif powerup.power_type == "multi_shot":
                    self.multi_shot_active = True
                    self.multi_shot_timer = 15.0  # 15 seconds

        # --- Win condition ---
        # If the enemy list is empty, advance to next level
        if not self.enemy_list:
            self.level += 1
            self.setup_enemies()
            # Give bonus points for completing level
            self.score += 100 * self.level

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
            self.shoot()

    def shoot(self):
        """Handle player shooting with cooldown and power-ups"""
        # Check cooldown
        if self.last_shot_time < self.shoot_cooldown:
            return

        self.last_shot_time = 0

        # Play shoot sound
        if self.shoot_sound:
            arcade.play_sound(self.shoot_sound, volume=0.2)

        if self.multi_shot_active:
            # Shoot 3 bullets in a spread pattern
            angles = [-10, 0, 10]
            for angle in angles:
                bullet = arcade.Sprite(
                    ":resources:images/space_shooter/laserBlue01.png", 0.8
                )
                bullet.center_x = self.player_sprite.center_x
                bullet.bottom = self.player_sprite.top
                bullet.angle = angle - 90
                # Calculate velocity based on angle
                import math

                bullet.change_y = BULLET_SPEED * math.cos(math.radians(angle))
                bullet.change_x = BULLET_SPEED * math.sin(math.radians(angle))
                self.bullet_list.append(bullet)
        else:
            # Normal single shot
            bullet = arcade.Sprite(
                ":resources:images/space_shooter/laserBlue01.png", 0.8
            )
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top
            bullet.angle = -90
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
