#Rock, paper, scisors
import random
while True:
    uzivatel = input("Zadej kamen, nuzky nebo papir.\n").lower()
    los_pocitac = random.randint(0,2)
    pocitac = ["kamen", "nuzky", "papir"]
    print(pocitac[los_pocitac])
    if uzivatel == "kamen" and pocitac == "nuzky" or uzivatel == "nuzky" and pocitac == "papir" or uzivatel == "papir" and pocitac == "kamen":
        print("Vyhral jsi.")
    elif uzivatel == pocitac:
        print("Remíza!")
    else:
        print("Pocitac vyhral:)")
    repeat = input("Znova? a/n\n").lower()
    if repeat == "n":
        break
