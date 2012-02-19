import os.path

import scanner
from tree import *
import copy


class Parser:

    def syntax_error(self, string):
        print string
        print "at line", self.tokens.line(), ",", self.tokens.char()
        exit(1)

    def parse(self, string):
        self.scope = {}
        self.offset = 0
        self.tokens = scanner.Tokenize(string)

        global_declarations = []
        while self.tokens.peek():
            global_declarations.append(self.parse_global_declaration())

        for global_declaration in global_declarations:
            global_declaration.generate_code()

    def parse_global_declaration(self):
        self.tokens.expect("int")
        if self.tokens.check_next("("):
            #function
            return self.parse_declare_function()
        else:
            #variable
            return self.parse_declare()

    def parse_declare_function(self):
        name = self.tokens.pop()
        self.tokens.expect("(")
        args = []
        stored_offset = self.offset
        self.offset = 0
        while not self.tokens.check(")"):
            self.tokens.expect("int")
            argname = self.tokens.pop()
            self.scope[argname] = self.offset
            self.offset += 1
            args.append(name)
            if self.tokens.check(","):
                self.tokens.expect(",")
            else:
                break
        self.offset = stored_offset
        self.tokens.expect(")")
        statement = self.parse_statement()
        node = DeclareFunction(args, statement)
        self.scope[name] = node
        return node

    def parse_statement(self):
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
        else:
            expression = self.parse_expression()
            self.tokens.expect(";")
            return Discard(expression)

    def parse_block(self):
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
        self.tokens.expect("while")
        self.tokens.expect("(")
        expression = self.parse_expression()
        self.tokens.expect(")")
        statement = self.parse_statement()
        return While(expression, statement)

    def parse_do_while(self):
        self.tokens.expect("do")
        statement = self.parse_statement()
        self.tokens.expect("while")
        self.tokens.expect("(")
        expression = self.parse_expression()
        self.tokens.expect(")")
        self.tokens.expect(";")
        return DoWhile(expression, statement)

    def parse_for(self):
        self.tokens.expect("for")
        self.tokens.expect("(")
        if not self.tokens.check(";"):
            initialise = self.parse_assignment()
        self.tokens.expect(";")
        if not self.tokens.check(";"):
            expression = self.parse_expression()
        self.tokens.expect(";")
        if not self.tokens.check(")"):
            iterate = self.parse_assignment()
        self.tokens.expect(")")
        statement = self.parse_statement()
        return For(initialise, expression, iterate, statement)

    def parse_return(self):
        self.tokens.expect("return")
        expression = self.parse_expression()
        self.tokens.expect(";")
        return Return(expression)

    def parse_declare(self):
        declarators = [self.parse_declarator()]
        while self.tokens.check(","):
            self.tokens.expect(",")
            declarators.append(self.parse_declarator())
        self.tokens.expect(";")
        return Declare(declarators)

    def parse_declarator(self):
        name = self.tokens.pop()
        self.scope[name] = self.offset
        size = 1
        if self.tokens.check("["):
            print name
            self.tokens.expect("[")
            size = self.parse_constant_expression().value()
            self.tokens.expect("]")
        if self.tokens.check("="):
            self.tokens.expect("=")
            initialise = self.parse_expression()
        else:
            initialise = None
        declarator = Declarator(size, initialise, name, self.offset)
        self.offset += size
        return declarator

    def parse_constant_expression(self):
        return self.parse_or_expression()


    def parse_expression(self):
        for token in ["=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "&=", 
            "|=", "^="]:
            if self.tokens.check_next(token):
                variable = self.tokens.pop()
                self.tokens.expect(token)
                expression = self.parse_expression()
                try:
                    offset = self.scope[variable]
                except KeyError:
                    self.syntax_error("unknown identifier: " + variable)
                if token == "=":
                    return Assignment(offset, expression)
                else:
                    return Assignment(offset, Binary(Variable(offset, variable), 
                    expression, token[:-1]))
        return self.parse_or_expression()

    def parse_or_expression(self):
        expression = self.parse_and_expression()
        while self.tokens.peek() in ["||"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_and_expression(), 
                function)
        return expression

    def parse_and_expression(self):
        expression = self.parse_bitwise_xor_expression()
        while self.tokens.peek() in ["&&"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_bitwise_xor_expression(), 
                function)
        return expression

    def parse_bitwise_xor_expression(self):
        expression = self.parse_bitwise_or_expression()
        while self.tokens.peek() in ["^"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_bitwise_or_expression(), 
                function)
        return expression

    def parse_bitwise_or_expression(self):
        expression = self.parse_bitwise_and_expression()
        while self.tokens.peek() in ["|"]:
            function = self.tokens.pop()
            expression =  Binary(expression, self.parse_bitwise_and_expression(), 
                function)
        return expression

    def parse_bitwise_and_expression(self):
        expression = self.parse_comparison_expression()
        while self.tokens.peek() in ["&"]:
            function = self.tokens.pop()
            expression =  Binary(expression, self.parse_conparison_expression(), 
                function)
        return expression

    def parse_comparison_expression(self):
        expression = self.parse_equality_expression()
        while self.tokens.peek() in ["<", "<=", ">", ">="]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_equality_expression(), 
                function)
        return expression

    def parse_equality_expression(self):
        expression = self.parse_shift_expression()
        while self.tokens.peek() in ["==", "!="]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_shift_expression(), 
                function)
        return expression

    def parse_shift_expression(self):
        expression = self.parse_arithmetic_expression()
        while self.tokens.peek() in ["<<", ">>"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_arithmetic_expression(), 
                function)
        return expression

    def parse_arithmetic_expression(self):
        expression = self.parse_mult_expression()
        while self.tokens.peek() in ["+", "-"]:
            function = self.tokens.pop()
            expression =  Binary( expression, self.parse_mult_expression(), 
                function)
        return expression

    def parse_mult_expression(self):
        expression = self.parse_unary_expression()
        while self.tokens.peek() in ["*", "/", "%"]:
            function = self.tokens.pop()
            expression = Binary(expression, self.parse_unary_expression(), 
                function)
        return expression

    def parse_unary_expression(self):
        while self.tokens.peek() in ["&", "*", "-", "+", "!", "~"]:
            function = self.tokens.pop()
            return Unary(self.parse_paren_expression(), function)
        else:
            return self.parse_paren_expression()

    def parse_paren_expression(self):
        if self.tokens.check("("):
            self.tokens.expect("(")
            expression = self.parse_expression()
            self.tokens.expect(")")
        else:
            expression = self.parse_numvar()
        return expression

    def parse_numvar(self):
        if self.tokens.peek()[0].isdigit():
            return self.parse_number()
        elif self.tokens.peek()[0].isalpha():
            return self.parse_identifier()

    def parse_number(self):
        number =  self.tokens.pop() 
        return Constant(int(number))

    def parse_identifier(self):
        token = self.tokens.peek()
        if token in ["++", "--"]:
            self.tokens.expect(token)
            name = self.tokens.pop()
            try:
                offset = self.scope[name]
            except KeyError:
                self.syntax_error("unknown identifier: " + name)
            if token == "++":
                return PreIncrement(offset)
            else:
                return PreDecrement(offset)
        else:
            name = self.tokens.pop()
            if self.tokens.check("("):
                return self.parse_function_call(name)
            else:
                try:
                    offset = self.scope[name]
                except KeyError:
                    self.syntax_error("unknown identifier: " + name)
                if self.tokens.check("++"):
                    self.tokens.expect("++")
                    return PostIncrement(offset)
                elif self.tokens.check("--"):
                    self.tokens.expect("--")
                    return PostDecrement(offset)
                else:
                    return Variable(offset, name)

    def parse_function_call(self, name):
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
