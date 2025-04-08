from lexer import get_lexer, get_parser, find_column
import sys

lexer = get_lexer()
parser = get_parser()

def main():
    
    print("Analizador para lenguaje especial - Consola interactiva")
    print("Escribe 'salir' para terminar el programa")
    print("Escribe 'ejemplo' para ver un ejemplo de código válido")
    print("-------------------------------------------------------")
    
    while True:
        try:
            # Modo interactivo o lectura de archivo
            if len(sys.argv) > 1:
                # Modo archivo
                with open(sys.argv[1], 'r') as file:
                    input_text = file.read()
                print(f"\nAnalizando archivo: {sys.argv[1]}")
            else:
                # Modo interactivo
                input_text = input("\nIngresa código (o comando): ")
                if input_text.lower() == 'salir':
                    break
                if input_text.lower() == 'ejemplo':
                    print("\nEjemplo de código válido:")
                    print("""WW bd ASSIGN_OP OO SEMICOLON_SPEC
PRINT LPAREN_SPEC bd RPAREN_SPEC SEMICOLON_SPEC
IF LPAREN_SPEC bd EQ_OP OO RPAREN_SPEC LBRACE_SPEC
    PRINT LPAREN_SPEC WV RPAREN_SPEC SEMICOLON_SPEC
RBRACE_SPEC""")
                    continue
            
            # Análisis léxico
            print("\n--- Tokens reconocidos ---")
            lexer.input(input_text)
            for tok in lexer:
                print(f"Tipo: {tok.type}, Valor: {tok.value}, Línea: {tok.lineno}, Posición: {find_column(input_text, tok)}")
            
            # Análisis sintáctico
            print("\n--- Árbol de Sintaxis Abstracta (AST) ---")
            ast = parser.parse(input_text)
            if ast:
                print(ast)
            
            # Si estaba en modo archivo, salir después de analizar
            if len(sys.argv) > 1:
                break
                
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {sys.argv[1]}")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            if len(sys.argv) > 1:
                break  # Salir si hay error en modo archivo

if __name__ == "__main__":
    main()
