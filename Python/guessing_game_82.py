#Guessing game

import random
import os

print("Vitej ve hre. Poraz pocitac. \n Myslim si cislo od 1 do 100")

def guessing_game():
    num = random.randint(1,100)
    #lives = 0
    diff = input("Vyber obtiznost. Napsi 'easy' nebo 'hard:' \n").lower()
    if diff == "easy":
        lives = 10
    else:
        lives = 5

    

    while lives > 0:
        another_game = ""
        print(f"Vas pocet zivotu je {lives}")
        guess = int(input("Tipni si cislo: \n"))
        if guess > num:
            print("Moc velke")        
            lives -= 1
        elif guess < num:
            print("Moc male")        
            lives -= 1
        else:
            print("Dobre ty")
            another_game = input("Chces hrat znova? ano/ne \n").lower()
            #break
        if lives == 0:
            print("Bohuzel")
            another_game = input("Chces hrat znova? ano/ne \n").lower()
            break
        
        if another_game == "ano":
            os.system("cls")   
            guessing_game()
        
        #os.system("clear")
    
guessing_game()  
