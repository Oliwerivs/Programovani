while True:

    pizza_size = input("Velikost pizzy(s,m,l):\n")
    bill = 0
    if pizza_size == "s":
        bill = 100
    elif pizza_size == "m":
        bill = 150
    elif pizza_size == "l":
        bill = 200

    feferonky = input("Chceš feferonky? a/n\n")
    if feferonky == "a" and pizza_size == "s":
        bill += 20
    elif feferonky == "a":
        bill += 30

    syr = input("Chces sejra? a/n\n")
    if syr == "a":
        bill += 15

    print(f"Celekm zaplatis {bill}")
    jeste = input("Jeste jednu? a/n\n")
    if jeste == "n":
        break