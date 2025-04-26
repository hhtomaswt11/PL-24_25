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


    # def _generate_var_declaration(self, node):
    #     ids_node, type_node = node.children
    #     var_type = type_node.leaf
    #     for id_node in ids_node.children:
    #         var_name = id_node.leaf
    #         symbol = self.symtab.lookup(var_name)
    #         if symbol:
    #             if symbol.address is None:
    #                 symbol.address = self.current_offset
    #                 self.current_offset += 1
    #             # Gerar declaração da variável
    #             #comment = f"// inicio declaracao da variavel \"{var_name}\""
    #             #self.var_declarations.append(comment)
    #             self.var_declarations.append(f"pushi 0")
    #             self.var_declarations.append(f"storeg {symbol.address}")
    #             #self.var_declarations.append(f"// fim declaracao da variavel \"{var_name}\"")







    def _generate_var_declaration(self, node):
        ids_node, type_node = node.children
        var_type = type_node.leaf if type_node.leaf else type_node.type  # cobre tipo simples e array_type

        for id_node in ids_node.children:
            var_name = id_node.leaf
            symbol = self.symtab.lookup(var_name)

            if symbol:
                if symbol.address is None:
                    symbol.address = self.current_offset

                    if symbol.type == "array":
                        for i in range(symbol.size):
                            self.var_declarations.append("pushi 0")
                            self.var_declarations.append(f"storeg {symbol.address + i}")
                        self.current_offset += symbol.size
                    else:
                        self.var_declarations.append("pushi 0")
                        self.var_declarations.append(f"storeg {symbol.address}")
                        self.current_offset += 1











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
        
        
    # def _generate_formatted_output(self, node): # NOVO 
    #     var_node = node.children[0]
    #     width = node.children[1].leaf
    #     precision = node.children[2].leaf if len(node.children) > 2 else None

    #     symbol = self.symtab.lookup(var_node.leaf)
    #     self.emit(f"pushg {symbol.address}")

    #     if symbol.type == 'real':
    #         if precision is not None:
    #             self.emit(f"fprecision {precision}")
    #         self.emit(f"fwidth {width}")
    #         self.emit("writef")
    #     elif symbol.type == 'integer':
    #         self.emit(f"iwidth {width}")
    #         self.emit("writei")
    #     else:
    #         self.emit("writes")  # Para string, sem formatação por agora
            


    # def _generate_formatted_output(self, node):
    #     var_node = node.children[0]
    #     symbol = self.symtab.lookup(var_node.leaf)

    #     # Verifica o tipo e gera o código correto
    #     if symbol.type == 'real':
    #         self.emit(f"pushg {symbol.address}")
    #         self.emit("strf")       # Converte real para string
    #         self.emit("writes")     # Escreve string
    #     elif symbol.type == 'integer':
    #         self.emit(f"pushg {symbol.address}")
    #         self.emit("stri")       # Converte inteiro para string
    #         self.emit("writes")     # Escreve string
    #     else:
    #         self.emit(f"pushg {symbol.address}")
    #         self.emit("writes")     # String já é string :)







    # def _generate_formatted_output(self, node):
    #     var_node = node.children[0]
    #     symbol = self.symtab.lookup(var_node.leaf)

    #     self.emit(f"pushg {symbol.address}")
    #     if symbol.type == 'real':
    #         self.emit("strf")
    #     elif symbol.type == 'integer':
    #         self.emit("stri")
    #     self.emit("writes")




         
        
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

        # self.emit("sup" if direction == "to" else "inf")
        # self.emit(f"jnz {end_label}")
        self.emit("sup" if direction == "to" else "inf")
        self.emit("not")  # Inverte a condição
        self.emit(f"jz {end_label}")




        self._generate_code(node.children[3])

        self.emit(f"pushg {symbol.address}")
        self.emit(f"pushi {-1 if direction == 'downto' else 1}")
        self.emit("add")
        self.emit(f"storeg {symbol.address}")
        self.emit(f"jump {start_label}")
        self.emit(f"{end_label}:")

    # def _generate_writeln(self, node):
    #     if node.children:
    #         for expr in node.children[0].children:
    #             self._generate_code(expr)
    #             if expr.type == 'string':
    #                 self.emit("writes")
    #             else:
    #                 self.emit("writei")
    #     self.emit("writeln")
    
    def _generate_writeln(self, node):
        if node.children:
            for expr in node.children[0].children:
                if expr.type == 'formatted_output':
                    self._generate_code(expr)  # já inclui writef ou writei
                else:
                    self._generate_code(expr)
                    if expr.type == 'string':
                        self.emit("writes")
                    elif expr.type == 'real':
                        self.emit("writef")  # ← opcional se tiveres float direto
                    else:
                        self.emit("writei")
        self.emit("writeln")





    # def _generate_readln(self, node):
    #     for var_node in node.children:
    #         if var_node.type == 'variable':
    #             symbol = self.symtab.lookup(var_node.leaf)
    #             self.emit("read")
    #             if symbol.type == 'real':
    #                 self.emit("atof")
    #             else:
    #                 self.emit("atoi")
    #             self.emit(f"storeg {symbol.address}")
            
    #         elif var_node.type == 'array_access':
    #             array_name = var_node.leaf
    #             symbol = self.symtab.lookup(array_name)
    #             if symbol is None or symbol.type != 'array':
    #                 print(f"[ERRO] _generate_readln: '{array_name}' não é um array válido")
    #                 continue

    #             # Gera o índice
    #             self._generate_code(var_node.children[0])  # índice
    #             lower_bound = symbol.dimensions[0]
    #             if lower_bound != 0:
    #                 self.emit(f"pushi {lower_bound}")
    #                 self.emit("sub")

    #             self.emit("read")
    #             if symbol.element_type == 'real':
    #                 self.emit("atof")
    #             else:
    #                 self.emit("atoi")
                
    #             # Calcula endereço: base + deslocamento
    #             self.emit(f"pushi {symbol.address}")
    #             self.emit("add")  # offset + base
    #             self.emit("store 0")  # store no endereço calculado

    #         else:
    #             print(f"[ERRO] _generate_readln: tipo inesperado {var_node.type}")




    # Correção para a função que lê valores para arrays
    def _generate_readln(self, node):
        for var_node in node.children:
            if var_node.type == 'variable':
                symbol = self.symtab.lookup(var_node.leaf)
                self.emit("read")
                if symbol.type == 'real':
                    self.emit("atof")
                else:
                    self.emit("atoi")
                self.emit(f"storeg {symbol.address}")
            
            elif var_node.type == 'array_access':
                array_name = var_node.leaf
                symbol = self.symtab.lookup(array_name)
                if symbol is None or symbol.type != 'array':
                    print(f"[ERRO] _generate_readln: '{array_name}' não é um array válido")
                    continue

                # Coloca o endereço base do array na pilha
                self.emit(f"pushi {symbol.address}")
                
                # Gera o índice
                self._generate_code(var_node.children[0])  # índice
                
                # Subtrai o lower bound se não for zero
                lower_bound = symbol.dimensions[0]
                if lower_bound != 0:
                    self.emit(f"pushi {lower_bound}")
                    self.emit("sub")
                
                # Calcula endereço: base + deslocamento
                self.emit("add")  # Agora temos o endereço calculado no topo da pilha
                
                # Lê o valor e converte conforme necessário
                self.emit("read")
                if symbol.element_type == 'real':
                    self.emit("atof")
                else:
                    self.emit("atoi")
                
                # Armazena o valor no endereço calculado
                # ATENÇÃO: A ordem aqui é crucial - o valor lido está no topo da pilha,
                # e precisamos trocá-lo com o endereço para usar store corretamente
                self.emit("store 0")  # Armazena o valor lido no endereço calculado
            
            else:
                print(f"[ERRO] _generate_readln: tipo inesperado {var_node.type}")
            

    # ant 
    # def _generate_array_access(self, node):
    #         array_name = node.leaf
    #         index_expr = node.children[0]

    #         symbol = self.symtab.lookup(array_name)
    #         if symbol is None or symbol.type != 'array':
    #             print(f"[ERRO] _generate_array_access: '{array_name}' não é um array válido")
    #             return

    #         self._generate_code(index_expr)

    #         # Subtrai o lower bound se não for zero
    #         lower_bound = symbol.dimensions[0]
    #         if lower_bound != 0:
    #             self.emit(f"pushi {lower_bound}")
    #             self.emit("sub")

    #         # Adiciona ao endereço base do array
    #         self.emit(f"pushi {symbol.address}")
    #         self.emit("add")
    #         self.emit("load 0")  # ← leitura indireta do endereço calculado
    
    
    # Correção para a função que acessa arrays
    def _generate_array_access(self, node):
        array_name = node.leaf
        index_expr = node.children[0]

        symbol = self.symtab.lookup(array_name)
        if symbol is None or symbol.type != 'array':
            print(f"[ERRO] _generate_array_access: '{array_name}' não é um array válido")
            return

        # Primeiro coloca o endereço base do array na pilha
        self.emit(f"pushi {symbol.address}")
        
        # Gera o índice
        self._generate_code(index_expr)
        
        # Subtrai o lower bound se não for zero
        lower_bound = symbol.dimensions[0]
        if lower_bound != 0:
            self.emit(f"pushi {lower_bound}")
            self.emit("sub")
        
        # Adiciona ao endereço base do array (que já está na pilha)
        self.emit("add")  # Agora temos o endereço calculado no topo da pilha
        
        # Carrega o valor do endereço calculado
        self.emit("pushg 0")  # Coloca um valor qualquer na pilha
        self.emit("load 0")   # Carrega o valor do endereço calculado



    def _new_label(self, base):
        label = f"{base}{self.label_counter}"
        self.label_counter += 1
        return label

