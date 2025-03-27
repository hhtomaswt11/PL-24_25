#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from colorama import init, Fore, Back, Style
import sys
from src.lexer import create_lexer
from src.parser import create_parser
from src.semantic import SemanticAnalyzer
from src.codegen import CodeGenerator
from vm import VirtualMachine
from pprint import pprint
init(autoreset=True)

def main(pascal_file):
    # 1. Ler o código Pascal
    with open(pascal_file, 'r') as f:
        source_code = f.read()

    # 2. Análise sintática
    parser = create_parser()
    ast = parser.parse(source_code)

    if parser.errors:
        print("Erros de parsing:")
        for e in parser.errors:
            print(" -", e)
        return

    print("---Análise sintática concluída---")

    # 3. Análise semântica
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    if not success:
        print("Erros semânticos:")
        for e in analyzer.errors:
            print(" -", e)
        return

    print("---Análise semântica concluída---")

    # 4. Geração de código
    generator = CodeGenerator(analyzer.symtab)
    code = generator.generate(ast)

    output_file = pascal_file.replace(".pas", ".vm")
    with open(output_file, "w") as f:
        for line in code:
            f.write(line + "\n")

    print(f"\nCódigo gerado em: {output_file}")

    
    # print("\nCódigo a ser executado na VM...")
    # print("---------------INÍCIO----------------")
    # vm = VirtualMachine()
    # vm.load_code(code)
    # vm.run()
    # print("----------------FIM------------------")

    print(Fore.CYAN + "\nCódigo a ser executado na VM...")
    print(Fore.GREEN + "{INICIO}")
    vm = VirtualMachine()
    vm.load_code(code)
    vm.run()
    print(Fore.RED + "{FIM}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python main.py <ficheiro.pas>")
    else:
        main(sys.argv[1])
