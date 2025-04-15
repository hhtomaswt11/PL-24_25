import ply.lex as lex, sys 

class PascalLexer:
    """
    Analisador léxico para a linguagem Pascal Standard.
    Converte o código fonte em uma sequência de tokens.
    """
    
    # Lista de nomes de tokens
    tokens = [
        'ID',             # Identificadores
        'INTEGER',        # Números inteiros
        'REAL',           # Números reais
        'STRING',         # Strings
        'PLUS',           # Operador +
        'MINUS',          # Operador -
        'TIMES',          # Operador *
        'DIVIDE',         # Operador /
        'LPAREN',         # (
        'RPAREN',         # )
        'LBRACKET',       # [
        'RBRACKET',       # ]
        'SEMICOLON',      # ;
        'COLON',          # :
        'COMMA',          # ,
        'PERIOD',         # .
        'ASSIGN',         # :=
        'EQ',             # =
        'NEQ',            # <>
        'LT',             # <
        'GT',             # >
        'LE',             # <=
        'GE',             # >=
        'APOSTROPHE',     # '
        'COMMENT',        # Comentários
    ]
    
    # Palavras-chave da linguagem Pascal
    reserved = {
        'and': 'AND',
        'array': 'ARRAY',
        'begin': 'BEGIN',
        'case': 'CASE',
        'const': 'CONST',
        'div': 'DIV',
        'do': 'DO',
        'downto': 'DOWNTO',
        'else': 'ELSE',
        'end': 'END',
        'file': 'FILE',
        'for': 'FOR',
        'function': 'FUNCTION',
        'goto': 'GOTO',
        'if': 'IF',
        'in': 'IN',
        'label': 'LABEL',
        'mod': 'MOD',
        'nil': 'NIL',
        'not': 'NOT',
        'of': 'OF',
        'or': 'OR',
        'packed': 'PACKED',
        'procedure': 'PROCEDURE',
        'program': 'PROGRAM',
        'record': 'RECORD',
        'repeat': 'REPEAT',
        'set': 'SET',
        'then': 'THEN',
        'to': 'TO',
        'type': 'TYPE',
        'until': 'UNTIL',
        'var': 'VAR',
        'while': 'WHILE',
        'with': 'WITH',
        'true': 'TRUE',
        'false': 'FALSE',
        'boolean': 'BOOLEAN',
        'integer': 'INTEGER_TYPE',
        'real': 'REAL_TYPE',
        'string': 'STRING_TYPE',
        'char': 'CHAR_TYPE',
        'writeln': 'WRITELN',
        'readln': 'READLN',
        'write': 'WRITE',
        'read': 'READ',
        'halt': 'HALT',
    }
    
    # Adiciona as palavras-chave à lista de tokens
    tokens = tokens + list(reserved.values())
    
    # Regras de expressões regulares para tokens simples
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_SEMICOLON = r';'
    t_COLON = r':'
    t_COMMA = r','
    t_PERIOD = r'\.'
    t_EQ = r'='
    t_NEQ = r'<>'
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_APOSTROPHE = r'\''

    # Regra para o operador de atribuição (:=)
    def t_ASSIGN(self, t):
        r':='
        return t
    
    # Regra para identificadores
    def t_ID(self, t): # Para poder diferenciar qual string recebe 
        r'[a-zA-Z][a-zA-Z0-9_]*'
        # Verifica se é uma palavra-chave
        t.type = self.reserved.get(t.value.lower(), 'ID')
        return t
    
    # Regra para números reais
    def t_REAL(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t
    
    # Regra para números inteiros
    def t_INTEGER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t
    
    # Regra para strings
    def t_STRING(self, t):
        r"'[^']*'"
        t.value = t.value[1:-1]  # remove as aspas
        return t

    
    # Regra para comentários
    def t_COMMENT(self, t):
        r'\{[^}]*\}|\(\*[\s\S]*?\*\)'
        # Ignora comentários
        pass
    
    # Regra para ignorar espaços e tabs
    t_ignore = ' \t'
    
    # Regra para novas linhas
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    # Tratamento de erros
    def t_error(self, t):
        print(f"Caracter ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
        t.lexer.skip(1)
    
    # Construção do lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer
    
    # Análise de uma entrada
    # def test(self, data):
    #     self.lexer.input(data)
    #     tokens = []
    #     for tok in self.lexer:
    #         tokens.append(tok)
    #     return tokens
    
    # Reinicializa o lexer
    def reset(self):
        self.lexer.lineno = 1


# Função para criar uma instância do lexer
def create_lexer():
    lexer = PascalLexer()
    return lexer.build()


