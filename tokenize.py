operators = [",", "=", "==", "<", ">", ">=", "<=", "<<", ">>", "(", ")", "+", "-", "*", "//", "~", "&", "|", "^", ":"]

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

        #string
        elif token.startswith("'"):
            if char != "'":
                token += char
            else:
                tokens.append(token) #strip front quote
                token = ""

        #string
        elif token.startswith('"'):
            if char != '"':
                token += char
            else:
                tokens.append(token) #strip front quote
                token = ""

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
                #tokens.append(token)
                token = ""

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
