#Silent auction Project 72
import os

auction_logo = '''
                         ___________
                         \         /
                          )_______(
                          |"""""""|_.-._,.---------.,_.-._
                          |       | | |               | | ''-.
                          |       |_| |_             _| |_..-'
                          |_______| '-' `'---------'` '-'
                          )"""""""(
                         /_________\\
                         `'-------'`
                       .-------------.
                      /_______________\\
'''

print(auction_logo,"\n Vítejete v programu pro tichou drazbu.")

bidders = {}
while True:
    name = input("Zadejte sve jmeno.\n")
    bid = int(input("Zadejte castku v dolarech.\n"))
    bidders[name] = bid
    dalsi = input("Jsou dalis zajemci? ano/ne\n").lower()
    if dalsi == "ne":
        os.system('cls||clear')
        break
    
highest_bid = 0
winner = ""
print(bidders)
for i in bidders:
    if bidders[i] > highest_bid:
        highest_bid = bidders[i]
        winner = i
print(f"Vitez je {winner} s castkou {bidders[i]}.")

    
    
    
    

  


#os.system('cls||clear')