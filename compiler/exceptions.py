class CConstantError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message) 

class CTypeError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message) 

class CSyntaxError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message) 
