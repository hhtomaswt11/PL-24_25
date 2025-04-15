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

    def __repr__(self):
        return f"Symbol(name='{self.name}', type='{self.type}', kind='{self.kind}', scope='{self.scope}')"


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
        
    def enter_scope(self, name):
        """Cria um novo escopo aninhado."""
        self.scopes.append({})
        self.current_scope += 1
        self.scope_names.append(name)
        return self.current_scope
    
    def exit_scope(self):
        """Sai do escopo atual e retorna para o escopo pai."""
        if self.current_scope > 0:
            self.scopes.pop()
            self.scope_names.pop()
            self.current_scope -= 1
        return self.current_scope

    def add_symbol(self, name, type=None, value=None, kind=None, params=None, address=None, size=1, dimensions=None, element_type=None):
        """Adiciona um símbolo na tabela de símbolos, incluindo suporte para arrays."""
        scope_name = self.scope_names[self.current_scope]
        
        # Criar um símbolo normal
        symbol = Symbol(name, type, value, kind, params, scope_name, address)
        
        # Se for um array, definir as propriedades específicas
        if type == "array":
            symbol.type = "array"  # Define explicitamente o tipo como array
            symbol.size = size
            symbol.dimensions = dimensions
            symbol.element_type = element_type  # Define o tipo dos elementos (ex: integer)

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


if __name__ == "__main__":
    # Teste da tabela de símbolos
    symtab = SymbolTable()
    
    # Adiciona símbolos ao escopo global
    symtab.add_symbol("x", "integer", kind="variable")
    symtab.add_symbol("y", "real", kind="variable")
    
    # Adiciona um array
    symtab.add_symbol("numeros", type="array", kind="variable", size=5, dimensions=(1, 5), element_type="integer")
    print(symtab.lookup("numeros"))  # Deve mostrar um objeto com element_type='integer'

    
    # Cria um novo escopo para uma função
    symtab.enter_scope("func1")
    symtab.add_symbol("a", "integer", kind="parameter")
    symtab.add_symbol("result", "integer", kind="variable")
    
    # Testa lookup
    print(symtab.lookup("a"))  # Deve encontrar no escopo atual
    print(symtab.lookup("x"))  # Deve encontrar no escopo global
    print(symtab.lookup("z"))  # Não deve encontrar (None)
    
    # Sai do escopo da função
    symtab.exit_scope()
    
    # Deve retornar None porque 'a' está no escopo da função
    print(symtab.lookup("a"))
    
    # Testar se o array está com as propriedades certas
    print(symtab.lookup("numeros"))
