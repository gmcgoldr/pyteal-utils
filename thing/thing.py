from pyteal import *

def doit():
    for x in range(10):
        Log(Itob(x))
