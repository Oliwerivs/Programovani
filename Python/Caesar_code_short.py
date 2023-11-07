#Cezarova sifra
import time
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
punctuation = ['.',',',' ']

def cipher(message, shift, encrypt):
    end_text = ""
    for i in message:
            if i in punctuation:
                end_text += " "
            else:
                index = alphabet.index(i)
            
            if encrypt == "encode":
                if index + shift >25:
                    index = (index + shift) - 26
                else:
                    index = index + shift
            elif encrypt == "decode":
               
                    index = index - shift
            if i not in punctuation:
                end_text += alphabet[index]
            
    print(end_text)    
       
while True:
    encrypt = input("Chcete spravu zasifrovat 'encode' nedo rozsifrovat 'decode' ?\n").lower()
    if encrypt == "encode" or encrypt == "decode":
        message = input("Zadejte zpravu pro sifrovani.\n").lower()
        shift = int(input("Zadej posun:\n"))
    else:
        print("Co to sakra meles, ty vorechu?!")
    start_time = time.time()
 
    cipher(message,shift, encrypt)
    stop_time = time.time()
        
    znova = input("Chces pokracovat? ano/ne\n").lower()
    if znova != "ano":
        break
    
elapsed_time = stop_time - start_time
print(f"Elapsed time {elapsed_time} seconds.")
