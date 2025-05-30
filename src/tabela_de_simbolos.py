class Simbolo:
    """
    Representa um símbolo na tabela de símbolos.
    Pode ser uma variável, constante, função, procedimento, etc.
    """
    def __init__(self, nome, tipo=None, valor=None, categoria=None, parametros=None, escopo=None, endereco=None):
        self.nome = nome                # Nome do símbolo
        self.tipo = tipo                # Tipo de dados (ex: inteiro, real, booleano, etc.)
        self.valor = valor              # Valor, se for uma constante
        self.categoria = categoria      # Papel do símbolo: variável, função, parâmetro, etc.
        self.parametros = parametros    # Lista de parâmetros (se for função ou procedimento)
        self.escopo = escopo            # Nome do escopo onde o símbolo foi definido
        self.endereco = endereco        # Endereço na memória (para VM)
        self.tamanho = 1                # Tamanho (útil para arrays)
        self.dimensoes = None           # Dimensões (se for array)
        self.tipo_elemento = None       # Tipo dos elementos do array

    def __repr__(self):
        return f"Simbolo(nome='{self.nome}', tipo='{self.tipo}', categoria='{self.categoria}', escopo='{self.escopo}')"


class TabelaSimbolos:
    """
    Estrutura para armazenar informações sobre identificadores do programa.
    Suporta escopos aninhados.
    """
    def __init__(self):
        self.escopos = [{}]                # Lista de dicionários por escopo
        self.escopo_atual = 0              # Índice do escopo atual
        self.nomes_escopos = ["global"]    # Nomes dos escopos

    def entrar_escopo(self, nome):
        """Cria um novo escopo."""
        self.escopos.append({})
        self.escopo_atual += 1
        self.nomes_escopos.append(nome)
        return self.escopo_atual

    def sair_escopo(self):
        """Sai do escopo atual, voltando ao anterior."""
        if self.escopo_atual > 0:
            self.escopos.pop()
            self.nomes_escopos.pop()
            self.escopo_atual -= 1
        return self.escopo_atual

    def adicionar_simbolo(self, nome, tipo=None, valor=None, categoria=None, parametros=None, endereco=None, tamanho=1, dimensoes=None, tipo_elemento=None):
        """Adiciona um símbolo à tabela, com suporte a arrays."""
        escopo_nome = self.nomes_escopos[self.escopo_atual]

        simbolo = Simbolo(nome, tipo, valor, categoria, parametros, escopo_nome, endereco)

        if tipo == "array":
            simbolo.tipo = "array"
            simbolo.tamanho = tamanho
            simbolo.dimensoes = dimensoes
            simbolo.tipo_elemento = tipo_elemento

        self.escopos[self.escopo_atual][nome] = simbolo
        return simbolo

    def procurar(self, nome, apenas_escopo_atual=False):
        """
        Procura um símbolo pelo nome, começando no escopo atual.
        Se `apenas_escopo_atual` for True, só procura nesse escopo.
        """
        if apenas_escopo_atual:
            return self.escopos[self.escopo_atual].get(nome)

        for i in range(self.escopo_atual, -1, -1):
            if nome in self.escopos[i]:
                return self.escopos[i][nome]
        return None

    def atualizar_simbolo(self, nome, **novos_valores):
        """Atualiza os atributos de um símbolo existente."""
        simbolo = self.procurar(nome)
        if simbolo:
            for chave, valor in novos_valores.items():
                if hasattr(simbolo, chave):
                    setattr(simbolo, chave, valor)
            return simbolo
        return None

    def obter_todos_simbolos(self):
        """Retorna todos os símbolos de todos os escopos."""
        simbolos = []
        for escopo in self.escopos:
            simbolos.extend(escopo.values())
        return simbolos



# if __name__ == "__main__":
#     # Teste da tabela de símbolos
#     tabela = TabelaSimbolos()
    
#     # Adicionar símbolos ao escopo global
#     tabela.adicionar_simbolo("x", "inteiro", categoria="variável")
#     tabela.adicionar_simbolo("y", "real", categoria="variável")
    
#     # Adicionar um array
#     tabela.adicionar_simbolo("numeros", tipo="array", categoria="variável", tamanho=5, dimensoes=(1, 5), tipo_elemento="inteiro")
#     print(tabela.procurar("numeros"))  # Deve mostrar um objeto com tipo_elemento='inteiro'

#     # Criar um novo escopo para uma função
#     tabela.entrar_escopo("funcao1")
#     tabela.adicionar_simbolo("a", "inteiro", categoria="parâmetro")
#     tabela.adicionar_simbolo("resultado", "inteiro", categoria="variável")
    
#     # Testar procura
#     print(tabela.procurar("a"))  # Deve encontrar no escopo atual
#     print(tabela.procurar("x"))  # Deve encontrar no escopo global
#     print(tabela.procurar("z"))  # Não deve encontrar (None)

#     # Sair do escopo da função
#     tabela.sair_escopo()
    
#     # Deve retornar None porque 'a' está no escopo da função
#     print(tabela.procurar("a"))
    
#     # Verificar se o array está com as propriedades certas
#     print(tabela.procurar("numeros"))
