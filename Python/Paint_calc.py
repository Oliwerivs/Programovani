import math
#1 plechovka 5m2
vyska = int(input("Vyska zdi:\n"))
sirka = int(input("Sirka zdi:\n"))
pokryti = 5

def kolik_barvy(vyska,sirka,pokryti):
    plocha = vyska * sirka
    plechovky = math.ceil(plocha /pokryti)
    print(f"Budete potrebovat {plechovky} plechovek barvy.")
    
kolik_barvy(vyska,sirka,pokryti)


#Pokusny koment