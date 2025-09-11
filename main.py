#!/usr/bin/env python3

import argparse
import pickle
from snake_game import train, play, play_multiple_games
from collections import OrderedDict

def load_q_table(filename):
    try:
        with open(filename, "rb") as f:
            q_table = pickle.load(f)
        print(f"Q-table loaded from {filename}. Number of entries: {len(q_table)}")
        # Convert to OrderedDict to maintain insertion order
        return OrderedDict(q_table)
    except FileNotFoundError:
        print(f"No Q-table found at {filename}. Starting with an empty Q-table.")
        return OrderedDict()

def save_q_table(q_table, filename):
    with open(filename, "wb") as f:
        pickle.dump(q_table, f)
    print(f"Q-table saved to {filename}.")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Learn2Slither: Snake AI with Q-Learning")
    parser.add_argument("-mode", choices=["train", "play"], required=True, help="Mode to run: 'train' or 'play'")
    parser.add_argument("-sessions", type=int, default=1000, help="Number of training episodes (default: 10)")
    parser.add_argument("-load", type=str, default="q_table.pkl", help="Path to the Q-table file to load (default: q_table.pkl)")
    parser.add_argument("-save", type=str, default="q_table.pkl", help="Path to save the Q-table after training (default: q_table.pkl)")
    parser.add_argument("-verbose", action="store_true", help="Enable verbose output in play mode")

    args = parser.parse_args()

    # Load the Q-table from file passed as argument (or start with an empty one)
    q_table = load_q_table(args.load)

    print(f"Number of entries in Q-table: {len(q_table)}")
    print("Sample entries:", list(q_table.items())[-5:])

    if args.mode == "train":
        print(f"Training the AI for {args.sessions} episodes...")
        epsilon = 0.01  # Initial exploration rate for training
        alpha = 0.1    # Learning rate
        gamma = 0.9    # Discount factor

        train(args.sessions, epsilon, alpha, gamma, q_table)
        save_q_table(q_table, args.save)
    elif args.mode == "play":
        print("Starting the game...")
        play(q_table, verbose=args.verbose)
        # play_multiple_games(q_table, verbose=args.verbose, num_games=100)

if __name__ == "__main__":
    main()