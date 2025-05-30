from src.tabela_de_simbolos import TabelaSimbolos

class AnalisadorSemantico:
    def __init__(self):
        self.tabela_de_simbolos = TabelaSimbolos()
        self.erros = []
        self.alertas = []
        self.escopo_atual = None

    def analisar(self, ast):
        if ast is None:
            return False
        self._analisar_no(ast)
        return len(self.erros) == 0

    def _analisar_no(self, no):
        if no is None:
            return None
        
        print(f"📍 Analisando nó: {no.tipo}")

        nome_metodo = f"_analisar_{no.tipo}"
        metodo = getattr(self, nome_metodo, None)
        if metodo:
            return metodo(no)
        else:
            for filho in no.filhos:
                self._analisar_no(filho)

    def _analisar_programa(self, no):
        return self._analisar_no(no.filhos[0])

    def _analisar_bloco(self, no):
        for filho in no.filhos:
            self._analisar_no(filho)

    def _analisar_declaracoes(self, no):
        for filho in no.filhos:
            self._analisar_no(filho)

    def _analisar_declaracoes_variaveis(self, no):
        for filho in no.filhos:
            self._analisar_no(filho)

    def _analisar_declaracao_variavel(self, no):
        lista_ids, no_tipo = no.filhos
        tipo_var = no_tipo.folha

        if tipo_var == "string_bounded":
            tamanho_str = no_tipo.filhos[0].folha
            for var in lista_ids.filhos:
                self.tabela_de_simbolos.adicionar_simbolo(
                    var.folha,
                    tipo="string",
                    categoria="variable",
                    tamanho=int(tamanho_str)
                )
        else:
            for var in lista_ids.filhos:
                if no_tipo.tipo == "array_tipo":
                    no_intervalo = no_tipo.filhos[0]
                    tipo_base = no_tipo.filhos[1].folha

                    limite_inferior = int(no_intervalo.filhos[0].folha)
                    limite_superior = int(no_intervalo.filhos[1].folha)
                    tamanho = limite_superior - limite_inferior + 1

                    self.tabela_de_simbolos.adicionar_simbolo(
                        var.folha,
                        tipo="array",
                        categoria="variable",
                        tamanho=tamanho,
                        dimensoes=(limite_inferior, limite_superior),
                        tipo_elemento=tipo_base
                    )
                else:
                    self.tabela_de_simbolos.adicionar_simbolo(
                        var.folha,
                        tipo=tipo_var,
                        categoria="variable"
                    )

    def _analisar_declaracao_funcao(self, no):
        id_func = no.filhos[0].folha
        lista_params = no.filhos[1]
        tipo_retorno = no.filhos[2].folha

        self.tabela_de_simbolos.adicionar_simbolo(id_func, tipo=tipo_retorno, categoria='function')
        self.tabela_de_simbolos.enter_scope(id_func)

        for param in lista_params.filhos:
            ids, no_tipo = param.filhos
            for id_no in ids.filhos:
                self.tabela_de_simbolos.adicionar_simbolo(id_no.folha, tipo=no_tipo.folha, categoria='parameter')

        self._analisar_no(no.filhos[3])
        self.tabela_de_simbolos.exit_scope()

    def _analisar_composto(self, no):
        return self._analisar_no(no.filhos[0])

    def _analisar_lista_comandos(self, no):
        for instrucao in no.filhos:
            self._analisar_no(instrucao)

    def _analisar_atribuicao(self, no):
        no_var = no.filhos[0]
        no_expr = no.filhos[1]
        tipo_var = self._obter_tipo_expressao(no_var)
        tipo_expr = self._obter_tipo_expressao(no_expr)
        if tipo_var and tipo_expr and tipo_var != tipo_expr:
            self.erros.append(f"Erro de tipo: não é possível atribuir '{tipo_expr}' a '{tipo_var}'")

    def _analisar_se(self, no):
        tipo_cond = self._obter_tipo_expressao(no.filhos[0])
        if tipo_cond != 'boolean':
            self.erros.append("Erro: condição do 'se' deve ser booleana")
        self._analisar_no(no.filhos[1])
        if len(no.filhos) > 2:
            self._analisar_no(no.filhos[2])

    def _analisar_enquanto(self, no):
        tipo_cond = self._obter_tipo_expressao(no.filhos[0])
        if tipo_cond != 'boolean':
            self.erros.append("Erro: condição do 'enquanto' deve ser booleana")
        self._analisar_no(no.filhos[1])

    def _analisar_para(self, no):
        self._analisar_no(no.filhos[1])  # valor inicial
        self._analisar_no(no.filhos[2])  # valor final
        self._analisar_no(no.filhos[3])  # corpo

    def _analisar_chamada_procedimento(self, no):
        nome_proc = no.filhos[0].folha
        simbolo = self.tabela_de_simbolos.procurar(nome_proc)
        if not simbolo:
            self.erros.append(f"Erro: procedimento '{nome_proc}' não declarado")

    def _analisar_escreva(self, no):
        if no.filhos:
            self._analisar_no(no.filhos[0])

    def _analisar_leia(self, no):
        for no_var in no.filhos:
            if self.tabela_de_simbolos.procurar(no_var.folha) is None:
                self.erros.append(f"Erro: variável '{no_var.folha}' não declarada")

    def _analisar_operacao_binaria(self, no):
        tipo_esq = self._obter_tipo_expressao(no.filhos[0])
        tipo_dir = self._obter_tipo_expressao(no.filhos[1])
        op = no.folha.lower()
        # continue sua lógica aqui

    def _analisar_operacao_unaria(self, no):
        return self._obter_tipo_expressao(no.filhos[0])

    def _obter_tipo_expressao(self, no):
        if no is None:
            return None
        if no.tipo == 'inteiro':
            return 'integer'
        elif no.tipo == 'real':
            return 'real'
        elif no.tipo == 'saida_formatada':
            return self._obter_tipo_expressao(no.filhos[0])
        elif no.tipo == 'booleano':
            return 'boolean'
        elif no.tipo == 'string':
            return 'string'
        elif no.tipo == 'variavel':
            simbolo = self.tabela_de_simbolos.procurar(no.folha)
            if simbolo:
                return simbolo.tipo
            else:
                self.erros.append(f"Erro: variável '{no.folha}' não declarada")
                return None
        elif no.tipo == 'acesso_array':
            nome_array = no.folha
            info_array = self.tabela_de_simbolos.procurar(nome_array)
            if info_array is None:
                self.erros.append(f"Erro: variável '{nome_array}' não declarada")
                return None
            if not hasattr(info_array, "tipo_elemento") or info_array.tipo_elemento is None:
                self.erros.append(f"Erro: '{nome_array}' não é um array")
                return None
            tipo_indice = self._obter_tipo_expressao(no.filhos[0])
            if tipo_indice != 'integer':
                self.erros.append(f"Erro: índice do array '{nome_array}' deve ser inteiro")
            return info_array.tipo_elemento
        elif no.tipo in ['operacao_binaria', 'operacao_unaria']:
            return self._analisar_no(no)
        return None
