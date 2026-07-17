# Задача 3
# (A5^A1 / √B2) * cos(A2) + ln(B1)
# B1 = A1*A5 если A4<5.7 иначе A3;  B2 = A5^A1 если B1>=15 иначе √A5.  A2 — ГРАДУСЫ.
import math

def r5(x):
    return round(x, 5)

with open('in-1-03.txt', encoding='utf-8') as f:
    a1, a2, a3, a4, a5 = map(float, f.read().split())

if a4 < 5.7:
    b1 = r5(a1 * a5)
else:
    b1 = a3

if b1 >= 15:
    b2 = r5(a5 ** a1)
else:
    b2 = r5(math.sqrt(a5))

num  = r5(a5 ** a1)               # A5^A1
den  = r5(math.sqrt(b2))          # √B2
frac = r5(num / den)              # A5^A1 / √B2

a2r  = r5(math.radians(a2))       # A2: градусы -> радианы
cs   = r5(math.cos(a2r))          # cos(A2)
term = r5(frac * cs)              # * cos(A2)

lg   = r5(math.log(b1))           # ln(B1)
res  = r5(term + lg)

print(f"{res:.2f}")
