from mathutils import Vector
from random import random

def random_tangent(dir):
    v = random_on_unit_sphere()
    return v.cross(dir)

def random_on_unit_sphere():
    return Vector((random()-.5, random()-.5, random()-.5)).normalized()
    