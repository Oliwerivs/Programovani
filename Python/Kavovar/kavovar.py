from source_data import MENU
from source_data import resources

def enough_resources(coffee):
    ingredients_count = []
    resources_count = []
    for i in MENU[coffee]["ingredients"]:
        ingredients_count.append(MENU[coffee]["ingredients"][i])
    for i in resources:
        resources_count.append(resources[i])
    if resources_count >= ingredients_count:
        return True
     
def update_resources(coffee):
    resources["water"] = resources["water"] - MENU[coffee]["ingredients"]["water"]
    resources["milk"] = resources["milk"] - MENU[coffee]["ingredients"]["milk"]
    resources["coffee"] = resources["coffee"] - MENU[coffee]["ingredients"]["coffee"]

def cash_collection(coffee):
    coin_values = [1, 2, 5, 10, 20, 50]
    cash = 0
    total = 0
    price = MENU[coffee]['cost']
    cash_return = 0

    print(f"Cena napoje je {price} Kc.\n")
    print("Prosim, vlozte mince 1, 2, 5, 10, 20, 50\n")

    for i in range(len(coin_values)):
        coin = int(input(f"Kolik {coin_values[i]} Kc chcete vlozit?: "))
        cash = coin * coin_values[i]
        total += cash
    cash_return = total - price

    print(f"Celkem jste vlozili {total} Kc.\nVas napoj se pripravuje.")
    print(f"Zde jsou penize zpet: {cash_return} Kc.")

while True:
    #Vyber druhu kavy.    
    request = input("Dobry den, jakou kavu byste si dal? espresso/latte/cappuccino\n").lower()

    if request == "report":
        resources_left = resources
        for i in resources:
            print(f"{i} : {resources_left[i]}")
        
    if request != "report":
        if enough_resources(request) != True:
                print("Bohuzel nemam z ceho varit.")
                break
        else:
            update_resources(request)
            print("Vseho dost")
            cash_collection(request)
