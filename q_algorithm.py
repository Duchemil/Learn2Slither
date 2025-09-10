import random
from collections import Counter

def choose_action(state, epsilon, current_dir, q_table):
    directions = {
        0: (0, -1),  # Up
        1: (0, 1),   # Down
        2: (-1, 0),  # Left
        3: (1, 0)    # Right
    }

    valid_actions = [
        action for action, direction in directions.items()
        if not (direction[0] == -current_dir[0] and direction[1] == -current_dir[1])
    ]

    if random.uniform(0, 1) < epsilon:
        return random.choice(valid_actions)
    else:
        return max(valid_actions, key=lambda a: q_table.get((state, a), 0), default=random.choice(valid_actions))


def update_q_value(state, action, reward, next_state, alpha, gamma, q_table):
    max_next_q = max([q_table.get((next_state, a), 0) for a in range(4)], default=0)
    current_q = q_table.get((state, action), 0)
    new_q = current_q + alpha * (reward + gamma * max_next_q - current_q)
    q_table[(state, action)] = new_q
    # print(f"Updated Q-value for state-action ({state}, {action}): {new_q}")

 
def get_state(snake, green_apples, red_apple, GRID_SIZE):
    head_x, head_y = snake[0]

    # Normalize distances to the grid size
    def normalize(value):
        return round(value / GRID_SIZE, 2)

    # Calculate distances to objects in a given direction
    def calculate_distance(dx, dy):
        wall_distance = 0
        green_apple_distance = float('inf')
        red_apple_distance = float('inf')
        body_distance = float('inf')

        x, y = head_x + dx, head_y + dy
        while 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            wall_distance += 1
            if (x, y) in green_apples and green_apple_distance == float('inf'):
                green_apple_distance = wall_distance
            if (x, y) == red_apple and red_apple_distance == float('inf'):
                red_apple_distance = wall_distance
            if (x, y) in snake and body_distance == float('inf'):
                body_distance = wall_distance
            x += dx
            y += dy

        return (
            normalize(wall_distance),
            normalize(green_apple_distance) if green_apple_distance != float('inf') else 1.0,
            normalize(red_apple_distance) if red_apple_distance != float('inf') else 1.0,
            normalize(body_distance) if body_distance != float('inf') else 1.0
        )

    # Get information in all four directions
    up_info = calculate_distance(0, -1)
    down_info = calculate_distance(0, 1)
    left_info = calculate_distance(-1, 0)
    right_info = calculate_distance(1, 0)

    # Return the state as a tuple
    return (*up_info, *down_info, *left_info, *right_info)


def action_to_direction(action, current_dir):
    # Define the possible directions
    directions = {
        0: (0, -1),  # Up
        1: (0, 1),   # Down
        2: (-1, 0),  # Left
        3: (1, 0)    # Right
    }

    return directions[action]


def calculate_reward(snake, green_apples, red_apple, GRID_SIZE):
    head = snake[0]

    # Reward for eating green apple
    if head in green_apples:
        return 10
    
    # Penalty for eating red apple
    if head == red_apple:
        return -10

    # Penalty for hitting wall or itself
    if head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE or head in snake[1:]:
        return -100

    # If the snake has only one segment, skip distance-based rewards/penalties
    if len(snake) < 2:
        return -1  # Small penalty for each move to encourage shorter paths

    prev_head = snake[1]  # The previous head position

    # Reward for moving closer to a green apple
    closest_green_apple = min(green_apples, key=lambda apple: abs(apple[0] - head[0]) + abs(apple[1] - head[1]))
    prev_distance_to_green = abs(closest_green_apple[0] - prev_head[0]) + abs(closest_green_apple[1] - prev_head[1])
    new_distance_to_green = abs(closest_green_apple[0] - head[0]) + abs(closest_green_apple[1] - head[1])
    if new_distance_to_green < prev_distance_to_green:
        return 1  # Small reward for moving closer

    # Penalty for moving closer to a red apple
    # prev_distance_to_red = abs(red_apple[0] - prev_head[0]) + abs(red_apple[1] - prev_head[1])
    # new_distance_to_red = abs(red_apple[0] - head[0]) + abs(red_apple[1] - head[1])
    # if new_distance_to_red < prev_distance_to_red:
    #     return -1  # Small penalty for moving closer to a red apple

    # Small penalty for each move to encourage shorter paths
    return -1