"""
Stack and Register Usage
========================

A stack is implemented in memory. The start, and end of the current stack frame
are held in general purpose registers reserved for this purpose. Local
variables are stored at the beginning of the stack frame, at a known offset
from the start of the frame. The absolute address of a variable is calculated
by adding the known stack offset, to the value of the start register. It is
neccassary to calculate the address at run time, because the start of the frame
in any particular function invokation is not know at compile time. During
function execution, the stack is expanded to calculate intermediate values when
evaluating expressions. After an expression is evaluated, the value of the
expression is held at the top of the stack, pointed to by the end register.

Calling Conventions
===================

Functions are called using the "jump and link" instruction. The jump and link
instruction saves the return address in a general purpose register, by
convention, the return_address register is always used. A function returns
using the "goto register" instruction. It is the reponsibility of the function
caller to save the return_address and start registers using the stack. The
caller uses the new register to mark the start of the new frame. Arguments are
then evaluated, allowing variables addresses to be calculated using the
unmodified start value. Once arguments have been place on the stack, the start
register is then set to point to the start of the new frame. Execution then
passes to the callee function. The callee function can access the arguments by
calculating their offset from the start of the frame in the same way as local
variables.  The callee can return a value using the return_value register. When
execution of the callee function completes, control then returns to the caller
function. The caller then removes all items from the stack by setting the end
register to the value of the start register. The start and return_address are
then popped from the stack, therby resoring the state prior to the function
call. The return_value register is then be placed on top of the stack.

"""

from exceptions import CConstantError, CTypeError, CSyntaxError
from common import c_style_division, c_style_modulo, value, constant_fold

# registers 0-23 are general purpose
maxgpr = 23

#registers 24-31 are defined as follows
start = 24
end = 25
offset = 26
new = 27
temp = 28
temp1 = 29
return_value = 30
return_address = 31

sizes = {"int" : 4, "float" : 4, "int*": 4, "float*":4}

binary_operations = {
    "int" : {
            "+" : "add", 
            "-" : "sub", 
            "*" : "mul", 
            "/" : "div", 
            "%" : "mod",
            "<<" : "lshift", 
            ">>" : "rshift", 
            "&" : "and", 
            "|" : "or", 
            "^" : "xor",  
            "==" : "eq", 
            "!=" : "ne", 
            "<=" : "le", 
            ">=" : "ge", 
            "<" : "lt", 
            ">" : "gt",
    }, "float" : {
            "+" : "fpadd", 
            "-" : "fpsub", 
            "*" : "fpmul", 
            "/" : "fpdiv", 
            "==" : "fpeq", 
            "!=" : "fpne", 
            "<=" : "fple", 
            ">=" : "fpge", 
            "<" : "fplt",
            ">" : "fpgt",
    }, "int*" : {
            "+" : "add", 
            "-" : "sub", 
            "==" : "eq", 
            "!=" : "ne", 
            "<=" : "le",
            ">=" : "ge", 
            "<" : "lt",
            ">" : "gt",
    }, "float*" : {
            "+" : "add", 
            "-" : "sub", 
            "==" : "eq", 
            "!=" : "ne", 
            "<=" : "le",
            ">=" : "ge", 
            "<" : "lt", 
            ">" : "gt",
    },
}
unary_operations = {
    "!" : "not", 
    "~" : "invert", 
    "-" : "negate"}


class CodeGenerator:

    def generate_code(self, leaf):
        global gpr
        stored_gpr = gpr
        #attempt to generate code in registers
        if hasattr(leaf, "generate_code_reg"):
            try:
                #generate in registers
                instructions = leaf.generate_code_reg(self)
                decrement_gpr()
                #then move to the stack
                instructions.append(("store", 0, end, gpr))
                instructions.append(("addl", end, end, 1))
                return instructions
            except GPRException:
                gpr = stored_gpr
        #if this fails for some reason use the stack
        return leaf.generate_code(self)

    def generate_code_reg(self, leaf):
        if hasattr(leaf, "generate_code_reg"):
            return leaf.generate_code_reg(self)
        else:
            raise GPRException

    def compilation_unit_generate_code(self, leaf):
        instructions = [
            ("literal", end, 0, leaf.start_address),
            ("literal", start, 0, leaf.start_address),
            ("jump and link", return_address, 0, leaf.main),
            ("label", "end", 0, 0),
            ("goto", 0, 0, "end"),
        ]
        for declaration in leaf.declarations:
            instructions.extend(declaration.generate_code(self))

        return instructions

    def string_generate_code(self, leaf):
	instructions = [
	    ("literal", offset, 0, leaf.reserved),
            ("store", 0, end, offset),
            ("addl", end, end, 1),
	]

	for char in leaf.constant:
            instructions.extend([
                ("literal", temp, 0, ord(char)),
                ("store", 0, offset, temp),
	        ("addl", offset, offset, 1),
            ])

        return instructions

    def constant_generate_code(self, leaf):
        return [
            ("literal", temp, 0, leaf.constant),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ]

    def constant_generate_code_reg(self, leaf):
        instructions = [("literal", get_gpr(), 0, leaf.constant)]
        increment_gpr()
        return instructions

    def variable_generate_code(self, leaf):
        return [
            #load
            ("addl", offset, start, leaf.declarator.offset),
            ("load", temp, offset, 0),
            #push
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ]

    def variable_generate_code_reg(self, leaf):
        instructions = [
            ("addl", offset, start, leaf.declarator.offset),
            ("load", get_gpr(), offset, 0),
        ]
        increment_gpr()
        return instructions

    def variable_generate_code_write(self, leaf):
        return [
            #pop
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            #push
            ("addl", end, end, 1),
            #store
            ("addl", offset, start, leaf.declarator.offset),
            ("store", 0, offset, temp)
        ]

    def variable_generate_code_address(self, leaf):
        return [
            ("addl", temp, start, leaf.declarator.offset),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ]

    def declare_generate_code(self, leaf):
        instructions = []
        for declarator in leaf.declarators:
            instructions.extend(declarator.generate_code(self))
        return instructions

    def declarator_generate_code(self, leaf):
        global gpr
        instructions = [("addl", end, end, sizes[leaf._type]//4)]
        if leaf.expression:
            stored_gpr = gpr
            try:
                instructions.extend(self.generate_code_reg(leaf.expression))
                decrement_gpr()
                instructions.append(("addl", offset, start, leaf.offset))
                instructions.append(("store", 0, offset, gpr))
            except GPRException:
                gpr = stored_gpr
                instructions.extend(self.generate_code(leaf.expression))
                instructions.append(("addl", end, end, -1))
                instructions.append(("load", temp, end, 0))
                instructions.append(("addl", offset, start, leaf.offset))
                instructions.append(("store", 0, offset, temp))
        return instructions

    def declare_function_generate_code(self, leaf):
        instructions = [("label", str(id(leaf)), 0, 0)] 
        instructions.extend(leaf.statement.generate_code(self))
        instructions.append(("goto register", 0, return_address, 0))
        return instructions

    def if_generate_code(self, leaf):
        try:
            if value(leaf.expression == 0):
                if leaf.false:
                    return self.generate_code(leaf.false)
                else:
                    return []
            else:
                return self.generate_code(leaf.true)
        except CConstantError:
            instructions = self.generate_code(leaf.expression)
            instructions.extend([
                ("addl", end, end, -1),
                ("load", temp, end, 0),
                ("jump if false", 0, temp, str(id(leaf)))
            ])
            instructions.extend(leaf.true.generate_code(self))
            instructions.append(("goto", 0, 0, str(id(leaf))+"end"))
            instructions.append(("label", str(id(leaf)), 0, 0))
            if leaf.false:
                instructions.extend(leaf.false.generate_code(self))
            instructions.append(("label", str(id(leaf))+"end", 0, 0))
            return instructions

    def switch_generate_code(self, leaf):
        instructions = self.generate_code(leaf.expression)
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
        ])
        for case_value, case in leaf.cases.iteritems():
            instructions.extend([
                ("literal", temp1, 0, case_value),
                ("ne", temp1, temp, temp1),
                ("jump if false", 0, temp1, str(id(case)))
            ])
        if hasattr(leaf, "default"):
            instructions.extend([("goto", 0, 0, str(id(leaf.default)))])
        instructions.extend([("goto", 0, 0, str(id(leaf))+"end")])
        instructions.extend(leaf.statement.generate_code(self))
        instructions.extend([("label", str(id(leaf)) + "end", 0, 0)])
        return instructions

    def case_generate_code(self, leaf):
        return [("label", str(id(leaf)), 0, 0)]

    def default_generate_code(self, leaf):
        return [("label", str(id(leaf)), 0, 0)]

    def label_generate_code(self, leaf):
        return [("label", str(id(leaf)), 0, 0)]

    def goto_generate_code(self, leaf):
        try:
            label = leaf.function.labels[leaf.label]
        except KeyError:
            raise CSyntaxError("Unknown Label")
            
        return [("goto", 0, 0, label)]

    def while_generate_code(self, leaf):
        try:
            if value(leaf.expression):
                instructions = [("label", str(id(leaf))+"start", 0, 0)]
                instructions.extend(leaf.statement.generate_code(self))
                instructions.append(("goto", 0, 0, str(id(leaf)) + "start"))
                instructions.append(("label", str(id(leaf))+"end", 0, 0))
            else:
                instructions = [("label", str(id(leaf))+"start", 0, 0)]
                instructions.append(("label", str(id(leaf))+"end", 0, 0))
        except CConstantError:
            instructions = [("label", str(id(leaf))+"start", 0, 0)]
            instructions.extend(self.generate_code(leaf.expression))
            instructions.extend([
                ("addl", end, end, -1),
                ("load", temp, end, 0),
                ("jump if false", 0, temp, str(id(leaf)) + "end")
            ])
            instructions.extend(leaf.statement.generate_code(self))
            instructions.extend([
                ("goto", 0, 0, str(id(leaf)) + "start"),
                ("label", str(id(leaf)) + "end", 0, 0)
            ])
        return instructions

    def do_while_generate_code(self, leaf):
        try:
            if value(expression.generate_code(self)):
                instructions = [("label", str(id(leaf))+"start", 0, 0)]
                instructions.extend(leaf.statement.generate_code(self))
                instructions.append(("goto", 0, 0, str(id(leaf)) + "start"))
                instructions.append(("label", str(id(leaf))+"end", 0, 0))
            else:
                instructions = [("label", str(id(leaf))+"start", 0, 0)]
                instructions.extend(leaf.statement.generate_code(self))
                instructions.append(("label", str(id(leaf))+"end", 0, 0))
        except CConstantError:
            instructions = [("label", str(id(leaf))+"start", 0, 0)]
            instructions.extend(leaf.statement.generate_code(self))
            instructions.extend(self.generate_code(leaf.expression))
            instructions.extend([
                ("addl", end, end, -1),
                ("load", temp, end, 0),
                ("jump if false", 0, temp, str(id(leaf)) + "end")
                ("goto", 0, 0, str(id(leaf)) + "start"),
                ("label", str(id(leaf))+"end", 0, 0)
            ])

    def return_generate_code(self, leaf):
        instructions = self.generate_code(leaf.expression)
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", return_value, end, 0))
        instructions.append(("goto register", 0, return_address, 0))
        return instructions

    def function_call_generate_code(self, leaf):
        instructions = [
          ("store", 0, end, start),
          ("addl", end, end, 1),
          ("store", 0, end, return_address),
          ("addl", end, end, 1),
          ("addl", new, end, 0),
        ]
        for arg in leaf.args:
            instructions.extend(self.generate_code(arg))
        instructions.extend([
          ("addl", start, new, 0),
          ("jump and link", return_address, 0, str(id(leaf.declaration))),
          ("addl", end, start, 0),
          ("addl", end, end, -1),
          ("load", return_address, end, 0),
          ("addl", end, end, -1),
          ("load", start, end, 0),
          ("store", 0, end, return_value),
          ("addl", end, end, 1),
        ])
        return instructions

    def convert_generate_code(self, leaf):
        instructions = self.generate_code(leaf.expression)
        if leaf._type_ != leaf.expression._type():
            instructions.append(("addl", end, end, -1))
            instructions.append(("load", temp, end, 0))
            instructions.append(("to_"+leaf._type_, 0, end, temp))
            instructions.append(("store", 0, end, temp))
            instructions.append(("addl", end, end, 1))
        return instructions

    def convert_generate_code_reg(self, leaf):
        instructions = self.generate_code_reg(leaf.expression)
        if leaf._type_ != leaf.expression._type():
            instructions.append(("to_"+leaf._type_, 0, gpr, gpr))
        return instructions

    def ternary_generate_code(self, leaf):
        try:
            if value(leaf.expression):
                return self.generate_code(leaf.true_expression)
            else:
                return self.generate_code(leaf.false_expression)
        except CConstantError:
            instructions = self.generate_code(leaf.expression)
            instructions.append(("addl", end, end, -1))
            instructions.append(("load", temp, end, 0))
            instructions.append(("jump if false", 0, temp, str(id(leaf))+"false"))
            instructions.extend(leaf.true_expression.generate_code(self))
            instructions.append(("goto", 0, 0, str(id(leaf))+"end"))
            instructions.append(("label", str(id(leaf))+"false", 0, 0))
            instructions.extend(leaf.false_expression.generate_code(self))
            instructions.append(("label", str(id(leaf))+"end", 0, 0))
            return instructions

    def binary_generate_code_reg(self, leaf):
        operation = binary_operations[leaf._type()][leaf.function]
        instructions = self.generate_code_reg(leaf.left)
        instructions.extend(self.generate_code_reg(leaf.right))
        decrement_gpr()
        instructions.append((operation, gpr-1, gpr-1, gpr))
        return instructions

    def binary_generate_code(self, leaf):
        operation = binary_operations[leaf._type()][leaf.function]
        instructions = leaf.left.generate_code(self)
        instructions.extend(leaf.right.generate_code(self))
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", temp, end, 0))
        instructions.append(("addl", end, end, -1))
        instructions.append(("load", temp1, end, 0))
        instructions.append((operation, temp, temp1, temp))
        instructions.append(("store", 0, end, temp))
        instructions.append(("addl", end, end, 1))
        return instructions

    def unary_generate_code(self, leaf):
        instructions = self.generate_code(leaf.expression)
        if leaf.function != "+":
            instructions.extend([
                ("addl", end, end, -1),
                ("load", temp, end, 0),
                (unary_operations[leaf.function], temp, end, 0),
                ("store", end, temp, 0),
                ("addl", end, end, 1),
            ])
        return instructions

    def post_increment_generate_code(self, leaf):
        instructions = self.generate_code(leaf.expression)
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
            ("addl", temp, temp, 1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(leaf.expression.generate_code_write(self))
        instructions.append(("addl", end, end, -1))
        return instructions

    def post_decrement_generate_code(self, leaf):
        instructions = self.generate_code(leaf.expression)
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
            ("addl", temp, temp, -1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(leaf.expression.generate_code_write(self))
        instructions.append(("addl", end, end, -1))
        return instructions

    def pre_increment_generate_code(self, leaf):
        instructions = leaf.expression.generate_code(self)
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("addl", temp, temp, 1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(leaf.expression.generate_code_write(self))
        return instructions

    def pre_decrement_generate_code(self, leaf):
        instructions = leaf.expression.generate_code(self)
        instructions.extend([
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            ("addl", temp, temp, -1),
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        instructions.extend(leaf.expression.generate_code_write(self))
        return instructions

    def block_generate_code(self, leaf):
        instructions = []
        for declaration in leaf.declarations:
            instructions.extend(declaration.generate_code(self))
        for statement in leaf.statements:
            instructions.extend(statement.generate_code(self))
        return instructions

    def break_generate_code(self, leaf):
        return [("goto", 0, 0, str(id(leaf.surrounding_statement))+"end")]

    def continue_generate_code(self, leaf):
        return [("goto", 0, 0, str(id(leaf.surrounding_statement))+"start")]

    def discard_generate_code(self, leaf):
        instructions = leaf.expression.generate_code(self)
        instructions.append(("addl", end, end, -1))
        return instructions

    def compound_expression_generate_code(self, leaf):
        instructions = leaf.right.generate_code(self)
        instructions.append(("addl", end, end, -1))
        instructions = leaf.left.generate_code(self)
        return instructions

    def assignment_generate_code(self, leaf):
        instructions = self.generate_code(leaf.right)
        instructions.extend(leaf.left.generate_code_write(self))
        return instructions

    def sizeof_generate_code(self, leaf):
        return leaf.expression.generate_code(self)


    def address_generate_code(self, leaf):
        return leaf.expression.generate_code_address(self)

    def dereference_generate_code(self, leaf):
        instructions = leaf.expression.generate_code(self)
        instructions.extend([
            #pop
            ("addl", end, end, -1),
            ("load", offset, end, 0),
            #load
            ("load", temp, offset, 0),
            #push
            ("store", 0, end, temp),
            ("addl", end, end, 1),
        ])
        return instructions

    def dereference_generate_code_write(self, leaf):
        instructions = leaf.expression.generate_code(self)
        instructions.extend([
            #pop
            ("addl", end, end, -1),
            ("load", offset, end, 0),
            #pop
            ("addl", end, end, -1),
            ("load", temp, end, 0),
            #push
            ("addl", end, end, 1),
            #store
            ("store", 0, offset, temp)
        ])
        return instructions

    def dereference_generate_code_address(self, leaf):
        return [
            ("addl", temp, start, leaf.declarator.offset),
            #push
            ("store", 0, end, temp)
            ("addl", end, end, 1),
        ]

class GPRException(Exception):
    pass

gpr = 0

def get_gpr():
    global gpr
    return gpr

def increment_gpr():
    global gpr
    if gpr < maxgpr:
        gpr += 1;
    else:
        raise GPRException

def decrement_gpr():
    global gpr
    if gpr > 0:
        gpr -= 1;
    else:
        raise GPRException


def size(expression):
    return sizes[expression._type()]
