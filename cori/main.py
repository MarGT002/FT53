import ply.lex as lex
import ply.yacc as yacc
import re

# Lista de nombres de tokens
tokens = [
    # Palabras clave
    'ENTERO', 'FLOTANTE', 'STRING', 'IF', 'WHILE', 'RETURN', 'NULL', 'BREAK',
    'SWITCH', 'CASE', 'DEFAULT', 'ARRAY', 'PRINT', 'CHAR', 'ELSE', 'TRUE', 'FALSE', 
    
    # Números hexadecimales
    'HEX_0', 'HEX_1', 'HEX_2', 'HEX_3', 'HEX_4', 'HEX_5', 'HEX_6', 'HEX_7',
    'HEX_8', 'HEX_9', 'HEX_A', 'HEX_B', 'HEX_C', 'HEX_D', 'HEX_E', 'HEX_F',
    
    # Caracteres (solo algunos representativos, la lista completa sería muy larga)
    'NULL_CHAR', 'HT', 'SPACE', 'EXCLAMATION', 'DOUBLE_QUOTE', 'HASH', 'DOLLAR',
    'PERCENT', 'AMPERSAND', 'SINGLE_QUOTE', 'LPAREN', 'RPAREN', 'ASTERISK',
    'PLUS', 'COMMA', 'MINUS', 'DOT', 'SLASH', 'COLON', 'SEMICOLON', 'LESS_THAN',
    'EQUALS', 'GREATER_THAN', 'QUESTION', 'AT', 'LBRACKET', 'RBRACKET', 'BACKSLASH',
    'CARET', 'UNDERSCORE', 'GRAVE', 'LBRACE', 'RBRACE', 'VERTICAL_BAR', 'TILDE',
    
    # Operadores
    'PLUS_OP', 'MINUS_OP', 'MULT_OP', 'DIV_OP', 'ASSIGN_OP', 'EQ_OP', 'NE_OP',
    
    # Símbolos especiales
    'LPAREN_SPEC', 'RPAREN_SPEC', 'SEMICOLON_SPEC', 'LBRACE_SPEC', 'RBRACE_SPEC',
    'LBRACKET_SPEC', 'RBRACKET_SPEC',
    
    # Identificadores
    'IDENTIFIER'
]

# Palabras clave definidas por combinaciones de W, w, V, v
keyword_lexemes = {
    'WW': 'ENTERO',
    'Ww': 'FLOTANTE',  # Nota: Hay conflicto con ENTERO, mismo lexema
    'WV': 'STRING',
    'Wv': 'IF',
    'Vv': 'ELSE',
    'wW': 'WHILE',
    'ww': 'RETURN',
    'wV': 'NULL',
    'wv': 'BREAK',
    'VW': 'SWITCH',
    'Vw': 'CASE',
    'VV': 'DEFAULT',
    'Vv': 'ARRAY',
    'vW': 'PRINT',
    'TV': 'TRUE',
    'Tv': 'FALSE'
}

# Números hexadecimales definidos por combinaciones de O, o, C, c
hex_lexemes = {
    'OO': 'HEX_0',
    'Oo': 'HEX_1',
    'OC': 'HEX_2',
    'Oc': 'HEX_3',
    'oO': 'HEX_4',
    'oo': 'HEX_5',
    'oC': 'HEX_6',
    'oc': 'HEX_7',  
    'CO': 'HEX_8',
    'Co': 'HEX_9',
    'CC': 'HEX_A',  
    'Co': 'HEX_B',  
    'cO': 'HEX_C',
    'co': 'HEX_D',
    'cC': 'HEX_E',
    'cc': 'HEX_F'
}

# Operadores definidos por combinaciones de I, L, T
operator_lexemes = {
    'II': 'PLUS_OP',
    'IL': 'MINUS_OP',
    'IT': 'MULT_OP',
    'LI': 'DIV_OP',
    'LL': 'ASSIGN_OP',
    'LT': 'EQ_OP',
    'TT': 'NE_OP'
}

# Caracteres definidos por combinaciones de Z, z (8 caracteres)
# Solo incluiremos algunos ejemplos, la lista completa sería muy extensa
char_lexemes = {
    'zzzzzzzz': 'NULL_CHAR',
    'zzzzZzzZ': 'HT',
    'zzZzzzzz': 'SPACE',
    'zzZzzzzZ': 'EXCLAMATION',
    'zzZzzzZz': 'DOUBLE_QUOTE',
    'zzZzzzZZ': 'HASH',
    'zzZzzZzz': 'DOLLAR',
    'zzZzzZzZ': 'PERCENT',
    'zzZzzZZz': 'AMPERSAND',
    'zzZzzZZZ': 'SIMPLE_QUOTE',
    # Símbolos básicos
    '(': 'zzZzZzzz',
    ')': 'zzZzZzzZ',
    '*': 'zzZzZzZz',
    '+': 'zzZzZzZZ',
    ',': 'zzZzZZzz',
    '-': 'zzZzZZzZ',
    '.': 'zzZzZZZz',
    '/': 'zzZzZZZZ',
    
    # Números
    '0': 'zzZZzzzz',
    '1': 'zzZZzzzZ',
    '2': 'zzZZzzZz',
    '3': 'zzZZzzZZ',
    '4': 'zzZZzZzz',
    '5': 'zzZZzZzZ',
    '6': 'zzZZzZZz',
    '7': 'zzZZzZZZ',
    '8': 'zzZZZzzz',
    '9': 'zzZZZzzZ',
    
    # Signos de puntuación
    ':': 'zzZZZzZz',
    ';': 'zzZZZzZZ',
    '<': 'zzZZZZzz',
    '=': 'zzZZZZzZ',
    '>': 'zzZZZZZz',
    '?': 'zzZZZZZZ',
    '@': 'zZzzzzzz',
    
    # Letras mayúsculas A-Z
    'A': 'zZzzzzzZ',
    'B': 'zZzzzzZz',
    'C': 'zZzzzzZZ',
    'D': 'zZzzzZzz',
    'E': 'zZzzzZzZ',
    'F': 'zZzzzZZz',
    'G': 'zZzzzZZZ',
    'H': 'zZzzZzzz',
    'I': 'zZzzZzzZ',
    'J': 'zZzzZzZz',
    'K': 'zZzzZzZZ',
    'L': 'zZzzZZzz',
    'M': 'zZzzZZzZ',
    'N': 'zZzzZZZz',
    'O': 'zZzzZZZZ',
    'P': 'zZzZzzzz',
    'Q': 'zZzZzzzZ',
    'R': 'zZzZzzZz',
    'S': 'zZzZzzZZ',
    'T': 'zZzZzZzz',
    'U': 'zZzZzZzZ',
    'V': 'zZzZzZZz',
    'W': 'zZzZzZZZ',
    'X': 'zZzZZzzz',
    'Y': 'zZzZZzzZ',
    'Z': 'zZzZZzZz',
    
    # Símbolos adicionales
    '[': 'zZzZZzZZ',
    '\\': 'zZzZZZzz',
    ']': 'zZzZZZzZ',
    '^': 'zZzZZZZz',
    '_': 'zZzZZZZZ',
    '`': 'zZZzzzzz',
    
    # Letras minúsculas a-z
    'a': 'zZZzzzzZ',
    'b': 'zZZzzzZz',
    'c': 'zZZzzzZZ',
    'd': 'zZZzzZzz',
    'e': 'zZZzzZzZ',
    'f': 'zZZzzZZz',
    'g': 'zZZzzZZZ',
    'h': 'zZZzZzzz',
    'i': 'zZZzZzzZ',
    'j': 'zZZzZzZz',
    'k': 'zZZzZzZZ',
    'l': 'zZZzZZzz',
    'm': 'zZZzZZzZ',
    'n': 'zZZzZZZz',
    'o': 'zZZzZZZZ',
    'p': 'zZZZzzzz',
    'q': 'zZZZzzzZ',
    'r': 'zZZZzzZz',
    's': 'zZZZzzZZ',
    't': 'zZZZzZzz',
    'u': 'zZZZzZzZ',
    'v': 'zZZZzZZz',
    'w': 'zZZZzZZZ',
    'x': 'zZZZZzzz',
    'y': 'zZZZZzzZ',
    'z': 'zZZZZzZz',
    
    # Símbolos de agrupación
    '{': 'zZZZZzZZ',
    '|': 'zZZZZZzz',
    '}': 'zZZZZZzZ',
    '~': 'zZZZZZZz',
    
    # Caracteres especiales
    'SUPR': 'zZZZZZZZ',
    'Ç': 'Zzzzzzzz',
    'ü': 'ZzzzzzzZ',
    'é': 'ZzzzzzZz',
    'â': 'ZzzzzzZZ',
    'ä': 'ZzzzzZzz',
    'à': 'ZzzzzZzZ',
    'å': 'ZzzzzZZz',
    'ç': 'ZzzzzZZZ',
    'Á': 'ZzZZzZzZ',
    'Â': 'ZzZZzZZz',
    'À': 'ZzZZzZZZ',
    'Ä': 'ZzzzZZZz',
    'Å': 'ZzzzZZZZ',
    'É': 'ZzzZzzzz',
    'Æ': 'ZzzZzzZz',
    'Ö': 'ZzzZZzzZ',
    'Ü': 'ZzzZZzZz',
    'Ñ': 'ZzZzzZzZ',
     # Letras con acentos y diéresis minúsculas
    'á': 'ZzZzzzzz',
    'â': 'ZzzzzzZZ',
    'à': 'ZzzzzZzZ',
    'ä': 'ZzzzzZzz',
    'å': 'ZzzzzZZz',
    'é': 'ZzzzzzZz',
    'ê': 'ZzzzZzzz',
    'ë': 'ZzzzZzzZ',
    'è': 'ZzzzZzZz',
    'í': 'ZzZzzzzZ',
    'ï': 'ZzzzZzZZ',
    'î': 'ZzzzZZzz',
    'ì': 'ZzzzZZzZ',
    'ó': 'ZzZzzzZz',
    'ô': 'ZzzZzzZZ',
    'ö': 'ZzzZzZzz',
    'ò': 'ZzzZzZzZ',
    'ú': 'ZzZzzzZZ',
    'û': 'ZzzZzZZz',
    'ù': 'ZzzZzZZZ',
    'ü': 'ZzzzzzzZ',
    'ÿ': 'ZzzZZzzz',
    'ñ': 'ZzZzzZzz',
    
    # Caracteres gráficos
    '╣': 'ZzZZZzzZ',
    '║': 'ZzZZZzZz',
    '╗': 'ZzZZZzZZ',
    '╝': 'ZzZZZZzz',
    '░': 'ZzZZzzzz',
    '▒': 'ZzZZzzzZ',
    '▓': 'ZzZZzzZz',
    '│': 'ZzZZzzZZ',
    '┤': 'ZzZZzZzz',
    
    # Símbolos monetarios
    '©': 'ZzZZZzzz',
    '£': 'ZzzZZZzz',
    'Ø': 'ZzzZZZzZ',
    '×': 'ZzzZZZZz',
    'ƒ': 'ZzzZZZZZ',
    '¬': 'ZzZzZzZz',
    '½': 'ZzZzZzZZ',
    '¼': 'ZzZzZZzz',
    '÷': 'ZZZZzZZz',
    '¢': 'ZzZZZZzZ',
    '¥': 'ZzZZZZZz',
    '¤': 'ZZzzZZZZ',

     # Símbolos tipográficos
    'ª': 'ZzZzzZZz',
    'º': 'ZzZzzZZZ',
    '¿': 'ZzZzZzzz',
    '®': 'ZzZzZzzZ',
    '¡': 'ZzZzZZzZ',
    '«': 'ZzZzZZZz',
    '»': 'ZzZzZZZZ',
    'æ': 'ZzzZzzzZ',
    'ø': 'ZzzZZzZZ',
    
    # Símbolos matemáticos
    '≡': 'ZZZZzzzz',
    '±': 'ZZZZzzzZ',
    '÷': 'ZZZZzZZz',
    
    # Caracteres de formato
    # Caracteres especiales
    'SUPR': 'zZZZZZZZ',
    'nbsp': 'ZZZZZZZZ'
}

# Símbolos especiales (se representan a sí mismos)
special_symbols = {
    '(': 'LPAREN_SPEC',
    ')': 'RPAREN_SPEC',
    ';': 'SEMICOLON_SPEC',
    '{': 'LBRACE_SPEC',
    '}': 'RBRACE_SPEC',
    '[': 'LBRACKET_SPEC',
    ']': 'RBRACKET_SPEC'
}
char_lexemes_inverted = {v: k for k, v in char_lexemes.items()}

# Expresiones regulares para tokens simples
t_PLUS_OP = r'II'
t_MINUS_OP = r'IL'
t_MULT_OP = r'IT'
t_DIV_OP = r'LI'
t_ASSIGN_OP = r'LL'
t_EQ_OP = r'LT'
t_NE_OP = r'TT'

# Símbolos especiales
t_LPAREN_SPEC = r'\('
t_RPAREN_SPEC = r'\)'
t_SEMICOLON_SPEC = r';'
t_LBRACE_SPEC = r'\{'
t_RBRACE_SPEC = r'\}'
t_LBRACKET_SPEC = r'\['
t_RBRACKET_SPEC = r'\]'

# Ignorar espacios y tabulaciones
t_ignore = ' \t'
# Definición de los operadores de comparación en el lexer


# Manejo de errores
def t_error(t):
    print(f"Token inválido: '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

def t_COMMENT(t):
    r'//.|\/\[\s\S]?\\/'
    pass  # Se ignoran



# Reglas para tokens complejos
def t_KEYWORD(t):
    r'[WwVv]{2}'
    if t.value in keyword_lexemes:
        t.type = keyword_lexemes[t.value]
        return t
    else:
        t.type = 'IDENTIFIER'
        return t
def t_HEX(t):
    r'[OoCc]{2}'
    if t.value in hex_lexemes:
        t.type = hex_lexemes[t.value]
        return t


def t_CHAR(t):
    r'z[Zz]{7}'
    if t.value in char_lexemes:
        t.type = char_lexemes[t.value]
        return t

def t_IDENTIFIER(t):
    r'[bd]+'
    t.type = 'IDENTIFIER'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Construir el lexer
lexer = lex.lex()

# Función para probar el analizador léxico
def test_lexer(input_text):
    lexer.input(input_text)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr)
    return column
def p_program(p):
    '''program : statement_list'''
    p[0] = ('program', p[1])

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : PRINT LPAREN_SPEC IDENTIFIER RPAREN_SPEC SEMICOLON_SPEC'''
    p[0] = ('print', p[3])

def p_error(p):
    print(f"Error de sintaxis en: {p.value}" if p else "Error de sintaxis inesperado")


    
parser = yacc.yacc()

# Precedencia de operadores (de menor a mayor precedencia)
precedence = (
    ('left', 'EQ_OP', 'NE_OP'),
    ('left', 'PLUS_OP', 'MINUS_OP'),
    ('left', 'MULT_OP', 'DIV_OP'),
)

# Reglas gramaticales

def p_program(p):
    '''program : statement_list'''
    p[0] = ('program', p[1])

def p_statement_list(p):
    '''statement_list : statement
                     | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : declaration_statement
                | expression_statement
                | print_statement
                | if_statement
                | while_statement
                | return_statement
                | break_statement
                | block_statement
                | switch_statement'''
    p[0] = p[1]

def p_declaration_statement(p):
    '''declaration_statement : type IDENTIFIER SEMICOLON_SPEC
                            | type IDENTIFIER ASSIGN_OP expression SEMICOLON_SPEC'''
    if len(p) == 4:
        p[0] = ('declare', p[1], p[2], None)
    else:
        p[0] = ('declare', p[1], p[2], p[4])

def p_type(p):
    '''type : ENTERO
            | FLOTANTE
            | STRING
            | CHAR
            | ARRAY'''
    p[0] = p[1]

def p_expression_statement(p):
    '''expression_statement : expression SEMICOLON_SPEC
                            | SEMICOLON_SPEC'''
    if len(p) == 3:
        p[0] = ('expr_stmt', p[1])
    else:
        p[0] = ('empty_stmt',)

def p_print_statement(p):
    '''print_statement : PRINT LPAREN_SPEC expression RPAREN_SPEC SEMICOLON_SPEC'''
    p[0] = ('print', p[3])

def p_if_statement(p):
    '''if_statement : IF LPAREN_SPEC expression RPAREN_SPEC statement
                   | IF LPAREN_SPEC expression RPAREN_SPEC statement ELSE statement'''
    if len(p) == 6:
        p[0] = ('if', p[3], p[5], None)
    else:
        p[0] = ('if', p[3], p[5], p[7])

def p_while_statement(p):
    '''while_statement : WHILE LPAREN_SPEC expression RPAREN_SPEC statement'''
    p[0] = ('while', p[3], p[5])

def p_return_statement(p):
    '''return_statement : RETURN expression SEMICOLON_SPEC
                       | RETURN SEMICOLON_SPEC'''
    if len(p) == 4:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

def p_break_statement(p):
    '''break_statement : BREAK SEMICOLON_SPEC'''
    p[0] = ('break',)

def p_block_statement(p):
    '''block_statement : LBRACE_SPEC statement_list RBRACE_SPEC
                       | LBRACE_SPEC RBRACE_SPEC'''
    if len(p) == 4:
        p[0] = ('block', p[2])
    else:
        p[0] = ('block', [])

def p_switch_statement(p):
    '''switch_statement : SWITCH LPAREN_SPEC expression RPAREN_SPEC LBRACE_SPEC case_list RBRACE_SPEC
                        | SWITCH LPAREN_SPEC expression RPAREN_SPEC LBRACE_SPEC RBRACE_SPEC'''
    if len(p) == 8:
        p[0] = ('switch', p[3], p[6])
    else:
        p[0] = ('switch', p[3], [])

def p_case_list(p):
    '''case_list : case
                | case_list case'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_case(p):
    '''case : CASE expression COLON statement_list
            | DEFAULT COLON statement_list'''
    if len(p) == 5:
        p[0] = ('case', p[2], p[4])
    else:
        p[0] = ('default_case', p[3])

def p_expression(p):
    '''expression : assignment_expression
                  | binary_expression
                  | unary_expression
                  | primary_expression'''
    p[0] = p[1]

def p_assignment_expression(p):
    '''assignment_expression : IDENTIFIER ASSIGN_OP expression'''
    p[0] = ('assign', p[1], p[3])

def p_binary_expression(p):
    '''binary_expression : expression PLUS_OP expression
                        | expression MINUS_OP expression
                        | expression MULT_OP expression
                        | expression DIV_OP expression
                        | expression EQ_OP expression
                        | expression NE_OP expression'''
    p[0] = ('binary', p[2], p[1], p[3])

def p_unary_expression(p):
    '''unary_expression : PLUS_OP expression
                       | MINUS_OP expression'''
    p[0] = ('unary', p[1], p[2])

def p_primary_expression(p):
    '''primary_expression : literal
                         | IDENTIFIER
                         | LPAREN_SPEC expression RPAREN_SPEC'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_literal(p):
    '''literal : numeric_literal
               | string_literal
               | boolean_literal
               | null_literal'''
    p[0] = p[1]

def p_numeric_literal(p):
    '''numeric_literal : HEX_0
                       | HEX_1
                       | HEX_2
                       | HEX_3
                       | HEX_4
                       | HEX_5
                       | HEX_6
                       | HEX_7
                       | HEX_8
                       | HEX_9
                       | HEX_A
                       | HEX_B
                       | HEX_C
                       | HEX_D
                       | HEX_E
                       | HEX_F'''
    p[0] = ('number', p[1])

def p_string_literal(p):
    '''string_literal : STRING'''
    p[0] = ('string', p[1])

def p_boolean_literal(p):
    '''boolean_literal : TRUE
                       | FALSE'''
    p[0] = ('boolean', p[1])

def p_null_literal(p):
    '''null_literal : NULL'''
    p[0] = ('null',)

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}' en la línea {p.lineno}, posición {find_column(lexer.lexdata, p)}")
    else:
        print("Error de sintaxis: Fin de archivo inesperado")

# Construir el parser
parser = yacc.yacc()

def find_column(input_text, token):
    """Calcula la columna exacta donde ocurre un token/error"""
    last_cr = input_text.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    return (token.lexpos - last_cr) + 1  # +1 para convertir a base 1

# Función para probar el parser
def test_parser(input_text):
    result = parser.parse(input_text)
    print(result)

def get_lexer():
    return lexer

def get_parser():
    return parser

if _name_ == "_main_":
    print("Intérprete del lenguaje COR (Escriba 'salir' para terminar)")
    while True:
        try:
            # Leer entrada del usuario
            input_text = input("COR> ")
            
            if input_text.lower() == 'salir':
                print("Saliendo del intérprete...")
                break
                
            if not input_text.strip():
                continue  # Ignorar líneas vacías
                
            # Procesar la entrada
            print("\n=== Análisis Léxico ===")
            test_lexer(input_text)
            
            print("\n=== Análisis Sintáctico ===")
            result = test_parser(input_text)
            print("AST generado:", result)
            
        except Exception as e:
            print(f"Error: {str(e)}")


#Ww diferencia = Co IL oO; vW(diferencia);
#WW resultado = Oo II Oc; vW(resultado);
#WW a = Oo; WW b = Oc; WW c = a II b; vW(c);