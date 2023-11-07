import math
import time

# Primes 
n = int(input("Zadej cele cislo:\n"))
start_time = time.time()
primes_list = []

def count_primes(number):
    result = "Je to Prvocislo"
    for i in range (2, number):
        if number % i == 0:
            result = "Neni to prvocislo"
    print(result)

count_primes(n)


    
stop_time = time.time()

elapsed_time = stop_time - start_time
print(f"Elapsed time {elapsed_time} seconds.")
100010717