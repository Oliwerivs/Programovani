# Coun vowels script
vowels = "aeiou"

def count_vowels(t):
    count = 0
    t_lowered = ""
    t_lowered = t.lower()
    for char in t_lowered:
        if char in vowels:
            count += 1
    return count
    
text = input("Zadejte text: ")

print(f"V textu je {count_vowels(text)} samohlasek")