
def optimize(instructions):
    instructions = dict(enumerate(instructions))
    new_instructions = []
    index = 0
    while index < len(instructions):
        op, dest, srca, srcb = instructions[index]
        next_op, next_dest, next_srca, next_srcb = (
                instructions.get(index + 1, (None, None, None, None))
        )
        if (op == next_op == "addl" and 
            dest == next_dest and
            srca == next_srca and
            (srcb + next_srcb) == 0):
            index += 2
        else:
            new_instructions.append(instructions[index])
            index += 1
    return new_instructions
