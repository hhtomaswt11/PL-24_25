class GeradorDeCodigo:
    def __init__(self, tabela_simbolos):
        self.tabela_simbolos = tabela_simbolos
        self.codigo = []
        self.contador_temporario = 0
        self.contador_labels = 0
        self.offset_atual = 0
        self.contador = 0
        self.declaracoes_variaveis = []
        self.codigo_principal = []
        self.erros = []

    def emitir(self, instrucao):
        self.codigo_principal.append(instrucao)

    def gerar(self, ast):
        if ast is None:
            return []

        self.codigo = []
        self.declaracoes_variaveis = []
        self.codigo_principal = []

        self._gerar_codigo(ast)

        # Junta declarações + start + corpo + stop
        codigo_completo = []
        codigo_completo += self.declaracoes_variaveis
        codigo_completo.append("start")
        codigo_completo += self.codigo_principal
        codigo_completo.append("stop")

        return codigo_completo

    def _gerar_codigo(self, no):
        if no is None:
            return

        metodo = getattr(self, f"_gerar_{no.tipo}", None)
        if metodo:
            metodo(no)
        else:
            for filho in no.filhos:
                self._gerar_codigo(filho)

    def _gerar_program(self, no):
        self._gerar_codigo(no.filhos[0])

    def _gerar_block(self, no):
        for filho in no.filhos:
            self._gerar_codigo(filho)

    def _gerar_declarations(self, no):
        for filho in no.filhos:
            self._gerar_codigo(filho)

    def _gerar_var_declarations(self, no):
        for filho in no.filhos:
            self._gerar_codigo(filho)

    def _gerar_halt(self, no):
        self.emitir("stop")

    def _gerar_var_declaration(self, no):
        ids_node, tipo_node = no.filhos
        tipo_variavel = tipo_node.folha if tipo_node.folha else tipo_node.tipo

        for id_node in ids_node.filhos:
            nome_variavel = id_node.folha
            simbolo = self.tabela_simbolos.lookup(nome_variavel)

            if simbolo:
                if simbolo.address is None:
                    simbolo.address = self.offset_atual

                    if simbolo.tipo == "array":
                        self.declaracoes_variaveis.append(f"pushi {simbolo.size}")
                        self.declaracoes_variaveis.append("allocn")
                        self.declaracoes_variaveis.append(f"storeg {simbolo.address}")

                        for i in range(simbolo.size):
                            self.declaracoes_variaveis.append(f"pushst {simbolo.address}")
                            self.declaracoes_variaveis.append("pushi 0")
                            self.declaracoes_variaveis.append(f"store {i}")

                        self.offset_atual += 1
                    else:
                        self.declaracoes_variaveis.append("pushi 0")
                        self.declaracoes_variaveis.append(f"storeg {simbolo.address}")
                        self.offset_atual += 1

    def _gerar_statement_list(self, no):
        for stmt in no.filhos:
            self._gerar_codigo(stmt)

    def _gerar_assignment(self, no):
        var_node = no.filhos[0]
        expr_node = no.filhos[1]

        self._gerar_codigo(expr_node)

        if var_node.tipo == 'variable':
            simbolo = self.tabela_simbolos.lookup(var_node.folha)
            self.emitir(f"storeg {simbolo.address}")

    def _gerar_variable(self, no):
        simbolo = self.tabela_simbolos.lookup(no.folha)
        
        if hasattr(self, '_apos_loadn') and self._apos_loadn:
            self._apos_loadn = False
            return
        
        print('sexto pushg')
        self.emitir(f"pushg {simbolo.address}")

    def _gerar_integer(self, no):
        self.emitir(f"pushi {no.folha}")

    def _gerar_real(self, no):
        self.emitir(f"pushf {no.folha}")

    def _gerar_string(self, no):
        self.emitir(f'pushs "{no.folha}"')

    def _gerar_boolean(self, no):
        self.emitir(f"pushi {1 if no.folha == 'true' else 0}")

    def _gerar_binary_op(self, no):
        self._gerar_codigo(no.filhos[0])
        self._gerar_codigo(no.filhos[1])

        op = no.folha
        match op:
            case '+': self.emitir("add")
            case '-': self.emitir("sub")
            case '*': self.emitir("mul")
            case 'div': self.emitir("div")
            case '/': self.emitir("fdiv")
            case 'mod': self.emitir("mod")
            case '=': self.emitir("equal")
            case '<': self.emitir("inf")
            case '<=': self.emitir("infeq")
            case '>': self.emitir("sup")
            case '>=': self.emitir("supeq")
            case '<>':
                self.emitir("equal")
                self.emitir("not")
            case 'and': self.emitir("and")
            case 'or': self.emitir("or")

    def _gerar_unary_op(self, no):
        self._gerar_codigo(no.filhos[0])
        if no.folha == 'not':
            self.emitir("not")
        elif no.folha == '-':
            self.emitir("pushi -1")
            self.emitir("mul")

    def _gerar_if(self, no):
        rotulo_falso = self._novo_rotulo("SENAO")
        rotulo_fim = self._novo_rotulo("FIMSE")

        self._gerar_codigo(no.filhos[0])
        self.emitir(f"jz {rotulo_falso}")
        self._gerar_codigo(no.filhos[1])
        self.emitir(f"jump {rotulo_fim}")
        self.emitir(f"{rotulo_falso}:")
        if len(no.filhos) > 2:
            self._gerar_codigo(no.filhos[2])
        self.emitir(f"{rotulo_fim}:")

    def _gerar_while(self, no):
        rotulo_inicio = self._novo_rotulo("ENQUANTO")
        rotulo_fim = self._novo_rotulo("FIMENQUANTO")

        self.emitir(f"{rotulo_inicio}:")
        self._gerar_codigo(no.filhos[0])
        self.emitir(f"jz {rotulo_fim}")
        self._gerar_codigo(no.filhos[1])
        self.emitir(f"jump {rotulo_inicio}")
        self.emitir(f"{rotulo_fim}:")

    def _gerar_for(self, no):
        var_node = no.filhos[0]
        nome_var = var_node.folha
        direcao = no.folha  # "to" ou "downto"
        simbolo = self.tabela_simbolos.lookup(nome_var)

        if not simbolo:
            self.erros.append(f"Erro: variável '{nome_var}' não declarada")
            return

        self.contador = simbolo.address
        rotulo_fim = self._novo_rotulo("FIMPARA")
        rotulo_inicio = self._novo_rotulo("PARA")

        self._gerar_codigo(no.filhos[1])
        self.emitir(f"storeg {simbolo.address}")

        final_var = self.offset_atual
        self.offset_atual += 1
        self.declaracoes_variaveis.append("pushi 0")
        self.declaracoes_variaveis.append(f"storeg {final_var}")

        self._gerar_codigo(no.filhos[2])
        self.emitir(f"storeg {final_var}")

        self.emitir(f"{rotulo_inicio}:")
        self.emitir(f"pushg {simbolo.address}")
        self.emitir(f"pushg {final_var}")

        self.emitir("sup" if direcao == "to" else "inf")
        self.emitir("not")
        self.emitir(f"jz {rotulo_fim}")

        self._gerar_codigo(no.filhos[3])
        self.emitir(f"pushg {simbolo.address}")
        self.emitir(f"pushi {-1 if direcao == 'downto' else 1}")
        self.emitir("add")
        self.emitir(f"storeg {simbolo.address}")
        self.emitir(f"jump {rotulo_inicio}")
        self.emitir(f"{rotulo_fim}:")

    def _gerar_writeln(self, no):
        if no.filhos:
            for expr in no.filhos[0].filhos:
                if expr.tipo == 'formatted_output':
                    self._gerar_codigo(expr)
                else:
                    self._gerar_codigo(expr)
                    if expr.tipo == 'string':
                        self.emitir("writes")
                    elif expr.tipo == 'real':
                        self.emitir("writef")
                    else:
                        self.emitir("writei")
        self.emitir("writeln")

    def _gerar_readln(self, no):
        for var_node in no.filhos:
            if var_node.tipo == 'variable':
                simbolo = self.tabela_simbolos.lookup(var_node.folha)
                self.emitir("read")
                if simbolo.tipo == 'real':
                    self.emitir("atof")
                else:
                    self.emitir("atoi")
                self.emitir(f"storeg {simbolo.address}")
            elif var_node.tipo == 'array_access':
                nome_array = var_node.folha
                simbolo = self.tabela_simbolos.lookup(nome_array)
                if simbolo is None or simbolo.tipo != 'array':
                    print(f"[ERRO] _gerar_readln: '{nome_array}' não é um array válido")
                    continue

                self.emitir(f"pushst {simbolo.address}")
                self.emitir(f"pushg {self.contador}")
                self.emitir("pushi 1")
                self.emitir("sub")
                self.emitir("read")
                self.emitir("atoi")
                self.emitir("storen")
            else:
                print(f"[ERRO] _gerar_readln: tipo inesperado {var_node.tipo}")

    def _gerar_array_access(self, no):
        nome_array = no.folha
        index_expr = no.filhos[0]

        simbolo = self.tabela_simbolos.lookup(nome_array)
        if simbolo is None or simbolo.tipo != 'array':
            print(f"[ERRO] _gerar_array_access: '{nome_array}' não é um array válido")
            return

        self.emitir(f"pushst {simbolo.address}")
        self.emitir(f"pushg {self.contador}")
        self.emitir("pushi 1")
        self.emitir("sub")
        self.emitir("loadn")

        self._apos_loadn = True

        self._gerar_codigo(index_expr)

    def _novo_rotulo(self, base):
        rotulo = f"{base}{self.contador_labels}"
        self.contador_labels += 1
        return rotulo
