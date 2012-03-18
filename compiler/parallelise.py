instructions = [
    (0,6),
    (1,5),
    (2,0),
    (3,1)
]

parallel_instructions = []

def dependent(a, b):
    a_dest, a_src = a
    b_dest, b_src = b
    return a_src == b_dest

while instructions:
    instruction = instructions.pop(0)
 
    frame = [instruction]

    i = 0
    while i < len(instructions):
        promote_i = True

        for j in frame:
            if dependent(instructions[i], j):
                promote_i = False
                break

        for j in instructions[:i]:
            if dependent(instructions[i], j):
                promote_i = False

        if promote_i:
            frame.append(instructions.pop(i))
        else:
            i += 1

    parallel_instructions.append(frame)

for frame in parallel_instructions:
    print frame
