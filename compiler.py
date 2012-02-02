import chips

operators = ["=", "==", "<", ">", ">=", "<=", "<<", ">>", "(", ")", "+", "-", "*", "//", "~", "&", "|", "^", ":"]

def tokenize(string):
    token = ""
    tokens = []
    indentation_level_stack = [1]

    for char in string:
        if not token:
            token = char

        #white space
        elif token.isspace():
            if char.isspace():
                token += char
            else:
                #count indentation
                if token.startswith("\n") or token.startswith("\r"):
                    tokens.append("end of line")
                    indentation_level = len(token.expandtabs())
                    if indentation_level > indentation_level_stack[-1]:
                        tokens.append("indent")
                        indentation_level_stack.append(indentation_level)
                    elif indentation_level < indentation_level_stack[-1]:
                        while indentation_level < indentation_level_stack[-1]:
                            indentation_level_stack.pop()
                            tokens.append("dedent")
                token = char

        #identifier
        elif token[0].isalpha():
            if char.isalnum() or char == "_":
                token += char
            else:
                tokens.append(token)
                token = char

        #number
        elif token[0].isdigit():
            if char.isdigit() or char in [".", "x", "X"]:
                token += char
            else:
                tokens.append(token)
                token = char

        #operator
        elif token in operators:
            if token + char in operators:
                token += char
            else:
                tokens.append(token)
                token = char

        #comment
        elif token[0] == "#":
            if char not in ["\n", "\r\n" "\r"]:
                token += char
            else:
                tokens.append(token)
                token = char

    tokens.append("end of line")
    for i in indentation_level_stack:
        if i > 1:
            tokens.append("dedent")

    return tokens

def check_token(tokens, token):
    if tokens and tokens[0] == token:
        return True
    else:
        return False

def expect_token(tokens, token):
    if tokens and tokens[0] == token:
        tokens.pop(0)
    else:
        print "Error expected:", token, "got:", tokens[0]
        exit(0)

def parse(string):
    variables = {}
    inputs = {}
    outputs = {}
    process_bits = 0

    def parse_statement(tokens):
        if check_token(tokens, "if"):
            return parse_if(tokens)
        elif check_token(tokens, "loop"):
            return parse_loop(tokens)
        elif check_token(tokens, "while"):
            return parse_while(tokens)
        elif check_token(tokens, "until"):
            return parse_until(tokens)
        elif check_token(tokens, "pass"):
            return parse_pass(tokens)
        elif check_token(tokens, "break"):
            return parse_break(tokens)
        elif check_token(tokens, "continue"):
            return parse_continue(tokens)
        elif check_token(tokens, "waitus"):
            return parse_waitus(tokens)
        elif check_token(tokens, "read"):
            return parse_read(tokens)
        elif check_token(tokens, "write"):
            return parse_write(tokens)
        elif check_token(tokens, "print"):
            return parse_print(tokens)
        elif check_token(tokens, "variable"):
            return parse_variable_declare(tokens)
        elif check_token(tokens, "input"):
            return parse_input_declare(tokens)
        elif check_token(tokens, "output"):
            return parse_output_declare(tokens)
        elif tokens[0][0].isalpha():
            return parse_assignment(tokens)
        else:
            print tokens

    def parse_input_declare(tokens):
        expect_token(tokens, "input")
        input_ = tokens.pop(0)
        expect_token(tokens, ":")
        type_ = tokens.pop(0)
        bits = int(parse_expression(tokens))
        expect_token(tokens, "bits")
        expect_token(tokens, "end of line")

    def parse_output_declare(tokens):
        expect_token(tokens, "output")
        output = tokens.pop(0)
        expect_token(tokens, ":")
        type_ = tokens.pop(0)
        bits = int(parse_expression(tokens))
        expect_token(tokens, "bits")
        expect_token(tokens, "end of line")
        outputs[output] = chips.Output()

    def parse_variable_declare(tokens):
        expect_token(tokens, "variable")
        variable = tokens.pop(0)
        expect_token(tokens, ":")
        type_ = tokens.pop(0)
        bits = int(parse_expression(tokens))
        expect_token(tokens, "bits")
        initial_value = 0
        #if check_token(tokens, "="):
        #    expect_token(tokens, "=")
       #     initial_value = int(parse_expression(tokens))
        expect_token(tokens, "end of line")
        variables[variable] = chips.Variable(initial_value)

    def parse_pass(tokens):
        expect_token(tokens, "pass")
        expect_token(tokens, "end of line")

    def parse_break(tokens):
        expect_token(tokens, "break")
        expect_token(tokens, "end of line")
        return chips.Break()

    def parse_continue(tokens):
        expect_token(tokens, "continue")
        expect_token(tokens, "end of line")
        return chips.Continue()

    def parse_waitus(tokens):
        expect_token(tokens, "waitus")
        expect_token(tokens, "end of line")
        return chips.WaitUs()

    def parse_read(tokens):
        expect_token(tokens, "read")
        in_ = tokens.pop(0)
        var = tokens.pop(0)
        if var not in variables:
            variable[var] = Variable(0)
        if in_ not in inputs:
            inputs[in_] = chips.Output()
        expect_token(tokens, "end of line")
        try:
            return inputs[in_].read(variables[var])
        except KeyError:
            print "unknown input", in_

    def parse_write(tokens):
        expect_token(tokens, "write")
        out_ = tokens.pop(0)
        expression = parse_expression(tokens)
        expect_token(tokens, "end of line")
        try:
            return outputs[out_].write(expression)
        except KeyError:
            print "unknown output", out_

    def parse_print(tokens):
        expect_token(tokens, "print")
        out_ = tokens.pop(0)
        expression = parse_expression(tokens)
        expect_token(tokens, "end of line")
        return chips.Print(outputs[out_], expression)

    def parse_if(tokens):

        #if statement
        expect_token(tokens, "if")
        expression = parse_expression(tokens)
        expect_token(tokens, ":")
        expect_token(tokens, "end of line")
        expect_token(tokens, "indent")
        statements = [parse_statement(tokens)]
        while not check_token(tokens, "dedent"):
            statements.append(parse_statement(tokens))
        expect_token(tokens, "dedent")
        statement = chips.If(expression, *statements)

        #elif statement
        while check_token(tokens, "elif"):
            expect_token(tokens, "elif")
            expression = parse_expression(tokens)
            expect_token(tokens, ":")
            expect_token(tokens, "end of line")
            expect_token(tokens, "indent")
            statements = [parse_statement(tokens)]
            while not check_token(tokens, "dedent"):
                statements.append(parse_statement(tokens))
            expect_token(tokens, "dedent")
            statement = statement.Elif(expression, *statements)

        #else statement
        if check_token(tokens, "else"):
            expect_token(tokens, "else")
            expect_token(tokens, ":")
            expect_token(tokens, "end of line")
            expect_token(tokens, "indent")
            statements = [parse_statement(tokens)]
            while not check_token(tokens, "dedent"):
                statements.append(parse_statement(tokens))
            expect_token(tokens, "dedent")
            statement = statement.Else(*statements)

        return statement

    def parse_loop(tokens):

        #loop statement
        expect_token(tokens, "loop")
        expect_token(tokens, ":")
        expect_token(tokens, "end of line")
        expect_token(tokens, "indent")
        statements = [parse_statement(tokens)]
        while not check_token(tokens, "dedent"):
            statements.append(parse_statement(tokens))
        expect_token(tokens, "dedent")
        statement = chips.Loop(*statements)
        return statement

    def parse_while(tokens):

        #whil statement
        expect_token(tokens, "while")
        expression = parse_expression(tokens)
        expect_token(tokens, ":")
        expect_token(tokens, "end of line")
        expect_token(tokens, "indent")
        statements = [parse_statement(tokens)]
        while not check_token(tokens, "dedent"):
            statements.append(parse_statement(tokens))
        expect_token(tokens, "dedent")
        statement = chips.While(expression, *statements)
        return statement

    def parse_until(tokens):

        #whil statement
        expect_token(tokens, "until")
        expression = parse_expression(tokens)
        expect_token(tokens, ":")
        expect_token(tokens, "end of line")
        expect_token(tokens, "indent")
        statements = [parse_statement(tokens)]
        while not check_token(tokens, "dedent"):
            statements.append(parse_statement(tokens))
        expect_token(tokens, "dedent")
        statement = chips.Until(expression, *statements)
        return statement

    def parse_assignment(tokens):
        variable = tokens.pop(0)
        expect_token(tokens, "=")
        expression = parse_expression(tokens)
        expect_token(tokens, "end of line")
        return variables[variable].set(expression)

    def parse_expression(tokens):
        if check_token(tokens, "not"):
            tokens.pop(0)
            return chips.Not(parse_comparison(tokens))
        else:
            return parse_comparison(tokens)

    def parse_comparison(tokens):
        expression = parse_or_expression(tokens)
        if check_token(tokens, ">"):
            tokens.pop(0)
            return expression > parse_or_expression(tokens)
        elif check_token(tokens, "<"):
            tokens.pop(0)
            return expression < parse_or_expression(tokens)
        elif check_token(tokens, "<="):
            tokens.pop(0)
            return expression <= parse_or_expression(tokens)
        elif check_token(tokens, ">="):
            tokens.pop(0)
            return expression >= parse_or_expression(tokens)
        elif check_token(tokens, "=="):
            tokens.pop(0)
            return expression == parse_or_expression(tokens)
        elif check_token(tokens, "!="):
            tokens.pop(0)
            return expression != parse_or_expression(tokens)
        else:
            return expression

    def parse_or_expression(tokens):
        expression = parse_xor_expression(tokens)
        if check_token(tokens, "|"):
            tokens.pop(0)
            return expression | parse_xor_expression(tokens)
        else:
            return expression

    def parse_xor_expression(tokens):
        expression = parse_and_expression(tokens)
        if check_token(tokens, "^"):
            tokens.pop(0)
            return expression ^ parse_and_expression(tokens)
        else:
            return expression

    def parse_and_expression(tokens):
        expression = parse_shift_expression(tokens)
        if check_token(tokens, "&"):
            tokens.pop(0)
            return expression & parse_shift_expression(tokens)
        else:
            return expression

    def parse_shift_expression(tokens):
        expression = parse_arithmetic_expression(tokens)
        if check_token(tokens, "<<"):
            tokens.pop(0)
            return expression << parse_arithmetic_expression(tokens)
        elif check_token(tokens, ">>"):
            tokens.pop(0)
            return expression >> parse_arithmetic_expression(tokens)
        else:
            return expression

    def parse_arithmetic_expression(tokens):
        expression = parse_mult_expression(tokens)
        if check_token(tokens, "+"):
            tokens.pop(0)
            return expression + parse_mult_expression(tokens)
        elif check_token(tokens, "-"):
            tokens.pop(0)
            return expression - parse_mult_expression(tokens)
        else:
            return expression

    def parse_mult_expression(tokens):
        expression = parse_unary_expression(tokens)
        if check_token(tokens, "*"):
            tokens.pop(0)
            return expression * parse_unary_expression(tokens)
        elif check_token(tokens, "//"):
            tokens.pop(0)
            return expression // parse_unary_expression(tokens)
        else:
            return expression

    def parse_unary_expression(tokens):
        if check_token(tokens, "-"):
            tokens.pop(0)
            return 0 - parse_paren_expression(tokens)
        elif check_token(tokens, "+"):
            tokens.pop(0)
            return 0 + parse_paren_expression(tokens)
        elif check_token(tokens, "~"):
            tokens.pop(0)
            return ~parse_paren_expression(tokens)
        else:
            return parse_paren_expression(tokens)

    def parse_paren_expression(tokens):
        if check_token(tokens, "("):
            expect_token(tokens, "(")
            expression = parse_expression(tokens)
            expect_token(tokens, ")")
            return expression
        else:
            return parse_numvar(tokens)

    def parse_numvar(tokens):
        if tokens[0][0].isdigit():
            return parse_number(tokens)
        elif tokens[0][0].isalpha():
            return parse_variable(tokens)

    def parse_number(tokens):
        return int(tokens.pop(0))

    def parse_variable(tokens):
        token = tokens.pop(0)
        try:
            return variables[token]
        except KeyError:
            print "unknown variable", token

    tokens = tokenize(string)
    statements = []
    while tokens:
        print tokens
        statement = parse_statement(tokens)
        if statement is not None:
            statements.append(statement)
    return statements
    #return chips.Process(32, *statements)


print parse(
"""variable a : integer 8 bits
variable b : integer 8 bits
input a : integer 8 bits
output b : integer 8 bits
a = 1
b = 1 + 1
read a a
write b b
""")

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    file = open(filenamei, 'r')
    file = file.read()
    print parse(file)
    
