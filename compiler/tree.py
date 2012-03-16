"""Define the nodes of the pass tree"""
from exceptions import CConstantError, CTypeError, CSyntaxError
from common import c_style_division, c_style_modulo
from registers import *

class GPRException(Exception):
    pass

gpr = 0

def get_gpr():
    global gpr
    return gpr

def increment_gpr():
    global gpr
    if gpr < maxgpr:
        gpr += 1;
    else:
        raise GPRException

def decrement_gpr():
    global gpr
    if gpr > 0:
        gpr -= 1;
    else:
        raise GPRException

def generate_code(leaf):
    global gpr
    stored_gpr = gpr
    #attempt to generate code in registers
    if hasattr(leaf, "generate_code_reg"):
        try:
            #generate in registers
            instructions = leaf.generate_code_reg()
            decrement_gpr()
            #then move to the stack
            instructions.append(("store", 0, end, gpr))
            instructions.append(("addl", end, end, 1))
            return instructions
        except GPRException:
            gpr = stored_gpr
    #if this fails for some reason use the stack
    return leaf.generate_code()

def generate_code_reg(leaf):
    if hasattr(leaf, "generate_code_reg"):
        return leaf.generate_code_reg()
    else:
        raise GPRException

sizes = {"int" : 4, "float" : 4, "int*": 4, "float*":4}
def size(expression):
    return sizes[expression._type()]


def value(expression):
    if hasattr(expression, "value"):
        return expression.value()
    else:
        raise CConstantError("Expression is not a constant")


def constant_fold(potential_constant):
    if potential_constant is None:
        return None
    try:
        return Constant(value(potential_constant))
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

    def generate_code_reg(self):
        instructions = [("literal", get_gpr(), 0, self.constant)]
        increment_gpr()
        return instructions

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
            #load
            ("addl", offset, start, self.declarator.offset),
            ("load", temp, offset, 0),
            #push
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ]

    def generate_code_reg(self):
        instructions = [
            ("addl", offset, start, self.declarator.offset),
            ("load", get_gpr(), offset, 0),
        ]
        increment_gpr()
        return instructions

    def generate_code_write(self):
        return [
            #pop
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            #push
            ("addl", end, end, 1),
            #store
            ("addl", offset, start, self.declarator.offset),
            ("store", 0, offset, temp)
        ]

    def generate_code_address(self):
        return [
            ("addl", temp, start, self.declarator.offset),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ]

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
        self.expression = constant_fold(expression)
        self.name = name
        self.offset = offset
        self._type = _type

    def generate_code(self):
        global gpr
        instructions = [("addl", end, end, sizes[self._type]//4)]
        if self.expression:
            stored_gpr = gpr
            try:
                instructions.extend(generate_code_reg(self.expression))
                decrement_gpr()
                instructions.append(("addl", offset, start, self.offset))
                instructions.append(("store", 0, offset, gpr))
            except GPRException:
                gpr = stored_gpr
                instructions.extend(generate_code(self.expression))
                instructions.append(("addl", end, end, -1))
                instructions.append(("load", temp, end, 0))
                instructions.append(("addl", offset, start, self.offset))
                instructions.append(("store", 0, offset, temp))
        return instructions


class DeclareFunction:

    def __init__(self, args, _type):
        self.args = args
        self._type =_type
        self.labels = {}

    def define(self, statement):
        self.statement = statement
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
        try:
            if value(self.expression == 0):
                if self.false:
                    return generate_code(self.false)
                else:
                    return []
            else:
                return generate_code(self.true)
        except CConstantError:
            instructions = generate_code(self.expression)
            instructions.extend([
                ("addl", end, end, -1),
                ("load", temp, end, 0),
                ("jump if false", 0, temp, str(id(self)))
            ])
            instructions.extend(self.true.generate_code())
            instructions.append(("goto", 0, 0, str(id(self))+"end"))
            instructions.append(("label", str(id(self)), 0, 0))
            if self.false:
                instructions.extend(self.false.generate_code())
            instructions.append(("label", str(id(self))+"end", 0, 0))
            return instructions

    def set_surrounding_statement(self, s):
        if hasattr(self.true, "set_surrounding_statement"):
            self.true.set_surrounding_statement(s)
        if self.false and hasattr(self.false, "set_surrounding_statement"):
            self.false.set_surrounding_statement(s)

    def set_surrounding_function(self, s):
        if hasattr(self.true, "set_surrounding_function"):
            self.true.set_surrounding_function(s)
        if self.false and hasattr(self.false, "set_surrounding_function"):
            self.false.set_surrounding_function(s)


class Switch:

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement
        self.cases = {}
        if hasattr(statement, "set_surrounding_statement"):
            statement.set_surrounding_statement(self)

    def generate_code(self):
        instructions = generate_code(self.expression)
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
        self.expression = value(expression)

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
        try:
            if value(self.expression):
                instructions = [("label", str(id(self))+"start", 0, 0)]
                instructions.extend(self.statement.generate_code())
                instructions.append(("goto", 0, 0, str(id(self)) + "start"))
                instructions.append(("label", str(id(self))+"end", 0, 0))
            else:
                instructions = [("label", str(id(self))+"start", 0, 0)]
                instructions.append(("label", str(id(self))+"end", 0, 0))
        except CConstantError:
            instructions = [("label", str(id(self))+"start", 0, 0)]
            instructions.extend(generate_code(self.expression))
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
        try:
            if value(expression.generate_code()):
                instructions = [("label", str(id(self))+"start", 0, 0)]
                instructions.extend(self.statement.generate_code())
                instructions.append(("goto", 0, 0, str(id(self)) + "start"))
                instructions.append(("label", str(id(self))+"end", 0, 0))
            else:
                instructions = [("label", str(id(self))+"start", 0, 0)]
                instructions.extend(self.statement.generate_code())
                instructions.append(("label", str(id(self))+"end", 0, 0))
        except CConstantError:
            instructions = [("label", str(id(self))+"start", 0, 0)]
            instructions.extend(self.statement.generate_code())
            instructions.extend(generate_code(self.expression))
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
        instructions = generate_code(self.expression)
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
            instructions.extend(generate_code(arg))
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

    def _type(self):
        return self.declaration._type


class Convert:
    def __init__(self, expression, _type):
        self.expression = expression
        self.__type = _type

    def generate_code(self):
        instructions = generate_code(self.expression)
        if self.__type != self.expression._type():
            instructions.append(("addl", end, end, -1))
            instructions.append(("load", temp, end, 0))
            instructions.append(("to_"+self.__type, 0, end, temp))
            instructions.append(("store", 0, end, temp))
            instructions.append(("addl", end, end, 1))
        return instructions

    def generate_code_reg(self):
        instructions = generate_code_reg(self.expression)
        if self.__type != self.expression._type():
            instructions.append(("to_"+self.__type, 0, gpr, gpr))
        return instructions

    def _type(self):
        return self.__type


def Or(left, right):
    return Ternary(
            left, 
            Constant(1), 
            Ternary(
                right, 
                Constant(1), 
                Constant(0)
            )
    )


def And(left, right):
    return Ternary(
            left, 
            Ternary(
                right, 
                Constant(1), 
                Constant(0)
            ), 
            Constant(0)
    )


class Ternary:

    def __init__(self, expression, true_expression, false_expression):
        self.expression = constant_fold(expression)
        self.true_expression = constant_fold(true_expression)
        self.false_expression = constant_fold(false_expression)

    def generate_code(self):
        try:
            if value(self.expression):
                return generate_code(self.true_expression)
            else:
                return generate_code(self.false_expression)
        except CConstantError:
            instructions = generate_code(self.expression)
            instructions.append(("addl", end, end, -1))
            instructions.append(("load", temp, end, 0))
            instructions.append(("jump if false", 0, temp, str(id(self))+"false"))
            instructions.extend(self.true_expression.generate_code())
            instructions.append(("goto", 0, 0, str(id(self))+"end"))
            instructions.append(("label", str(id(self))+"false", 0, 0))
            instructions.extend(self.false_expression.generate_code())
            instructions.append(("label", str(id(self))+"end", 0, 0))
            return instructions

    def value(self):
        if value(self.expression):
            return value(self.true_expression)
        else:
            return value(self.false_expression)


class Binary:

    def __init__(self, left, right, function):
        self.left = constant_fold(left)
        self.right = constant_fold(right)
        self.function = function
        self.operations = {
          "int" : {
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
            "==" : "eq", 
            "!=" : "ne", 
            "<=" : "le", 
            ">=" : "ge", 
            "<" : "lt", 
            ">" : "gt",
          },
          "float" : {
            "+" : "fpadd", 
            "-" : "fpsub", 
            "*" : "fpmul", 
            "/" : "fpdiv", 
            "==" : "fpeq", 
            "!=" : "fpne", 
            "<=" : "fple", 
            ">=" : "fpge", 
            "<" : "fplt",
            ">" : "fpgt",
          },
          "int*" : {
            "+" : "add", 
            "-" : "sub", 
            "==" : "eq", 
            "!=" : "ne", 
            "<=" : "le",
            ">=" : "ge", 
            "<" : "lt",
            ">" : "gt",
          },
          "float*" : {
            "+" : "add", 
            "-" : "sub", 
            "==" : "eq", 
            "!=" : "ne", 
            "<=" : "le",
            ">=" : "ge", 
            "<" : "lt", 
            ">" : "gt",
          },
        }

        for i in ["float", "int"]:
            if self.left._type() == i:
                self.right = Convert(self.right, i)
                break
            elif self.right._type() == i:
                self.left = Convert(self.left, i)
                break

        if self.left._type() != self.right._type():
            raise CTypeError("incompatible types:" + left._type() + ", " + right._type())

    def generate_code_reg(self):
        operation = self.operations[self._type()][self.function]
        instructions = generate_code_reg(self.left)
        instructions.extend(generate_code_reg(self.right))
        decrement_gpr()
        instructions.append((operation, gpr-1, gpr-1, gpr))
        return instructions

    def generate_code(self):
        operation = self.operations[self._type()][self.function]
        instructions = self.left.generate_code()
        instructions.extend(self.right.generate_code())
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", temp, end, 0))
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", temp1, end, 0))
        instructions.append((operation, temp, temp1, temp))
        instructions.append(("store", 0, end, temp))
        instructions.append(("addl", end, end, 1))
        return instructions

    def value(self):
        functions = {
          "int" : {
            "+"  : lambda x, y:x+y, 
            "-"  : lambda x, y:x-y, 
            "*"  : lambda x, y:x*y,
            "/"  : c_style_division, 
            "%"  : c_style_modulo, 
            "<<" : lambda x, y:x<<y,
            ">>" : lambda x, y:x>>y, 
            "&"  : lambda x, y:x&y, 
            "|"  : lambda x, y:x|y,
            "^"  : lambda x, y:x^y, 
            "==" : lambda x, y:x==y, 
            "!=" : lambda x, y:x!=y, 
            "<=" : lambda x, y:x<=y,
            ">=" : lambda x, y:x>=y, 
            "<"  : lambda x, y:x<y, 
            ">"  : lambda x, y:x>y,
          },
          "float" : {
            "+"  : lambda x, y:x+y, 
            "-"  : lambda x, y:x-y, 
            "*"  : lambda x, y:x*y,
            "/"  : lambda x, y:x/y, 
            "==" : lambda x, y:x==y, 
            "!=" : lambda x, y:x!=y,
            "<=" : lambda x, y:x<=y, 
            ">=" : lambda x, y:x>=y, 
            "<"  : lambda x, y:x<y,
            ">"  : lambda x, y:x>y,
          },
          "int*" : {
            "+"  : lambda x, y:x+y, 
            "-"  : lambda x, y:x-y, 
            "==" : lambda x, y:x==y, 
            "!=" : lambda x, y:x!=y, 
            "<=" : lambda x, y:x<=y, 
            ">=" : lambda x, y:x>=y, 
            "<"  : lambda x, y:x<y, 
            ">"  : lambda x, y:x>y,
          },
          "float*" : {
            "+"  : lambda x, y:x+y, 
            "-"  : lambda x, y:x-y, 
            "==" : lambda x, y:x==y, 
            "!=" : lambda x, y:x!=y, 
            "<=" : lambda x, y:x<=y, 
            ">=" : lambda x, y:x>=y, 
            "<"  : lambda x, y:x<y, 
            ">"  : lambda x, y:x>y,
          }
        }
        return functions[self.left._type()][self.function](value(self.left), value(self.right))

    def _type(self):
        types = {
          "int" : {
            "+"  : "int", 
            "-"  : "int", 
            "*"  : "int", 
            "/"  : "int", 
            "%"  : "int", 
            "<<" : "int", 
            ">>" : "int", 
            "&"  : "int", 
            "|"  : "int", 
            "^"  : "int", 
            "&&" : "int",
            "||" : "int", 
            "==" : "int", 
            "!=" : "int", 
            "<=" : "int", 
            ">=" : "int", 
            "<"  : "int", 
            ">"  : "int",
          },
          "float" : {
            "+"  : "float", 
            "-"  : "float", 
            "*"  : "float", 
            "/"  : "float", 
            "==" : "int",
            "!=" : "int",
            "<=" : "int", 
            ">=" : "int", 
            "<"  : "int", 
            ">"  : "int",
          },
          "int*" : {
            "+"  : "int*", 
            "-"  : "int*", 
            "==" : "int", 
            "!=" : "int", 
            "<=" : "int", 
            ">=" : "int", 
            "<"  : "int", 
            ">"  : "int",
          },
          "float*" : {
            "+"  : "float*", 
            "-"  : "float*", 
            "==" : "int", 
            "!=" : "int", 
            "<=" : "int", 
            ">=" : "int", 
            "<"  : "int", 
            ">"  : "int",
          }
        }
        return types[self.left._type()][self.function]


class Unary:

    def __init__(self, expression, function):
        self.expression = constant_fold(expression)
        self.function = function
        if self.expression._type() != "int":
            raise CTypeError("only integer operands are supported")

    def generate_code(self):
        operations = { "!" : "not", "~" : "invert", "-" : "negate"}
        instructions = generate_code(self.expression)
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
            "!" : lambda x:1 if x == 0 else 0,
            "~" : lambda x:~x,
            "-" : lambda x:-x,
            "+" : lambda x:+x,
        }
        return functions[self.function](value(self.expression))

    def _type():
        return self.expression._type()


class PostIncrement:

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        instructions = generate_code(self.expression)
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
            ("addl", temp, temp, 1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(generate_code(self.expression))
        instructions.append(("addl", end, end, -1))
        return instructions

    def _type(self):
        return self.expression._type()


class PostDecrement:

    def __init__(self, declarator):
        self.declarator = declarator

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
            ("addl", temp, temp, -1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(self.expression.generate_code_write())
        instructions.append(("addl", end, end, -1))
        return instructions

    def _type(self):
        return self.expression._type()


class PreIncrement:

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("addl", temp, temp, 1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(self.expression.generate_code_write())
        return instructions

    def _type(self):
        return self.expression._type()


class PreDecrement:

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("addl", temp, temp, -1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(self.expression.generate_code_write())
        return instructions

    def _type(self):
        return self.expression._type()


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


class CompoundExpression:

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def generate_code(self):
        instructions = self.right.generate_code()
        instructions.append(("addl", end, end, -1))
        instructions = self.left.generate_code()
        return instructions

    def _type(self):
        return self.left._type()


class Assignment:

    def __init__(self, left, right):
        self.left = left
        self.right = constant_fold(right)

        if self.left._type() in ["int", "float"]:
            self.right = Convert(self.right, self.left._type())

        if self.left._type() != self.right._type():
            raise CTypeError("Cannot assign " + self.right._type() + 
            " to " + self.left._type())

    def generate_code(self):
        instructions = generate_code(self.right)
        instructions.extend(self.left.generate_code_write())
        return instructions

    def _type(self):
        return self.left._type()


class SizeOf:

    def __init__(self, expression):
        self.expression = Constant(size(self))

    def generate_code(self):
        return self.expression.generate_code()

    def value(self):
        return size(self)

    def _type(self):
        return "int"


def SizeOfType(_type):
    return Constant(sizes[_type])


class Address:

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        return self.expression.generate_code_address()

    def _type(self):
        return self.expression._type() + "*"


class Dereference:

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self):
        instructions = self.expression.generate_code()
        instructions.extend([
            #pop
            ("addl", end, end, -1),
            ("load", offset, end, 0),
            #load
            ("load", temp, offset, 0),
            #push
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        return instructions

    def generate_code_write(self):
        instructions = self.expression.generate_code()
        instructions.extend([
            #pop
            ("addl", end, end, -1),
            ("load", offset, end, 0),
            #pop
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            #push
            ("addl", end, end, 1),
            #store
            ("store", 0, offset, temp)
        ])
        return instructions

    def generate_code_address(self):
        return [
            ("addl", temp, start, self.declarator.offset),
            #push
            ("store", 0, end, temp)
            ("addl", end, end, 1),
        ]

    def _type(self):
        if not self.expression._type().endswith("*"):
            raise CTypeError("Expression is not a pointer")
        return self.expression._type()[:-1]
