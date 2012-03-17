"""This module implements common functions."""
from exceptions import CConstantError
import parser

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

def value(expression):
    """

    This is a helper function, instead of dirrectly calling a leaf's value() function, 
    this function is used. This function checks whether the leaf implements a value()
    expression, if it doesn't an exception is raised.

    """
    if hasattr(expression, "value"):
        return expression.value()
    else:
        raise CConstantError("Expression is not a constant")


def constant_fold(potential_constant):
    """

    Used to implement constant folding optimisations, tries to calculate the
    value of an expression. If the calculation is successfull, the expression
    is replaced by a constant of the same value. If the calculation fails for
    some reason, the expression is not constant, the expression is returned.

    """
    if potential_constant is None:
        return None
    try:
        return parser.Constant(value(potential_constant))
    except CConstantError:
        return potential_constant
