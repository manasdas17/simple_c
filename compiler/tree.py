"""Define the nodes of the pass tree"""
from exceptions import CConstantError, CTypeError, CSyntaxError
from common import c_style_division, c_style_modulo, value, constant_fold

import code_generator as cg

class CompilationUnit:

    """C source file root"""

    def __init__(self, declarations, main):
        self.declarations = declarations
        self.main = main

    def generate_code(self):
        code_generator = cg.CodeGenerator()
        return code_generator.compilation_unit_generate_code(self)


class Constant:

    """constant value leaf"""

    def __init__(self, constant):
        self.constant = constant

    def generate_code(self, code_generator):
        return code_generator.constant_generate_code(self)

    def generate_code_reg(self, code_generator):
        return code_generator.constant_generate_code_reg(self)

    def value(self):
        return self.constant

    def _type(self):
        if type(self.constant) is int:
            return "int"
        elif type(self.constant) is float:
            return "float"


class Variable:

    """variable leaf """

    def __init__(self, declarator, name):
        self.declarator = declarator
        self.name = name

    def generate_code(self, code_generator):
        return code_generator.variable_generate_code(self)

    def generate_code_reg(self, code_generator):
        return code_generator.variable_generate_code_reg(self)

    def generate_code_write(self, code_generator):
        return code_generator.variable_generate_code_write(self)

    def generate_code_address(self, code_generator):
        return code_generator.variable_generate_code_address(self)

    def _type(self):
        return self.declarator._type


class Declare:

    """A variable declaration. i.e. int (declarator)*;"""

    def __init__(self, declarators):
        self.declarators = declarators

    def generate_code(self, code_generator):
        return code_generator.declare_generate_code(self)


class Declarator:

    """A variable declarator, has a variable and an initial value leaf"""

    def __init__(self, size, expression, name, offset, _type):
        self.expression = constant_fold(expression)
        self.name = name
        self.offset = offset
        self._type = _type

    def generate_code(self, code_generator):
        return code_generator.declarator_generate_code(self)


class DeclareFunction:

    """A function declaration leaf"""

    def __init__(self, args, _type):
        self.args = args
        self._type =_type
        self.labels = {}

    def define(self, statement):
        self.statement = statement
        if hasattr(statement, "set_surrounding_function"):
            statement.set_surrounding_function(self)

    def generate_code(self, code_generator):
        return code_generator.declare_function_generate_code(self)


class If:

    """An if statement (with optional else clause) leaf"""

    def __init__(self, expression, true, false):
        self.expression = constant_fold(expression)
        self.true = true
        self.false = false

    def generate_code(self, code_generator):
        return code_generator.if_generate_code(self)

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

    """switch statement leaf"""

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement
        self.cases = {}
        if hasattr(statement, "set_surrounding_statement"):
            statement.set_surrounding_statement(self)

    def generate_code(self, code_generator):
        return code_generator.switch_generate_code(self)


class Case:

    """case statement leaf"""

    def __init__(self, expression):
        self.expression = value(expression)

    def generate_code(self, code_generator):
        return code_generator.case_generate_code(self)

    def set_surrounding_statement(self, statement):
        statement.cases[self.expression] = self


class Default:

    """default statement leaf"""

    def generate_code(self, code_generator):
        return code_generator.default_generate_code(self)

    def set_surrounding_statement(self, statement):
        statement.default = self


class Label:

    """label statement leaf"""

    def __init__(self, label):
        self.label = label

    def generate_code(self, code_generator):
        return code_generator.label_generate_code(self)

    def set_surrounding_function(self, function):
        function.labels[self.label] =  str(id(self))


class Goto:

    """goto statement leaf"""

    def __init__(self, label):
        self.label = label

    def generate_code(self, code_generator):
        return code_generator.goto_generate_code(self)

    def set_surrounding_function(self, function):
        self.function = function


class While:

    """while statement leaf"""

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement
        if hasattr(statement, "set_surrounding_statement"):
            statement.set_surrounding_statement(self)

    def generate_code(self, code_generator):
        return code_generator.while_generate_code(self)


class DoWhile:

    """do while statement leaf"""

    def __init__(self, expression, statement):
        self.expression = constant_fold(expression)
        self.statement = statement
        if hasattr(statement, "set_surrounding_statement"):
            statement.set_surrounding_statement(self)

    def generate_code(self, code_generator):
        return code_generator.do_while_generate_code(self)


def For(initialise, expression, iterate, statement):

    """for statement is syntactic sugar for a while statement"""

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

    """return statement leaf"""

    def __init__(self, expression):
        self.expression = constant_fold(expression)

    def generate_code(self, code_generator):
        return code_generator.return_generate_code(self)


class FunctionCall:

    """function call expression leaf"""

    def __init__(self, args, declaration):
        self.args = [constant_fold(arg) for arg in args]
        self.declaration = declaration

    def generate_code(self, code_generator):
        return code_generator.function_call_generate_code(self)

    def _type(self):
        return self.declaration._type


class Convert:

    """type conversion"""

    def __init__(self, expression, _type):
        self.expression = expression
        self._type_ = _type

    def generate_code(self, code_generator):
        return code_generator.convert_generate_code(self)

    def generate_code_reg(self, code_generator):
        return code_generator.convert_generate_code_reg(self)

    def _type(self):
        return self._type_


def Or(left, right):

    """or expression is syntactic sugar for ternary expression"""

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

    """or expression is syntactic sugar for ternary expression"""

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

    """conditional expression leaf"""

    def __init__(self, expression, true_expression, false_expression):
        self.expression = constant_fold(expression)
        self.true_expression = constant_fold(true_expression)
        self.false_expression = constant_fold(false_expression)

    def generate_code(self, code_generator):
        return code_generator.ternary_generate_code(self)

    def value(self):
        if value(self.expression):
            return value(self.true_expression)
        else:
            return value(self.false_expression)


class Binary:

    """binary expression leaf"""

    def __init__(self, left, right, function):
        self.left = constant_fold(left)
        self.right = constant_fold(right)
        self.function = function

        for i in ["float", "int"]:
            if self.left._type() == i:
                self.right = Convert(self.right, i)
                break
            elif self.right._type() == i:
                self.left = Convert(self.left, i)
                break

        if self.left._type() != self.right._type():
            raise CTypeError("incompatible types:" + left._type() + ", " + right._type())

    def generate_code_reg(self, code_generator):
        return code_generator.binary_generate_code_reg(self)

    def generate_code(self, code_generator):
        return code_generator.binary_generate_code(self)

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

    """unary expression leaf"""

    def __init__(self, expression, function):
        self.expression = constant_fold(expression)
        self.function = function
        if self.expression._type() != "int":
            raise CTypeError("only integer operands are supported")

    def generate_code(self, code_generator):
        return code_generator.unary_generate_code(self)

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

    """post increment expression leaf"""

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self, code_generator):
        return code_generator.post_increment_generate_code(self)

    def _type(self):
        return self.expression._type()


class PostDecrement:

    """post decrement expression leaf"""

    def __init__(self, declarator):
        self.declarator = declarator

    def generate_code(self, code_generator):
        return code_generator.post_decrement_generate_code(self)

    def _type(self):
        return self.expression._type()


class PreIncrement:

    """pre increment expression leaf"""

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self, code_generator):
        return code_generator.pre_increment_generate_code(self)

    def _type(self):
        return self.expression._type()


class PreDecrement:

    """pre decrement expression leaf"""

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self, code_generator):
        return code_generator.pre_decrement_generate_code(self)

    def _type(self):
        return self.expression._type()


class Block:

    """block {} statement leaf"""

    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements

    def generate_code(self, code_generator):
        return code_generator.block_generate_code(self)

    def set_surrounding_statement(self, s):
        for statement in self.statements:
            if hasattr(statement, "set_surrounding_statement"):
                statement.set_surrounding_statement(s)

    def set_surrounding_function(self, s):
        for statement in self.statements:
            if hasattr(statement, "set_surrounding_function"):
                statement.set_surrounding_function(s)


class Break:

    """break statement leaf"""

    def generate_code(self, code_generator):
        return code_generator.break_generate_code(self)

    def set_surrounding_statement(self, statement):
        self.surrounding_statement = statement


class Continue:

    """continue statement leaf"""

    def generate_code(self, code_generator):
        return code_generator.continue_generate_code(self)

    def set_surrounding_statement(self, statement):
        self.surrounding_statement = statement


class Discard:

    """discard expression"""

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self, code_generator):
        return code_generator.discard_generate_code(self)


class CompoundExpression:

    """compound expression list leaf"""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def generate_code(self, code_generator):
        return code_generator.compound_expression_generate_code(self)

    def _type(self):
        return self.left._type()


class Assignment:

    """assignment expression leaf"""

    def __init__(self, left, right):
        self.left = left
        self.right = constant_fold(right)

        if self.left._type() in ["int", "float"]:
            self.right = Convert(self.right, self.left._type())

        if self.left._type() != self.right._type():
            raise CTypeError("Cannot assign " + self.right._type() + 
            " to " + self.left._type())

    def generate_code(self, code_generator):
        return code_generator.assignment_generate_code(self)

    def _type(self):
        return self.left._type()


class SizeOf:

    """sizeof expression leaf"""

    def __init__(self, expression):
        self.expression = Constant(size(self))

    def generate_code(self, code_generator):
        return code_generator.size_of_generate_code(self)

    def value(self):
        return size(self)

    def _type(self):
        return "int"


def SizeOfType(_type):

    """sizeof(<type>) expression leaf"""

    return Constant(sizes[_type])


class Address:

    """address & expression leaf"""

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self, code_generator):
        return code_generator.address_generate_code(self)

    def _type(self):
        return self.expression._type() + "*"


class Dereference:

    """dereference * expression leaf"""

    def __init__(self, expression):
        self.expression = expression

    def generate_code(self, code_generator):
        return code_generator.dereference_generate_code(self)

    def generate_code_write(self, code_generator):
        return code_generator.dereference_generate_code_write(self)

    def generate_code_address(self, code_generator):
        return code_generator.dereference_generate_code_address(self)

    def _type(self):
        if not self.expression._type().endswith("*"):
            raise CTypeError("Expression is not a pointer")
        return self.expression._type()[:-1]

