import ply.yacc as yacc
from src.analisador_lexico import AnalisadorLexico, criar_analisador_lexico
from src.tabela_de_simbolos import TabelaSimbolos

class NoAST:
    """Classe base para nós da Árvore Sintática Abstrata (AST)."""
    def __init__(self, tipo, filhos=None, folha=None):
        self.tipo = tipo            # Tipo do nó - inteiro, operacao_binaria, etc 
        self.filhos = filhos if filhos else []  # Filhos do nó - operandos de uma operação, etc
        self.folha = folha          # Valor da folha, se for folha - valor literal 'x', '2', '4', etc
    
    def __repr__(self):
        return f"{self.tipo}({self.folha if self.folha is not None else ''})"


class PascalParser:
    """
    Analisador sintático para a linguagem Pascal Standard.
    Cria uma árvore sintática abstrata (AST) a partir dos tokens.
    """
    
    def __init__(self):
        # Inicializa o lexer
        self.lexer = criar_analisador_lexico()
        
        # Obtém os tokens do lexer
        # self.tokens = AnalisadorLexico.tokens + list(AnalisadorLexico.reserved.values())
        self.tokens = AnalisadorLexico.tokens
        
        # Inicializa a tabela de símbolos
        self.tabela_simbolos = TabelaSimbolos()
        
        # Variáveis para rastreio de erros
        self.erros = []
        
        # Inicializa o parser
        self.parser = yacc.yacc(module=self) # Cria o parser compilando as regras p_ 
        
    # Definições das regras gramaticais.
    
    # Regra para a unidade completa do programa
    def p_programa(self, p):
        '''programa : PROGRAM ID SEMICOLON bloco PERIOD'''
        p[0] = NoAST('programa', [p[4]], p[2])
    
    # Regra para blocos (estrutura base do programa)
    def p_bloco(self, p):
        '''bloco : declaracoes comando_composto'''
        p[0] = NoAST('bloco', [p[1], p[2]])

    def p_declaracoes(self, p):
        '''declaracoes : VAR declaracoes_variaveis
                       | declaracao_funcao
                       | vazio'''
        if len(p) == 3:
            p[0] = NoAST('declaracoes', [p[2]])
        elif p[1] is not None:
            p[0] = NoAST('declaracoes', [p[1]])
        else:
            p[0] = NoAST('declaracoes')
        
    def p_bloco_funcao(self, p):
        '''bloco_funcao : VAR declaracoes_variaveis comando_composto
                        | comando_composto'''
        if len(p) == 4:
            # VAR declarações + begin...end
            p[0] = NoAST('bloco', [NoAST('declaracoes', [p[2]]), p[3]])
        else:
            # apenas begin...end
            p[0] = NoAST('bloco', [NoAST('declaracoes'), p[1]])


    def p_declaracao(self, p):
        '''declaracao : VAR declaracoes_variaveis
                      | declaracao_funcao'''
        p[0] = p[2] if p[1].lower() == 'var' else p[1]

    
    # Regra para declarações de variáveis
    def p_declaracoes_variaveis(self, p):
        '''declaracoes_variaveis : declaracoes_variaveis declaracao_variavel
                                 | declaracao_variavel'''
        if len(p) > 2:
            p[1].filhos.append(p[2])
            p[0] = p[1]
        else:
            p[0] = NoAST('declaracoes_variaveis', [p[1]])
    
    # Regra para uma única declaração de variável
    def p_declaracao_variavel(self, p):
        '''declaracao_variavel : lista_ids COLON especificacao_tipo SEMICOLON'''
        p[0] = NoAST('declaracao_variavel', [p[1], p[3]])
        
        # Adiciona as variáveis à tabela de símbolos
        tipo_var = p[3].folha
        for id_var in p[1].filhos:
            self.tabela_simbolos.adicionar_simbolo(id_var.folha, tipo_var, categoria="variavel")
    
    # Regra para lista de identificadores
    def p_lista_ids(self, p):
        '''lista_ids : lista_ids COMMA ID
                     | ID'''
        if len(p) > 2:
            p[1].filhos.append(NoAST('id', folha=p[3]))
            p[0] = p[1]
        else:
            p[0] = NoAST('lista_ids', [NoAST('id', folha=p[1])])
    
    # Regra para especificação de tipos
    def p_especificacao_tipo(self, p):
        '''especificacao_tipo : INTEGER_TYPE
                              | REAL_TYPE
                              | BOOLEAN
                              | STRING_TYPE
                              | CHAR_TYPE
                              | tipo_array'''
        if len(p) == 2:
            if isinstance(p[1], NoAST):  # Se for tipo_array
                p[0] = p[1]
            else:
                p[0] = NoAST('tipo', folha=p[1])
    
    # Regra para tipos array
    def p_tipo_array(self, p):
        '''tipo_array : ARRAY LBRACKET INTEGER PERIOD PERIOD INTEGER RBRACKET OF especificacao_tipo'''
        p[0] = NoAST('tipo_array', [NoAST('intervalo', [NoAST('inteiro', folha=p[3]), NoAST('inteiro', folha=p[6])]), p[9]])
    
    # Regra para bloco de comandos
    def p_comando_composto(self, p):
        '''comando_composto : BEGIN lista_comandos END'''
        p[0] = NoAST('composto', [p[2]])
    
    # Regra para lista de comandos
    def p_lista_comandos(self, p):
        '''lista_comandos : lista_comandos SEMICOLON comando
                          | comando'''
        if len(p) > 2:
            if p[3] is not None:  # Ignorar comandos vazios
                p[1].filhos.append(p[3])
            p[0] = p[1]
        else:
            if p[1] is not None:
                p[0] = NoAST('lista_comandos', [p[1]])
            else:
                p[0] = NoAST('lista_comandos')
    
    # Regra para um único comando
    def p_comando(self, p):
        '''comando : comando_composto
                   | comando_atribuicao
                   | comando_if
                   | comando_while
                   | comando_for
                   | chamada_procedimento
                   | comando_halt
                   | vazio'''
        p[0] = p[1]
    
    # Regra para comando de atribuição
    def p_comando_atribuicao(self, p):
        '''comando_atribuicao : variavel ASSIGN expressao'''
        p[0] = NoAST('atribuicao', [p[1], p[3]])
    
    def p_variavel(self, p):
        '''variavel : ID
                    | ID LBRACKET expressao RBRACKET''' # arrays 
        if len(p) > 2:
            p[0] = NoAST('acesso_array', [p[3]], folha=p[1])
        else:
            p[0] = NoAST('variavel', folha=p[1])
            

    # Regra para comando if-then-else
    def p_comando_if(self, p):
        '''comando_if : IF expressao THEN comando
                      | IF expressao THEN comando ELSE comando'''
                        
        if len(p) > 5:
            p[0] = NoAST('if', [p[2], p[4], p[6]])
        else:
            p[0] = NoAST('if', [p[2], p[4]])
    
    # Regra para comando while
    def p_comando_while(self, p):
        '''comando_while : WHILE expressao DO comando'''
        p[0] = NoAST('while', [p[2], p[4]])

    # Regra para comando for
    def p_comando_for(self, p):
        '''comando_for : FOR ID ASSIGN expressao TO expressao DO comando
                       | FOR ID ASSIGN expressao DOWNTO expressao DO comando'''
        direcao = 'to' if p[5] == 'to' else 'downto'
        p[0] = NoAST('for', [NoAST('id', folha=p[2]), p[4], p[6], p[8]], direcao)
    
    # Regra para chamada de procedimento
    def p_chamada_procedimento(self, p):
        '''chamada_procedimento : ID LPAREN lista_expressoes RPAREN
                                | ID LPAREN RPAREN
                                | WRITELN LPAREN lista_expressoes RPAREN
                                | WRITELN LPAREN RPAREN
                                | READLN LPAREN variavel RPAREN
                                | READLN LPAREN RPAREN'''
        if p[1].lower() in ('writeln', 'readln'):
            if len(p) > 4:
                if p[1].lower() == 'writeln':
                    p[0] = NoAST('writeln', [p[3]])
                else:  # readln
                    p[0] = NoAST('readln', [p[3]])
            else:
                p[0] = NoAST(p[1].lower(), [])
        else:
            if len(p) > 4:
                p[0] = NoAST('chamada_procedimento', [NoAST('id', folha=p[1]), p[3]])
            else:
                p[0] = NoAST('chamada_procedimento', [NoAST('id', folha=p[1])])
    
    def p_lista_expressoes(self, p):
        '''lista_expressoes : lista_expressoes COMMA expressao
                            | expressao'''
        if len(p) > 2:
              p[1].filhos.append(p[3])
              p[0] = p[1]
        else:
             p[0] = NoAST('lista_expressoes', [p[1]])



    # Regra para expressões
    def p_expressao(self, p):
        '''expressao : expressao_simples
                     | expressao_simples relop expressao_simples'''
        if len(p) > 2:
            p[0] = NoAST('operacao_binaria', [p[1], p[3]], p[2])
        else:
            p[0] = p[1]
    
    # Regra para operadores relacionais
    def p_relop(self, p):
        '''relop : EQ
                 | NEQ
                 | LT
                 | LE
                 | GT
                 | GE
                 | IN'''
        p[0] = p[1]
    
    # Regra para expressões simples
    def p_expressao_simples(self, p):
        '''expressao_simples : termo
                             | expressao_simples addop termo'''
        if len(p) > 2:
            p[0] = NoAST('operacao_binaria', [p[1], p[3]], p[2])
        else:
            p[0] = p[1]
    
    # Regra para operadores de adição
    def p_addop(self, p):
        '''addop : PLUS
                 | MINUS
                 | OR'''
        p[0] = p[1]
    
    # Regra para termos
    def p_termo(self, p):
        '''termo : fator
                 | termo mulop fator'''
        if len(p) > 2:
            p[0] = NoAST('operacao_binaria', [p[1], p[3]], p[2])
        else:
            p[0] = p[1]
    
    # Regra para operadores de multiplicação
    def p_mulop(self, p):
        '''mulop : TIMES
                 | DIVIDE
                 | DIV
                 | MOD
                 | AND'''
        p[0] = p[1]
    
    # Regra para fatores
    def p_fator(self, p):
        '''fator : variavel
                 | INTEGER
                 | REAL
                 | STRING
                 | TRUE
                 | FALSE
                 | LPAREN expressao RPAREN
                 | NOT fator
                 | chamada_funcao'''
        if len(p) == 2:
            if isinstance(p[1], NoAST):  # Variável ou chamada de função
                p[0] = p[1]
            elif isinstance(p[1], int):
                p[0] = NoAST('inteiro', folha=p[1])
            elif isinstance(p[1], float):
                p[0] = NoAST('real', folha=p[1])
            elif p[1] in ('true', 'false'):
                p[0] = NoAST('booleano', folha=p[1])
            else:
                p[0] = NoAST('string', folha=p[1])
        elif len(p) == 3:  # NOT fator
            p[0] = NoAST('operacao_unaria', [p[2]], p[1])
        else:  # LPAREN expressao RPAREN
            p[0] = p[2]
    
    def p_expressao_formatada(self,p): # NOVO 
        '''expressao : variavel COLON INTEGER
                     | variavel COLON INTEGER COLON INTEGER'''
        if len(p) == 4:
            p[0] = NoAST('saida_formatada', [p[1], NoAST('inteiro', folha=p[3])])
        else:
            p[0] = NoAST('saida_formatada', [p[1], NoAST('inteiro', folha=p[3]), NoAST('inteiro', folha=p[5])])
    

    # Regra para chamada de função
    def p_chamada_funcao(self, p):
        '''chamada_funcao : ID LPAREN lista_expressoes RPAREN
                          | ID LPAREN RPAREN'''
        if len(p) > 4:
            p[0] = NoAST('chamada_funcao', [NoAST('id', folha=p[1]), p[3]])
        else:
            p[0] = NoAST('chamada_funcao', [NoAST('id', folha=p[1])])
    

    def p_declaracao_funcao(self, p):
        '''declaracao_funcao : FUNCTION ID LPAREN lista_parametros RPAREN COLON especificacao_tipo SEMICOLON bloco_funcao SEMICOLON'''
        p[0] = NoAST('declaracao_funcao', [NoAST('id', folha=p[2]), p[4], p[7], p[9]])

            
    def p_lista_parametros(self, p):
        '''lista_parametros : lista_parametros SEMICOLON parametro
                            | parametro'''
        if len(p) > 2:
            p[1].filhos.append(p[3])
            p[0] = p[1]
        else:
            p[0] = NoAST('lista_parametros', [p[1]])

    def p_parametro(self, p):
        '''parametro : lista_ids COLON especificacao_tipo'''
        p[0] = NoAST('parametro', [p[1], p[3]])


    # Regra para comando halt
    def p_comando_halt(self, p):
        '''comando_halt : HALT SEMICOLON'''
        p[0] = NoAST('halt')


    # Regra para produções vazias
    def p_vazio(self, p):
        'vazio :'
        p[0] = None

    # Tratamento de erros
    def p_error(self, p):
        if p:
            mensagem_erro = f"Erro de sintaxe na linha {p.lineno}, token '{p.value}'"
            self.erros.append(mensagem_erro)
            print(mensagem_erro)
        else:
            self.erros.append("Erro de sintaxe: fim inesperado do ficheiro")
            print("Erro de sintaxe: fim inesperado do ficheiro")


    # Método para analisar uma string
    def parse(self, dados):
        self.erros = []
        return self.parser.parse(dados, lexer=self.lexer)
    # Inicia a análise léxica e sintática ao mesmo tempo.
    # O texto é entregue ao lexer, que o transforma em TOKENS com base nas regras t_.
    # Com base nos tokens, o parser tenta casar com alguma regra p_. Se casar, a AST começa a ser construída.
    # Cada regra retorna um NoAST, atribuindo-o a p[0].
    # No fim da análise, o valor de p[0] na regra inicial (p_programa) é retornado.
    # É aplicada uma análise semântica sobre a AST, recursivamente.
    # Retorna a AST.


# Função para criar uma instância do parser
def criar_parser():
    return PascalParser()
