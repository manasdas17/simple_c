import chips
from tokenize import tokenize, check_token, expect_token

sinks = {
    "port" : chips.OutPort,
    "console" : chips.Console,
    "serial" : chips.SerialOut,
    "assert" : chips.Asserter,
}

sink_usage = {
    "port"    : "output <stream> : port <name>",
    "console" : "output <stream> : console",
    "serial"  : "output <stream> : serial [<name> [, <clock rate> [, <baud rate>]]])",
    "assert"  : "output <stream> : assert",
}

builtins = {
    "serial" : chips.SerialIn,
    "port" : chips.InPort,
}

usage = {
    "port" : "port(<name>, <bits>)",
}


class Parser:

    def parse(self, string):
        self.streams = {}
        self._locals = {}
        self.sinks = {}
        self.tokens = tokenize(string)
        print self.tokens

        while self.tokens:
            if check_token(self.tokens, "process"):
                self.parse_process()
            elif check_token(self.tokens, "output"):
                self.parse_sink()
            else:
                self.parse_connection()

        return chips.Chip(*self.sinks.values())

    def parse_sink(self):
        expect_token(self.tokens, "output")
        stream = self.parse_expression()
        expect_token(self.tokens, ":")
        sink = self.tokens.pop(0)
        parameters = [stream]
        while True:
            parameters.append(self.parse_expression())
            if check_token(self.tokens, ","):
                expect_token(self.tokens, ",")
            else:
                break
        expect_token(self.tokens, "end of line")
        try:
            self.sinks[sink] = sinks[sink](*parameters)
        except TypeError:
            print "Incorrect use of", sink
            print "Usage: ", sink_usage[sink]
        except KeyError:
            print "unknown output type", sink

    def parse_connection(self):
        target_name = self.tokens.pop(0)
        expect_token(self.tokens, "<=")
        expression = self.parse_expression()
        expect_token(self.tokens, "end of line")
        self.streams[target_name] = expression

    def parse_process(self):
        self._locals = {}
        self.process_bits = 0

        expect_token(self.tokens, "process")
        expect_token(self.tokens, ":")
        expect_token(self.tokens, "end of line")
        expect_token(self.tokens, "indent")
        statements = []
        while not check_token(self.tokens, "dedent"):
            statements.append(self.parse_statement())
        expect_token(self.tokens, "dedent")
        chips.Process(32, *statements)

    def parse_statement(self):
        if check_token(self.tokens, "if"):
            return self.parse_if()
        elif check_token(self.tokens, "loop"):
            return self.parse_loop()
        elif check_token(self.tokens, "while"):
            return self.parse_while()
        elif check_token(self.tokens, "until"):
            return self.parse_until()
        elif check_token(self.tokens, "pass"):
            return self.parse_pass()
        elif check_token(self.tokens, "break"):
            return self.parse_break()
        elif check_token(self.tokens, "continue"):
            return self.parse_continue()
        elif check_token(self.tokens, "waitus"):
            return self.parse_waitus()
        elif check_token(self.tokens, "read"):
            return self.parse_read()
        elif check_token(self.tokens, "write"):
            return self.parse_write()
        elif check_token(self.tokens, "print"):
            return self.parse_print()
        elif self.tokens[0][0].isalpha():
            return self.parse_assignment()
        else:
            print self.tokens

    def parse_pass(self):
        expect_token(self.tokens, "pass")
        expect_token(self.tokens, "end of line")

    def parse_break(self):
        expect_token(self.tokens, "break")
        expect_token(self.tokens, "end of line")
        return chips.Break()

    def parse_continue(self):
        expect_token(self.tokens, "continue")
        expect_token(self.tokens, "end of line")
        return chips.Continue()

    def parse_waitus(self):
        expect_token(self.tokens, "waitus")
        expect_token(self.tokens, "end of line")
        return chips.WaitUs()

    def parse_read(self):
        expect_token(self.tokens, "read")
        in_ = self.tokens.pop(0)
        var = self.tokens.pop(0)
        if var not in self._locals:
            self._locals[var] = Variable(0)
        if _in not in self.streams:
            print "unknown stream", _in
        expect_token(self.tokens, "end of line")
        self.tagets[_in] = self.streams[_in]
        return self.streams[_in]

    def parse_write(self):
        expect_token(self.tokens, "write")
        out_ = self.tokens.pop(0)
        expression = self.parse_expression()
        expect_token(self.tokens, "end of line")
        if _out not in self.streams:
            self.streams[_out] = chips.Output()
        return self.streams[out_].write(expression)

    def parse_print(self):
        expect_token(self.tokens, "print")
        out_ = self.tokens.pop(0)
        expression = self.parse_expression()
        expect_token(self.tokens, "end of line")
        return chips.Print(outputs[out_], expression)

    def parse_if(self):

        #if statement
        expect_token(self.tokens, "if")
        expression = self.parse_expression()
        expect_token(self.tokens, ":")
        expect_token(self.tokens, "end of line")
        expect_token(self.tokens, "indent")
        statements = [self.parse_statement()]
        while not check_token(self.tokens, "dedent"):
            statements.append(self.parse_statement())
        expect_token(self.tokens, "dedent")
        statement = chips.If(expression, *statements)

        #elif statement
        while check_token(self.tokens, "elif"):
            expect_token(self.tokens, "elif")
            expression = self.parse_expression()
            expect_token(self.tokens, ":")
            expect_token(self.tokens, "end of line")
            expect_token(self.tokens, "indent")
            statements = [self.parse_statement()]
            while not check_token(self.tokens, "dedent"):
                statements.append(self.parse_statement())
            expect_token(self.tokens, "dedent")
            statement = statement.Elif(expression, *statements)

        #else statement
        if check_token(self.tokens, "else"):
            expect_token(self.tokens, "else")
            expect_token(self.tokens, ":")
            expect_token(self.tokens, "end of line")
            expect_token(self.tokens, "indent")
            statements = [self.parse_statement()]
            while not check_token(self.tokens, "dedent"):
                statements.append(self.parse_statement())
            expect_token(self.tokens, "dedent")
            statement = statement.Else(*statements)

        return statement

    def parse_loop(self):

        #loop statement
        expect_token(self.tokens, "loop")
        expect_token(self.tokens, ":")
        expect_token(self.tokens, "end of line")
        expect_token(self.tokens, "indent")
        statements = [self.parse_statement()]
        while not check_token(self.tokens, "dedent"):
            statements.append(self.parse_statement())
        expect_token(self.tokens, "dedent")
        statement = chips.Loop(*statements)
        return statement

    def parse_while(self):

        #while statement
        expect_token(self.tokens, "while")
        expression = self.parse_expression()
        expect_token(self.tokens, ":")
        expect_token(self.tokens, "end of line")
        expect_token(self.tokens, "indent")
        statements = [self.parse_statement()]
        while not check_token(self.tokens, "dedent"):
            statements.append(self.parse_statement())
        expect_token(self.tokens, "dedent")
        statement = chips.While(expression, *statements)
        return statement

    def parse_until(self):

        #until statement
        expect_token(self.tokens, "until")
        expression = self.parse_expression()
        expect_token(self.tokens, ":")
        expect_token(self.tokens, "end of line")
        expect_token(self.tokens, "indent")
        statements = [self.parse_statement()]
        while not check_token(self.tokens, "dedent"):
            statements.append(self.parse_statement())
        expect_token(self.tokens, "dedent")
        statement = chips.Until(expression, *statements)
        return statement

    def parse_assignment(self):

        variable = self.tokens.pop(0)
        expect_token(self.tokens, "=")
        expression = self.parse_expression()
        expect_token(self.tokens, "end of line")
        if variable not in self._locals:
            self._locals[variable] = Variable(0)
        return self._locals[variable].set(expression)

    def parse_expression(self):

        if check_token(self.tokens, "not"):
            self.tokens.pop(0)
            return chips.Not(self.parse_comparison())
        else:
            return self.parse_comparison()

    def parse_comparison(self):

        expression = self.parse_or_expression()
        if check_token(self.tokens, ">"):
            self.tokens.pop(0)
            return expression > self.parse_or_expression()
        elif check_token(self.tokens, "<"):
            self.tokens.pop(0)
            return expression < self.parse_or_expression()
        elif check_token(self.tokens, "<="):
            self.tokens.pop(0)
            return expression <= self.parse_or_expression()
        elif check_token(self.tokens, ">="):
            self.tokens.pop(0)
            return expression >= self.parse_or_expression()
        elif check_token(self.tokens, "=="):
            self.tokens.pop(0)
            return expression == self.parse_or_expression()
        elif check_token(self.tokens, "!="):
            self.tokens.pop(0)
            return expression != self.parse_or_expression()
        else:
            return expression

    def parse_or_expression(self):

        expression = self.parse_xor_expression()
        if check_token(self.tokens, "|"):
            self.tokens.pop(0)
            return expression | self.parse_xor_expression()
        else:
            return expression

    def parse_xor_expression(self):

        expression = self.parse_and_expression()
        if check_token(self.tokens, "^"):
            self.tokens.pop(0)
            return expression ^ self.parse_and_expression()
        else:
            return expression

    def parse_and_expression(self):

        expression = self.parse_shift_expression()
        if check_token(self.tokens, "&"):
            self.tokens.pop(0)
            return expression & self.parse_shift_expression()
        else:
            return expression

    def parse_shift_expression(self):

        expression = self.parse_arithmetic_expression()
        if check_token(self.tokens, "<<"):
            self.tokens.pop(0)
            return expression << self.parse_arithmetic_expression()
        elif check_token(self.tokens, ">>"):
            self.tokens.pop(0)
            return expression >> self.parse_arithmetic_expression()
        else:
            return expression

    def parse_arithmetic_expression(self):

        expression = self.parse_mult_expression()
        if check_token(self.tokens, "+"):
            self.tokens.pop(0)
            return expression + self.parse_mult_expression()
        elif check_token(self.tokens, "-"):
            self.tokens.pop(0)
            return expression - self.parse_mult_expression()
        else:
            return expression

    def parse_mult_expression(self):

        expression = self.parse_unary_expression()
        if check_token(self.tokens, "*"):
            self.tokens.pop(0)
            return expression * self.parse_unary_expression()
        elif check_token(self.tokens, "//"):
            self.tokens.pop(0)
            return expression // self.parse_unary_expression()
        else:
            return expression

    def parse_unary_expression(self):

        if check_token(self.tokens, "-"):
            self.tokens.pop(0)
            return 0 - self.parse_paren_expression()
        elif check_token(self.tokens, "+"):
            self.tokens.pop(0)
            return 0 + self.parse_paren_expression()
        elif check_token(self.tokens, "~"):
            self.tokens.pop(0)
            return ~self.parse_paren_expression()
        else:
            return self.parse_paren_expression()

    def parse_paren_expression(self):

        if check_token(self.tokens, "("):
            expect_token(self.tokens, "(")
            expression = self.parse_expression()
            expect_token(self.tokens, ")")
            return expression
        else:
            return self.parse_numvar()

    def parse_numvar(self):

        if self.tokens[0][0].isdigit():
            return self.parse_number()
        elif self.tokens[0][0] in ("'", '"'):
            return self.parse_string()
        elif self.tokens[0][0].isalpha():
            return self.parse_identifier()

    def parse_number(self):

        number =  self.tokens.pop(0) 
        if "." in number:
            return float(number)
        else:
            return int(number)

    def parse_string(self):

        return self.tokens.pop(0)[1:] #strip quote

    def parse_identifier(self):

        name = self.tokens.pop(0)
        try:
            atom = self._locals[name]
        except KeyError:
            try:
                atom =  self.streams[name]
            except KeyError:
                try:
                    atom =  builtins[name]
                except KeyError:
                    print "unknown identifier", name

        if check_token(self.tokens, "("):
            return self.parse_invoke(name, atom)
        else:
            return atom

    def parse_invoke(self, name, atom):
        expect_token(self.tokens, "(")
        parameters = []
        while not check_token(self.tokens, ")"):
            parameters.append(self.parse_expression())
            if check_token(self.tokens, ","):
                expect_token(self.tokens, ",")
            else:
                break
        expect_token(self.tokens, ")")
        try:
            return atom(*parameters)
        except TypeError:
            print "Incorrect use of", name 
            if name in usage:
                print "Usage: ", usage[name]

