import random
from guessing_stages import stages
#Hangman game

#Generovani nahodneho slova
character = ["harry","dumbledore","voldemort","snape","sirius","hermione"] 
character_picked = character[random.randint(0,len(character)-1)]

#Generovani podtrzitek
hidden_word =[]
word_len = len(character_picked)

#Pocet zivotu
lives = 6
print(stages[lives])

for i in character_picked:
    hidden_word.append("*")
#hidden_word = "".join(hidden_word)
#print(hidden_word)


while "*" in hidden_word:   
    guess = input("Hadej pismeno hledaneho jmena : \n").lower()
     
    for i in range (0, len(character_picked)):
        if guess == character_picked[i]:
            hidden_word[i] = guess
    # Lives check
    if guess not in hidden_word:
        print(stages[lives])
        lives -= 1 
    
    hidden_word_part = "".join(hidden_word)
 
    print(hidden_word_part)
    print(f"Zbyva {lives} zivotu.")
    
    if lives == 0:
        print("Smolík")
        print(stages[0])
        break
    #Check win
    if "*" not in hidden_word:
        print("Vyhrali jste!!!")
        break


