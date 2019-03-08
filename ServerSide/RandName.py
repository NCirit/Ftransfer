import random

class RandomName:
    def Create(size):
        name = ""
        charset="qwertyuıopğüasdfghjklşizxcvbnmöçQWERTYUIOPĞÜASDFGHJKLŞİZXCVBNMÖÇ1234567890"
        for i in range(size):
            rn = random.randint(0,len(charset) - 1)
            name += charset[rn]
        return name

def Main():
    print(RandomName.Create(18))
if __name__ == "__main__":
    Main()
