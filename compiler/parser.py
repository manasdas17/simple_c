import os.path

import scanner
from tree import *
import copy
from exceptions import CSyntaxError, CTypeError, CConstantError

types = ["int", "float"]

class Parser:

    """

    parser
    ======

    The parser consumes tokens from the lexical scanner, and uses them to 
    form a parse tree. The leaves of the parse tree are defines in tree.py

    The parse function accepts an input string, and returns the parse tree.

    """


    def syntax_error(self, string):

        """Generate an Error message and exit"""

        raise CSyntaxError(
            "{0}\nat line {1}, {2}".format(string, self.tokens.line(), self.tokens.char())
        )

    def parse(self, string):

        """Parse the input file. Return the parse tree."""

        self.scope = {} #A dictionary of all currently visible objects
        self._locals = [] #A list of localy declared objects
        self.offset = 0
        self.reserved = 0
        self.tokens = scanner.Tokenize(string)

        #try:
        global_declarations = []
        while self.tokens.peek():
            global_declarations.append(self.parse_global_declaration())
        main = str(id(self.scope["main"]))
        return CompilationUnit(global_declarations, main, self.reserved)

        #except CConstantError:
        #    self.syntax_error("Expression must be a constant")
        #except CTypeError:
        #    self.syntax_error("Type error in expression")
        #except CSyntaxError:
        #    self.syntax_error("Syntax error in expression")

        return instructions

    def parse_global_declaration(self):

        """Parse global function or variable declaration."""

        _type = self.tokens.pop()
        if self.tokens.check_next("("):
            #function
            return self.parse_declare_function(_type)
        else:
            #variable
            return self.parse_declare(_type)

    def parse_declare_function(self, _type):

        """Parse global function declaration."""

        name = self.tokens.pop()
        self.tokens.expect("(")
        args = []
        stored_offset = self.offset
        self.offset = 0
        while not self.tokens.check(")"):
            arg_type = self.tokens.pop()
            if self.tokens.check("*"):
                arg_type += "*"
                self.tokens.expect("*")
            argname = self.tokens.pop()
            declarator = Declarator(1, None, argname, self.offset, arg_type)
            self.scope[argname] = declarator
            self.offset += 1
            args.append(name)
            if self.tokens.check(","):
                self.tokens.expect(",")
            else:
                break
        self.tokens.expect(")")
        node = DeclareFunction(args, _type)
        self.scope[name] = node
        node.define(self.parse_statement())
        self.offset = stored_offset
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
        stored_locals = copy.copy(self._locals)
        self._locals = []
        self.tokens.expect("{")
        declarations = []
        while self.tokens.peek() in types:
            _type = self.tokens.pop()
            declarations.append(self.parse_declare(_type))
        statements = []
        while not self.tokens.check("}"):
            statements.append(self.parse_statement())
        self.tokens.expect("}")
        self.scope = stored_scope
        self._locals = stored_locals
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

    def parse_declare(self, _type):

        """Parse a local variable declaration."""

        declarators = [self.parse_declarator(_type)]
        while self.tokens.check(","):
            self.tokens.expect(",")
            declarators.append(self.parse_declarator(_type))
        self.tokens.expect(";")
        return Declare(declarators)

    def parse_declarator(self, _type):

        """Parse each variable within a compound variable declaration."""

        if self.tokens.check("*"):
            _type += "*"
            self.tokens.expect("*")
        name = self.tokens.pop()
        if self.tokens.check("="):
            self.tokens.expect("=")
            initialise = self.parse_assignment_expression()
        else:
            initialise = None

        #check for redeclaration
        if name in self._locals:
            self.syntax_error("Redefinition of {0}".format(name))
        else:
            self._locals.append(name)

        declarator = Declarator(1, initialise, name, self.offset, _type)
        self.scope[name] = declarator
        self.offset += 1
        return declarator

    def parse_constant_expression(self):

        """

        constant_expression ::=
            ternary_expression
        
        """

        unary = self.parse_unary_expression()
        return self.parse_ternary_expression(unary)

    def parse_expression(self):

        """

        expression ::=
            assignment_expression ( "," assignment_expression )*

        """
        
        expression = self.parse_assignment_expression()
        while self.tokens.check(","):
            self.tokens.expect(",")
            expression = CompoundExpression(expression, self.parse_expression)
        return expression

    def parse_assignment_expression(self):

        """

        assignment_operator ::=
            ("=" | "+=" | "-=" | "*=" | "/=" | "%=" | "<<=" | ">>=" | "&=" | 
            "|=" | "^=")

        assignment_expression ::=
            ternary_expression | 
            (unary_expression assignment_operator assignment_expression)

        """

        left = self.parse_unary_expression()
        for token in ["=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "&=", 
            "|=", "^="]:
            if self.tokens.check(token):
                self.tokens.expect(token)
                right = self.parse_expression()
                if token == "=":
                    return Assignment(left, right)
                else:
                    return Assignment(
                        left, Binary(left, right, token[:-1]))

        return self.parse_ternary_expression(left)

    def parse_ternary_expression(self, unary):

        """

        ternary_expression ::= 
            or_expression ( "?" expression ":" ternary_expression )?

        """

        expression = self.parse_or_expression(unary)
        if self.tokens.check("?"):
            self.tokens.expect("?")
            true_expression = self.parse_expression()
            self.tokens.expect(":")
            unary = self.parse_unary_expression()
            false_expression = self.parse_ternary_expression(unary)
            expression = Ternary(expression, true_expression, false_expression)
        return expression

    def parse_or_expression(self, unary):

        """
       
        or_expression ::=
            and_expression ( "||"  and_expression )*
        
        """

        expression = self.parse_and_expression(unary)
        while self.tokens.peek() in ["||"]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression = Or(
                expression, self.parse_and_expression(unary))
        return expression

    def parse_and_expression(self, unary):

        """
        
        and_expression ::=
            bitwise_or_expression ( "&&" bitwise_or_expression )*
        
        """

        expression = self.parse_bitwise_or_expression(unary)
        while self.tokens.peek() in ["&&"]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression = And(
                expression, self.parse_bitwise_or_expression(unary))
        return expression

    def parse_bitwise_or_expression(self, unary):

        """
        
        bitwise_or_expression ::=
            bitwise_xor_expression ( "|" bitwise_xor_expression )*
        
        """

        expression = self.parse_bitwise_xor_expression(unary)
        while self.tokens.peek() in ["|"]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression =  Binary(
                expression, self.parse_bitwise_xor_expression(unary), function)
        return expression

    def parse_bitwise_xor_expression(self, unary):

        """
        
        bitwise_xor_expression ::=
            bitwise_and_expression ( "^" bitwise_and_expression )*
        
        """

        expression = self.parse_bitwise_and_expression(unary)
        while self.tokens.peek() in ["^"]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression = Binary(
                expression, self.parse_bitwise_and_expression(unary), function)
        return expression

    def parse_bitwise_and_expression(self, unary):

        """
        
        bitwise_and_expression ::=
            bitwise_comparison_expression ( "&" bitwise_comparison_expression )*
        
        """

        expression = self.parse_comparison_expression(unary)
        while self.tokens.peek() in ["&"]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression =  Binary(
                expression, self.parse_comparison_expression(unary), function)
        return expression

    def parse_comparison_expression(self, unary):

        """
        
        comparison_expression ::=
            equality_expression ( ("<" | "<=" | ">" | ">=") equality_expression )*
        
        """

        expression = self.parse_equality_expression(unary)
        while self.tokens.peek() in ["<", "<=", ">", ">="]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression = Binary(
                expression, self.parse_equality_expression(unary), function)
        return expression

    def parse_equality_expression(self, unary):

        """
        
        equality_expression ::=
            shift_expression ( ("==" | "!=") shift_expression )*
        
        """

        expression = self.parse_shift_expression(unary)
        while self.tokens.peek() in ["==", "!="]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression = Binary(
                expression, self.parse_shift_expression(unary), function)
        return expression

    def parse_shift_expression(self, unary):

        """
        
        shift_expression ::=
            arithmetic_expression ( ("<<" | ">>") arithmetic_expression )*
        
        """

        expression = self.parse_arithmetic_expression(unary)
        while self.tokens.peek() in ["<<", ">>"]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression = Binary(
                expression, self.parse_arithmetic_expression(unary), function)
        return expression

    def parse_arithmetic_expression(self, unary):

        """
        
        arithmetic_expression ::=
            multiplicative_expression ( ("+" | "-") multiplicative_expression )*
        
        """

        expression = self.parse_mult_expression(unary)
        while self.tokens.peek() in ["+", "-"]:
            function = self.tokens.pop()
            unary = self.parse_unary_expression()
            expression =  Binary(
                expression, self.parse_mult_expression(unary), function)
        return expression

    def parse_mult_expression(self, unary):

        """
        
        multiplicative_expression ::=
            unary_expression ( ("*" | "/" | "%") unary_expression )*
        
        """

        expression = unary
        while self.tokens.peek() in ["*", "/", "%"]:
            function = self.tokens.pop()
            expression = Binary(
                expression, self.parse_unary_expression(), function)
        return expression

    def parse_unary_expression(self):

        """Parse a unary expression."""

        if self.tokens.peek() in ["-", "+", "!", "~"]:
            function = self.tokens.pop()
            return Unary(self.parse_unary_expression(), function)
        elif self.tokens.check("&"):
            self.tokens.expect("&")
            return Address(self.parse_unary_expression())
        elif self.tokens.check("*"):
            self.tokens.expect("*")
            return Dereference(self.parse_unary_expression())
        elif self.tokens.peek() in ["++", "--"]:
            return self.parse_prefix_expression()
        elif self.tokens.check("sizeof"):
            return self.parse_sizeof_expression()
        else:
            return self.parse_primary_expression()

    def parse_primary_expression(self):

        """Parse a primary expression."""

        if self.tokens.check("("):
            self.tokens.expect("(")
            expression = self.parse_expression()
            self.tokens.expect(")")
        elif self.tokens.peek()[0].isdigit():
            expression = self.parse_number()
        elif self.tokens.peek()[0].isalpha():
            expression = self.parse_identifier()
        elif self.tokens.peek().startswith("'"):
            expression = self.parse_char()
        elif self.tokens.peek().startswith('"'):
            expression = self.parse_string()
        return expression

    def parse_char(self):

        """Parse a character literal."""

        number = self.tokens.pop()

        return Constant(ord(number[1:]))

    def parse_string(self):

        """Parse a string literal."""

        string = self.tokens.pop()
        #get rid of leading quote
        string = string[1:]
        #expand escape sequences
        string = eval('"{0}"'.format(string))
        #append null char
        string += '\x00'
        #reserve some memory for the string
        reserved = self.reserved
        self.reserved += len(string)
        return String(string, reserved)

    def parse_number(self):

        """Parse a number."""

        number = self.tokens.pop() 
        try:
            value = int(number, 0)
        except ValueError:
            value = float(number)

        return Constant(value)

    def parse_sizeof_expression(self):

        """Parse sizeof expression."""

        self.tokens.expect("sizeof")
        for token in types:
            if self.tokens.check("(") and self.tokens.check_next(token):
                self.tokens.expect("(")
                _type = self.tokens.pop()
                self.tokens.expect(")")
                return SizeOfType(_type)
        return SizeOf(self.parse_unary_expression())

    def parse_prefix_expression(self):

        """Parse prefix expression."""

        if self.tokens.check("++"):
            self.tokens.expect("++")
            return PreIncrement(self.parse_unary_expression())
        else:
            self.tokens.expect("--")
            return PreDecrement(self.parse_unary_expression())

    def parse_identifier(self):

        """Parse a variable or function call."""

        name = self.tokens.pop()
        if self.tokens.check("("):
            expression = self.parse_function_call(name)
        else:
            try:
                declarator = self.scope[name]
            except KeyError:
                self.syntax_error("unknown identifier: " + name)
            expression = Variable(declarator, name)
        while self.tokens.peek() in ["++", "--", "[", ".", "->"]:
            expression = self.parse_postfix_expression(expression)
        return expression

    def parse_postfix_expression(self, expression):

        """Parse a postfix expression."""

        if self.tokens.check("++"):
            self.tokens.expect("++")
            return PostIncrement(expression)
        elif self.tokens.check("--"):
            self.tokens.expect("--")
            return PostDecrement(expression)

    def parse_function_call(self, name):

        """Parse a function call."""

        self.tokens.expect("(")
        args = []
        while not self.tokens.check(")"):
            args.append(self.parse_assignment_expression())
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
