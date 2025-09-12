#!/usr/bin/env python3

import argparse
import pickle
from snake_game import train, play, play_multiple_games
from collections import OrderedDict
from gui import run_gui


def load_q_table(filename):
    try:
        with open(filename, "rb") as f:
            q_table = pickle.load(f)
        # Convert to OrderedDict to maintain insertion order
        return OrderedDict(q_table)
    except FileNotFoundError:
        return OrderedDict()


def save_q_table(q_table, filename):
    with open(filename, "wb") as f:
        pickle.dump(q_table, f)
    # print(f"Q-table saved to {filename}.")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Learn2Slither:\
        Snake AI with Q-Learning")
    parser.add_argument("-mode", choices=["train", "play"],
                        required=True, help="Mode to run: 'train' or 'play'")
    parser.add_argument("-sessions", type=int, default=1000,
                        help="Number of training episodes (default: 10)")
    parser.add_argument("-load", type=str, default="q_table.pkl",
                        help="Path to the Q-table file to load (default: \
                            q_table.pkl)")
    parser.add_argument("-save", type=str, default="q_table.pkl",
                        help="Path to save the Q-table after training \
                            (default: q_table.pkl)")
    parser.add_argument("-verbose", action="store_true",
                        help="Enable verbose output in play mode")
    parser.add_argument("-max", type=int, default=0,
                        help="Show max score game in play mode (default: 100)")
    parser.add_argument("-g", "-gui", "--gui", dest="gui",
                        action="store_true", help="Launch GUI lobby")

    args = parser.parse_args()

    q_table = load_q_table(args.load)

    if args.mode == "train":
        print(f"Training the AI for {args.sessions} episodes...")
        epsilon = 0.00  # Initial exploration rate for training
        alpha = 0.1    # Learning rate
        gamma = 0.9    # Discount factor

        train(args.sessions, epsilon, alpha, gamma, q_table)
        save_q_table(q_table, args.save)
    elif args.mode == "play":
        if args.gui:
            run_gui(q_table)
            return
        print("Starting the game...")
        if args.max:
            print("Showing max score games, it may takes a \
                  few seconds to find the max game...")
            play_multiple_games(q_table, verbose=args.verbose,
                                num_games=args.max)
        else:
            play(q_table, verbose=args.verbose)


if __name__ == "__main__":
    main()
