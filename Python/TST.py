def format_phone_number(number):
    if not number:  
        return ""  # Base case: return an empty string if there's nothing left to process
    
    if number[0].isdigit():  
        return number[0] + format_phone_number(number[1:])  # Keep digits and process the rest recursively
    else:
        return format_phone_number(number[1:])  # Skip non-digit characters and continue recursively

# Testing the result
print(format_phone_number("(123) 456-7890"))
print(format_phone_number("  +1-800-555-0199  "))
print(format_phone_number("987.654.3210"))