"""This module implements common functions."""

def sign(x):
    return -1 if x < 0 else 1

def c_style_modulo(x, y):
    """

    Division and modulo work differently in python, than in a typical C 
    implementation. In python, the result of an integer division is rounded 
    to -infinity, whereas most processors would normaly round to zero i.e. 
    truncate. This function truncates.

    """
    return sign(x)*(abs(x)%abs(y))

def c_style_division(x, y):
    """

    Division and modulo work differently in python, than in a typical C 
    implementation. In python, the result of an integer division is rounded 
    to -infinity, whereas most processors would normaly round to zero i.e. 
    truncate. This function truncates.

    """
    return sign(x)*sign(y)*(abs(x)//abs(y))
