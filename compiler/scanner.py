operators = [",", ".","=", "<<", ">>", "==", "<", ">", ">=", "<=", "(", ")", "{", "}", "+", "-", "*", "/", "//", "~", "&", "|", "^", ";", "&&", "||"]

class Tokenize:
    def __init__(self, string):
        token = ""
        tokens = []
        lineno = 1
        charno = 1

        for line in string.splitlines():
            for char in line + " ":
                if not token:
                    token = char

                #comment
                elif (token + char).startswith("/*"):
                    if (token + char).endswith("*/"):
                        token = ""
                    else:
                        token += char

                #white space
                elif token.isspace():
                    if char.isspace():
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
                elif token.startswith('"'):
                    if char != '"' or (token.endswith("\\") and not token.endswith("\\\\")):
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


                charno += 1
            lineno += 1
            charno = 1

        for token, line, char in tokens:
            print token, "line", line, ",", char

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
