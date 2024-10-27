import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Centered Triangle Character with Constant Movement")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
DARK_GREEN = (0, 100, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Character settings
character_size = 50
character_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
character_speed = 1.5  # Set constant slow speed
character_angle = 0
character_hp = 4  # Player can be hit up to 4 times before dying

# Enemy settings
enemy_size = 30
enemies = []
enemy_spawn_rate = 100  # Spawn enemies more frequently  # milliseconds
last_spawn_time = 0

# Bullet settings
bullets = []
bullet_speed = 10  # Increased bullet speed for accuracy
bullet_radius = 5
bullet_cooldown = int(100)  # milliseconds (1.4x faster shoot rate)
last_shot_time = 0

# World settings (a larger background)
WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200
world_offset = [0, 0]

# Load background image
background_image = pygame.image.load('space.png')
background_image = pygame.transform.scale(background_image, (WORLD_WIDTH, WORLD_HEIGHT))
world_surface = background_image

# Draw grid background
grid_size = 40  # Size of each grid cell
for x in range(0, WORLD_WIDTH, grid_size):
    pygame.draw.line(world_surface, DARK_GREEN, (x, 0), (x, WORLD_HEIGHT))
for y in range(0, WORLD_HEIGHT, grid_size):
    pygame.draw.line(world_surface, DARK_GREEN, (0, y), (WORLD_WIDTH, y))

# Function to draw a triangle
def draw_triangle(surface, position, size, color, angle):
    half_size = size // 2
    points = [
        (0, -half_size),  # Top point
        (-half_size, half_size),  # Bottom left
        (half_size, half_size)  # Bottom right
    ]
    # Rotate points based on the angle
    rotated_points = []
    cos_theta = math.cos(math.radians(angle))
    sin_theta = math.sin(math.radians(angle))
    for x, y in points:
        rotated_x = x * cos_theta - y * sin_theta + position[0]
        rotated_y = x * sin_theta + y * cos_theta + position[1]
        rotated_points.append((rotated_x, rotated_y))
    pygame.draw.polygon(surface, color, rotated_points)

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and character_hp <= 0:
            # Restart the game if player clicks after death
            character_hp = 4
            enemies = []
            bullets = []
            last_spawn_time = current_time
            last_shot_time = current_time

    # Get keys pressed
    keys = pygame.key.get_pressed()
    
    # Disable movement when character is dead
    if character_hp > 0:
        # Movement controls (affect the world offset instead of character position)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            world_offset[0] += character_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            world_offset[0] -= character_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            world_offset[1] += character_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            world_offset[1] -= character_speed

    # Enemy spawning
    if current_time - last_spawn_time > enemy_spawn_rate and character_hp > 0:
        # Spawn enemies outside the FOV of the player
        spawn_side = random.choice(['left', 'right', 'top', 'bottom'])
        if spawn_side == 'left':
            new_enemy_pos = [random.randint(-WORLD_WIDTH, -SCREEN_WIDTH // 2), random.randint(0, WORLD_HEIGHT)]
        elif spawn_side == 'right':
            new_enemy_pos = [random.randint(SCREEN_WIDTH // 2, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)]
        elif spawn_side == 'top':
            new_enemy_pos = [random.randint(0, WORLD_WIDTH), random.randint(-WORLD_HEIGHT, -SCREEN_HEIGHT // 2)]
        else:
            new_enemy_pos = [random.randint(0, WORLD_WIDTH), random.randint(SCREEN_HEIGHT // 2, WORLD_HEIGHT)]
        new_enemy_speed = random.uniform(0.5, 1.5)
        enemies.append({"pos": new_enemy_pos, "speed": new_enemy_speed})
        last_spawn_time = current_time

    # Enemy behavior
    for enemy in enemies[:]:
        enemy_pos = enemy["pos"]
        speed = enemy["speed"]

        # Calculate direction vector towards the player
        dir_vector = [character_pos[0] - (enemy_pos[0] + world_offset[0]), character_pos[1] - (enemy_pos[1] + world_offset[1])]
        distance = math.hypot(dir_vector[0], dir_vector[1])

        if distance != 0:
            # Normalize direction vector
            dir_vector[0] /= distance
            dir_vector[1] /= distance

            # Update enemy position
            enemy_pos[0] += dir_vector[0] * speed
            enemy_pos[1] += dir_vector[1] * speed

        # Check for collision with player
        if distance < (character_size + enemy_size) // 2:
            character_hp -= 1
            enemies.remove(enemy)

    # Auto-aim and shoot bullets within FOV
    if current_time - last_shot_time > bullet_cooldown and character_hp > 0:
        if enemies:
            # Find the closest enemy within FOV
            closest_enemy = min(enemies, key=lambda e: math.hypot(character_pos[0] - (e["pos"][0] + world_offset[0]), character_pos[1] - (e["pos"][1] + world_offset[1])))
            enemy_pos = closest_enemy["pos"]
            dir_vector = [enemy_pos[0] + world_offset[0] - character_pos[0], enemy_pos[1] + world_offset[1] - character_pos[1]]
            distance = math.hypot(dir_vector[0], dir_vector[1])

            if distance < SCREEN_WIDTH // 2 and distance != 0:
                # Normalize direction vector
                dir_vector[0] /= distance
                dir_vector[1] /= distance


                # Set the character's angle to point towards the enemy
                character_angle = math.degrees(math.atan2(dir_vector[1], dir_vector[0]))


                # Shoot multiple pellets in a cone
                num_pellets = 3  # Number of pellets for shotgun effect
                cone_angle = 20  # Degrees for the shotgun spread
                for i in range(num_pellets):
                    angle_offset = (i - num_pellets // 2) * (cone_angle / num_pellets)
                    pellet_angle = math.radians(character_angle + angle_offset)
                    bullet_velocity = [math.cos(pellet_angle) * bullet_speed, math.sin(pellet_angle) * bullet_speed]
                    bullets.append({"pos": character_pos[:], "velocity": bullet_velocity})
                last_shot_time = current_time

    # Update bullet positions
    for bullet in bullets[:]:
        bullet["pos"][0] += bullet["velocity"][0]
        bullet["pos"][1] += bullet["velocity"][1]

        # Remove bullets that go off-screen
        if (bullet["pos"][0] < 0 or bullet["pos"][0] > SCREEN_WIDTH or
                bullet["pos"][1] < 0 or bullet["pos"][1] > SCREEN_HEIGHT):
            bullets.remove(bullet)

    # Check for bullet collisions with enemies
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            enemy_screen_pos = [enemy["pos"][0] + world_offset[0], enemy["pos"][1] + world_offset[1]]
            distance = math.hypot(bullet["pos"][0] - enemy_screen_pos[0], bullet["pos"][1] - enemy_screen_pos[1])
            if distance < enemy_size // 2:
                enemies.remove(enemy)
                bullets.remove(bullet)
                break

    # Drawing
    screen.fill(BLACK)  # Clear the screen

    # Blit (draw) the world surface onto the screen using the world offset
    screen.blit(world_surface, world_offset)

    # Draw the character as a black triangle (always in the center of the screen)
    pygame.draw.circle(screen, (255, 105, 180), character_pos, character_size // 2)
    # Draw an arrow in the middle facing the shooting direction
    arrow_length = character_size
    end_x = character_pos[0] + arrow_length * math.cos(math.radians(character_angle))
    end_y = character_pos[1] + arrow_length * math.sin(math.radians(character_angle))
    pygame.draw.line(screen, WHITE, character_pos, (end_x, end_y), 3)

    # Draw enemies only if player is alive
    if character_hp > 0:
        for enemy in enemies:
            enemy_screen_pos = [enemy["pos"][0] + world_offset[0], enemy["pos"][1] + world_offset[1]]
            pygame.draw.circle(screen, GREEN, (int(enemy_screen_pos[0]), int(enemy_screen_pos[1])), enemy_size // 2)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, RED, (int(bullet["pos"][0]), int(bullet["pos"][1])), bullet_radius)

    # Draw character HP
    font = pygame.font.Font(None, 36)
    hp_text = font.render(f"HP: {character_hp}", True, WHITE)
    screen.blit(hp_text, (10, 10))

    # If character HP is 0, draw game over text and start over button
    if character_hp <= 0:
        game_over_text = font.render("Game Over! Click to Start Over", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))

    # Update the display
    pygame.display.flip()

    # Ensure a constant frame rate (e.g., 60 frames per second)
    clock.tick(60)

# Quit Pygame
pygame.quit()
