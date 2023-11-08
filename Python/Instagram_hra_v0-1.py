from instagram_data import data
import random

print("===================Hadaci hra.===================")

def pick_items():
    items = []
    for i in range (0,2):
        index_pick = random.randint(0,1)
        items.append(data[index_pick])
    if items[0] == items[1]:
        items = []
        pick_items()
    else:
        return items   

def comparison(x):
    picked_answer = 0
    if x == "a":
        picked_answer = compare_a["follower_count"]
        second_count = compare_b["follower_count"]
    elif x == "b":
        picked_answer = compare_b["follower_count"]
        second_count = compare_a["follower_count"]
    else:
        print("Chybne zadani, zkus to znova.")
          
    if picked_answer > second_count: 
        return True
    else:
        return False

items_list = pick_items()
compare_a = items_list[0]
compare_b = items_list[1]

print(f"A: {compare_a['name']}, {compare_a['description']} z {compare_a['country']} --------- {compare_a['follower_count']}")
print(f"B: {compare_b['name']}, {compare_b['description']} z {compare_b['country']} --------- {compare_b['follower_count']}")
user = input("Kdo ma vice sledujicich na Instagramu? A/B\n").lower()

result = comparison(user)
print(result)
    
    



