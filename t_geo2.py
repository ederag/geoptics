from geoptics.elements.vector import Point, Vector
from geoptics.elements.arc import Arc

m1 = Point(60, 110)
m2 = Point(80, 110)
tg = Vector(10, 10)

a = Arc(m1, m2, tg)
c = a.center()
print(c)
print(a.radius())

print(a.C)
print(a.r)
