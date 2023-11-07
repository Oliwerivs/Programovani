#Generator hesel
import time
import random
#for i in range (0,100):


letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
special_char = ['%', '#', '$', '!', '&', '(', ')', '*', '+', '?']

letters_len = int(input("Kolik znaku?\n"))
numbers_len = int(input("Kolik cisel?\n"))
special_char_len = int(input("Kolik specialnich znaku?\n"))
password = []
start_time = time.time()
for i in range(0, letters_len):
    password.append(letters[random.randint(0, len(letters)-1)])
        
for i in range(0, numbers_len):
    password.append(numbers[random.randint(0, len(numbers)-1)])
        
for i in range(0, special_char_len):
    password.append(special_char[random.randint(0, len(special_char)-1)])
  
    
    #Prehazeni. Normalne existuje random.shuffle()
random.shuffle(password)
    #Prevod listu na str. Noralne existuje "".join()
password = "".join(password)
        
print(password)
    
    

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Elapsed time:{elapsed_time}")

   