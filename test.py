import pickle

with open("q_table.pkl", "rb") as f:
    q_table = pickle.load(f)
    print(f"Number of entries in Q-table: {len(q_table)}")
    print("Sample entries:", list(q_table.items())[-5:])