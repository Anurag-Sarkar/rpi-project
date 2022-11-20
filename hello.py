l = [1,2,3,4,5,6]
dir = input("enter side: ")
count = int(input("enter times: "))
print(l)
for i in range(count):
    if dir == "left":
        val = l.pop((len(l)-1))
        l.insert(0,val)
        
    if dir == "right":
        val = l.pop(0)
        l.insert((len(l)),val)

print(l)