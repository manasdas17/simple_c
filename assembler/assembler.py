def assemble(instructions):
    address = 0
    labels = {}

    new_instructions = []
    for instruction in instructions:
        operation, dest, srca, srcb = instruction
        if operation == "label":
            labels[dest] = address
        else:
            new_instructions.append(instruction)
            address += 1
    
    instructions = new_instructions
    new_instructions = []
    for instruction in instructions:
        operation, dest, srca, srcb = instruction
        if srcb in labels:
            srcb = labels[srcb]
        new_instructions.append((operation, dest, srca, srcb))

    return new_instructions
