import sys, shlex

# python3 vm.py examples/vm/hello.vm

class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.gp = [0] * 1000  # memória global simulada
        self.labels = {}
        self.ip = 0  # instruction pointer
        self.code = []
        self.running = True

    def load_code(self, code_lines):
        self.code = code_lines
        self._map_labels()

    def _map_labels(self):
        for i, line in enumerate(self.code):
            if line.endswith(":"):
                label = line[:-1]
                self.labels[label] = i

    def run(self):
        self.ip = 0
        while self.running and self.ip < len(self.code):
            line = self.code[self.ip]
            if line.endswith(":"):
                self.ip += 1
                continue

            #parts = shlex.split(line)
            
            if line.strip().startswith("//") or line.strip() == "":
                self.ip += 1
                continue

            parts = shlex.split(line)
            
            instr = parts[0].lower()

            match instr:
                case "pushi":
                    self.stack.append(int(parts[1]))
                case "pushf":
                    self.stack.append(float(parts[1]))
                case "pushg":
                    self.stack.append(self.gp[int(parts[1])])
                case "pushs":
                    self.stack.append(parts[1])
                case "storeg":
                    value = self.stack.pop()
                    self.gp[int(parts[1])] = value
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
                    value = input()
                    self.stack.append(value)
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
                    self.ip = self.labels[parts[1]]
                    continue
                case "jz":
                    label = parts[1]
                    val = self.stack.pop()
                    if val == 0:
                        self.ip = self.labels[label]
                        continue
                case "jnz":
                    label = parts[1]
                    val = self.stack.pop()
                    if val != 0:
                        self.ip = self.labels[label]
                        continue
                case "start":
                    pass  # FP inicializado no web editor
                case "stop":
                    self.running = False
                case _:
                    print(f"Instrução desconhecida: {instr}")
                    self.running = False

            self.ip += 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 vm.py <ficheiro.vm>")
        sys.exit(1)
    
    vm_file = sys.argv[1]

    with open(vm_file, "r") as f:
        code = [line.strip() for line in f.readlines()]

    vm = VirtualMachine()
    vm.load_code(code)
    vm.run()