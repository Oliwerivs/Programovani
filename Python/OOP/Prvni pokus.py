from typing import Any


class Robot:
    
    # constructor
    def __init__(self, baterie, delka_rukou):
        self.bat = baterie
        self.del_ruk = delka_rukou
        self.ukony_do_kontroly = 365
        
    def krok_vpred(self):
        print("Robot udelal krok vpred")
        self.ukony_do_kontroly -=1
        print(f"Ukonu do kontroly zbyva {self.ukony_do_kontroly}")
        
    def krok_vzad(self):
        print("Robot udelal krok vzad")
        self.ukony_do_kontroly -=1
        print(f"Ukonu do kontroly zbyva {self.ukony_do_kontroly}")

    
# Tvorime objekty podle Class
robot_1 = Robot(24,0.6)
robot_2 = Robot(48, 0.5)
robot_3 = Robot(12, 0.4)
robot_4 = Robot(18, 0.8)

print(f"Vydrz baterky {robot_4.bat}")
print(f"Delka rukou {robot_4.del_ruk}")
print(f"Do opravy {robot_4.ukony_do_kontroly}")
robot_4.krok_vpred()
robot_4.krok_vzad()
robot_4.krok_vpred()
robot_4.krok_vzad()
print(f"Do opravy {robot_4.ukony_do_kontroly}")
