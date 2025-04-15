import sys
from src.parser import create_parser
from src.lexer import create_lexer

if __name__ == "__main__":
    pascal_file= sys.argv[1]
    with open(pascal_file, 'r') as file:
      source_code = file.read()
    
    parser = create_parser()
    lexer = create_lexer()
    
    lexer.input(source_code)
    ast = parser.parse(source_code)
    
    # TOKENIZER
    for tok in lexer:
        print(tok)
        
    # CHECK AST 
    if ast:
        print("Análise sintática bem-sucedida!")
    else:
        print("Erros na análise sintática:")
        for error in parser.errors:
            print(f"  - {error}")
