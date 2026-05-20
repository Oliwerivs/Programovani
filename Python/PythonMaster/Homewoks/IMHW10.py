#CHeck palindrome
text = input("Zadejte text: ")
text = text.lower()
upraveny = text.split()
upraveny = upraveny.join()
print(upraveny)

reverse = text[::-1]
if text == reverse:
    print("Text je palindrom.")
else:
    print("Text není palindrom.")
