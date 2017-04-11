locList = []
for i in range(10000):
    locList.append(i)

if len(locList) > 10:
    newList = [locList[0]]

    indexValue = len(locList) // 8

    for pos in range(indexValue,len(locList),indexValue):
        newList.append(locList[pos])
        if len(newList) == 9:
            break

    newList.append(locList[-1])

    locList = newList
print(len(locList),locList)
