import math

a = float(input("Input side A : "))
b = float(input("Input side B : "))
c = float(input("Input side C : "))

#Calculate semi-perimeter
s = (a+b+c)/2

#Calculate Area
area = math.sqrt(s*(s-a)*(s-b)*(s-c))

print("Triangle area is: ", round(area,2))