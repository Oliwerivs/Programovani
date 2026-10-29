import random  # Importing the random module
import os  # Importing os for clearing the console

# List of words used for the Hangman game
WORDS = [
    "python",
    "hangman",
    "developer",
    "console",
    "project",
    "function",
    "integer",
    "variable"
]

# Symbol used to represent hidden letters
HIDDEN_SYMBOL = "_"

# Maximum number of incorrect attempts allowed
MAX_ATTEMPTS = 6


def choose_word_random():
    # Returning a random word from the list
    return random.choice(WORDS)


def is_word_guessed(secret_word, guessed_letters):
    # Checking whether all letters of the word are guessed
    return all(letter in guessed_letters for letter in secret_word)


def get_guessed_word(secret_word, guessed_letters):
    # Creating a masked version of the secret word
    return "".join(
        [letter if letter in guessed_letters else HIDDEN_SYMBOL for letter in secret_word]
    )


def get_available_letters(guessed_letters):
    # Returning letters that have not been guessed yet
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return "".join([char for char in alphabet if char not in guessed_letters])


def hints_match(pattern, candidate):
    # Checking if the pattern and candidate match
    if len(pattern) != len(candidate):
        return False

    for i in range(len(pattern)):
        if pattern[i] != HIDDEN_SYMBOL and pattern[i] != candidate[i]:
            return False

    return True


def show_possible_matches(pattern):
    # Returning all words that match the given pattern
    matches = []
    for word in WORDS:
        if hints_match(pattern, word):
            matches.append(word)
    return matches


def clear_screen():
    # Clearing the console screen
    os.system("cls" if os.name == "nt" else "clear")


def hangman(secret_word):
    # Running the main Hangman game loop with ASCII art
    stages = [
        """
           -----
           |   |
               |
               |
               |
               |
        """,
        """
           -----
           |   |
           O   |
               |
               |
               |
        """,
        """
           -----
           |   |
           O   |
           |   |
               |
               |
        """,
        """
           -----
           |   |
           O   |
          /|   |
               |
               |
        """,
        """
           -----
           |   |
           O   |
          /|\  |
               |
               |
        """,
        """
           -----
           |   |
           O   |
          /|\  |
          /    |
               |
        """,
        """
           -----
           |   |
           O   |
          /|\  |
          / \  |
               |
        """
    ]

    guessed_letters = []
    mistakes = 0

    while not is_word_guessed(secret_word, guessed_letters) and mistakes < MAX_ATTEMPTS:
        clear_screen()
        print(stages[mistakes])
        print("Word:", get_guessed_word(secret_word, guessed_letters))
        print("Available letters:", get_available_letters(guessed_letters))

        guess = input("Guess a letter: ").lower()
        if guess == "?":
            pattern = get_guessed_word(secret_word, guessed_letters)
            print("Possible matches:", show_possible_matches(pattern))
            input("Press Enter to continue...")
        elif guess in secret_word and guess not in guessed_letters:
            guessed_letters.append(guess)
        elif guess not in secret_word:
            mistakes += 1
        
        

    #clear_screen()
    print(stages[mistakes])

    if is_word_guessed(secret_word, guessed_letters):
        print("You won!")
    else:
        print("You lost. The word was:", secret_word)


def main():
    secret_word = choose_word_random()
    hangman(secret_word)


if __name__ == "__main__":
    main()