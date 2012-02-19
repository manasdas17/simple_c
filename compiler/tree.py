"""Define the nodes of the pass tree"""

class Constant:

    def __init__(self, constant):
        self.constant = constant

    def generate_code(self):
        print "memory[end++] = ", self.constant

class Variable:

    def __init__(self, offset):
        self.offset = offset

    def generate_code(self):
        print "memory[end++] = memory[start+", self.offset, "]"

class DeclareVariable:

    def generate_code(self):
        print "end++"

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
        self.expression = expression
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
        self.expression = expression
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
        self.expression = expression
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
        self.initialise = initialise
        self.expression = expression
        self.iterate = iterate
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
        self.expression = expression

    def generate_code(self):
        self.expression.generate_code()
        print "return"

class FunctionCall:

    def __init__(self, args, declaration):
        self.args = args
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

class Binary:

    def __init__(self, left, right, function):
        self.left = left
        self.right = right
        self.function = function

    def generate_code(self):
        self.left.generate_code()
        self.right.generate_code()
        print "memory[end++] = memory[--end]", self.function, "memory[--end]"

class Block:

    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements

    def generate_code(self):
        for declaration in self.declarations:
            declaration.generate_code()
        for statement in self.statements:
            statement.generate_code()

class Assignment:

    def __init__(self, offset, expression):
        self.offset = offset
        self.expression = expression

    def generate_code(self):
        self.expression.generate_code()
        print "memory[start+", self.offset, "] = memory[--end]"
