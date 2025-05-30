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

        # Mapeamento entre tipos do nó e métodos
        mapa_tipos = {
            "programa": "programa",
            "bloco": "bloco",
            "declaracoes": "declaracoes",
            "declaracoes_variaveis": "declaracoes_variaveis",
            "declaracao_variavel": "declaracao_variavel",
            "composto": "composto",
            "lista_comandos": "lista_comandos",
            "writeln": "writeln",
            "readln": "readln",
            "variavel": "variavel",
            "atribuicao": "atribuicao",
            "for": "for",
            "id": "id",
            "inteiro": "inteiro",
            "real": "real",
            "string": "string",
            "booleano": "booleano",
            "operacao_binaria": "operacao_binaria",
            "operacao_unaria": "operacao_unaria",
            "se": "se",
            "enquanto": "enquanto",
            "acesso_array": "acesso_array",
            # Adicione mais se necessário
        }

        tipo = no.tipo
        metodo_nome = f"_gerar_{mapa_tipos.get(tipo, '')}"
        metodo = getattr(self, metodo_nome, None)

        if metodo:
            metodo(no)
        else:
            # Caso não encontre método, desce recursivamente
            for filho in no.filhos:
                self._gerar_codigo(filho)

    def _gerar_programa(self, no):
        self._gerar_codigo(no.filhos[0])

    def _gerar_bloco(self, no):
        for filho in no.filhos:
            self._gerar_codigo(filho)

    def _gerar_declaracoes(self, no):
        for filho in no.filhos:
            self._gerar_codigo(filho)

    def _gerar_declaracoes_variaveis(self, no):
        for filho in no.filhos:
            self._gerar_codigo(filho)

    def _gerar_declaracao_variavel(self, no):
        ids_node, tipo_node = no.filhos
        tipo_variavel = tipo_node.folha if tipo_node.folha else tipo_node.tipo

        for id_node in ids_node.filhos:
            nome_variavel = id_node.folha
            simbolo = self.tabela_simbolos.procurar(nome_variavel)

            if simbolo:
                if simbolo.endereco is None:
                    simbolo.endereco = self.offset_atual

                    if simbolo.tipo == "array":
                        self.declaracoes_variaveis.append(f"pushi {simbolo.size}")
                        self.declaracoes_variaveis.append("allocn")
                        self.declaracoes_variaveis.append(f"storeg {simbolo.endereco}")

                        for i in range(simbolo.size):
                            self.declaracoes_variaveis.append(f"pushst {simbolo.endereco}")
                            self.declaracoes_variaveis.append("pushi 0")
                            self.declaracoes_variaveis.append(f"store {i}")

                        self.offset_atual += 1
                    else:
                        self.declaracoes_variaveis.append("pushi 0")
                        self.declaracoes_variaveis.append(f"storeg {simbolo.endereco}")
                        self.offset_atual += 1

    def _gerar_composto(self, no):
        for filho in no.filhos:
            self._gerar_codigo(filho)

    def _gerar_lista_comandos(self, no):
        for stmt in no.filhos:
            self._gerar_codigo(stmt)

    def _gerar_atribuicao(self, no):
        var_node = no.filhos[0]
        expr_node = no.filhos[1]

        self._gerar_codigo(expr_node)

        simbolo = self.tabela_simbolos.procurar(var_node.folha)
        if simbolo is None:
            print(f"[ERRO] variável '{var_node.folha}' não declarada")
            return
        
        if simbolo.endereco is None:
            simbolo.endereco = self.offset_atual
            self.declaracoes_variaveis.append("pushi 0")
            self.declaracoes_variaveis.append(f"storeg {simbolo.endereco}")
            self.offset_atual += 1

        self.emitir(f"storeg {simbolo.endereco}")

    def _gerar_variavel(self, no):
        simbolo = self.tabela_simbolos.procurar(no.folha)
        if simbolo is None:
            print(f"[ERRO] variável '{no.folha}' não declarada")
            return
        
        if simbolo.endereco is None:
            simbolo.endereco = self.offset_atual
            self.declaracoes_variaveis.append("pushi 0")
            self.declaracoes_variaveis.append(f"storeg {simbolo.endereco}")
            self.offset_atual += 1

        self.emitir(f"pushg {simbolo.endereco}")

    def _gerar_inteiro(self, no):
        self.emitir(f"pushi {no.folha}")

    def _gerar_real(self, no):
        self.emitir(f"pushf {no.folha}")

    def _gerar_string(self, no):
        self.emitir(f'pushs "{no.folha}"')

    def _gerar_booleano(self, no):
        self.emitir(f"pushi {1 if no.folha == 'true' else 0}")

    def _gerar_operacao_binaria(self, no):
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

    def _gerar_operacao_unaria(self, no):
        self._gerar_codigo(no.filhos[0])
        if no.folha == 'not':
            self.emitir("not")
        elif no.folha == '-':
            self.emitir("pushi -1")
            self.emitir("mul")

    def _gerar_se(self, no):
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

    def _gerar_enquanto(self, no):
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
        simbolo = self.tabela_simbolos.procurar(nome_var)

        if not simbolo:
            self.erros.append(f"Erro: variável '{nome_var}' não declarada")
            return

        self.contador = simbolo.endereco
        rotulo_fim = self._novo_rotulo("FIMPARA")
        rotulo_inicio = self._novo_rotulo("PARA")

        self._gerar_codigo(no.filhos[1])
        self.emitir(f"storeg {simbolo.endereco}")

        final_var = self.offset_atual
        self.offset_atual += 1
        self.declaracoes_variaveis.append("pushi 0")
        self.declaracoes_variaveis.append(f"storeg {final_var}")

        self._gerar_codigo(no.filhos[2])
        self.emitir(f"storeg {final_var}")

        self.emitir(f"{rotulo_inicio}:")
        self.emitir(f"pushg {simbolo.endereco}")
        self.emitir(f"pushg {final_var}")

        self.emitir("sup" if direcao == "to" else "inf")
        self.emitir("not")
        self.emitir(f"jz {rotulo_fim}")

        self._gerar_codigo(no.filhos[3])
        self.emitir(f"pushg {simbolo.endereco}")
        self.emitir(f"pushi {-1 if direcao == 'downto' else 1}")
        self.emitir("add")
        self.emitir(f"storeg {simbolo.endereco}")
        self.emitir(f"jump {rotulo_inicio}")
        self.emitir(f"{rotulo_fim}:")

    def _gerar_writeln(self, no):
        if no.filhos:
            for expr in no.filhos[0].filhos:
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
            if var_node.tipo == 'variavel':
                simbolo = self.tabela_simbolos.procurar(var_node.folha)
                if simbolo is None:
                    print(f"[ERRO] _gerar_readln: variável '{var_node.folha}' não declarada")
                    continue
                self.emitir("read")
                if simbolo.tipo == 'real':
                    self.emitir("atof")
                else:
                    self.emitir("atoi")
                self.emitir(f"storeg {simbolo.endereco}")

            elif var_node.tipo == 'acesso_array':
                nome_array = var_node.folha
                simbolo = self.tabela_simbolos.procurar(nome_array)
                if simbolo is None:
                    print(f"[ERRO] _gerar_readln: variável '{nome_array}' não declarada")
                    continue
                self.emitir("read")
                if simbolo.tipo == 'real':
                    self.emitir("atof")
                else:
                    self.emitir("atoi")

                self._gerar_codigo(var_node.filhos[0])  # índice do array
                self.emitir(f"storean {simbolo.endereco}")

    def _novo_rotulo(self, prefixo):
        self.contador_labels += 1
        return f"{prefixo}_{self.contador_labels}"
