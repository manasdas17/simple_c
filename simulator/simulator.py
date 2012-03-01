from compiler.common import c_style_division, c_style_modulo
from compiler.registers import *

class Simulator:
    def __init__(self, instructions):
        self.instructions = instructions
        self.registers = {}
        self.program_counter = 0
        self.memory = {}

    def execute(self):
        instruction = self.instructions[self.program_counter]
        operation, dest, srca, srcb = instruction

        if operation == "load":
            address = self.registers[srca]
            self.registers[dest] = self.memory[address]
            self.program_counter += 1

        elif operation == "store":
            address = self.registers[srca]
            self.memory[address] = self.registers[srcb]
            self.program_counter += 1

        elif operation in ["add", 'sub', 'mul', 'div', 'mod', 'lt', 'gt', 'lshift', 'rshift', 'le', 'ge', 'and', 'or', 'xor', 'eq', 'ne']:
            functions = {
              "add" : lambda x, y:x+y,
              "sub" : lambda x, y:x-y,
              "mul" : lambda x, y:x*y,
              "div" : c_style_division,
              "mod" : c_style_modulo,
              "lt" : lambda x, y:-1 if x<y else 0,
              "gt" : lambda x, y:-1 if x>y else 0,
              "lshift" : lambda x, y:x<<y,
              "rshift" : lambda x, y:x>>y,
              "le" : lambda x, y:-1 if x<=y else 0,
              "ge" : lambda x, y:-1 if x>=y else 0,
              "and" : lambda x, y:x&y,
              "or" : lambda x, y:x|y,
              "xor" : lambda x, y:x^y,
              "eq" : lambda x, y:-1 if x==y else 0,
              "ne" : lambda x, y:-1 if x!=y else 0,
            }
            self.registers[dest] = functions[operation](
                  self.registers[srca],
                  self.registers[srcb]
            )
            self.program_counter += 1

        elif operation in ["addl"]:
            self.registers[dest] = self.registers[srca] + srcb
            self.program_counter += 1

        elif operation in ["literal"]:
            self.registers[dest] = srcb
            self.program_counter += 1

        elif operation in ["not", 'invert', 'negate']:
            functions = {
              "not" : lambda x: -1 if x == 0 else 0,
              "invert" : lambda x:~x,
              "negate" : lambda x:-x,
            }
            self.registers[dest] = functions[operation](
                 self.registers[srca]
            )
            self.program_counter += 1

        elif operation == "goto":
            self.program_counter = srcb

        elif operation == "jump if false":
            if self.registers[srca] == 0:
                self.program_counter = srcb
            else:
                self.program_counter  += 1

        elif operation == "goto register":
            self.program_counter = self.registers[srca]

        elif operation == "jump and link":
            self.registers[dest] = self.program_counter + 1
            self.program_counter = srcb
        else:
            print "Unknown Instruction", operation

