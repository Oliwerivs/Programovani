year = int(input("Zadete rok: \n"))
if year % 4 == 0 and year % 100 == 0 and year % 400 == 0:
    print("Rok je přestupný.")
elif year % 4 == 0 and year % 100 != 0:
    print("Rok je přestupný.")
else:
    print("Rok není přestupný.")