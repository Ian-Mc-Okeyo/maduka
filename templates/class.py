import math


x=2.3
y=(x**2)+0.25*x-5
print(y)

def quadratic(y, a, b, c):
    c = c-y
    x1=((-1*b)+math.sqrt((b**2)-(4*a*c)))/(2*a)
    x2=((-1*b)-math.sqrt((b**2)-(4*a*c)))/(2*a)
    print(f'x={x1} OR x:{x2}')

# print('Enter the value of Y:')
# y = float(input())
# print('Enter the value of a:')
# a=float(input())
# print('Enter the value of b')
# b=float(input())
# print('Enter the value of c:')
# c=float(input())
# quadratic(y, a, b, c)

# dict = {'names':[1,2,3,4,5], 'numbers': ['ian', 'Mark']}
# for value in dict:
#     for x in dict[value]:
#         print(x)

class Person():
    def __init__(self, name, age):
        self.name=name
        self.age=age

person1=Person('Ian', 23)
print(type(person1.name))
if type(person1)==Person:
    print('yes')
else:
    print('No')

print(len('ian'))

