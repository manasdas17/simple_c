operators = ["=>", ",", ".","=", "==", "<", ">", ">=", "<=", "(", ")", "+", "-", "*", "/", "//", "~", "&", "|", "^", ":"]

class Tokenize:
    def __init__(self, string):
        token = ""
        tokens = []
        indentation_level_stack = [1]
        lineno = 1
        charno = 1

        for char in string:
            if not token:
                token = char

            elif token.startswith("\n"):
                if char == "\n":
                    token = char
                    lineno += 1
                    charno = 1
                elif char.isspace() and char != "\n":
                    token += char
                else:
                    #count indentation
                    if token.startswith("\n") or token.startswith("\r"):
                        tokens.append(("#end of line", lineno, charno))
                        indentation_level = len(token.expandtabs())
                        lineno += 1
                        charno = 1
                        if indentation_level > indentation_level_stack[-1]:
                            tokens.append(("#indent", lineno, charno))
                            indentation_level_stack.append(indentation_level)
                        elif indentation_level < indentation_level_stack[-1]:
                            while indentation_level < indentation_level_stack[-1]:
                                indentation_level_stack.pop()
                                tokens.append(("#dedent", lineno, charno))
                    token = char
                

            #white space
            elif token.isspace():
                if char.isspace() and char != "\n":
                    token += char
                else:
                    token = char

            #identifier
            elif token[0].isalpha():
                if char.isalnum() or char == "_":
                    token += char
                else:
                    tokens.append((token, lineno, charno))
                    token = char

            #number
            elif token[0].isdigit():
                if char.isdigit() or char in [".", "x", "X"]:
                    token += char
                else:
                    tokens.append((token, lineno, charno))
                    token = char

            #string
            elif token.startswith("'"):
                if char != "'":
                    token += char
                else:
                    tokens.append((token, lineno, charno))
                    token = ""

            #string
            elif token.startswith('"'):
                if char != '"':
                    token += char
                else:
                    tokens.append((token, lineno, charno))
                    token = ""

            #operator
            elif token in operators:
                if token + char in operators:
                    token += char
                else:
                    tokens.append((token, lineno, charno))
                    token = char

            #comment
            elif token[0] == "#":
                if char not in ["\n", "\r\n" "\r"]:
                    token += char
                else:
                    #tokens.append(token)
                    token = ""

            charno += 1

        tokens.append(("#end of line", lineno, charno))
        for i in indentation_level_stack:
            if i > 1:
                tokens.append(("#dedent", lineno, charno))

        print tokens
        self.tokens = tokens
        self.lineno = 1
        self.charno = 1

    def check(self, token):
        if self.tokens and self.tokens[0][0] == token:
            return True
        else:
            return False

    def check_next(self, token):
        if len(self.tokens) > 1 and self.tokens[1][0] == token:
            return True
        else:
            return False

    def expect(self, token):
        if self.tokens:
            if self.tokens[0][0] == token:
                value, self.lineno, self.charno = self.tokens.pop(0)
            else:
                print "Error expected:", token, "got:", self.tokens[0][0]
                print "at line", self.lineno, ",", self.charno
                exit(0)
        else:
            print "Error expected:", token
            print "at line", self.lineno, ",", self.charno
            exit(0)

    def pop(self):
        if self.tokens:
            value, self.lineno, self.charno = self.tokens.pop(0)
            return value

    def peek(self):
        if self.tokens:
            return self.tokens[0][0]

    def line(self):
        return self.lineno

    def char(self):
        return self.charno

