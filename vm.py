import sys, shlex

# python3 vm.py examples/vm/hello.vm

class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.memoria_global = [0] * 1000  # memória global simulada
        self.labels = {}
        self.ponteiro_instrucao = 0  # instruction pointer
        self.codigo = []
        self.running = True

    def load_code(self, linhas_codigo):
        self.codigo = linhas_codigo
        self._mapear_labels()

    def _mapear_labels(self):
        for i, linha in enumerate(self.codigo):
            if linha.endswith(":"):
                label = linha[:-1]
                self.labels[label] = i

    def run(self):
        self.ponteiro_instrucao = 0
        while self.running and self.ponteiro_instrucao < len(self.codigo):
            linha = self.codigo[self.ponteiro_instrucao]
            if linha.endswith(":"):
                self.ponteiro_instrucao += 1
                continue

            if linha.strip().startswith("//") or linha.strip() == "":
                self.ponteiro_instrucao += 1
                continue

            partes = shlex.split(linha)
            instr = partes[0].lower()

            match instr:
                case "pushi":
                    self.stack.append(int(partes[1]))
                case "pushf":
                    self.stack.append(float(partes[1]))
                case "pushg":
                    self.stack.append(self.memoria_global[int(partes[1])])
                case "pushs":
                    self.stack.append(partes[1])
                case "storeg":
                    valor = self.stack.pop()
                    self.memoria_global[int(partes[1])] = valor

                case "load":
                    indice = int(partes[1])
                    if indice != 0:
                        print(f"LOAD só suporta índice 0. Recebido: {indice}")
                        self.running = False
                        return
                    endereco = self.stack.pop()
                    self.stack.append(self.memoria_global[endereco])

                case "add":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(a + b)
                case "sub":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(a - b)
                case "mul":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(a * b)
                case "div":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(a // b)
                case "fdiv":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(a / b)
                case "mod":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(a % b)
                case "sup":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(int(a > b))
                case "inf":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(int(a < b))
                case "supeq":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(int(a >= b))
                case "infeq":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(int(a <= b))
                case "equal":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(int(a == b))
                case "and":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(int(bool(a) and bool(b)))
                case "or":
                    b, a = self.stack.pop(), self.stack.pop()
                    self.stack.append(int(bool(a) or bool(b)))
                case "not":
                    a = self.stack.pop()
                    self.stack.append(int(not a))
                case "read":
                    valor = input()
                    self.stack.append(valor)
                case "atoi":
                    s = self.stack.pop()
                    self.stack.append(int(s))
                case "atof":
                    s = self.stack.pop()
                    self.stack.append(float(s))
                case "writei":
                    print(self.stack.pop(), end=' ')
                case "writes":
                    print(self.stack.pop(), end=' ')
                case "writeln":
                    print()
                case "jump":
                    self.ponteiro_instrucao = self.labels[partes[1]]
                    continue

                case "storen":
                    valor = self.stack.pop()
                    indice = self.stack.pop()
                    endereco = self.stack.pop()
                    endereco_final = endereco + indice
                    if endereco_final >= len(self.memoria_global):
                        self.memoria_global.extend([0] * ((endereco_final + 1) - len(self.memoria_global)))  # Expande a memória se necessário
                    self.memoria_global[endereco_final] = valor

                case "loadn":
                    indice = self.stack.pop()
                    endereco = self.stack.pop()
                    endereco_final = endereco + indice
                    if endereco_final >= len(self.memoria_global):
                        print(f"[ERRO] LOADN: endereço {endereco_final} fora da memória")
                        self.running = False
                        return
                    self.stack.append(self.memoria_global[endereco_final])

                case "store":
                    indice = int(partes[1])
                    valor = self.stack.pop()
                    endereco = self.stack.pop()
                    if endereco + indice >= len(self.memoria_global):
                        self.memoria_global.extend([0] * ((endereco + indice + 1) - len(self.memoria_global)))  # Expande memória se necessário
                    self.memoria_global[endereco + indice] = valor

                case "stri":
                    valor = self.stack.pop()
                    self.stack.append(str(valor))  # converte int para string

                case "strf":
                    valor = self.stack.pop()
                    self.stack.append(f"{valor:.2f}")  # converte float para string com 2 casas decimais

                case "allocn":
                    n = self.stack.pop()
                    endereco = len(self.memoria_global)
                    self.memoria_global.extend([0] * n)
                    self.stack.append(endereco)

                case "pushst":
                    indice = int(partes[1])
                    endereco = self.memoria_global[indice]  # Este é o endereço da heap guardado em memoria_global[indice]
                    self.stack.append(endereco)

                case "jz":
                    label = partes[1]
                    valor = self.stack.pop()
                    if valor == 0:
                        self.ponteiro_instrucao = self.labels[label]
                        continue
                case "jnz":
                    label = partes[1]
                    valor = self.stack.pop()
                    if valor != 0:
                        self.ponteiro_instrucao = self.labels[label]
                        continue
                case "start":
                    pass  # FP inicializado no web editor
                case "stop":
                    self.running = False
                case _:
                    print(f"Instrução desconhecida: {instr}")
                    self.running = False

            self.ponteiro_instrucao += 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 vm.py <ficheiro.vm>")
        sys.exit(1)

    vm_file = sys.argv[1]

    with open(vm_file, "r") as f:
        codigo = [linha.strip() for linha in f.readlines()]

    vm = VirtualMachine()
    vm.load_code(codigo)
    vm.run()
