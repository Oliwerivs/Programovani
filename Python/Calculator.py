#Calc
import os

def sum (n1, n2):
  return n1 + n2

def subs (n1, n2):
  return n1 - n2

def mult (n1, n2):
  return n1 * n2

def div (n1, n2):
  return n1 / n2

operations = {
  "+": sum,
  "-": subs,
  "*": mult,
  "/": div
  }
def calculator():
  num1 = float(input("Jake je prvni cislo?\n"))

  znova = "ano"
  while znova == "ano":
    for i in operations:
      print(i)
    user_symb = input("Zvlote jednu z operaci vyse:\n")
    num2 = float(input("Jake je dalsi cislo?\n"))

    calc_func = operations[user_symb]
    result = calc_func(num1, num2)

    print(f"{num1} {user_symb} {num2} = {result}")
    znova = input("Napsi ano, pokud chces pokracovat. \nNapis ne, pokud chces kalkulacku spustit znova \n").lower()
    if znova == "ano":
      num1 = result
    else:
      os.system("clear")
      calculator()
      
calculator()