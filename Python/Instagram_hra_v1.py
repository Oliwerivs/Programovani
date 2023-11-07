from instagram_data import data
import random

print("===================Hadaci hra.===================")

def pick_items(x):
        index_pick = random.randint(0,len(x)-1)
        items = data[index_pick]
        return items  

def print_outs(acc1, acc2):
    print(f"A: {acc1['name']}, {acc1['description']} z {acc1['country']}")
    print(f"B: {acc2['name']}, {acc2['description']} z {acc2['country']}")



def game():
    same_accounts = True
    while same_accounts == True:
        compare_a = pick_items(data)
        compare_b = pick_items(data)
        if compare_b != compare_a:
            same_accounts = False
        
    right_answer =""
    score = 0
    lets_continue = True
    while lets_continue:
        same_accounts = True
        while same_accounts == True:
            compare_b = pick_items(data)
            if compare_b != compare_a:
                same_accounts = False

        print_outs(compare_a, compare_b)
        user = input("Kdo ma vice sledujicich na Instagramu? A/B\n").lower()

        if compare_a["follower_count"] > compare_b["follower_count"]:
            right_answer = "a"
        else:
            right_answer = "b"
            compare_a = compare_b

        if user == right_answer:
            score += 1
            print(f"Uhadli jste, Vase skore je {score}")
            compare_b = pick_items(data)
                       
        else:
            print(f"Spatne. Vase konecne skore je {score}")
            lets_continue = False
game()





