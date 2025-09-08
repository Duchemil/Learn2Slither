import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 20
CELL_SIZE = 40
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
FPS = 50

# Colors
BACKGROUND_COLOR = (30, 30, 30)  # Dark gray
GRID_COLOR = (50, 50, 50)  # Slightly lighter gray
SNAKE_COLOR = (0, 200, 0)  # Bright green
SNAKE_EYE_COLOR = (255, 255, 255)  # White for eyes
APPLE_GREEN_COLOR = (0, 255, 0)  # Bright green
APPLE_RED_COLOR = (255, 0, 0)  # Bright red

# Initialize screen
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Snake Game")

# Clock
clock = pygame.time.Clock()

# Snake initialization
snake = [(5, 5)]
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
    for apple in green_apples:
        rect = pygame.Rect(apple[0] * CELL_SIZE, apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, APPLE_GREEN_COLOR, rect)
    rect = pygame.Rect(red_apple[0] * CELL_SIZE, red_apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, APPLE_RED_COLOR, rect)


# Function to move the snake
def move_snake():
    global snake, snake_length
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    snake = [new_head] + snake[:snake_length - 1]


# Function to check collisions
def check_collisions():
    global snake_length, green_apples, red_apple

    # Check wall collision
    head_x, head_y = snake[0]
    if head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE:
        return True

    # # Check self collision
    # if snake[0] in snake[1:]:
    #     return True

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


# Function for AI to decide direction
def ai_decide_direction():
    global snake, green_apples, snake_dir

    head_x, head_y = snake[0]
    target_x, target_y = green_apples[0]  # Target the first green apple

    # Calculate the direction to the target
    if target_x > head_x and snake_dir != (-1, 0):  # Move right
        return (1, 0)
    elif target_x < head_x and snake_dir != (1, 0):  # Move left
        return (-1, 0)
    elif target_y > head_y and snake_dir != (0, -1):  # Move down
        return (0, 1)
    elif target_y < head_y and snake_dir != (0, 1):  # Move up
        return (0, -1)

    # Default to the current direction if no better option is found
    return snake_dir


# Main game loop
def main():
    global snake_dir
    running = True

    # Timer for controlling snake movement
    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, 1000 // FPS)

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_grid()
        draw_snake()
        draw_apples()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == MOVE_EVENT:
                # Let the AI decide the next move
                snake_dir = ai_decide_direction()
                move_snake()
                if check_collisions():
                    print("Game Over!")
                    running = False

        clock.tick(60)  # Run the game loop at 60 FPS for smooth rendering

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()