import os.path

import scanner
from tree import *
import copy
from exceptions import CSyntaxError, CTypeError, CConstantError


class Parser:

    """
    Parser

    The parser consumes tokens from the lexical scanner, and uses them to 
    form a parse tree. The leaves of the parse tree are defines in tree.py

    The parse function accepts an input string, and returns the parse tree.

    Example::

        input string:

        int main(){
          int a = 1;
          return a + 2;
        }

        The lexical scanner converts to:

        ["int", "main", "(", ")", "{", "}", "int", "a", "=", "a", "+", "1"]

        The Parser converts this to:

                              FunctionDefinition
                                      |
                                      v
                                    Block
                                    /   \
                                   v     v
                       [Declaration(a)] Return
                                           \
                                            v
                                         Binary(+)
                                          /     \
                                         v       v
                                   Variable(a) Constant(1)

    """

    def syntax_error(self, string):

        """Generate an Error message and exit"""

        print string
        print "at line", self.tokens.line(), ",", self.tokens.char()
        exit(1)

    def parse(self, string):

        """Parse the input file. Return the parse tree."""

        self.scope = {}
        self.offset = 0
        self.tokens = scanner.Tokenize(string)

        try:
            global_declarations = []
            while self.tokens.peek():
                global_declarations.append(self.parse_global_declaration())
            main = str(id(self.scope["main"]))
            return CompilationUnit(global_declarations, main)

        except CConstantError:
            self.syntax_error("Expression must be a constant")
        except CTypeError:
            self.syntax_error("Type error in expression")
        except CSyntaxError:
            self.syntax_error("Syntax error in expression")

        return instructions

    def parse_global_declaration(self):

        """Parse global function or variable declaration."""

        self.tokens.expect("int")
        if self.tokens.check_next("("):
            #function
            return self.parse_declare_function()
        else:
            #variable
            return self.parse_declare()

    def parse_declare_function(self):

        """Parse global function declaration."""

        name = self.tokens.pop()
        self.tokens.expect("(")
        args = []
        stored_offset = self.offset
        self.offset = 0
        while not self.tokens.check(")"):
            self.tokens.expect("int")
            argname = self.tokens.pop()
            declarator = Declarator(1, None, argname, self.offset, "int")
            self.scope[argname] = declarator
            self.offset += 1
            args.append(name)
            if self.tokens.check(","):
                self.tokens.expect(",")
            else:
                break
        self.offset = stored_offset
        self.tokens.expect(")")
        statement = self.parse_statement()
        node = DeclareFunction(args, statement, "int")
        self.scope[name] = node
        return node

    def parse_statement(self):

        """Parse a statement."""

        if self.tokens.check("{"):
            return self.parse_block()
        elif self.tokens.check("if"):
            return self.parse_if()
        elif self.tokens.check("while"):
            return self.parse_while()
        elif self.tokens.check("do"):
            return self.parse_do_while()
        elif self.tokens.check("for"):
            return self.parse_for()
        elif self.tokens.check("return"):
            return self.parse_return()
        elif self.tokens.check("break"):
            return self.parse_break()
        elif self.tokens.check("continue"):
            return self.parse_continue()
        elif self.tokens.check("switch"):
            return self.parse_switch()
        elif self.tokens.check("default"):
            return self.parse_default()
        elif self.tokens.check("case"):
            return self.parse_case()
        elif self.tokens.check("goto"):
            return self.parse_goto()
        elif self.tokens.check_next(":"):
            return self.parse_label()
        else:
            expression = self.parse_expression()
            self.tokens.expect(";")
            return Discard(expression)

    def parse_block(self):

        """Parse a block statement."""

        #A block causes a new lexical scope to be created. Names declared 
        #within the local scope are added to, or override names defined in 
        #the surrounding scope. Outside the block, the surrounding scope is 
        #restored.

        #To implement this, a copy of the scope is made. Within the block, 
        #the scope may be modified. When the block has been parsed, the stored
        #scope is restored.

        stored_scope = copy.copy(self.scope)
        self.tokens.expect("{")
        declarations = []
        while self.tokens.check("int"):
            self.tokens.expect("int")
            declarations.append(self.parse_declare())
        statements = []
        while not self.tokens.check("}"):
            statements.append(self.parse_statement())
        self.tokens.expect("}")
        self.scope = stored_scope
        return Block(declarations, statements)

    def parse_if(self):

        """Parse an if statement."""

        self.tokens.expect("if")
        self.tokens.expect("(")
        expression = self.parse_expression()
        self.tokens.expect(")")
        true_statement = self.parse_statement()
        false_statement = None
        if self.tokens.check("else"):
            self.tokens.expect("else")
            false_statement = self.parse_statement()
        return If(expression, true_statement, false_statement)

    def parse_while(self):

        """Parse a while statement."""

        self.tokens.expect("while")
        self.tokens.expect("(")
        expression = self.parse_expression()
        self.tokens.expect(")")
        statement = self.parse_statement()
        return While(expression, statement)

    def parse_do_while(self):

        """Parse a do-while statement."""

        self.tokens.expect("do")
        statement = self.parse_statement()
        self.tokens.expect("while")
        self.tokens.expect("(")
        expression = self.parse_expression()
        self.tokens.expect(")")
        self.tokens.expect(";")
        return DoWhile(expression, statement)

    def parse_for(self):

        """Parse a for statement."""

        initialise = expression = iterate = None
        self.tokens.expect("for")
        self.tokens.expect("(")
        if not self.tokens.check(";"):
            initialise = self.parse_expression()
        self.tokens.expect(";")
        if not self.tokens.check(";"):
            expression = self.parse_expression()
        self.tokens.expect(";")
        if not self.tokens.check(")"):
            iterate = self.parse_expression()
        self.tokens.expect(")")
        statement = self.parse_statement()
        return For(initialise, expression, iterate, statement)

    def parse_return(self):

        """Parse a return statement."""

        self.tokens.expect("return")
        expression = self.parse_expression()
        self.tokens.expect(";")
        return Return(expression)

    def parse_break(self):

        """Parse a break statement."""

        self.tokens.expect("break")
        self.tokens.expect(";")
        return Break()

    def parse_switch(self):

        """Parse a switch statement."""

        self.tokens.expect("switch")
        self.tokens.expect("(")
        expression = self.parse_expression()
        self.tokens.expect(")")
        statement = self.parse_statement()
        return Switch(expression, statement)

    def parse_case(self):

        """Parse a case statement."""

        self.tokens.expect("case")
        expression = self.parse_constant_expression()
        self.tokens.expect(":")
        return Case(expression)

    def parse_goto(self):

        """Parse a goto statement."""

        self.tokens.expect("goto")
        label = self.tokens.pop()
        self.tokens.expect(";")
        return Goto(label)

    def parse_label(self):

        """Parse a label statement."""

        label = self.tokens.pop()
        self.tokens.expect(":")
        return Label(label)

    def parse_default(self):

        """Parse a default statement."""

        self.tokens.expect("default")
        self.tokens.expect(":")
        return Default()

    def parse_continue(self):

        """Parse a continue statement."""

        self.tokens.expect("continue")
        self.tokens.expect(";")
        return Continue()

    def parse_declare(self):

        """Parse a local variable declaration."""

        declarators = [self.parse_declarator()]
        while self.tokens.check(","):
            self.tokens.expect(",")
            declarators.append(self.parse_declarator())
        self.tokens.expect(";")
        return Declare(declarators)

    def parse_declarator(self):

        """Parse each variable within a compound variable declaration."""

        name = self.tokens.pop()
        size = 1
        _type = "int"
        if self.tokens.check("["):
            _type = "array of int"
            self.tokens.expect("[")
            size = self.parse_constant_expression().value()
            self.tokens.expect("]")
        if self.tokens.check("="):
            self.tokens.expect("=")
            initialise = self.parse_expression()
        else:
            initialise = None
        declarator = Declarator(size, initialise, name, self.offset, _type)
        self.scope[name] = declarator
        self.offset += size
        return declarator

    def parse_constant_expression(self):

        """Parse a constant expression used in variable initialisation."""

        return self.parse_or_expression()


    def parse_expression(self):

        """Parse an assignment expression."""

        for token in ["=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "&=", 
            "|=", "^="]:
            if self.tokens.check_next(token):
                variable = self.tokens.pop()
                self.tokens.expect(token)
                expression = self.parse_expression()
                try:
                    declarator = self.scope[variable]
                except KeyError:
                    self.syntax_error("unknown identifier: " + variable)
                if token == "=":
                    return Assignment(declarator, expression)
                else:
                    return Assignment(declarator, Binary(Variable(declarator, variable), 
                    expression, token[:-1]))
        return self.parse_or_expression()

    def parse_or_expression(self):

        """Parse a logical or expression."""

        expression = self.parse_and_expression()
        while self.tokens.peek() in ["||"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_and_expression(), 
                function)
        return expression

    def parse_and_expression(self):

        """Parse a logical and expression."""

        expression = self.parse_bitwise_xor_expression()
        while self.tokens.peek() in ["&&"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_bitwise_xor_expression(), 
                function)
        return expression

    def parse_bitwise_xor_expression(self):

        """Parse a bitwise xor expression."""

        expression = self.parse_bitwise_or_expression()
        while self.tokens.peek() in ["^"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_bitwise_or_expression(), 
                function)
        return expression

    def parse_bitwise_or_expression(self):

        """Parse a bitwise or expression."""

        expression = self.parse_bitwise_and_expression()
        while self.tokens.peek() in ["|"]:
            function = self.tokens.pop()
            expression =  Binary(expression, self.parse_bitwise_and_expression(), 
                function)
        return expression

    def parse_bitwise_and_expression(self):

        """Parse a bitwise and expression."""

        expression = self.parse_comparison_expression()
        while self.tokens.peek() in ["&"]:
            function = self.tokens.pop()
            expression =  Binary(expression, self.parse_conparison_expression(), 
                function)
        return expression

    def parse_comparison_expression(self):

        """Parse a comparison expression."""

        expression = self.parse_equality_expression()
        while self.tokens.peek() in ["<", "<=", ">", ">="]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_equality_expression(), 
                function)
        return expression

    def parse_equality_expression(self):

        """Parse an equality (or inequality) expression."""

        expression = self.parse_shift_expression()
        while self.tokens.peek() in ["==", "!="]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_shift_expression(), 
                function)
        return expression

    def parse_shift_expression(self):

        """Parse a left or right shift expression."""

        expression = self.parse_arithmetic_expression()
        while self.tokens.peek() in ["<<", ">>"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_arithmetic_expression(), 
                function)
        return expression

    def parse_arithmetic_expression(self):

        """Parse an arithmetic expression."""

        expression = self.parse_mult_expression()
        while self.tokens.peek() in ["+", "-"]:
            function = self.tokens.pop()
            expression =  Binary( expression, self.parse_mult_expression(), 
                function)
        return expression

    def parse_mult_expression(self):

        """Parse a multiply, divide or modulo expression."""

        expression = self.parse_unary_expression()
        while self.tokens.peek() in ["*", "/", "%"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_unary_expression(), 
                function)
        return expression

    def parse_unary_expression(self):

        """Parse a unary expression."""

        while self.tokens.peek() in ["&", "*", "-", "+", "!", "~"]:
            function = self.tokens.pop()
            return Unary(self.parse_paren_expression(), function)
        else:
            return self.parse_paren_expression()

    def parse_paren_expression(self):

        """Parse a parenthesised expression."""

        if self.tokens.check("("):
            self.tokens.expect("(")
            expression = self.parse_expression()
            self.tokens.expect(")")
        else:
            expression = self.parse_numvar()
        return expression

    def parse_numvar(self):

        """Parse a number, or identifier."""

        if self.tokens.peek()[0].isdigit():
            return self.parse_number()
        elif self.tokens.peek()[0].isalpha():
            return self.parse_identifier()

    def parse_number(self):

        """Parse a number."""

        number =  self.tokens.pop() 
        return Constant(int(number))

    def parse_identifier(self):

        """Parse a variable or function call."""

        token = self.tokens.peek()
        if token in ["++", "--"]:
            self.tokens.expect(token)
            name = self.tokens.pop()
            try:
                declarator = self.scope[name]
            except KeyError:
                self.syntax_error("unknown identifier: " + name)
            if token == "++":
                return PreIncrement(declarator)
            else:
                return PreDecrement(declarator)
        else:
            name = self.tokens.pop()
            if self.tokens.check("("):
                return self.parse_function_call(name)
            else:
                try:
                    declarator = self.scope[name]
                except KeyError:
                    self.syntax_error("unknown identifier: " + name)
                if self.tokens.check("++"):
                    self.tokens.expect("++")
                    return PostIncrement(declarator)
                elif self.tokens.check("--"):
                    self.tokens.expect("--")
                    return PostDecrement(declarator)
                else:
                    return Variable(declarator, name)

    def parse_function_call(self, name):

        """Parse a function call."""

        self.tokens.expect("(")
        args = []
        while not self.tokens.check(")"):
            args.append(self.parse_expression())
            if self.tokens.check(","):
                self.tokens.expect(",")
            else:
                break
        self.tokens.expect(")")

        try:
            function_declaration = self.scope[name]
        except KeyError:
            self.syntax_error("unknown identifier: " + name)

        if len(args) != len(function_declaration.args):
            self.syntax_error("wrong number of arguments")
        return FunctionCall(args, function_declaration)
