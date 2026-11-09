#Leap year checker
def year(x):
    if ((x % 4 == 0 and x % 100 != 0) or (x % 400 == 0)):
        return "is leap."
    else:
        return "isn't leap."
year_in = int(input("Zadejte rok: "))

print(f"Provided year {year(year_in)}")