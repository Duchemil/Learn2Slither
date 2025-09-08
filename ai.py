import random

q_table = {}

def choose_action(state, epsilon):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, 3)
    else:
        return max(range(4), key=lambda a: q_table.get((state, a), 0), default=random.randint(0, 3))

def update_q_value(state, action, reward, next_state, alpha, gamma):
    max_next_q = max([q_table.get((state, a), 0) for a in range(4)], default=0)
    current_q = q_table.get((state, action), 0)
    q_table[(state, action)] = current_q + alpha * (reward + gamma * max_next_q - current_q)