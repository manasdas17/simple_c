operators = [",", ".", "=", "<<", ">>", "==","!=", "<", ">", ">=", "<=", "(",
")", "{", "}", "+", "-", "*", "%", "/", "//", "~", "!", "&", "|", "^", ";",
"&&", "||", "++", "--", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=",
">>=", "[", "]", ":"]

class Tokenize:
    """
    Lexical Scanner

    Breaks source file into tokens a stream of tokens. Tokens can be:

    * number - characters 0-9, x, X or .
    * identifier - characters a-z, 0-9, or _
    * Keywords - characters a-z
    * Operators - +, -, *, /, %, ....
    * Strings - any character enclosed in quotes, \ escapes \\\\ is literal \\
    * Comments - /* followed by any sequence of characters followed by */
    * Blank Space - Any blank space or line end

    The lexical scanner provides functions to consume, and expect tokens in 
    the token stream. The scanner also keeps track of line numbers and 
    characters for use in Error messages. 
    """

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
                    if char.isdigit() or char in [
                            "e", "E", "x", "X", ".", "a", "A", "b", "B", "c", "C", "d", "D", "f", "F"]:
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

                #character
                elif token.startswith("'"):
                    if char != "'" or (token.endswith("\\") and not token.endswith("\\\\")):
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

        #for token, line, char in tokens:
            #print token, "line", line, ",", char

        self.tokens = tokens
        self.lineno = 1
        self.charno = 1

    def check(self, token):

        """Check whether *token* is the next token in the stream"""

        if self.tokens and self.tokens[0][0] == token:
            return True
        else:
            return False

    def check_next(self, token):

        """Check whether *token* is the next but one token in the stream"""

        if len(self.tokens) > 1 and self.tokens[1][0] == token:
            return True
        else:
            return False

    def expect(self, token):

        """Consumes the next oken in the stream, an Error is generated if the
        next token in the stream does not match *token*."""

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

        """Consumes the next token in the stream. The consumed token is 
        returned."""

        if self.tokens:
            value, self.lineno, self.charno = self.tokens.pop(0)
            return value

    def peek(self):

        """Returns the next token in the stream without consuming it."""

        if self.tokens:
            return self.tokens[0][0]

    def line(self):

        """Return the line number of the next token in the stream."""

        return self.lineno

    def char(self):

        """Return the column of the next token in the stream."""

        return self.charno
