"""Define the nodes of the pass tree"""
from exceptions import ConstantError

def constant_fold(potential_constant):
    if potential_constant is None:
        return None
    try:
        return Constant(potential_constant.value())
    except ConstantError:
        return potential_constant

class Constant:

    def __init__(self, constant):
        self.constant = constant

    def generate_code(self):
        print "memory[end++] = ", self.constant

    def value(self):
        return self.constant

    def _type(self):
        if type(self.constant) is int:
            return "int"
        elif type(self.constant) is float:
            return "float"

class Variable:
    def __init__(self, declarator, name):
        self.declarator = declarator
        self.name = name

    def generate_code(self):
        print "#variable", self.name, "at offset", self.declarator.offset
        print "memory[end++] = memory[start +", self.declarator.offset, "]"

    def value(self):
        raise ConstantError("Variable is not a constant")

    def _type(self):
        return self.declarator._type

class Declare:
    def __init__(self, declarators):
        self.declarators = declarators

    def generate_code(self):
        for declarator in self.declarators:
            declarator.generate_code()

class Declarator:
    def __init__(self, size, expression, name, offset, _type):
        self.size = size
        self.expression = constant_fold(expression)
        self.name = name
        self.offset = offset
        self._type = _type

    def generate_code(self):
        print "# declare variable", self.name, 'of type "', self._type, '" at offset', self.offset
        print "end +=", self.size
        if self.expression:
            self.expression.generate_code()
            print "memory[end++] = memory[start+", self.offset, "]"

class DeclareFunction:

    def __init__(self, args, statement):
        self.args = args
        self.statement = statement

    def generate_code(self):
        print ""
        print "label", id(self)
        self.statement.generate_code()
        print "return"
        print ""

class If:

    def __init__(self, expression, true, false):
        self.expression = constant_fold(expression)
        self.true = true
        self.false = false

    def generate_code(self):
        self.expression.generate_code()
        print "if !memory[--end] goto", id(self)
        self.true.generate_code()
        print "label", id(self)
        if self.false:
            self.false.generate_code()

class While:

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement

    def generate_code(self):
        print "label", id(self), "while"
        self.expression.generate_code()
        print "if !memory[--end] goto", id(self), "end_while"
        self.statement.generate_code()
        print "goto", id(self), "while"
        print "label", id(self), "end_while"

class DoWhile:

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement

    def generate_code(self):
        print "label", id(self)+"do"
        self.statement.generate_code()
        self.expression.generate_code()
        print "if !memory[--end] goto", id(self), "end_while"
        print "goto", id(self), "do"
        print "label", id(self), "end_while"

class For:

    def __init__(self, initialise, expression, iterate, statement):
        self.initialise = constant_fold(initialise)
        self.expression = constant_fold(expression)
        self.iterate = constant_fold(iterate)
        self.statement = statement

    def generate_code(self):
        if self.initialise:
            self.initialise.generate_code()
        print "label", id(self), "while"
        if self.expression:
            self.expression.generate_code()
            print "if !memory[--end] goto", id(self), "end_while"
        self.statement.generate_code()
        if self.iterate:
            self.iterate.generate_code()
        print "goto", id(self), "while"
        print "label", id(self), "end_while"

class Return:

    def __init__(self, expression):
        self.expression = constant_fold(expression)

    def generate_code(self):
        self.expression.generate_code()
        print "return"

class FunctionCall:

    def __init__(self, args, declaration):
        self.args = [constant_fold(arg) for arg in args]
        self.declaration = declaration

    def generate_code(self):
        print "memory[end++] = start"
        print "memory[end++] = return address"
        print "new = end"
        for n, arg in enumerate(self.args):
            arg.generate_code()
        print "start = new"
        print "call", id(self.declaration)
        print "end = start"
        print "return_address = memory[--end]"
        print "start = memory[--end]"

    def value():
        raise Exception("Expression is not a constant")

def sign(x):
    return -1 if x < 0 else 1

def c_style_modulo(x, y):
    return sign(x)*(abs(x)%abs(y))

def c_style_division(x, y):
    return sign(x)*sign(y)*(abs(x)//abs(y))

class Binary:

    def __init__(self, left, right, function):
        self.left = constant_fold(left)
        self.right = constant_fold(right)
        self.function = function

        if self.left._type() != "int":
            raise TypeError("only integer operands are supported")
        if self.right._type() != "int":
            raise TypeError("only integer operands are supported")


    def generate_code(self):
        self.left.generate_code()
        self.right.generate_code()
        print "memory[end++] = memory[--end]", self.function, "memory[--end]"

    def value(self):
        functions = {
            "+" : lambda x, y:x+y,
            "-" : lambda x, y:x-y,
            "*" : lambda x, y:x*y,
            "/" : c_style_division,
            "%" : c_style_modulo,
            "<<" : lambda x, y:x<<y,
            ">>" : lambda x, y:x>>y,
            "&" : lambda x, y:x+y,
            "|" : lambda x, y:x+y,
            "^" : lambda x, y:x+y,
            "&&" : lambda x, y:x and y,
            "||" : lambda x, y:x or y,
            "==" : lambda x, y:x+y,
            "!=" : lambda x, y:x+y,
            "<=" : lambda x, y:x+y,
            ">=" : lambda x, y:x+y,
            "<" : lambda x, y:x+y,
            ">" : lambda x, y:x+y,
        }
        return functions[self.function](self.left.value(), self.right.value())

    def _type():
        return "int"

class Unary:

    def __init__(self, expression, function):
        self.expression = constant_fold(expression)
        self.function = function
        if self.expression._type() != "int":
            raise TypeError("only integer operands are supported")

    def generate_code(self):
        self.expression.generate_code()
        print "memory[end++] =", self.function, "memory[--end]"

    def value(self):
        functions = {
            "!" : lambda x:-1 if x == 0 else 0,
            "~" : lambda x:~x,
            "-" : lambda x:-x,
            "+" : lambda x:+x,
        }
        return functions[self.function](self.left.value(), self.right.value())

    def _type():
        return "int"

class PostIncrement:
    def __init__(self, declarator):
        self.declarator = declarator

    def generate_code(self):
        print "#post increment offset", self.declarator.offset
        print "memory[end++] = memory[start+", self.declarator.offset, "]"
        print "memory[start+", self.declarator.offset, "] + memory[--end] + 1"
        print "end++"

    def value(self):
        raise ConstantError("Expression is not a constant")

    def _type(self):
        return self.declarator._type

class PostDecrement:
    def __init__(self, declarator):
        self.declarator = declarator

    def generate_code(self):
        print "#post decrement declarator", self.declarator.offset
        print "memory[end++] = memory[start+", self.declarator.offset, "]"
        print "memory[start+", self.declarator.offset, "] + memory[--end] - 1"
        print "end++"

    def value(self):
        raise ConstantError("Expression is not a constant")

    def _type(self):
        return self.declarator._type

class PreIncrement:
    def __init__(self, declarator):
        self.declarator = declarator

    def generate_code(self):
        print "#pre increment declarator", self.declarator.offset
        print "memory[end++] = memory[start+", self.declarator.offset, "]"
        print "memory[start+", self.declarator, "] + memory[--end] + 1"
        print "memory[end++] = memory[start+", self.declarator.offset, "]"

    def value(self):
        raise ConstantError("Expression is not a constant")

    def _type(self):
        return self.declarator._type

class PreDecrement:
    def __init__(self, declarator):
        self.declarator = declarator

    def generate_code(self):
        print "#pre deccrement declarator", self.declarator.offset
        print "memory[end++] = memory[start+", self.declarator.offset, "]"
        print "memory[start+", self.declarator.offset, "] + memory[--end] - 1"
        print "memory[end++] = memory[start+", self.declarator.offset, "]"

    def value(self):
        raise ConstantError("Expression is not a constant")

    def _type(self):
        return self.declarator._type

class Block:

    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements

    def generate_code(self):
        for declaration in self.declarations:
            declaration.generate_code()
        for statement in self.statements:
            statement.generate_code()

class Discard:

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        self.expression.generate_code()
        print "end--"

class Assignment:

    def __init__(self, declarator, expression):
        self.declarator = declarator
        self.expression = constant_fold(expression)
        if self.declarator._type != self.expression._type():
            raise TypeError("Cannot assign " + self.expression._type() + 
            " to " + self.declarator._type)

    def generate_code(self):
        self.expression.generate_code()
        print "memory[start+", self.declarator.offset, "] = memory[--end]"
        print "end++" #leave variable on top of stack

    def value(self):
        raise ConstantError("Expression is not a constant")

    def _type(self):
        return self.declarator._type
