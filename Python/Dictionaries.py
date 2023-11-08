students_results = {
  "Harry": 85,
  "Ron": 71,
  "Hermione": 98,
  "Draco": 69
}

# Stupnice
# 91 až 100 = "Excelentní"
# 81 až 90 = "Vynikající"
# 71 až 80 = "Splněno"
# méně jak 71 = "Nesplněno"
slovni_hodnoceni = {}
for key in students_results:
    if students_results[key] >= 91:
        slovni_hodnoceni[key] = "Excelentní"
    elif students_results[key] >= 81:
        slovni_hodnoceni[key] = "Vynikající"
    elif students_results[key] >= 71:
        slovni_hodnoceni[key] = "Splněno"
    else:
        slovni_hodnoceni[key] = "Nesplněno"
print(slovni_hodnoceni)
    
        
    