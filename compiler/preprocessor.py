def preprocess(text):

    #line splice
    spliced_line = "" 
    new_lines = []
    for line in text.splitlines():
        if line.endswith("\\"):
            spliced_line += line[:-1]
        else:
            spliced_line += line
            new_lines.append(line)
            spliced_line = "" 

    #includes
    lines = new_lines
    new_lines = []
    for line in lines:
        if line.strip().startswith("#"):
            directive = line.strip()
            if directive.startswith("#include"):
                filename = directive.split()[1]
                included_file = open(filename[1:-1])
                new_lines.extend(proprocess(included_file.read())
        else:
            new_lines.append(line)

    return new_lines

