while True:
    x = 10

    def my_function():
        global x
        x += 5
        print(x)

    my_function()
    print(x)