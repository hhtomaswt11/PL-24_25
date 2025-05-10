import ply.yacc as yacc
from src.lexer import PascalLexer, create_lexer
from src.symboltable import SymbolTable

class ASTNode:
    """Classe base para nós da Árvore Sintática Abstrata (AST)."""
    def __init__(self, type, children=None, leaf=None):
        self.type = type            # Tipo do nó - integer, binary_op, etc 
        self.children = children if children else []  # Filhos do nó - operandos de uma operação, etc
        self.leaf = leaf            # Valor da folha, se for uma folha - valor literal 'x' '2' '4', etc
    
    def __repr__(self):
        return f"{self.type}({self.leaf if self.leaf is not None else ''})"


class PascalParser:
    """
    Analisador sintático para a linguagem Pascal Standard.
    Cria uma árvore sintática abstrata (AST) a partir dos tokens.
    """
    
    def __init__(self):
        # Inicializa o lexer
        self.lexer = create_lexer()
        
        # Obtém os tokens do lexer
        # self.tokens = PascalLexer.tokens + list(PascalLexer.reserved.values())
        self.tokens = PascalLexer.tokens
        
        # Inicializa a tabela de símbolos
        self.symtab = SymbolTable()
        
        # Variáveis para rastreamento de erro
        self.errors = []
        
        self.current_function = None 
        
        
        # Inicializa o parser
        self.parser = yacc.yacc(module=self) # Cria o parser ao compilar as regras p_ 
        

    # Definem regras gramaticais.
    
    # Regra para a unidade de programa completa
    def p_program(self, p):
        '''program : PROGRAM ID SEMICOLON block PERIOD'''
        p[0] = ASTNode('program', [p[4]], p[2])
    
    # Regra para blocos (estrutura básica do programa)
    def p_block(self, p):
        '''block : declarations compound_statement'''
        p[0] = ASTNode('block', [p[1], p[2]])

    def p_declarations(self, p):
        '''declarations : declaration declarations
                        | empty'''
        if len(p) == 3:
            if p[2].type == 'declarations':
                p[2].children.insert(0, p[1])
                p[0] = p[2]
            else:
                p[0] = ASTNode('declarations', [p[1]])
        else:
            p[0] = ASTNode('declarations', [])
            
    def p_declaration(self, p):
        '''declaration : VAR var_declarations
                    | function_declaration
                    | procedure_declaration'''
        if len(p) == 3:  # caso VAR
            p[0] = ASTNode('var_section', [p[2]])
        else:
            p[0] = p[1]

            
            
    def p_function_block(self, p):
        '''function_block : declarations compound_statement
                          | compound_statement'''
        if len(p) == 3:
            p[0] = ASTNode('block', [p[1], p[2]])
        else:
            p[0] = ASTNode('block', [ASTNode('declarations', []), p[1]])


    # Regra para declarações de funções
    # def p_function_declaration(self, p):
    #     '''function_declaration : FUNCTION ID LPAREN param_list RPAREN COLON type_spec SEMICOLON function_block SEMICOLON
    #                             | FUNCTION ID COLON type_spec SEMICOLON function_block SEMICOLON'''
    #     if len(p) == 11:  # Com parâmetros
    #         # AST: function_decl(id, param_list, return_type, block)
    #         p[0] = ASTNode('function_decl', [
    #             ASTNode('id', leaf=p[2]),  # Nome da função
    #             p[4],                      # Lista de parâmetros
    #             p[7],                      # Tipo de retorno
    #             p[9]                       # Bloco da função
    #         ])
    #     else:  # Sem parâmetros
    #         p[0] = ASTNode('function_decl', [
    #             ASTNode('id', leaf=p[2]),
    #             ASTNode('param_list'),     # Lista vazia de parâmetros
    #             p[4],                      # Tipo de retorno
    #             p[6]                       # Bloco da função
    #         ])
    
    
    def p_function_declaration(self, p):
        '''function_declaration : FUNCTION ID LPAREN param_list RPAREN COLON type_spec SEMICOLON function_block SEMICOLON
                                | FUNCTION ID COLON type_spec SEMICOLON function_block SEMICOLON'''
        self.current_function = p[2]  # Guarda nome da função ativa

        if len(p) == 11:  # Com parâmetros
            p[0] = ASTNode('function_decl', [
                ASTNode('id', leaf=p[2]), p[4], p[7], p[9]
            ])
        else:
            p[0] = ASTNode('function_decl', [
                ASTNode('id', leaf=p[2]), ASTNode('param_list'), p[4], p[6]
            ])

        self.current_function = None  # Sai da função




    # Regra para declarações de procedimentos
    def p_procedure_declaration(self, p):
        '''procedure_declaration : PROCEDURE ID LPAREN param_list RPAREN SEMICOLON function_block SEMICOLON
                                 | PROCEDURE ID SEMICOLON function_block SEMICOLON'''
        if len(p) == 9:  # Com parâmetros
            p[0] = ASTNode('procedure_decl', [ASTNode('id', leaf=p[2]), p[4], p[7]])
            
            # Adiciona na tabela de símbolos
            self.symtab.add_symbol(p[2], type=None, kind="procedure", params=p[4])
        else:  # Sem parâmetros
            p[0] = ASTNode('procedure_decl', [ASTNode('id', leaf=p[2]), ASTNode('param_list'), p[4]])
            
            # Adiciona na tabela de símbolos
            self.symtab.add_symbol(p[2], type=None, kind="procedure", params=ASTNode('param_list'))
    
    # Regra para declarações de variáveis
    def p_var_declarations(self, p):
        '''var_declarations : var_declarations var_declaration
                           | var_declaration'''
        if len(p) > 2:
            p[1].children.append(p[2])
            p[0] = p[1]
        else:
            p[0] = ASTNode('var_declarations', [p[1]])
    
    # Regra para uma única declaração de variável
    def p_var_declaration(self, p):
        '''var_declaration : id_list COLON type_spec SEMICOLON'''
        p[0] = ASTNode('var_declaration', [p[1], p[3]])
        
        # Adiciona as variáveis na tabela de símbolos
        var_type = p[3].leaf
        for var_id in p[1].children:
            self.symtab.add_symbol(var_id.leaf, var_type, kind="variable")
    
    # Regra para lista de identificadores
    def p_id_list(self, p):
        '''id_list : id_list COMMA ID
                  | ID'''
        if len(p) > 2:
            p[1].children.append(ASTNode('id', leaf=p[3]))
            p[0] = p[1]
        else:
            p[0] = ASTNode('id_list', [ASTNode('id', leaf=p[1])])
    
    # Regra para especificação de tipos
    def p_type_spec(self, p):
        '''type_spec : INTEGER_TYPE
                     | REAL_TYPE
                     | BOOLEAN
                     | STRING_TYPE
                     | CHAR_TYPE
                     | array_type'''
        if len(p) == 2:
            if isinstance(p[1], ASTNode):  # Se for um array_type
                p[0] = p[1]
            else:
                p[0] = ASTNode('type', leaf=p[1])
        elif p[1] == "char":
         p[0] = ASTNode("type", leaf="char_type")
          
    
    # Regra para tipos de array
    def p_array_type(self, p):
        '''array_type : ARRAY LBRACKET INTEGER PERIOD PERIOD INTEGER RBRACKET OF type_spec'''
        p[0] = ASTNode('array_type', [ASTNode('range', [ASTNode('integer', leaf=p[3]), ASTNode('integer', leaf=p[6])]), p[9]])
    
    # Regra para bloco de comandos
    def p_compound_statement(self, p):
        '''compound_statement : BEGIN statement_list END'''
        p[0] = ASTNode('compound', [p[2]])
    
    # Regra para lista de comandos
    def p_statement_list(self, p):
        '''statement_list : statement_list SEMICOLON statement
                         | statement'''
        if len(p) > 2:
            if p[3] is not None:  # Ignorar comandos vazios
                p[1].children.append(p[3])
            p[0] = p[1]
        else:
            if p[1] is not None:  # Ignorar comandos vazios
                p[0] = ASTNode('statement_list', [p[1]])
            else:
                p[0] = ASTNode('statement_list')
    
    # Regra para um único comando
    def p_statement(self, p):
        '''statement : compound_statement
                     | assignment_statement
                     | if_statement
                     | while_statement
                     | for_statement
                     | procedure_call_statement
                     | function_call_statement
                     | halt_statement
                     | empty'''
        p[0] = p[1]
    
    # Regra para comando de atribuição
    # def p_assignment_statement(self, p):
    #     '''assignment_statement : variable ASSIGN expression
    #                             | ID ASSIGN expression'''
    #     if isinstance(p[1], ASTNode):
    #         p[0] = ASTNode('assignment', [p[1], p[3]])
    #     else:
    #         func_symbol = self.symtab.lookup(p[1])
    #         print(f"DEBUG: tentativa de atribuição a '{p[1]}' → símbolo: {func_symbol}")
    #         if func_symbol and func_symbol.kind == 'function':
    #             p[0] = ASTNode('function_return', [ASTNode('id', leaf=p[1]), p[3]])
    #             print(f"DEBUG: atribuição a função {p[1]}")
    #         else:
    #             p[0] = ASTNode('assignment', [ASTNode('variable', leaf=p[1]), p[3]])
    
    
    
    def p_assignment_statement(self, p):
        '''assignment_statement : variable ASSIGN expression
                                | ID ASSIGN expression'''
        # Caso 1: lado esquerdo é ID simples (ex: Soma := ...)
        if isinstance(p[1], str):
            if self.current_function and p[1].lower() == self.current_function.lower():
                print(f"DEBUG: retorno reconhecido da função '{p[1]}'")
                p[0] = ASTNode('function_return', [ASTNode('id', leaf=p[1]), p[3]])
            else:
                print(f"DEBUG: atribuição comum a '{p[1]}'")
                p[0] = ASTNode('assignment', [ASTNode('variable', leaf=p[1]), p[3]])

        # Caso 2: lado esquerdo já é um ASTNode (ex: variável ou array)
        elif isinstance(p[1], ASTNode):
            # Pode ser: variable(ID)
            if p[1].type == "variable" and self.current_function and p[1].leaf == self.current_function:
                print(f"DEBUG: retorno reconhecido da função '{p[1].leaf}'")
                p[0] = ASTNode('function_return', [ASTNode('id', leaf=p[1].leaf), p[3]])
            else:
                print(f"DEBUG: atribuição comum a '{p[1].leaf}'")
                p[0] = ASTNode('assignment', [p[1], p[3]])

                    
    def p_variable(self, p):
        '''variable : ID
                | ID LBRACKET expression RBRACKET''' # arrays 
        if len(p) > 2:
            p[0] = ASTNode('array_access', [p[3]], leaf=p[1])
        else:
            p[0] = ASTNode('variable', leaf=p[1])
            

    # Regra para comando if-then-else
    def p_if_statement(self, p):
        '''if_statement : IF expression THEN statement
                        | IF expression THEN statement ELSE statement'''
                        
        if len(p) > 5:
            p[0] = ASTNode('if', [p[2], p[4], p[6]])
        else:
            p[0] = ASTNode('if', [p[2], p[4]])
    
    # Regra para comando while
    def p_while_statement(self, p):
        '''while_statement : WHILE expression DO statement'''
        p[0] = ASTNode('while', [p[2], p[4]])

    # Regra para comando for
    def p_for_statement(self, p):
        '''for_statement : FOR ID ASSIGN expression TO expression DO statement
                        | FOR ID ASSIGN expression DOWNTO expression DO statement'''
        direction = 'to' if p[5] == 'to' else 'downto'
        p[0] = ASTNode('for', [ASTNode('id', leaf=p[2]), p[4], p[6], p[8]], direction)
    
    # Regra para chamada de procedimento
    def p_procedure_call_statement(self, p):
        '''procedure_call_statement : ID LPAREN expression_list RPAREN
                                   | ID LPAREN RPAREN
                                   | WRITELN LPAREN expression_list RPAREN
                                   | WRITELN LPAREN RPAREN
                                   | READLN LPAREN variable RPAREN
                                   | READLN LPAREN RPAREN'''
        if p[1].lower() in ('writeln', 'readln'):
            if len(p) > 4:
                if p[1].lower() == 'writeln':
                    p[0] = ASTNode('writeln', [p[3]])
                else:  # readln
                    p[0] = ASTNode('readln', [p[3]])
            else:
                p[0] = ASTNode(p[1].lower(), [])
        else:
            if len(p) > 4:
                p[0] = ASTNode('procedure_call', [ASTNode('id', leaf=p[1]), p[3]])
            else:
                p[0] = ASTNode('procedure_call', [ASTNode('id', leaf=p[1])])
    
    # Regra específica para chamada de função como um statement
    def p_function_call_statement(self, p):
        '''function_call_statement : function_call'''
        p[0] = ASTNode('function_call_stmt', [p[1]])
    
    def p_expression_list(self, p):
        '''expression_list : expression_list COMMA expression
                           | expression'''
        if len(p) > 2:
              p[1].children.append(p[3])
              p[0] = p[1]
        else:
             p[0] = ASTNode('expression_list', [p[1]])

    def p_param_list(self, p):
        '''param_list : param_list SEMICOLON param
                      | param
                      | empty'''
        if len(p) == 1 or p[1] is None:
            p[0] = ASTNode('param_list', [])
        elif len(p) > 2:
            p[1].children.append(p[3])
            p[0] = p[1]
        else:
            p[0] = ASTNode('param_list', [p[1]])

    def p_param(self, p):
        '''param : id_list COLON type_spec
                 | VAR id_list COLON type_spec'''
        if len(p) == 4:
            p[0] = ASTNode('param', [p[1], p[3]], leaf='value')  # Parâmetros normais (por valor)
        else:
            p[0] = ASTNode('param', [p[2], p[4]], leaf='reference')  # Parâmetros por referência (var)

    # Regra para expressões
    def p_expression(self, p):
        '''expression : simple_expression
                     | simple_expression relop simple_expression'''
        if len(p) > 2:
            p[0] = ASTNode('binary_op', [p[1], p[3]], p[2])
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
    def p_simple_expression(self, p):
        '''simple_expression : term
                            | simple_expression addop term'''
        if len(p) > 2:
            p[0] = ASTNode('binary_op', [p[1], p[3]], p[2])
        else:
            p[0] = p[1]
    
    # Regra para operadores de adição
    def p_addop(self, p):
        '''addop : PLUS
                | MINUS
                | OR'''
        p[0] = p[1]
    
    # Regra para termos
    def p_term(self, p):
        '''term : factor
                | term mulop factor'''
        if len(p) > 2:
            p[0] = ASTNode('binary_op', [p[1], p[3]], p[2])
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
    def p_factor(self, p):
        '''factor : string_access
                 | variable
                 | INTEGER
                 | REAL
                 | STRING
                 | TRUE
                 | FALSE
                 | LPAREN expression RPAREN
                 | NOT factor
                 | function_call'''
        if len(p) == 2:
            if isinstance(p[1], ASTNode):  # Se for uma variável ou chamada de função
                p[0] = p[1]
            elif isinstance(p[1], int):
                p[0] = ASTNode('integer', leaf=p[1])
            elif isinstance(p[1], float):
                p[0] = ASTNode('real', leaf=p[1])
            elif p[1] in ('true', 'false'):
                p[0] = ASTNode('boolean', leaf=p[1])
            else:
                p[0] = ASTNode('string', leaf=p[1])
        elif len(p) == 3:  # NOT factor
            p[0] = ASTNode('unary_op', [p[2]], p[1])
        else:  # LPAREN expression RPAREN
            p[0] = p[2]
    
    # Acesso a caracteres de uma string: str[index]
    def p_string_access(self, p):
        '''string_access : ID LBRACKET expression RBRACKET'''
        p[0] = ASTNode('string_access', [ASTNode('id', leaf=p[1]), p[3]])
    
    def p_formatted_expression(self,p): 
        '''expression : variable COLON INTEGER
                    | variable COLON INTEGER COLON INTEGER'''
        if len(p) == 4:
            p[0] = ASTNode('formatted_output', [p[1], ASTNode('integer', leaf=p[3])])
        else:
            p[0] = ASTNode('formatted_output', [p[1], ASTNode('integer', leaf=p[3]), ASTNode('integer', leaf=p[5])])
    

    # Regra para chamada de função
    def p_function_call(self, p):
        '''function_call : ID LPAREN expression_list RPAREN
                        | ID LPAREN RPAREN
                        | LENGTH LPAREN expression RPAREN'''
        if p[1].lower() == 'length':
            p[0] = ASTNode('length_function', [p[3]])
        elif len(p) > 4:
            p[0] = ASTNode('function_call', [ASTNode('id', leaf=p[1]), p[3]])
        else:
            p[0] = ASTNode('function_call', [ASTNode('id', leaf=p[1])])
        
    # Regra para comando halt
    def p_halt_statement(self, p):
        '''halt_statement : HALT'''
        p[0] = ASTNode('halt')


    # Regra para produções vazias
    def p_empty(self, p):
        'empty :'
        p[0] = None
        
    # Tratamento de erros
    def p_error(self, p):
        if p:
            error_msg = f"Erro de sintaxe na linha {p.lineno}, token '{p.value}'"
            self.errors.append(error_msg)
            print(error_msg)
        else:
            self.errors.append("Erro de sintaxe: fim inesperado do ficheiro")
            print("Erro de sintaxe: fim inesperado do ficheiro")
    

    # Método para analisar uma string
    def parse(self, data):
        self.errors = []
        return self.parser.parse(data, lexer=self.lexer)


# Função para criar uma instância do parser
def create_parser():
    return PascalParser()
