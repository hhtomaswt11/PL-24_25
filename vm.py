#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, shlex


class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.memory = {}
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

            try:
                parts = shlex.split(line)
            except ValueError as e:
                print(f"Erro de sintaxe na linha {self.ip + 1}, token '{line}'")
                print(e)
                self.running = False
                return

            if not parts:
                self.ip += 1
                continue

            instr = parts[0]


            if instr == "PUSH":
                # print(parts[1]) -- "Hello, World!"
                self.stack.append(self._parse_value(parts[1]))
            elif instr == "LOAD":
                addr = int(parts[1])
                self.stack.append(self.memory.get(addr, 0))
            elif instr == "STORE":
                addr = int(parts[1])
                value = self.stack.pop()
                self.memory[addr] = value
            elif instr == "ADD":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif instr == "SUB":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
            elif instr == "MUL":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
            elif instr == "DIV":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a / b)
            elif instr == "IDIV":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a // b)
            elif instr == "MOD":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a % b)
            elif instr == "AND":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(bool(a) and bool(b)))
            elif instr == "OR":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(bool(a) or bool(b)))
            elif instr == "EQ":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(a == b))
            elif instr == "NEQ":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(a != b))
            elif instr == "LT":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(a < b))
            elif instr == "LE":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(a <= b))
            elif instr == "GT":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(a > b))
            elif instr == "GE":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(int(a >= b))
            elif instr == "NOT":
                a = self.stack.pop()
                self.stack.append(int(not bool(a)))
            elif instr == "NEG":
                a = self.stack.pop()
                self.stack.append(-a)
            elif instr == "INC":
                a = self.stack.pop()
                self.stack.append(a + 1)
            elif instr == "DEC":
                a = self.stack.pop()
                self.stack.append(a - 1)
                
            elif instr == "CALL":
                self.stack.append(self.ip + 1)  # salva a posição de retorno
                self.ip = self.labels[parts[1]]
                continue

            elif instr == "RET":
                self.ip = self.stack.pop()
                continue

            elif instr == "JMP":
                label = parts[1]
                self.ip = self.labels[label]
                continue
            elif instr == "JZ":
                label = parts[1]
                val = self.stack.pop()
                if val == 0:
                    self.ip = self.labels[label]
                    continue
            elif instr == "JNZ":
                label = parts[1]
                val = self.stack.pop()
                if val != 0:
                    self.ip = self.labels[label]
                    continue
            elif instr == "PRINT":
                value = self.stack.pop()
                if isinstance(value, str):
                    print(value, end='')  
                else:
                    print(value, end=' ')
            elif instr == "PRINTLN":
                print()
            elif instr == "READ":
                value = input()
                try:
                    value = int(value)
                except:
                    pass
                self.stack.append(value)
            elif instr == "HALT":
                self.running = False

            self.ip += 1



    def _parse_value(self, val):
        try:
            return int(val)
        except:
            try:
                return float(val)
            except:
                return val



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

