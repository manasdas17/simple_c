import os.path

import chips
import tokenize

from chips.streams import _repeaterize

sinks = {
}

usage = {
    "asserter"    : "assert(<stream>)",
    "counter"     : "counter(start, stop, step)",
    "in_port"     : "in_port(<name>, <bits>)",
    "in_serial"   : "in_serial([ <name> [, <clock rate> [, <baud rate>]]])",
    "out_console" : "out_console(<stream>)",
    "out_port"    : "out_port(<stream>, <name>)",
    "out_serial"  : "out_serial(<stream>[, <name> [, <clock rate> [, <baud rate>]]])",
    "printer"     : "printer(<stream>)",
    "sequence"    : "sequence(<item 0> [, <item 1> [, <item n>]])",
}

builtins = {
    "asserter"    : chips.Asserter,
    "counter"     : chips.Counter,
    "in_port"     : chips.InPort,
    "in_serial"   : chips.SerialIn,
    "out_console" : chips.Console,
    "out_port"    : chips.OutPort,
    "out_serial"  : chips.SerialOut,
    "printer"     : chips.Printer,
    "sequence"    : chips.Sequence,
}

class Parser:

    def syntax_error(self, string):
        print string
        print "at line", self.tokens.line(), ",", self.tokens.char()
        exit(1)

    def parse(self, string):
        self._globals = {}
        self._locals = {}
        self.sinks = []
        self.tokens = tokenize.Tokenize(string)

        while self.tokens.peek():
            self.parse_module_statement()

        return chips.Chip(*self.sinks)

    def parse_module_statement(self):

            #process
            if self.tokens.check("process"):
                self.parse_process()

            #module import
            elif self.tokens.check("import"):
                self.tokens.expect("import")
                module_path = []
                while not self.tokens.check("as"):
                    module_path.append(self.tokens.pop())
                    if self.tokens.check("."):
                        self.tokens.pop()
                    else:
                        break
                self.tokens.expect("as")
                module_name = self.tokens.pop()
                self.tokens.expect("#end of line")
                self._globals[module_name] = os.path.join(*module_path)

            #concurrent connection
            elif self.tokens.check_next("<="):
                self.parse_connection()

            #concurrent expression with no target
            else:
                expression = self.parse_expression()
                if self.is_sink(expression):
                    self.sinks.append(expression)
                self.tokens.expect("#end of line")



    def parse_connection(self):
        target_name = self.tokens.pop()
        self.tokens.expect("<=")
        expression = self.parse_expression()
        self.tokens.expect("#end of line")
        self._globals[target_name] = expression

    def parse_process(self):
        self._locals = {}
        self.process_bits = 0

        self.tokens.expect("process")
        self.tokens.expect(":")
        self.tokens.expect("#end of line")
        self.tokens.expect("#indent")
        statements = []
        while not self.tokens.check("#dedent"):
            statements.append(self.parse_statement())
        self.tokens.expect("#dedent")
        chips.Process(32, *statements)
        self._locals = {}

    def parse_statement(self):
        if self.tokens.check("if"):
            return self.parse_if()
        elif self.tokens.check("loop"):
            return self.parse_loop()
        elif self.tokens.check("while"):
            return self.parse_while()
        elif self.tokens.check("until"):
            return self.parse_until()
        elif self.tokens.check("pass"):
            return self.parse_pass()
        elif self.tokens.check("break"):
            return self.parse_break()
        elif self.tokens.check("continue"):
            return self.parse_continue()
        elif self.tokens.check("waitus"):
            return self.parse_waitus()
        elif self.tokens.check("read"):
            return self.parse_read()
        elif self.tokens.check("write"):
            return self.parse_write()
        elif self.tokens.check("print"):
            return self.parse_print()
        elif self.tokens.peek()[0].isalpha():
            return self.parse_assignment()
        else:
            print self.tokens

    def parse_pass(self):
        self.tokens.expect("pass")
        self.tokens.expect("#end of line")

    def parse_break(self):
        self.tokens.expect("break")
        self.tokens.expect("#end of line")
        return chips.Break()

    def parse_continue(self):
        self.tokens.expect("continue")
        self.tokens.expect("#end of line")
        return chips.Continue()

    def parse_waitus(self):
        self.tokens.expect("waitus")
        self.tokens.expect("#end of line")
        return chips.WaitUs()

    def parse_read(self):
        self.tokens.expect("read")
        in_ = self.tokens.pop()
        self.tokens.expect("=>")
        var = self.tokens.pop()
        if var not in self._locals:
            self._locals[var] = chips.Variable(0)
        if in_ not in self._globals:
            self.syntax_error("unknown stream: {0}".format(in_))
        self.tokens.expect("#end of line")
        return _repeaterize(self._globals[in_]).read(self._locals[var])

    def parse_write(self):
        self.tokens.expect("write")
        out_ = self.tokens.pop()
        self.tokens.expect("<=")
        expression = self.parse_expression()
        self.tokens.expect("#end of line")
        if out_ not in self._globals:
            self._globals[out_] = chips.Output()
        return self._globals[out_].write(expression)

    def parse_print(self):
        self.tokens.expect("print")
        out_ = self.tokens.pop()
        self.tokens.expect("<=")
        parameter = self.parse_expression()
        self.tokens.expect("#end of line")
        if out_ not in self._globals:
            self._globals[out_] = chips.Output()
        return chips.Print(self._globals[out_], parameter)

    def parse_scan(self):
        self.tokens.expect("scan")
        in_ = self.tokens.pop()
        self.tokens.expect("=>")
        var = self.tokens.pop()
        if var not in self._locals:
            self._locals[var] = chips.Variable(0)
        if in_ not in self._globals:
            self.syntax_error("unknown stream: {0}".format(in_))
        self.tokens.expect("#end of line")
        return scan(self._globals[in_], self._locals[var])

    def parse_if(self):

        #if statement
        self.tokens.expect("if")
        expression = self.parse_expression()
        self.tokens.expect(":")
        self.tokens.expect("#end of line")
        self.tokens.expect("#indent")
        statements = [self.parse_statement()]
        while not self.tokens.check("#dedent"):
            statements.append(self.parse_statement())
        self.tokens.expect("#dedent")
        statement = chips.If(expression, *statements)

        #elif statement
        while self.tokens.check("elif"):
            self.tokens.expect("elif")
            expression = self.parse_expression()
            self.tokens.expect(":")
            self.tokens.expect("#end of line")
            self.tokens.expect("#indent")
            statements = [self.parse_statement()]
            while not self.tokens.check("#dedent"):
                statements.append(self.parse_statement())
            self.tokens.expect("#dedent")
            statement = statement.Elif(expression, *statements)

        #else statement
        if self.tokens.check("else"):
            self.tokens.expect("else")
            self.tokens.expect(":")
            self.tokens.expect("#end of line")
            self.tokens.expect("#indent")
            statements = [self.parse_statement()]
            while not self.tokens.check("#dedent"):
                statements.append(self.parse_statement())
            self.tokens.expect("#dedent")
            statement = statement.Else(*statements)

        return statement

    def parse_loop(self):

        #loop statement
        self.tokens.expect("loop")
        self.tokens.expect(":")
        self.tokens.expect("#end of line")
        self.tokens.expect("#indent")
        statements = [self.parse_statement()]
        while not self.tokens.check("#dedent"):
            statements.append(self.parse_statement())
        self.tokens.expect("#dedent")
        statement = chips.Loop(*statements)
        return statement

    def parse_while(self):

        #while statement
        self.tokens.expect("while")
        expression = self.parse_expression()
        self.tokens.expect(":")
        self.tokens.expect("#end of line")
        self.tokens.expect("#indent")
        statements = [self.parse_statement()]
        while not self.tokens.check("#dedent"):
            statements.append(self.parse_statement())
        self.tokens.expect("#dedent")
        statement = chips.While(expression, *statements)
        return statement

    def parse_until(self):

        #until statement
        self.tokens.expect("until")
        expression = self.parse_expression()
        self.tokens.expect(":")
        self.tokens.expect("#end of line")
        self.tokens.expect("#indent")
        statements = [self.parse_statement()]
        while not self.tokens.check("#dedent"):
            statements.append(self.parse_statement())
        self.tokens.expect("#dedent")
        statement = chips.Until(expression, *statements)
        return statement

    def parse_assignment(self):

        variable = self.tokens.pop()
        self.tokens.expect("=")
        expression = self.parse_expression()
        self.tokens.expect("#end of line")
        if variable not in self._locals:
            self._locals[variable] = chips.Variable(0)
        return self._locals[variable].set(expression)

    def parse_expression(self):

        if self.tokens.check("not"):
            self.tokens.pop()
            return chips.Not(self.parse_comparison())
        else:
            return self.parse_comparison()

    def parse_comparison(self):

        expression = self.parse_or_expression()
        if self.tokens.check(">"):
            self.tokens.pop()
            return expression > self.parse_or_expression()
        elif self.tokens.check("<"):
            self.tokens.pop()
            return expression < self.parse_or_expression()
        elif self.tokens.check("<="):
            self.tokens.pop()
            return expression <= self.parse_or_expression()
        elif self.tokens.check(">="):
            self.tokens.pop()
            return expression >= self.parse_or_expression()
        elif self.tokens.check("=="):
            self.tokens.pop()
            return expression == self.parse_or_expression()
        elif self.tokens.check("!="):
            self.tokens.pop()
            return expression != self.parse_or_expression()
        else:
            return expression

    def parse_or_expression(self):

        expression = self.parse_xor_expression()
        if self.tokens.check("|"):
            self.tokens.pop()
            return expression | self.parse_xor_expression()
        else:
            return expression

    def parse_xor_expression(self):

        expression = self.parse_and_expression()
        if self.tokens.check("^"):
            self.tokens.pop()
            return expression ^ self.parse_and_expression()
        else:
            return expression

    def parse_and_expression(self):

        expression = self.parse_shift_expression()
        if self.tokens.check("&"):
            self.tokens.pop()
            return expression & self.parse_shift_expression()
        else:
            return expression

    def parse_shift_expression(self):

        expression = self.parse_arithmetic_expression()
        if self.tokens.check("<<"):
            self.tokens.pop()
            return expression << self.parse_arithmetic_expression()
        elif self.tokens.check(">>"):
            self.tokens.pop()
            return expression >> self.parse_arithmetic_expression()
        else:
            return expression

    def parse_arithmetic_expression(self):

        expression = self.parse_mult_expression()
        if self.tokens.check("+"):
            self.tokens.pop()
            return expression + self.parse_mult_expression()
        elif self.tokens.check("-"):
            self.tokens.pop()
            return expression - self.parse_mult_expression()
        else:
            return expression

    def parse_mult_expression(self):

        expression = self.parse_unary_expression()
        if self.tokens.check("*"):
            self.tokens.pop()
            return expression * self.parse_unary_expression()
        elif self.tokens.check("//"):
            self.tokens.pop()
            return expression // self.parse_unary_expression()
        else:
            return expression

    def parse_unary_expression(self):

        if self.tokens.check("-"):
            self.tokens.pop()
            return 0 - self.parse_paren_expression()
        elif self.tokens.check("+"):
            self.tokens.pop()
            return 0 + self.parse_paren_expression()
        elif self.tokens.check("~"):
            self.tokens.pop()
            return ~self.parse_paren_expression()
        else:
            return self.parse_paren_expression()

    def parse_paren_expression(self):

        if self.tokens.check("("):
            self.tokens.expect("(")
            expression = self.parse_expression()
            self.tokens.expect(")")
            return expression
        else:
            return self.parse_numvar()

    def parse_numvar(self):

        if self.tokens.peek()[0].isdigit():
            return self.parse_number()
        elif self.tokens.peek()[0] in ("'", '"'):
            return self.parse_string()
        elif self.tokens.peek()[0].isalpha():
            return self.parse_identifier()

    def parse_number(self):

        number =  self.tokens.pop() 
        if "." in number:
            return float(number)
        else:
            return int(number)

    def parse_string(self):

        return self.tokens.pop()[1:] #strip quote

    def parse_identifier(self):

        name = self.tokens.pop()
        try:
            atom = self._locals[name]
        except KeyError:
            try:
                atom =  self._globals[name]
            except KeyError:
                try:
                    atom =  builtins[name]
                except KeyError:
                    self.syntax_error("unknown identifier: {0}".format(name))

        if self.tokens.check("("):
            return self.parse_invoke(name, atom)
        else:
            return atom

    def parse_invoke(self, name, atom):
        self.tokens.expect("(")
        parameters = []
        while not self.tokens.check(")"):
            parameters.append(self.parse_expression())
            if self.tokens.check(","):
                self.tokens.expect(",")
            else:
                break
        self.tokens.expect(")")
        try:
            return atom(*parameters)
        except TypeError:
            return self.parse_module(name, atom, parameters)

    def parse_module(self, name, path, parameters):

        #store current parser state
        stored__globals = self._globals
        stored_locals = self._locals
        stored_tokens = self.tokens

        string = open(path, 'r').read()
        self.tokens = tokenize.Tokenize(string)
        self.tokens.expect("input")
        parameter_names = []
        self.tokens.expect("(")
        while not self.tokens.check(")"):
            parameter_names.append(self.tokens.pop())
            if self.tokens.check(","):
                self.tokens.pop()
            else:
                break
        self.tokens.expect(")")
        self.tokens.expect("#end of line")

        if len(parameter_names) != len(parameters):
            self.syntax_error("{0} expects {1} parameters, {2} given".format(
                name,
                len(parameter_names),
                len(parameters)
            ))

        self._globals = dict(zip(parameter_names, parameters))
        self._locals = {}

        while not self.tokens.check("output"):
            self.parse_module_statement()
        self.tokens.expect("output")
        expression = self.parse_expression()
        self.tokens.expect("#end of line")

        #restore current parser state
        self._globals = stored__globals
        self._locals = stored_locals
        self.tokens = stored_tokens

        return expression

    def is_sink(self, expression):
        if hasattr(expression, "get"): return False
        if hasattr(expression, "is_process"): return False
        if not hasattr(expression, "set_chip"): return False
        return True
