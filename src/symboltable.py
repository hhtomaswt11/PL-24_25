class Symbol:
    """
    Classe que representa um símbolo na tabela de símbolos.
    Um símbolo pode ser uma variável, constante, função, procedimento, etc.
    """
    def __init__(self, name, type=None, value=None, kind=None, params=None, scope=None, address=None):
        self.name = name          # Nome do símbolo
        self.type = type          # Tipo do símbolo (inteiro, real, boolean, etc.)
        self.value = value        # Valor para constantes
        self.kind = kind          # Tipo de símbolo (variável, função, etc.)
        self.params = params      # Parâmetros para funções e procedimentos
        self.scope = scope        # Escopo do símbolo
        self.address = address    # Endereço na memória virtual
        self.size = 1             # Tamanho do símbolo (para arrays)
        self.dimensions = None    # Dimensões para arrays
        self.element_type = None  # Tipo dos elementos do array (ex: integer)
        self.return_value = None  # Para armazenar o valor de retorno da função durante a execução

    def __repr__(self):
        kind_str = f"'{self.kind}'" if self.kind else "None"
        type_str = f"'{self.type}'" if self.type else "None"
        scope_str = f"'{self.scope}'" if self.scope else "None"
        return f"Symbol(name='{self.name}', type={type_str}, kind={kind_str}, scope={scope_str})"


class SymbolTable:
    """
    Tabela de símbolos para armazenar informações sobre identificadores no programa.
    Implementa escopos aninhados.
    """
    def __init__(self):
        # Escopo global
        self.scopes = [{}]
        self.current_scope = 0
        self.scope_names = ["global"]
        
        # Rastreia os símbolos de função atualmente definidos
        self.current_function = None
        
    def enter_scope(self, name):
        """Cria um novo escopo aninhado."""
        self.scopes.append({})
        self.current_scope += 1
        self.scope_names.append(name)
        
        # Se o nome for de uma função, armazena como função atual
        if name != "global" and self.lookup(name) and self.lookup(name).kind in ("function", "procedure"):
            self.current_function = name
            
        return self.current_scope
    
    def exit_scope(self):
        """Sai do escopo atual e retorna para o escopo pai."""
        if self.current_scope > 0:
            self.scopes.pop()
            self.scope_names.pop()
            self.current_scope -= 1
            
            # Se saimos do escopo de uma função, limpa a função atual
            if self.current_function and self.current_scope == 0:
                self.current_function = None
                
        return self.current_scope



    def add_symbol(self, name, type=None, value=None, kind=None, params=None, address=None, size=1, dimensions=None, element_type=None):
        """Adiciona um símbolo na tabela de símbolos, incluindo suporte para arrays, funções e procedimentos."""
        
        # Escopo onde o símbolo será inicialmente criado
        scope_name = self.scope_names[self.current_scope]

        # Cria o símbolo principal
        symbol = Symbol(name, type, value, kind, params, scope_name, address)

        # Tratamento especial para arrays
        if type == "array":
            symbol.type = "array"
            symbol.size = size
            symbol.dimensions = dimensions
            symbol.element_type = element_type

        # Se for função ou procedimento, adicionar ao escopo global e criar escopo próprio
        if kind in ("function", "procedure"):
            # Força escopo global para visibilidade
            self.scopes[0][name] = symbol

            # Entra no escopo da função/procedimento
            self.enter_scope(name)

            # Atualiza o escopo do símbolo para o novo escopo
            symbol.scope = self.scope_names[self.current_scope]
            
            # debug 
            print(f">>> Escopo atual ({self.current_scope}) após entrar em {name}: {self.scope_names[self.current_scope]}")


            # Adiciona parâmetros ao escopo local da função
            if params and hasattr(params, "children"):
                for param in params.children:
                    param_kind = "parameter"
                    if hasattr(param, "leaf") and param.leaf == 'reference':
                        param_kind = "reference_parameter"

                    if hasattr(param, "children") and len(param.children) >= 2:
                        id_list = param.children[0]
                        type_node = param.children[1]
                        param_type = type_node.leaf if hasattr(type_node, "leaf") else None

                        for id_node in id_list.children:
                            if hasattr(id_node, "leaf"):
                                self.add_symbol(id_node.leaf, type=param_type, kind=param_kind)

            # Adiciona símbolo da própria função ao escopo local
            if kind == "function":
                #return_symbol = Symbol(name, type, value, kind, params, self.scope_names[self.current_scope], address)
                return_symbol = Symbol(name, type, value, kind, None, self.scope_names[self.current_scope], address)

                self.scopes[self.current_scope][name] = return_symbol

            return symbol

        # Símbolos normais (variáveis, constantes etc.)
        self.scopes[self.current_scope][name] = symbol
        return symbol

    
    
    
    
    def lookup(self, name, current_scope_only=False):
        """
        Procura um símbolo pelo nome. Começa pelo escopo atual
        e vai subindo na hierarquia de escopos se não encontrar.
        """
        if current_scope_only:
            if name in self.scopes[self.current_scope]:
                return self.scopes[self.current_scope][name]
            return None
        
        # Procura em todos os escopos, começando pelo atual
        for scope_idx in range(self.current_scope, -1, -1):
            if name in self.scopes[scope_idx]:
                return self.scopes[scope_idx][name]
        
        return None
    
    def update_symbol(self, name, **kwargs):
        """Atualiza um símbolo existente."""
        symbol = self.lookup(name)
        if symbol:
            for key, value in kwargs.items():
                if hasattr(symbol, key):
                    setattr(symbol, key, value)
            return symbol
        return None
    
    def get_all_symbols(self):
        """Retorna todos os símbolos de todos os escopos."""
        all_symbols = []
        for scope_idx, scope in enumerate(self.scopes):
            for name, symbol in scope.items():
                all_symbols.append(symbol)
        return all_symbols
    
    def get_current_function(self):
        """Retorna o símbolo da função atual, se estivermos dentro de uma função."""
        if self.current_function:
            return self.lookup(self.current_function)
        return None