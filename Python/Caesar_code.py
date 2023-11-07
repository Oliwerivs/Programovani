#Cezarova sifra
import time
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
punctuation = ['.',',',' ']
encoded_message = []
decoded_message = []

def encode(message, shift):
        for i in message:
            if i in punctuation:
                encoded_message.append(" ")
            else:
                index = alphabet.index(i)
                if index + shift >25:
                    index = (index + shift) - 26
                else:
                    index = index + shift
            
                encoded_message.append(alphabet[index])
        encoded = "".join(encoded_message)
        print(encoded)
    
def decode(message, shift):
        for i in message:
            if i in punctuation:
                decoded_message.append(" ")
            else:
                index = alphabet.index(i)
                if index - shift <0:
                    index = (index - shift) + 26
                else:
                    index = index - shift
            
                decoded_message.append(alphabet[index])
        decoded = "".join(decoded_message)
        print(decoded)

while True:
    encrypt = input("Chcete spravu zasifrovat 'encode' nedo rozsifrovat 'decode' ?\n").lower()
    if encrypt == "encode" or encrypt == "decode":
        message = input("Zadejte zpravu pro sifrovani.\n").lower()
        shift = int(input("Zadej posun:\n"))
    else:
        print("Co to sakra meles, ty vorechu?!")
    start_time = time.time()
 
    if encrypt == "encode":
        encode(message,shift)
    elif encrypt == "decode":
        decode(message,shift)
    stop_time = time.time()
        
    znova = input("Chces pokracovat? ano/ne\n").lower()
    if znova != "ano":
        break
    
elapsed_time = stop_time - start_time
print(f"Elapsed time {elapsed_time} seconds.")

#Naprosto skvelu
