from q_algorithm import (
    choose_action,
    get_state,
    update_q_value,
    action_to_direction,
    calculate_reward,
)
import pygame
import random
import sys
import matplotlib.pyplot as plt
from config import (
    GRID_SIZE,
    CELL_SIZE,
    SCREEN_SIZE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
)
from config import (
    BACKGROUND_COLOR,
    SNAKE_COLOR,
    SNAKE_EYE_COLOR,
    APPLE_GREEN_COLOR,
    APPLE_RED_COLOR,
)
import os

# Initialize pygame
pygame.init()


def init_snake(length=3):
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right
    dx, dy = random.choice(dirs)
    if dx == 1:        # moving right, body extends left
        min_x = length - 1
        max_x = GRID_SIZE - 1
    elif dx == -1:     # moving left, body extends right
        min_x = 0
        max_x = GRID_SIZE - length
    else:              # vertical movement, any x
        min_x = 0
        max_x = GRID_SIZE - 1

    if dy == 1:        # moving down, body extends up
        min_y = length - 1
        max_y = GRID_SIZE - 1
    elif dy == -1:     # moving up, body extends down
        min_y = 0
        max_y = GRID_SIZE - length
    else:              # horizontal movement, any y
        min_y = 0
        max_y = GRID_SIZE - 1

    head_x = random.randint(min_x, max_x)
    head_y = random.randint(min_y, max_y)

    # Body segments placed opposite movement direction
    snake = [(head_x, head_y)]
    for i in range(1, length):
        snake.append((head_x - dx * i, head_y - dy * i))
    return snake, (dx, dy), length


# Track the last 5 moves made by the AI
last_moves = []


# Initialize apples
green_apples = []  # List to store green apple positions
red_apple = None   # Variable to store red apple position

# Clock
clock = pygame.time.Clock()

# Random snake spawn
snake, snake_dir, snake_length = init_snake()

# Track when the current game started (ticks)
game_start_ticks = 0


def prune_q_table(q_table, threshold=0.01):
    """
    Remove entries with Q-values close to zero and keep only last 1000 entries.
    """
    # Remove entries with Q-values close to zero
    keys_to_remove = [
        key for key, value in q_table.items() if abs(value) < threshold
    ]
    for key in keys_to_remove:
        del q_table[key]
    return q_table


# Function to draw the grid
def draw_grid():
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        for y in range(0, SCREEN_SIZE, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            # Alternate between two shades of blue for the checkered pattern
            if (x // CELL_SIZE + y // CELL_SIZE) % 2 == 0:
                color = (100, 149, 237)
            else:
                color = (70, 130, 180)
            pygame.draw.rect(screen, color, rect)


# Function to draw the snake
def draw_snake():
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE,
                           CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, SNAKE_COLOR, rect)  # Fill the snake body
        if i == 0:  # Draw googly eyes on the head
            eye_radius = CELL_SIZE // 8
            eye_offset = CELL_SIZE // 4
            eye1 = (segment[0] * CELL_SIZE + eye_offset,
                    segment[1] * CELL_SIZE + eye_offset)
            eye2 = (segment[0] * CELL_SIZE + CELL_SIZE - eye_offset,
                    segment[1] * CELL_SIZE + eye_offset)
            pygame.draw.circle(screen, SNAKE_EYE_COLOR, eye1, eye_radius)
            pygame.draw.circle(screen, SNAKE_EYE_COLOR, eye2, eye_radius)


# Function to draw apples
def draw_apples():
    global red_apple

    G_S = GRID_SIZE

    def get_empty_spaces():
        # Get all grid positions that are not occupied by the snake or apples
        occupied = set(snake + green_apples + [red_apple])
        return [
            (x, y)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
            if (x, y) not in occupied
        ]

    # Ensure green_apples and red_apple are initialized
    if not green_apples:
        green_apples.extend([
            (random.randint(0, G_S - 1), random.randint(0, G_S - 1))
            for _ in range(2)
        ])
    if not red_apple:
        red_apple = (random.randint(0, GRID_SIZE - 1),
                     random.randint(0, GRID_SIZE - 1))

    empty_spaces = get_empty_spaces()

    # Redraw green apples if they overlap with the snake or each other
    for i in range(len(green_apples)):
        if green_apples[i] in snake or green_apples[i] in green_apples[:i]:
            if empty_spaces:
                green_apples[i] = random.choice(empty_spaces)
                empty_spaces.remove(green_apples[i])

    # Redraw red apple if it overlaps with the snake or green apples
    if red_apple in snake or red_apple in green_apples:
        if empty_spaces:
            red_apple = random.choice(empty_spaces)
            empty_spaces.remove(red_apple)

    # Draw green apples
    for apple in green_apples:
        rect = pygame.Rect(apple[0] * CELL_SIZE,
                           apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, APPLE_GREEN_COLOR, rect)

    # Draw red apple
    rect = pygame.Rect(red_apple[0] * CELL_SIZE,
                       red_apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, APPLE_RED_COLOR, rect)


# Function to move the snake
def move_snake():
    global snake
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    snake = [new_head] + snake[:snake_length - 1]
    # print(f"Snake moved to {new_head} in direction {snake_dir}")


# Function to check collisions
def check_collisions():
    global snake_length, red_apple

    # Helper function to get all empty spaces
    def get_empty_spaces():
        occupied = set(snake + green_apples + [red_apple])
        return [
            (x, y)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
            if (x, y) not in occupied
        ]

    # Check wall collision
    head_x, head_y = snake[0]
    if head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE:
        return True

    # Check self collision
    if snake[0] in snake[1:]:
        return True

    # Check green apple collision
    for apple in green_apples:
        if snake[0] == apple:
            snake_length += 1
            green_apples.remove(apple)
            empty_spaces = get_empty_spaces()
            if empty_spaces:
                green_apples.append(random.choice(empty_spaces))

    # Check red apple collision
    if snake[0] == red_apple:
        snake_length -= 1
        if snake_length <= 0:
            return True
        empty_spaces = get_empty_spaces()
        if empty_spaces:
            red_apple = random.choice(empty_spaces)

    return False


# New helper to get vision ray cells (same logic directions as get_state)
def get_vision_cells():
    head_x, head_y = snake[0]
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    vision = set()
    for dx, dy in dirs:
        x, y = head_x + dx, head_y + dy
        while 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            vision.add((x, y))
            x += dx
            y += dy
    return vision


def draw_mini_board():
    # Mini board parameters
    padding = 10
    area_width = 200 - 2 * padding
    mini_cell = max(6, area_width // GRID_SIZE)
    origin_x = SCREEN_SIZE + padding
    origin_y = padding

    vision_cells = get_vision_cells()
    head = snake[0]

    HIDDEN_COLOR = (15, 15, 15)   # Fully hidden
    VISION_BG_COLOR = (65, 65, 65)
    HEAD_COLOR = (0, 255, 0)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(origin_x + x * mini_cell,
                               origin_y + y * mini_cell,
                               mini_cell - 1,
                               mini_cell - 1)

            visible = (x, y) in vision_cells or (x, y) == head
            if not visible:
                # Completely hidden cell (no objects shown)
                pygame.draw.rect(screen, HIDDEN_COLOR, rect)
                continue

            # Background for visible ray cells
            pygame.draw.rect(screen, VISION_BG_COLOR, rect)

            # Draw entities only if visible
            if (x, y) == head:
                pygame.draw.rect(screen, HEAD_COLOR, rect)
            elif (x, y) in snake[1:]:
                pygame.draw.rect(screen, SNAKE_COLOR, rect)
            elif (x, y) in green_apples:
                pygame.draw.rect(screen, APPLE_GREEN_COLOR, rect)
            elif (x, y) == red_apple:
                pygame.draw.rect(screen, APPLE_RED_COLOR, rect)

    # Outline
    outline_rect = pygame.Rect(origin_x - 2, origin_y - 2,
                               GRID_SIZE * mini_cell + 3,
                               GRID_SIZE * mini_cell + 3)
    pygame.draw.rect(screen, (200, 200, 200), outline_rect, 2)


def draw_right_section():
    # Background
    right_section_rect = pygame.Rect(SCREEN_SIZE, 0, 200, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (40, 40, 40), right_section_rect)

    draw_mini_board()

    font = pygame.font.Font(None, 26)
    text_color = (255, 255, 255)

    # Position text under mini board
    text_start_y = 10 + (200 - 20) // GRID_SIZE * GRID_SIZE
    text_start_y = max(text_start_y,
                       10 + 10 + ((200 - 20) // GRID_SIZE) * GRID_SIZE)
    text_start_y += 20

    # Elapsed time in seconds
    elapsed_sec = max(0, (pygame.time.get_ticks() - game_start_ticks) / 1000.0)

    length_text = font.render(f"Length: {snake_length}", True, text_color)
    screen.blit(length_text, (SCREEN_SIZE + 10, text_start_y))

    time_text = font.render(f"Time: {elapsed_sec:.1f}s", True, text_color)
    screen.blit(time_text, (SCREEN_SIZE + 10, text_start_y + 28))

    for i, move in enumerate(last_moves[-5:]):
        mv = font.render(f"{move}", True, text_color)
        screen.blit(mv, (SCREEN_SIZE + 20, text_start_y + 55 + i * 22))

    pygame.draw.line(screen, (255, 255, 255),
                     (SCREEN_SIZE, 0), (SCREEN_SIZE, SCREEN_HEIGHT), 2)


def build_ascii_board():
    board = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    vision = get_vision_cells()
    head = snake[0]

    # Mark visible empty cells first
    for (x, y) in vision | {head}:
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            board[y][x] = '0'

    # Entities override
    # Body (excluding head)
    for seg in snake[1:]:
        if seg in vision:
            x, y = seg
            board[y][x] = 'S'
    # Apples
    for ax, ay in green_apples:
        if (ax, ay) in vision:
            board[ay][ax] = 'G'
    if red_apple in vision:
        rx, ry = red_apple
        board[ry][rx] = 'R'
    # Head last
    hx, hy = head
    board[hy][hx] = 'H'

    return "\n".join("".join(row) for row in board)


def wait_for_close():
    # Wait until user closes the window, presses any key, or clicks
    while True:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT,
                              pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
        pygame.time.delay(50)


def play(q_table, verbose=False):
    global snake, snake_dir, snake_length
    global green_apples, red_apple, screen, g_s_tick
    # Re-randomize snake & apples at start of play
    snake, snake_dir, snake_length = init_snake()
    green_apples = []
    red_apple = None

    # Start timer for this game
    g_s_tick = pygame.time.get_ticks()

    action_names = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}

    # Initialize the screen for playing
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game - Play Mode")

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_snake()
        draw_apples()
        draw_right_section()
        pygame.display.flip()

        # Get the current state
        state = get_state(snake, green_apples, red_apple)

        # Choose the best action based on the Q-table (exploit only)
        action = choose_action(state, 0.01, snake_dir, q_table)
        snake_dir = action_to_direction(action, snake_dir)

        if verbose:
            print(build_ascii_board())
            print(f"Chosen action: {action_names.get(action)}")

        # Move the snake
        move_snake()

        # Check for collisions
        if check_collisions():
            print(f"Game Over!, Final Length: {snake_length}")
            # Show final frame with a simple overlay and wait for user
            overlay_bg = pygame.Surface((SCREEN_WIDTH,
                                         SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay_bg.fill((0, 0, 0, 120))
            screen.blit(overlay_bg, (0, 0))
            font_big = pygame.font.Font(None, 48)
            font_small = pygame.font.Font(None, 28)
            elapsed_sec = max(0, (pygame.time.get_ticks() - g_s_tick) / 1000.0)
            text1 = font_big.render("Game Over", True, (255, 255, 255))
            text2 = font_small.render(
                f"Final Length: {snake_length}, Final Direction: {snake_dir} "
                f"Time: {elapsed_sec:.1f}s", True, (255, 255, 255)
            )
            text3 = font_small.render("Press any key or click to exit",
                                      True, (200, 200, 200))
            screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 60))
            screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 20))
            screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 20))
            pygame.display.flip()
            wait_for_close()
            return  # do not auto-quit; return to caller

        # Control the game speed
        clock.tick(FPS)


def play_multiple_games(q_table, verbose=False, num_games=1000):
    global snake, snake_dir, snake_length, green_apples, red_apple

    max_length = 0
    total_length = 0
    best_game_states = []

    action_names = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}

    for game in range(num_games):
        # Reset the game state (random spawn)
        snake, snake_dir, snake_length = init_snake()
        green_apples = [(random.randint(0, GRID_SIZE - 1),
                         random.randint(0, GRID_SIZE - 1)) for _ in range(2)]
        red_apple = (random.randint(0, GRID_SIZE - 1),
                     random.randint(0, GRID_SIZE - 1))

        game_states = []  # To store the states of this game
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # Save the current state for replay
            game_states.append((list(snake), snake_dir,
                                snake_length, list(green_apples), red_apple))

            # Get the current state
            state = get_state(snake, green_apples, red_apple)

            # Choose the best action based on the Q-table (exploit only)
            action = choose_action(state, 0.01, snake_dir, q_table)
            snake_dir = action_to_direction(action, snake_dir)

            if verbose:
                print(build_ascii_board())
                print(f"Chosen action: {action_names.get(action)}")

            # Move the snake
            move_snake()

            # Check for collisions
            if check_collisions():
                running = False

        # Update total length for average calculation
        total_length += snake_length

        # Check if this game achieved a new maximum length
        if snake_length > max_length:
            max_length = snake_length
            best_game_states = game_states

    avg_length = total_length / num_games
    print(f"All {num_games} games averaged a length of {avg_length:.2f}.")
    print(f"Best game achieved a length of {max_length}. Replaying it now...")

    # Replay the best game
    replay_game(best_game_states)


def replay_game(game_states):
    global snake, snake_dir, snake_length, green_apples, red_apple, screen

    # Initialize the screen for replay
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game - Replay of Best Game")

    clock = pygame.time.Clock()

    for state in game_states:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Exit the program gracefully
        snake, snake_dir, snake_length, green_apples, red_apple = state

        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_snake()
        draw_apples()
        draw_right_section()
        pygame.display.flip()

        clock.tick(FPS)  # Control the replay speed

    print("Replay completed!")
    # Show final frame with a simple overlay and wait for user
    overlay_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay_bg.fill((0, 0, 0, 120))
    screen.blit(overlay_bg, (0, 0))
    font_big = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 28)
    elapsed_sec = max(0, (pygame.time.get_ticks() - game_start_ticks) / 1000.0)
    text1 = font_big.render("Replay Over", True, (255, 255, 255))
    text2 = font_small.render(f"Final Length: {snake_length}, Final Direction:\
    {snake_dir}   Time: {elapsed_sec:.1f}s", True, (255, 255, 255))
    text3 = font_small.render("Press any key or click to exit", True,
                              (200, 200, 200))
    screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2,
                        SCREEN_HEIGHT // 2 - 60))
    screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2,
                        SCREEN_HEIGHT // 2 - 20))
    screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2,
                        SCREEN_HEIGHT // 2 + 20))
    pygame.display.flip()
    wait_for_close()
    return  # do not auto-quit; return to caller


def train(num_episodes, epsilon, alpha, gamma, q_table):
    global snake, snake_dir, snake_length, green_apples, red_apple, screen

    rewards_per_episode = []  # List to store rewards for each episode
    length_per_episode = []  # List to store length for each episode
    max_length = 0  # Track the global maximum length

    for episode in range(num_episodes):
        # Random snake each episode
        snake, snake_dir, snake_length = init_snake()
        green_apples = [(random.randint(0, GRID_SIZE - 1),
                         random.randint(0, GRID_SIZE - 1)) for _ in range(2)]
        red_apple = (random.randint(0, GRID_SIZE - 1),
                     random.randint(0, GRID_SIZE - 1))

        # Decay epsilon but keep it above 0.01
        epsilon = max(0.01, epsilon * 0.99995)

        # Track cumulative reward for this episode
        cumulative_reward = 0

        render = (episode + 1) % 10000 == 0  # Render every 1000 episodes

        if episode % 1000 == 0:  # Prune every 1000 episodes
            q_table = prune_q_table(q_table)

        if render:
            # Initialize the screen for rendering
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(f"Training - Episode {episode + 1}")

        while True:
            if render:
                screen.fill(BACKGROUND_COLOR)
                draw_grid()
                draw_snake()
                draw_apples()
                draw_right_section()
                pygame.display.flip()

            state = get_state(snake, green_apples, red_apple)
            action = choose_action(state, epsilon, snake_dir, q_table)
            snake_dir = action_to_direction(action, snake_dir)
            move_snake()
            reward = calculate_reward(snake, green_apples,
                                      red_apple, GRID_SIZE)
            cumulative_reward += reward  # Add reward to cumulative reward
            next_state = get_state(snake, green_apples, red_apple)
            update_q_value(state, action, reward, next_state,
                           alpha, gamma, q_table)

            if check_collisions():
                break  # End the episode if the snake collides

            if render:
                clock.tick(30)  # Limit the frame rate to 30 FPS for rendering

        # Store the cumulative reward and snake length for this episode
        rewards_per_episode.append(cumulative_reward)
        length_per_episode.append(snake_length)

        # Update the global max length if needed
        if snake_length > max_length:
            max_length = snake_length

        # Print progress and average reward every 100 episodes
        if (episode + 1) % 1000 == 0:
            avg_reward = sum(rewards_per_episode[-1000:]) / 1000
            avg_length = sum(length_per_episode[-1000:]) / 1000
            print(f"Episode {episode + 1}/{num_episodes} completed.\
                  Average reward (last 1000 episodes): {avg_reward:.2f}.\
                    Avg Length: {avg_length:.2f}. Max Length: {max_length}")

        if render:
            # Close the rendering window after the episode
            pygame.display.quit()
            pygame.display.init()

    print("Training completed!")
    plot_training_statistics(length_per_episode, max_length)


def plot_training_statistics(length_per_episode, max_length):
    # Calculate moving average of snake length over 1000 episodes
    moving_avg_length = [
        sum(length_per_episode[max(0, i-999):i+1]) / min(1000, i+1)
        for i in range(len(length_per_episode))
    ]

    # Track the maximum length over time
    max_lengths_over_time = []
    current_max = 0
    for length in length_per_episode:
        current_max = max(current_max, length)
        max_lengths_over_time.append(current_max)

    # Plot max length over time
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(max_lengths_over_time)), max_lengths_over_time,
             label="Max Length Over Time", color="blue", linewidth=2)

    # Plot moving average of snake length
    plt.plot(range(len(moving_avg_length)), moving_avg_length,
             label="Moving Avg (1000 episodes)", color="orange", linewidth=2)

    # Add grid, labels, and legend
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xlabel("Episode")
    plt.ylabel("Snake Length")
    plt.title("Snake Length Statistics During Training")
    plt.legend()
    plt.tight_layout()

    # Save the graph as an image to the folder training_stats
    folder = "training_statistics"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, "training_statistics.png")
    if os.path.exists(filename):
        base, ext = os.path.splitext("training_statistics.png")
        counter = 1
        while os.path.exists(os.path.join(folder, f"{base}_{counter}{ext}")):
            counter += 1
        filename = os.path.join(folder, f"{base}_{counter}{ext}")

    plt.savefig(filename)
    plt.show()
