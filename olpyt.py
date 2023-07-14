from ply import lex, yacc

code = ""
with open("code.olpyt", "r") as file:
    code = file.read()

tokens = ("NAME", "STRING", "INT", "FLOAT", "COMMA", "LIB_REF", "LIB_USE", "OPEN_BRAC", "CLOSE_BRAC", "OPEN_PARAN", "CLOSE_PARAN", "FUNC_CALL", "VAR_REF", "DIRECTIVE")

def t_error(t):
    print("LEXER Error")
    exit()

t_ignore = " \n\t"
t_STRING = r"\"[^\"]*\""
t_FLOAT = r"[0-9]+\.[0-9]+"
t_INT = r"[0-9]+"
def t_NAME(t):
    r"[A-Za-z]([A-Za-z0-9]|\_)*"
    keywords = ["import", "set", "call", "func", "end_func"]
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
t_FUNC_CALL = r"\@"
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
        | LIB_REF NAME
        | type_indicator VAR_REF NAME
        | type_indicator FUNC_CALL NAME OPEN_BRAC CLOSE_BRAC
        | type_indicator LIB_REF NAME LIB_USE VAR_REF NAME
        | type_indicator FUNC_CALL NAME OPEN_BRAC PARAMETERS CLOSE_BRAC
        | type_indicator LIB_REF NAME LIB_USE FUNC_CALL NAME OPEN_BRAC CLOSE_BRAC
        | type_indicator LIB_REF NAME LIB_USE FUNC_CALL NAME OPEN_BRAC PARAMETERS CLOSE_BRAC
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
    print("arg: ", list(p))

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
    print("PARAMETERS: ", list(p))

def p_line(p):
    r"""   
    line : DIRECTIVE PARAMETERS
         | DIRECTIVE
    """
    print("line: ", list(p))

start = "line"

lexer = lex.lex()
parser = yacc.yacc()

for line in code.split(";"):
    if line.strip():

        print(line)
        parser.parse(line)