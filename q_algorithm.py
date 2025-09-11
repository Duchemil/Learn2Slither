import random
from collections import Counter
from config import GRID_SIZE

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
        # Fetch Q-values for valid actions
        q_values = {a: q_table.get((state, a), 0) for a in valid_actions}
        print(f"Valid actions: {valid_actions}")
        print(f"Q-values for valid actions: {q_values}")
        return max(q_values, key=q_values.get, default=random.choice(valid_actions))


def update_q_value(state, action, reward, next_state, alpha, gamma, q_table):
    # Normalize the state and next state
    state = tuple(state)  # Ensure the state is hashable
    next_state = tuple(next_state)

    # Get the maximum Q-value for the next state
    max_next_q = max([q_table.get((next_state, a), 0) for a in range(4)], default=0)

    # Update the Q-value for the current state-action pair
    current_q = q_table.get((state, action), 0)
    new_q = current_q + alpha * (reward + gamma * max_next_q - current_q)
    q_table[(state, action)] = new_q

 
def normalize(value, grid_size):
    return round(value / grid_size, 2)

def get_state(snake, green_apples, red_apple):
    head_x, head_y = snake[0]

    def check_direction(dx, dy):
        distance = 0
        apple_nearby = False
        red_apple_nearby = False
        body_nearby = False

        x, y = head_x + dx, head_y + dy
        while True:
            distance += 1
            if x < 0 or y < 0 or x >= GRID_SIZE or y >= GRID_SIZE:
                break
            if (x, y) in green_apples:
                apple_nearby = True
            if (x, y) == red_apple:
                red_apple_nearby = True
            if (x, y) in snake:
                body_nearby = True
            x += dx
            y += dy

        return (
            normalize(distance, GRID_SIZE),
            apple_nearby,
            red_apple_nearby,
            body_nearby
        )

    up_info = check_direction(0, -1)
    down_info = check_direction(0, 1)
    left_info = check_direction(-1, 0)
    right_info = check_direction(1, 0)

    # Return the normalized state
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