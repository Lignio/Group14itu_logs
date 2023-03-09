import random


##All the functions below are just for simulating data for the graphs. Not needed in the end.
names = ["Johan", "Jakob", "Katrine", "Malte","Maxime","Adam","Oliver","Baldur","Isabella","Emilia"]
count = [0,0,0,0,0,0,0,0,0,0,0]
lengths = [0,1,2,3,4,5,6,7,8,9,10]
nameLength = [len(names[0]),len(names[1]),len(names[2]),len(names[3])]

def nameCounter(names):
    for i in names:
        count[len(i)] += 1
    return count

def genLists():
    lst1 = []
    lst2 = []
    for i in range(1000):
        lst1.append(random.randint(0,10000))
        lst2.append(random.randint(0,10000))
        

    return lst1, lst2
