"""Define the nodes of the pass tree"""
from exceptions import CConstantError, CTypeError, CSyntaxError
from common import c_style_division, c_style_modulo
from registers import *

def constant_fold(potential_constant):
    if potential_constant is None:
        return None
    try:
        return Constant(potential_constant.value())
    except CConstantError:
        return potential_constant

class CompilationUnit:
    def __init__(self, declarations, main):
        self.declarations = declarations
        self.main = main

    def generate_code(self):
        instructions = [
            ("literal", end, 0, 0),
            ("literal", start, 0, 0),
            ("jump and link", return_address, 0, self.main),
            ("label", "end", 0, 0),
            ("goto", 0, 0, "end"),
        ]
        for declaration in self.declarations:
            instructions.extend(declaration.generate_code())

        return instructions

class Constant:
    def __init__(self, constant):
        self.constant = constant

    def generate_code(self):
        return [
            ("literal", temp, 0, self.constant),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ]

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
        return [
            ("addl", offset, start, self.declarator.offset),
            ("load", temp, offset, 0),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ]

    def value(self):
        raise CConstantError("Variable is not a constant")

    def _type(self):
        return self.declarator._type

class Declare:
    def __init__(self, declarators):
        self.declarators = declarators

    def generate_code(self):
        instructions = []
        for declarator in self.declarators:
            instructions.extend(declarator.generate_code())
        return instructions

class Declarator:
    def __init__(self, size, expression, name, offset, _type):
        self.size = size
        self.expression = constant_fold(expression)
        self.name = name
        self.offset = offset
        self._type = _type

    def generate_code(self):
        instructions = [("addl", end, end, self.size)]
        if self.expression:
            #initialise expression
            instructions.extend(self.expression.generate_code())
            #pop
            instructions.append(("addl", end, end, -1))
            instructions.append(("load", temp, end, 0))
            #put in variable
            instructions.append(("addl", offset, start, self.offset))
            instructions.append(("store", 0, offset, temp))
        return instructions

class DeclareFunction:

    def __init__(self, args, statement, _type):
        self.args = args
        self.statement = statement
        self._type =_type
        self.labels = {}
        if hasattr(statement, "set_surrounding_function"):
            statement.set_surrounding_function(self)

    def generate_code(self):
        instructions = [("label", str(id(self)), 0, 0)] 
        instructions.extend(self.statement.generate_code())
        instructions.append(("goto register", 0, return_address, 0))
        return instructions

class If:

    def __init__(self, expression, true, false):
        self.expression = constant_fold(expression)
        self.true = true
        self.false = false

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("jump if false", 0, temp, str(id(self)))
        ])
        instructions.extend(self.true.generate_code())
        instructions.append(("label", str(id(self), 0, 0)))
        if self.false:
            instructions.extend(self.false.generate_code())
        return instructions

class Switch:

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement
        self.cases = {}
        if hasattr(statement, "set_surrounding_statement"):
            statement.set_surrounding_statement(self)

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
        ])
        for case_value, case in self.cases.iteritems():
            instructions.extend([
                ("literal", temp1, 0, case_value),
                ("ne", temp1, temp, temp1),
                ("jump if false", 0, temp1, str(id(case)))
            ])
        if hasattr(self, "default"):
            instructions.extend([("goto", 0, 0, str(id(self.default)))])
        instructions.extend([("goto", 0, 0, str(id(self))+"end")])
        instructions.extend(self.statement.generate_code())
        instructions.extend([("label", str(id(self)) + "end", 0, 0)])
        return instructions

class Case:

    def __init__(self, expression):
        self.expression = expression.value()

    def generate_code(self):
        return [("label", str(id(self)), 0, 0)]

    def set_surrounding_statement(self, statement):
        statement.cases[self.expression] = self

class Default:

    def generate_code(self):
        return [("label", str(id(self)), 0, 0)]

    def set_surrounding_statement(self, statement):
        statement.default = self

class Label:

    def __init__(self, label):
        self.label = label

    def generate_code(self):
        return [("label", str(id(self)), 0, 0)]

    def set_surrounding_function(self, function):
        function.labels[self.label] =  str(id(self))

class Goto:
    def __init__(self, label):
        self.label = label

    def generate_code(self):
        try:
            label = self.function.labels[self.label]
        except KeyError:
            raise CSyntaxError("Unknown Label")
            
        return [("goto", 0, 0, label)]

    def set_surrounding_function(self, function):
        self.function = function

class While:

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement
        if hasattr(statement, "set_surrounding_statement"):
            statement.set_surrounding_statement(self)

    def generate_code(self):
        instructions = [("label", str(id(self))+"start", 0, 0)]
        instructions.extend(self.expression.generate_code())
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("jump if false", 0, temp, str(id(self)) + "end")
        ])
        instructions.extend(self.statement.generate_code())
        instructions.extend([
            ("goto", 0, 0, str(id(self)) + "start"),
            ("label", str(id(self)) + "end", 0, 0)
        ])
        return instructions

class DoWhile:

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement
        if hasattr(statement, "set_surrounding_statement"):
            statement.set_surrounding_statement(self)

    def generate_code(self):
        instructions = [("label", str(id(self))+"start", 0, 0)]
        instructions.extend(self.statement.generate_code())
        instructions.extend(self.expression.generate_code())
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("jump if false", 0, temp, str(id(self)) + "end")
            ("goto", 0, 0, str(id(self)) + "start"),
            ("label", str(id(self))+"end", 0, 0)
        ])

def For(initialise, expression, iterate, statement):
    if iterate:
        statement = Block([], [statement, iterate])
    if expression:
        loop = While(expression, statement)
    else:
        loop = While(Constant(-1), statement)
    if initialise:
        loop = Block([], [initialise, loop])
    return loop

class Return:

    def __init__(self, expression):
        self.expression = constant_fold(expression)

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", return_value, end, 0))
        instructions.append(("goto register", 0, return_address, 0))
        return instructions

class FunctionCall:

    def __init__(self, args, declaration):
        self.args = [constant_fold(arg) for arg in args]
        self.declaration = declaration

    def generate_code(self):
        instructions = [
          ("store", 0, end, start),
          ("addl", end, end, 1),
          ("store", 0, end, return_address),
          ("addl", end, end, 1),
          ("addl", new, end, 0),
        ]
        for arg in self.args:
            instructions.extend(arg.generate_code())
        instructions.extend([
          ("addl", start, new, 0),
          ("jump and link", return_address, 0, str(id(self.declaration))),
          ("addl", end, start, 0),
          ("addl", end, end, -1),
          ("load", return_address, end, 0),
          ("addl", end, end, -1),
          ("load", start, end, 0),
          ("store", 0, end, return_value),
          ("addl", end, end, 1),
        ])
        return instructions

    def value(self):
        raise CConstantError("Expression is not a constant")

    def _type(self):
        return self.declaration._type

class Binary:

    def __init__(self, left, right, function):
        self.left = constant_fold(left)
        self.right = constant_fold(right)
        self.function = function

        if self.left._type() != "int":
            raise CTypeError("only integer operands are supported")
        if self.right._type() != "int":
            raise CTypeError("only integer operands are supported")


    def generate_code(self):
        operations = {
            "+" : "add",
            "-" : "sub",
            "*" : "mul",
            "/" : "div",
            "%" : "mod",
            "<<" : "lshift",
            ">>" : "rshift",
            "&" : "and",
            "|" : "or",
            "^" : "xor",
            "&&" : "blah",
            "||" : "blahblah",
            "==" : "eq",
            "!=" : "ne",
            "<=" : "le",
            ">=" : "ge",
            "<" : "lt",
            ">" : "gt",
        }
        instructions = self.left.generate_code()
        instructions.extend(self.right.generate_code())
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", temp, end, 0))
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", temp1, end, 0))
        instructions.append((operations[self.function], temp, temp1, temp))
        instructions.append(("store", 0, end, temp))
        instructions.append(("addl", end, end, 1))
        return instructions

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

    def _type(self):
        return "int"

class Unary:

    def __init__(self, expression, function):
        self.expression = constant_fold(expression)
        self.function = function
        if self.expression._type() != "int":
            raise CTypeError("only integer operands are supported")

    def generate_code(self):
        operations = { "!" : "not", "~" : "invert", "-" : "negate"}
        instructions = self.expression.generate_code()
        if self.function != "+":
            instructions.extend([
                ("addl", end, end, -1),
                ("load", temp, end, 0),
                (operations[self.function], temp, end, 0),
                ("store", end, temp, 0),
                ("addl", end, end, 1),
            ])
        return instructions

    def value(self):
        functions = {
            "!" : lambda x:-1 if x == 0 else 0,
            "~" : lambda x:~x,
            "-" : lambda x:-x,
            "+" : lambda x:+x,
        }
        return functions[self.function](self.expression.value())

    def _type():
        return self.expression._type()

class PostIncrement:
    def __init__(self, declarator):
        self.declarator = declarator

    def generate_code(self):
        print "#post increment offset", self.declarator.offset
        print "memory[end++] = memory[start+", self.declarator.offset, "]"
        print "memory[start+", self.declarator.offset, "] + memory[--end] + 1"
        print "end++"
        return []

    def value(self):
        raise CConstantError("Expression is not a constant")

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
        return []

    def value(self):
        raise CConstantError("Expression is not a constant")

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
        return []

    def value(self):
        raise CConstantError("Expression is not a constant")

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
        return []

    def value(self):
        raise CConstantError("Expression is not a constant")

    def _type(self):
        return self.declarator._type

class Block:

    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements

    def generate_code(self):
        instructions = []
        for declaration in self.declarations:
            instructions.extend(declaration.generate_code())
        for statement in self.statements:
            instructions.extend(statement.generate_code())
        return instructions

    def set_surrounding_statement(self, s):
        for statement in self.statements:
            if hasattr(statement, "set_surrounding_statement"):
                statement.set_surrounding_statement(s)

    def set_surrounding_function(self, s):
        for statement in self.statements:
            if hasattr(statement, "set_surrounding_function"):
                statement.set_surrounding_function(s)

class Break:

    def generate_code(self):
        return [("goto", 0, 0, str(id(self.surrounding_statement))+"end")]

    def set_surrounding_statement(self, statement):
        self.surrounding_statement = statement

class Continue:

    def generate_code(self):
        return [("goto", 0, 0, str(id(self.surrounding_statement))+"start")]

    def set_surrounding_statement(self, statement):
        self.surrounding_statement = statement

class Discard:

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.append(("addl", end, end, -1))
        return instructions

class Assignment:

    def __init__(self, declarator, expression):
        self.declarator = declarator
        self.expression = constant_fold(expression)
        if self.declarator._type != self.expression._type():
            raise CTypeError("Cannot assign " + self.expression._type() + 
            " to " + self.declarator._type)

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", temp, end, 0))
        instructions.append(("addl", end, end, 1))
        instructions.append(("addl", offset, start, self.declarator.offset))
        instructions.append(("store", 0, offset, temp))
        return instructions

    def value(self):
        raise CConstantError("Expression is not a constant")

    def _type(self):
        return self.declarator._type
