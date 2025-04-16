class CodeGenerator:
    def __init__(self, symtab):
        self.symtab = symtab
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_offset = 0
        self.var_declarations = []
        self.main_code = []
        self.errors = []

    def emit(self, instruction):
        self.main_code.append(instruction)

    def generate(self, ast):
        if ast is None:
            return []

        self.code = []
        self.var_declarations = []
        self.main_code = []

        self._generate_code(ast)

        # Concatena declarações + start + código + stop
        full_code = []
        full_code += self.var_declarations
        full_code.append("start")
        full_code += self.main_code
        full_code.append("stop")

        return full_code

    def _generate_code(self, node):
        if node is None:
            return

        method = getattr(self, f"_generate_{node.type}", None)
        if method:
            method(node)
        else:
            for child in node.children:
                self._generate_code(child)

    def _generate_program(self, node):
        self._generate_code(node.children[0])

    def _generate_block(self, node):
        for child in node.children:
            self._generate_code(child)

    def _generate_declarations(self, node):
        for child in node.children:
            self._generate_code(child)

    def _generate_var_declarations(self, node):
        for child in node.children:
            self._generate_code(child)
            
    def _generate_halt(self, node):
        self.emit("stop")


    def _generate_var_declaration(self, node):
        ids_node, type_node = node.children
        var_type = type_node.leaf
        for id_node in ids_node.children:
            var_name = id_node.leaf
            symbol = self.symtab.lookup(var_name)
            if symbol:
                if symbol.address is None:
                    symbol.address = self.current_offset
                    self.current_offset += 1
                # Gerar declaração da variável
                #comment = f"// inicio declaracao da variavel \"{var_name}\""
                #self.var_declarations.append(comment)
                self.var_declarations.append(f"pushi 0")
                self.var_declarations.append(f"storeg {symbol.address}")
                #self.var_declarations.append(f"// fim declaracao da variavel \"{var_name}\"")

    def _generate_statement_list(self, node):
        for stmt in node.children:
            self._generate_code(stmt)

    def _generate_assignment(self, node):
        var_node = node.children[0]
        expr_node = node.children[1]

        self._generate_code(expr_node)

        if var_node.type == 'variable':
            symbol = self.symtab.lookup(var_node.leaf)
            self.emit(f"storeg {symbol.address}")

    def _generate_variable(self, node):
        symbol = self.symtab.lookup(node.leaf)
        self.emit(f"pushg {symbol.address}")

    def _generate_integer(self, node):
        self.emit(f"pushi {node.leaf}")
        
    def _generate_real(self, node):
        self.emit(f"pushf {node.leaf}")

    def _generate_string(self, node):
        self.emit(f"pushs \"{node.leaf}\"")

    def _generate_boolean(self, node):
        self.emit(f"pushi {1 if node.leaf == 'true' else 0}")

    def _generate_binary_op(self, node):
        self._generate_code(node.children[0])
        self._generate_code(node.children[1])

        op = node.leaf
        if op == '+':
            self.emit("add")
        elif op == '-':
            self.emit("sub")
        elif op == '*':
            self.emit("mul")
        elif op == 'div':
            self.emit("div")
        elif op == '/':
            self.emit("fdiv")
        elif op == 'mod':
            self.emit("mod")
        elif op == '=':
            self.emit("equal")
        elif op == '<':
            self.emit("inf")
        elif op == '<=':
            self.emit("infeq")
        elif op == '>':
            self.emit("sup")
        elif op == '>=':
            self.emit("supeq")
        elif op == '<>':
            self.emit("equal")
            self.emit("not")
        elif op == 'and':
            self.emit("and")
        elif op == 'or':
            self.emit("or")

    def _generate_unary_op(self, node):
        self._generate_code(node.children[0])
        if node.leaf == 'not':
            self.emit("not")
        elif node.leaf == '-':
            self.emit("pushi -1")
            self.emit("mul")

    def _generate_if(self, node):
        false_label = self._new_label("ELSE")
        end_label = self._new_label("ENDIF")

        self._generate_code(node.children[0])
        self.emit(f"jz {false_label}")

        self._generate_code(node.children[1])
        self.emit(f"jump {end_label}")

        self.emit(f"{false_label}:")
        if len(node.children) > 2:
            self._generate_code(node.children[2])
        self.emit(f"{end_label}:")

    def _generate_while(self, node):
        start_label = self._new_label("WHILE")
        end_label = self._new_label("ENDWHILE")

        self.emit(f"{start_label}:")
        self._generate_code(node.children[0])
        self.emit(f"jz {end_label}")
        self._generate_code(node.children[1])
        self.emit(f"jump {start_label}")
        self.emit(f"{end_label}:")

    def _generate_for(self, node):
        var_node = node.children[0]
        var_name = var_node.leaf
        direction = node.leaf  # "to" ou "downto"
        symbol = self.symtab.lookup(var_name)
        if not symbol:
            self.errors.append(f"Erro: variável '{var_name}' não declarada")
            return

        end_label = self._new_label("ENDFOR")
        start_label = self._new_label("FOR")

        # Valor inicial
        self._generate_code(node.children[1])
        self.emit(f"storeg {symbol.address}")

        # Reserva memória e guarda valor final
        final_var = self.current_offset
        self.current_offset += 1
        self.var_declarations.append(f"pushi 0")
        self.var_declarations.append(f"storeg {final_var}")

        self._generate_code(node.children[2])
        self.emit(f"storeg {final_var}")

        self.emit(f"{start_label}:")
        self.emit(f"pushg {symbol.address}")
        self.emit(f"pushg {final_var}")

        self.emit("sup" if direction == "to" else "inf")
        self.emit(f"jnz {end_label}")


        self._generate_code(node.children[3])

        self.emit(f"pushg {symbol.address}")
        self.emit(f"pushi {-1 if direction == 'downto' else 1}")
        self.emit("add")
        self.emit(f"storeg {symbol.address}")
        self.emit(f"jump {start_label}")
        self.emit(f"{end_label}:")

    def _generate_writeln(self, node):
        if node.children:
            for expr in node.children[0].children:
                self._generate_code(expr)
                if expr.type == 'string':
                    self.emit("writes")
                else:
                    self.emit("writei")
        self.emit("writeln")

    def _generate_readln(self, node):
        for var_node in node.children:
            # Verifica o tipo da variável
            if var_node.type == 'variable':
                symbol = self.symtab.lookup(var_node.leaf)
                self.emit("read")

                if symbol.type == 'real':
                    self.emit("atof")  # <-- conversão para float
                else:
                    self.emit("atoi")  # <-- conversão para int (como antes)

                self.emit(f"storeg {symbol.address}")
            else:
                print(f"[ERRO] _generate_readln: tipo inesperado {var_node.type}")


    def _new_label(self, base):
        label = f"{base}{self.label_counter}"
        self.label_counter += 1
        return label
