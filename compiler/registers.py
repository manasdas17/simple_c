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
