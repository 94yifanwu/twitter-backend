
def print2500(n):
    print("{")
    for i in range(n):
        print('"name": "ProfAvery", "text": "this is text'+str(i)+'",')
    print("}")


print2500(250)
