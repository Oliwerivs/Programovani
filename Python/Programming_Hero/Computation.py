Mass1 = float(input("Weight of first object?  "))
Mass2 = float(input("Weight of second object?  "))
distance = float(input("Distance between objects: "))
G_Constant = 6.673*10**-11

GForce = (G_Constant*Mass1*Mass2)/distance**2
print(f"Gravitational pull is: {round(GForce,6)} N")
