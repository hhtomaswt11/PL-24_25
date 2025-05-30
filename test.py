import sys
from src.parser import criar_parser
from src.analisador_lexico import criar_analisador_lexico

if __name__ == "__main__":
    pascal_file= sys.argv[1]
    with open(pascal_file, 'r') as file:
      source_code = file.read()
    
    parser = criar_parser()
    lexer = criar_analisador_lexico()
    
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
