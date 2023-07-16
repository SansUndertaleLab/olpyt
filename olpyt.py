from ply import lex, yacc

code = ""
with open("code.olpyt", "r") as file:
    code = file.read()

tokens = ("NAME", "STRING", "INT", "FLOAT", "COMMA", "LIB_REF", "LIB_USE", "OPEN_BRAC", "CLOSE_BRAC", "OPEN_PARAN", "CLOSE_PARAN", "FUNC", "VAR_REF", "DIRECTIVE", "ARG")

def t_error(t):
    print("LEXER Error")
    exit()

t_ignore = " \n\t"
t_STRING = r"\"[^\"]*\""
t_ARG = r"\&"
t_FLOAT = r"[0-9]+\.[0-9]+"
t_INT = r"[0-9]+"
def t_NAME(t):
    r"[A-Za-z]([A-Za-z0-9]|\_)*"
    keywords = ["import", "set", "discard", "func", "end_func"]
    if t.value in keywords:
        t.type = "DIRECTIVE"

    return t

t_COMMA = r"\,"
t_LIB_REF = r"\%"
t_LIB_USE = r"\:\:"
t_OPEN_BRAC = r"\["
t_CLOSE_BRAC = r"\]"
t_OPEN_PARAN = r"\("
t_CLOSE_PARAN = r"\)"
t_FUNC = r"\@"
t_VAR_REF = r"\$"

def p_type_indicator(p):
    r"""
    type_indicator : OPEN_PARAN NAME CLOSE_PARAN
    """
    p[0] = p[2]

def p_arg(p):
    r"""
    arg : INT
        | STRING
        | FLOAT
        | ARG INT
        | LIB_REF NAME
        | FUNC NAME
        | VAR_REF NAME
        | type_indicator VAR_REF NAME
        | type_indicator FUNC NAME OPEN_BRAC CLOSE_BRAC
        | type_indicator LIB_REF NAME LIB_USE VAR_REF NAME
        | type_indicator FUNC NAME OPEN_BRAC PARAMETERS CLOSE_BRAC
        | type_indicator LIB_REF NAME LIB_USE FUNC NAME OPEN_BRAC CLOSE_BRAC
        | type_indicator LIB_REF NAME LIB_USE FUNC NAME OPEN_BRAC PARAMETERS CLOSE_BRAC
    """
    if len(p) == 2:
        typ = ""
        if p[1][0] == "\"" and p[1][-1] == "\"":
            typ = "str"
        elif "." in p[1]:
            typ = "float"
        else:
            typ = "int"
        p[0] = (typ, p[1])
    elif len(p) == 3:
        if p[1] == "@":
            typ = "func"
        elif p[1] == "$":
            typ = "var_write"
        elif p[1] == "&":
            typ = "arg"
        else:
            typ = "lib"
        p[0] = (typ, p[2])
    elif len(p) == 4:
        p[0] = ("var", p[1], p[3])
    elif len(p) == 6:
        p[0] = ("func_call", p[1], p[3])
    elif len(p) == 7:
        if p[2] == "%":
            p[0] = ("lib_var", p[3], p[1], p[6])
        else:
            p[0] = ("func_call", p[1], p[3], p[5])
    elif len(p) == 9:
        p[0] = ("lib_call", p[3], p[1], p[6])
    elif len(p) == 10:
        p[0] = ("lib_call", p[3], p[1], p[6], p[8])

def p_PARAMETERS(p):
    r"""
    PARAMETERS : PARAMETERS COMMA arg
               | arg
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        a = p[1]
        a.append(p[3])
        p[0] = a

output = "(lambda args : [scope := [[{}, {}]], libs := {}, "

def ensure(cond, msg):
    try:
            assert cond == 1
    except AssertionError:
        print(msg)
        exit()

def mult_arg(args):
    final = "["
    for i in args:
        final += interpret_arg(i) + ", "

    return final[:-2] + "]"

def interpret_arg(arg):
    final = ""

    if arg[0] == "int" or arg[0] == "float" or arg[0] == "str":
        final = arg[1]

    elif arg[0] == "lib":
        final = "libs[\"{}\"]".format(arg[1])

    elif arg[0] == "var":
        if arg[1] == "None":
            final = "None"
        else:
            final = "{}(scope[-1][0][\"{}\"])".format(arg[1], arg[2])

    elif arg[0] == "func_call":
        def_type = arg[1]
        if def_type == "none":
            def_type = ""
        if len(arg) == 4:
            final = "[{}(scope[0][1][\"{}\"]({})), None][{}]".format(def_type, arg[2], mult_arg(arg[3]), 1 if arg[1] == "none" else 0)
        elif len(arg) == 3:
            final = "[{}(scope[0][1][\"{}\"]()), None][{}]".format(def_type, arg[2], 1 if arg[1] == "none" else 0)

    elif arg[0] == "lib_var":
        if arg[1] == "None":
            final = "None"
        else:
            final = "{}(libs[\"{}\"][0][\"{}\"])".format(arg[2], arg[1], arg[3])
    
    elif arg[0] == "lib_call":
        def_type = arg[2]
        if def_type == "none":
            def_type = ""
        if len(arg) == 5:
            final = "[{}(libs[\"{}\"][1][\"{}\"]({})), None][{}]".format(def_type, arg[1], arg[3], mult_arg(arg[4]), 1 if arg[2] == "none" else 0)
        elif len(arg) == 4:
            final = "[{}(libs[\"{}\"][1][\"{}\"]()), None][{}]".format(def_type, arg[1], arg[3], 1 if arg[2] == "none" else 0)
    
    elif arg[0] == "arg":
        print(arg)
        final = "args[{}]".format(arg[1])

    #print("final:", final)
    return final

def p_line(p):
    r"""   
    line : DIRECTIVE PARAMETERS
         | DIRECTIVE
    """

    global output

    pat = p[1:]

    directive = pat[0]
    args = pat[1]

    if directive == "import":
        ensure(len(args) == 1, "Error: import directive requires 1 argument as library")
        ensure(args[0][0] == "lib", "Error: 'import' directive can only be used on libraries")

        import_lib = args[0][1]

        lib_code = ""
        with open(import_lib + ".py", "r") as file:
            lib_code = file.read()


        ensure(len(lib_code.strip().split("\n")) == 1, "Error: Imported library must be a one line program")

        output += ("libs.__setitem__(\"" + import_lib + "\", " + lib_code.replace("\n", "") + "[0][-1]), ")

    elif directive == "discard":
        if len(args) > 0:
            for i in args:
                output += interpret_arg(i) + ", "
        
    elif directive == "set":
        ensure(len(args) == 2, "Error: 'set' directive must have exactly two arguments")
        ensure(args[0][0] == "var_write", "Error: 'set' directive first argument must be a writable variable reference")

        output += "scope[-1][0].__setitem__(\"{}\", {}), ".format(args[0][1], interpret_arg(args[1]))

    #print("line: ", list(p[1:]))

line_val = 1

def p_error(p):
    global line_val

    print("Syntax error on line {}: {}".format(line_val, p))

if code.strip() == "":
    exit()

start = "line"

lexer = lex.lex()
parser = yacc.yacc()

for line in code.split(";"):
    if line.strip():
        parser.parse(line)
        line_val += 1

output = output[:-2]
output += "])(__import__(\"sys\").argv)"

with open("test.py", "w") as file:
    file.write(output)
