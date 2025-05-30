from colorama import init, Fore
import sys, os
from src.parser import criar_parser
from src.semantica import AnalisadorSemantico
from src.gerador_de_codigo import GeradorDeCodigo
from vm import VirtualMachine

# python3 main.py examples/pas/hello.pas

init(autoreset=True)

def main(pascal_file):
    # 1. Ler o código Pascal
    with open(pascal_file, 'r') as file:
        source_code = file.read()

    # 2. Análise sintática
    parser = criar_parser()
    ast = parser.parse(source_code)

    if parser.erros:
        print("Erros de parsing:")
        for e in parser.erros:
            print(" -", e)
        return

    print("--- Análise sintática concluída ---")

    # 3. Análise semântica
    analisador = AnalisadorSemantico()
    sucesso = analisador.analisar(ast)
    if not sucesso:
        print("Erros semânticos:")
        for e in analisador.erros:
            print(" -", e)
        return

    print("--- Análise semântica concluída ---")

    # 4. Geração de código
    gerador = GeradorDeCodigo(analisador.tabela_de_simbolos)
    code = gerador.gerar(ast)

    # Preparar caminho de saída na pasta examples/vm/
    filename = os.path.basename(pascal_file).replace(".pas", ".vm")
    output_dir = os.path.join("examples", "vm")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, filename)

    # Guardar o código gerado
    with open(output_file, "w") as f:
        for line in code:
            f.write(line + "\n")

    print(f"\nCódigo gerado em: {output_file}")

    print(Fore.CYAN + "\nCódigo a ser executado na VM...")
    print(Fore.GREEN + "{INICIO}")
    vm = VirtualMachine()
    vm.load_code(code)
    vm.run()
    print(Fore.RED + "{FIM}")


if __name__ == "__main__":
    if len(sys.argv) != 2: 
        print("Uso: python3 main.py <ficheiro.pas>")
    else:
        pascal_file = sys.argv[1]
        main(pascal_file)     # python3 main.py examples/pas/hello.pas