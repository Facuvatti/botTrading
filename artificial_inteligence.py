import random 
def aiDecides(x,y,isFloat=False):
    if isFloat:
        return random.uniform(x,y)
    else:
        return random.randint(x,y)
