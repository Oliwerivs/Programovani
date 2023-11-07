import random
print ("Kdo zaplati darek pro mamku?\n")
names = input("Zadej jmena oddelene carkou.\n")
list_names = names.split(", ")
random_number = random.randint(0,len(list_names)-1)
print (f"Zaplati to {list_names[random_number]} :)")
print(len(list_names))