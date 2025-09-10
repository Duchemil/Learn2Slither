from q_algorithm import choose_action, get_state, update_q_value, action_to_direction, calculate_reward
import pygame
import random
import sys
import pickle
import matplotlib.pyplot as plt
import os

# Initialize pygame
pygame.init()


# Track the last 5 moves made by the AI
last_moves = []


# Constants
GRID_SIZE = 10
CELL_SIZE = 40
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
SCREEN_WIDTH = SCREEN_SIZE + 200  # Add 200 pixels for the right section
SCREEN_HEIGHT = SCREEN_SIZE

FPS = 5

# Colors
BACKGROUND_COLOR = (30, 30, 30)  # Dark gray
GRID_COLOR = (50, 50, 50)  # Slightly lighter gray
SNAKE_COLOR = (0, 200, 0)  # Bright green
SNAKE_EYE_COLOR = (255, 255, 255)  # White for eyes
APPLE_GREEN_COLOR = (170, 255, 170)  # Bright green
APPLE_RED_COLOR = (255, 0, 0)  # Bright red


# Clock
clock = pygame.time.Clock()

# Snake initialization
snake = [(GRID_SIZE // 2, GRID_SIZE // 2 + i) for i in range(3)]
snake_dir = (0, -1)  # Start moving up
snake_length = 3

# Apple initialization
green_apples = [(random.randint(0, GRID_SIZE - 1),
                 random.randint(0, GRID_SIZE - 1)) for _ in range(2)]
red_apple = (random.randint(0, GRID_SIZE - 1),
             random.randint(0, GRID_SIZE - 1))


# Function to draw the grid
def draw_grid():
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        for y in range(0, SCREEN_SIZE, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)


# Function to draw the snake
def draw_snake():
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, SNAKE_COLOR, rect)
        if i == 0:  # Draw googly eyes on the head
            eye_radius = CELL_SIZE // 8
            eye_offset = CELL_SIZE // 4
            eye1 = (segment[0] * CELL_SIZE + eye_offset, segment[1] * CELL_SIZE + eye_offset)
            eye2 = (segment[0] * CELL_SIZE + CELL_SIZE - eye_offset, segment[1] * CELL_SIZE + eye_offset)
            pygame.draw.circle(screen, SNAKE_EYE_COLOR, eye1, eye_radius)
            pygame.draw.circle(screen, SNAKE_EYE_COLOR, eye2, eye_radius)


# Function to draw apples
def draw_apples():
    global red_apple  # Declare red_apple as global to avoid scope issues

    def get_empty_spaces():
        occupied = set(snake + green_apples + [red_apple])
        return [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if (x, y) not in occupied]

    empty_spaces = get_empty_spaces()

    # Redraw green apples if they overlap with the snake
    for i in range(len(green_apples)):
        if green_apples[i] in snake:
            if empty_spaces:
                green_apples[i] = random.choice(empty_spaces)
                empty_spaces.remove(green_apples[i])

    # Redraw red apple if it overlaps with the snake
    if red_apple in snake:
        if empty_spaces:
            new_red_apple = random.choice(empty_spaces)
            empty_spaces.remove(new_red_apple)
            red_apple = new_red_apple

    # Draw green apples
    for apple in green_apples:
        rect = pygame.Rect(apple[0] * CELL_SIZE, apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, APPLE_GREEN_COLOR, rect)

    # Draw red apple
    rect = pygame.Rect(red_apple[0] * CELL_SIZE, red_apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, APPLE_RED_COLOR, rect)


# Function to move the snake
def move_snake():
    global snake, snake_length
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    snake = [new_head] + snake[:snake_length - 1]
    # print(f"Snake moved to {new_head} in direction {snake_dir}")


# Function to check collisions
def check_collisions():
    global snake_length, green_apples, red_apple

    # Check wall collision
    head_x, head_y = snake[0]
    if head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE:
        return True

    # # # Check self collision
    if snake[0] in snake[1:]:
        return True

    # Check green apple collision
    for apple in green_apples:
        if snake[0] == apple:
            snake_length += 1
            green_apples.remove(apple)
            green_apples.append((random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)))

    # Check red apple collision
    if snake[0] == red_apple:
        snake_length -= 1
        if snake_length <= 0:
            return True
        red_apple = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

    return False


def draw_right_section():
    # Background for the right section
    right_section_rect = pygame.Rect(SCREEN_SIZE, 0, 200, SCREEN_HEIGHT)
    pygame.draw.rect(screen, (40, 40, 40), right_section_rect)  # Darker gray background

    # Font for text
    font = pygame.font.Font(None, 36)
    text_color = (255, 255, 255)  # White text

    # Display "Last Moves"
    moves_title = font.render("Last Moves:", True, text_color)
    screen.blit(moves_title, (SCREEN_SIZE + 10, 10))

    # Render each move
    for i, move in enumerate(last_moves):
        move_text = font.render(f"{i + 1}: {move}", True, text_color)
        screen.blit(move_text, (SCREEN_SIZE + 10, 50 + i * 30))

    # Display "Snake Length"
    length_text = font.render(f"Length: {snake_length}", True, text_color)
    screen.blit(length_text, (SCREEN_SIZE + 10, 200))

    # Draw a vertical line to separate the sections
    pygame.draw.line(screen, (255, 255, 255), (SCREEN_SIZE, 0), (SCREEN_SIZE, SCREEN_HEIGHT), 2)


def draw_last_moves():
    font = pygame.font.Font(None, 36)  # Use a default font with size 36
    text_color = (255, 255, 255)  # White text
    x, y = 10, 10  # Starting position for the text

    # Render each move
    for i, move in enumerate(last_moves):
        text_surface = font.render(f"Move {i + 1}: {move}", True, text_color)
        screen.blit(text_surface, (x, y + i * 30))  # Offset each line by 30 pixels


def save_q_table(filename="q_table.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(q_table, f)
    print(f"Q-table saved to {filename}.")


def load_q_table(filename="q_table.pkl"):
    global q_table
    try:
        with open(filename, "rb") as f:
            loaded_q_table = pickle.load(f)
        print(f"Q-table loaded from {filename}. Number of entries: {len(loaded_q_table)}")

        # Merge the loaded Q-table with the existing one
        q_table.update(loaded_q_table)

        print(f"Q-table updated. Total number of entries: {len(q_table)}")
        if len(q_table) > 0:
            print("Sample Q-table entries:")
            for key, value in list(q_table.items())[-5:]:  # Print the last 5 entries
                print(f"State-Action: {key}, Q-value: {value}")
    except FileNotFoundError:
        print(f"No Q-table found at {filename}. Starting with an empty Q-table.")


def play(q_table):
    global snake, snake_dir, snake_length, green_apples, red_apple, screen

    # Initialize the screen for playing
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game - Play Mode")

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_snake()
        draw_apples()
        draw_right_section()
        pygame.display.flip()

        # Get the current state
        state = get_state(snake, green_apples, red_apple, GRID_SIZE)

        # Choose the best action based on the Q-table (exploit only)
        action = choose_action(state, 0, snake_dir, q_table)  # epsilon=0 ensures no random moves
        snake_dir = action_to_direction(action, snake_dir)

        # Move the snake
        move_snake()

        # Check for collisions
        if check_collisions():
            print(f"Game Over!, Final Length: {snake_length}")
            running = False

        # Control the game speed
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


def train(num_episodes, epsilon, alpha, gamma, q_table):
    global snake, snake_dir, snake_length, green_apples, red_apple, screen

    rewards_per_episode = []  # List to store rewards for each episode
    length_per_episode = []  # List to store length for each episode
    max_length = 0  # Track the global maximum length

    for episode in range(num_episodes):
        # Reset the game state
        snake = [(GRID_SIZE // 2, GRID_SIZE // 2 + i) for i in range(3)]
        snake_dir = (0, -1)
        snake_length = 3
        green_apples = [(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)) for _ in range(2)]
        red_apple = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

        # if (episode + 1) % 50000 == 0:
        #     epsilon = 0.1
        #     print(f"Resetting epsilon to {epsilon} at episode {episode + 1}")
        epsilon = max(0.01, epsilon * 0.99995)  # Decay epsilon but keep it above 0.01

        # Track cumulative reward for this episode
        cumulative_reward = 0

        render = (episode + 1) % 10000 == 0  # Render every 1000 episodes

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

            state = get_state(snake, green_apples, red_apple, GRID_SIZE)
            action = choose_action(state, epsilon, snake_dir, q_table)
            snake_dir = action_to_direction(action, snake_dir)
            move_snake()
            reward = calculate_reward(snake, green_apples, red_apple, GRID_SIZE)
            cumulative_reward += reward  # Add reward to cumulative reward
            next_state = get_state(snake, green_apples, red_apple, GRID_SIZE)
            update_q_value(state, action, reward, next_state, alpha, gamma, q_table)

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
            print(f"Episode {episode + 1}/{num_episodes} completed. Average reward (last 1000 episodes): {avg_reward:.2f}. Avg Length: {avg_length:.2f}. Max Length: {max_length}")

        if render:
            # Close the rendering window after the episode
            pygame.display.quit()
            pygame.display.init()

    print("Training completed!")
    plot_training_statistics(length_per_episode, max_length)


def plot_training_statistics(length_per_episode, max_length):
    # Calculate moving average of snake length over 1000 episodes
    moving_avg_length = [
        sum(length_per_episode[i:i+1000]) / 1000
        for i in range(len(length_per_episode) - 999)
    ]

    # Track the maximum length over time
    max_lengths_over_time = []
    current_max = 0
    for length in length_per_episode:
        current_max = max(current_max, length)
        max_lengths_over_time.append(current_max)

    # Downsample the data to plot every 1000th episode for clarity
    episodes = range(0, len(max_lengths_over_time), 1000)
    downsampled_max_lengths = [max_lengths_over_time[i] for i in episodes]

    # Plot max length over time
    plt.figure(figsize=(12, 6))
    plt.plot(episodes, downsampled_max_lengths, label="Max Length Over Time", color="blue", linewidth=2)

    # Plot moving average of snake length
    plt.plot(range(999, len(length_per_episode)), moving_avg_length, label="Moving Avg (1000 episodes)", color="orange", linewidth=2)

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
