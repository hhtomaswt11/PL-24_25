#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class CodeGenerator:
    """
    Gerador de código para a linguagem Pascal Standard.
    Converte a AST em código para a máquina virtual.
    """
    
    def __init__(self, symtab):
        self.symtab = symtab
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_offset = 0
        self.function_scope = False
        self.errors = []
    
    def emit(self, instruction):
        """ Adiciona uma instrução ao código gerado """
        self.code.append(instruction)

    
    def generate(self, ast):
        """Gera código a partir da árvore sintática."""
        if ast is None:
            return []
        
        self.code = []
        self._generate_code(ast)
        return self.code
    
    def _generate_code(self, node):
        """Gera código para um nó da AST."""
        if node is None:
            return
        
        if node.type == 'program':
            self._generate_program(node)
            
        elif node.type == 'function_decl':
            self._gen_function_decl(node)
            
        elif node.type == 'function_call':
            self._generate_function_call(node)

        elif node.type == 'block':
            self._generate_block(node)
        elif node.type == 'compound':
            self._generate_compound(node)
        elif node.type == 'statement_list':
            self._generate_statement_list(node)
        elif node.type == 'assignment':
            self._generate_assignment(node)
        elif node.type == 'if':
            self._generate_if(node)
        elif node.type == 'while':
            self._generate_while(node)
        elif node.type == 'for':
            self._generate_for(node)
        elif node.type == 'writeln':
            self._generate_writeln(node)
        elif node.type == 'readln':
            self._generate_readln(node)
        elif node.type == 'binary_op':
            self._generate_binary_op(node)
        elif node.type == 'unary_op':
            self._generate_unary_op(node)
        elif node.type == 'variable':
            self._generate_variable(node)
        elif node.type == 'array_element':
            self._generate_array_element(node)
        elif node.type == 'integer':
            self._generate_integer(node)
        elif node.type == 'real':
            self._generate_real(node)
        elif node.type == 'string':
            self._generate_string(node)
        elif node.type == 'boolean':
            self._generate_boolean(node)
        elif node.type == 'procedure_call':
            self._generate_procedure_call(node)
     
    
    def _generate_program(self, node):
        """Gera código para o nó de programa."""
        # Nome do programa
        program_name = node.leaf
        self.code.append(f"PROGRAM {program_name}")
        
        # Gera código para o bloco principal
        if node.children:
            self._generate_code(node.children[0])
        
        # Finaliza o programa
        self.code.append("HALT")
        
    def _gen_function_decl(self, node):
        func_id = node.children[0].leaf
        param_list = node.children[1]
        body = node.children[2]  # Corrigido! Antes estava fchildren[3]

        self.emit(f"{func_id}:")  # Define o rótulo da função
        self._gen_node(body)  # Gera código para o corpo da função
        self.emit("RET")  # Retorno da função

        
    def _gen_function_call(self, node):
        func_id = node.children[0].leaf
        if len(node.children) > 1:
            for arg in node.children[1].children[::-1]:  # Correção na lista de argumentos
                self._gen_node(arg)  # Gera código para os argumentos

        self.emit(f"CALL {func_id}")  # Chama a função


    
    def _generate_block(self, node):
        """Gera código para o nó de bloco."""
        # Gera código para declarações
        if node.children and len(node.children) > 0:
            self._generate_code(node.children[0])
        
        # Gera código para o bloco de comandos
        if node.children and len(node.children) > 1:
            self._generate_code(node.children[1])
    
    def _generate_compound(self, node):
        """Gera código para o nó de bloco composto."""
        # Gera código para a lista de comandos
        if node.children:
            self._generate_code(node.children[0])
    
    def _generate_statement_list(self, node):
        """Gera código para a lista de comandos."""
        for child in node.children:
            self._generate_code(child)
    
    def _generate_assignment(self, node):
        """Gera código para o nó de atribuição."""
        # Gera código para a expressão (lado direito)
        if len(node.children) > 1:
            self._generate_code(node.children[1])
        
        # Gera código para a variável (lado esquerdo)
        var_node = node.children[0]
        
        if var_node.type == 'variable':
            var_name = var_node.leaf
            # Verifica se a variável existe na tabela de símbolos
            symbol = self.symtab.lookup(var_name)
            if symbol:
                if symbol.address is None:
                    # Atribui um endereço à variável se ainda não tiver
                    symbol.address = self.current_offset
                    self.current_offset += symbol.size
                
                # Gera instrução de armazenamento
                self.code.append(f"STORE {symbol.address} # {var_name}")
            else:
                self.errors.append(f"Erro: Variável '{var_name}' não declarada")
        
        elif var_node.type == 'array_element':
            # Implementar armazenamento em elementos de array
            array_id = var_node.children[0].leaf
            symbol = self.symtab.lookup(array_id)
            
            if symbol:
                # Gera código para calcular o índice
                self._generate_code(var_node.children[1])
                
                # Calcula o endereço do elemento
                self.code.append(f"ASTORE {symbol.address} # {array_id}[]")
            else:
                self.errors.append(f"Erro: Array '{array_id}' não declarado")
    
    def _generate_if(self, node):
        """Gera código para o nó de comando if."""
        # Gera label para o caso falso
        false_label = self._new_label()
        end_label = self._new_label()
        
        # Gera código para a expressão condicional
        self._generate_code(node.children[0])
        
        # Gera instrução de salto condicional
        self.code.append(f"JZ {false_label} # Se falso, pula para o false_label")
        
        # Gera código para o bloco verdadeiro
        self._generate_code(node.children[1])
        
        # Gera salto incondicional para o fim do if
        self.code.append(f"JMP {end_label}")
        
        # Label para o caso falso
        self.code.append(f"{false_label}:")
        
        # Gera código para o bloco falso, se existir
        if len(node.children) > 2:
            self._generate_code(node.children[2])
        
        # Label para o fim do if
        self.code.append(f"{end_label}:")
    
    def _generate_while(self, node):
        """Gera código para o nó de comando while."""
        # Gera labels para início e fim do laço
        start_label = self._new_label()
        end_label = self._new_label()
        
        # Label para o início do laço
        self.code.append(f"{start_label}:")
        
        # Gera código para a expressão condicional
        self._generate_code(node.children[0])
        
        # Gera instrução de salto condicional
        self.code.append(f"JZ {end_label} # Se falso, pula para o fim do laço")
        
        # Gera código para o corpo do laço
        self._generate_code(node.children[1])
        
        # Gera salto incondicional para o início do laço
        self.code.append(f"JMP {start_label}")
        
        # Label para o fim do laço
        self.code.append(f"{end_label}:")
    
    def _generate_for(self, node):
        """Gera código para o nó de comando for."""
        # Obtém informações do laço for
        var_node = node.children[0]
        var_name = var_node.leaf
        direction = node.leaf  # 'to' ou 'downto'
        
        # Gera labels para início e fim do laço
        start_label = self._new_label()
        end_label = self._new_label()
        
        # Verifica se a variável existe na tabela de símbolos
        symbol = self.symtab.lookup(var_name)
        if not symbol:
            self.errors.append(f"Erro: Variável '{var_name}' não declarada")
            return
        
        # Gera código para o valor inicial
        self._generate_code(node.children[1])
        
        # Atribui o valor inicial à variável de controle
        if symbol.address is None:
            symbol.address = self.current_offset
            self.current_offset += 1
        
        # Armazena o valor inicial
        self.code.append(f"STORE {symbol.address} # {var_name} (inicial)")
        
        # Salva o valor final em um temporário
        final_temp = self.current_offset
        self.current_offset += 1
        
        # Gera código para o valor final
        self._generate_code(node.children[2])
        self.code.append(f"STORE {final_temp} # valor final")
        
        # Label para o início do laço
        self.code.append(f"{start_label}:")
        
        # Carrega a variável de controle
        self.code.append(f"LOAD {symbol.address} # {var_name}")
        
        # Carrega o valor final para comparação
        self.code.append(f"LOAD {final_temp} # valor final")
        
        # Compara a variável de controle com o valor final
        if direction == 'to':
            self.code.append("GT # verifica se ultrapassou o valor final")
        else:  # downto
            self.code.append("LT # verifica se ultrapassou o valor final")
        
        # Sai do laço se a condição for falsa
        self.code.append(f"JNZ {end_label} # Sai do laço se ultrapassou o limite")
        
        # Gera código para o corpo do laço
        self._generate_code(node.children[3])
        
        # Incrementa ou decrementa a variável de controle
        self.code.append(f"LOAD {symbol.address} # {var_name}")
        if direction == 'to':
            self.code.append("INC # incrementa")
        else:  # downto
            self.code.append("DEC # decrementa")
        self.code.append(f"STORE {symbol.address} # {var_name} (atualizado)")
        
        # Volta para o início do laço
        self.code.append(f"JMP {start_label}")
        
        # Label para o fim do laço
        self.code.append(f"{end_label}:")
    
    # def _generate_writeln(self, node):
    #     """Gera código para o nó de comando writeln."""
    #     if node.children:
    #         # Gera código para a lista de expressões
    #         for expr in node.children[0].children:
    #             self._generate_code(expr)
    #             self.code.append("PRINT")
        
    #     # Adiciona quebra de linha
    #     self.code.append("PRINTLN")
    def _generate_writeln(self, node):
        if node.children:
            already_generated = set()
            for expr in node.children[0].children:
                if str(expr.leaf) not in already_generated:
                    self._generate_code(expr)
                    self.code.append("PRINT")
                    already_generated.add(str(expr.leaf))
        self.code.append("PRINTLN")

    
    def _generate_readln(self, node):
        """Gera código para o nó de comando readln."""
        if node.children:
            for var_node in node.children:
                # Lê o valor da entrada
                self.code.append("READ")
                
                # Armazena na variável
                if var_node.type == 'variable':
                    var_name = var_node.leaf
                    symbol = self.symtab.lookup(var_name)
                    
                    if symbol:
                        if symbol.address is None:
                            symbol.address = self.current_offset
                            self.current_offset += 1
                        
                        self.code.append(f"STORE {symbol.address} # {var_name}")
                    else:
                        self.errors.append(f"Erro: Variável '{var_name}' não declarada")
    
    def _generate_binary_op(self, node):
        """Gera código para operações binárias."""
        # Gera código para os operandos
        self._generate_code(node.children[0])
        self._generate_code(node.children[1])
        
        # Gera a instrução de operação correspondente
        op = node.leaf.lower()
        if op == '+':
            self.code.append("ADD")
        elif op == '-':
            self.code.append("SUB")
        elif op == '*':
            self.code.append("MUL")
        elif op == '/':
            self.code.append("DIV")
        elif op == 'div':
            self.code.append("IDIV")  # Divisão inteira
        elif op == 'mod':
            self.code.append("MOD")
        elif op == 'and':
            self.code.append("AND")
        elif op == 'or':
            self.code.append("OR")
        elif op == '=':
            self.code.append("EQ")
        elif op == '<>':
            self.code.append("NEQ")
        elif op == '<':
            self.code.append("LT")
        elif op == '<=':
            self.code.append("LE")
        elif op == '>':
            self.code.append("GT")
        elif op == '>=':
            self.code.append("GE")
    
    def _generate_unary_op(self, node):
        """Gera código para operações unárias."""
        # Gera código para o operando
        self._generate_code(node.children[0])
        
        # Gera a instrução de operação correspondente
        op = node.leaf.lower()
        if op == 'not':
            self.code.append("NOT")
        elif op == '-':
            self.code.append("NEG")
    
    def _generate_variable(self, node):
        """Gera código para carregar o valor de uma variável."""
        var_name = node.leaf
        symbol = self.symtab.lookup(var_name)
        
        if symbol:
            if symbol.address is None:
                symbol.address = self.current_offset
                self.current_offset += 1
            
            self.code.append(f"LOAD {symbol.address} # {var_name}")
        else:
            self.errors.append(f"Erro: Variável '{var_name}' não declarada")
    
    def _generate_array_element(self, node):
        """Gera código para acesso a elementos de array."""
        array_id = node.children[0].leaf
        symbol = self.symtab.lookup(array_id)
        
        if symbol:
            # Gera código para calcular o índice
            self._generate_code(node.children[1])
            
            # Carrega o valor do elemento
            self.code.append(f"ALOAD {symbol.address} # {array_id}[]")
        else:
            self.errors.append(f"Erro: Array '{array_id}' não declarado")
    
    def _generate_integer(self, node):
        """Gera código para carregar um valor inteiro."""
        self.code.append(f"PUSH {node.leaf}") # constante inteira")
    
    def _generate_real(self, node):
        """Gera código para carregar um valor real."""
        self.code.append(f"PUSH {node.leaf}") # constante real")
    
    def _generate_string(self, node):
        """Gera código para carregar uma string."""
        self.code.append(f"PUSH \"{node.leaf}\"") # constante string")
    
    def _generate_boolean(self, node):
        """Gera código para carregar um valor booleano."""
        value = 1 if node.leaf.lower() == 'true' else 0
        self.code.append(f"PUSH {value}") # constante booleana")
    
    def _generate_procedure_call(self, node):
        """Gera código para chamada de procedimento."""
        proc_name = node.children[0].leaf
        
        # Verifica se é um procedimento pré-definido
        if proc_name.lower() in ['writeln', 'readln']:
            if proc_name.lower() == 'writeln':
                self._generate_writeln(node)
            else:
                self._generate_readln(node)
            return
        
        # Procedimento definido pelo usuário
        symbol = self.symtab.lookup(proc_name)
        
        if symbol and symbol.kind == 'procedure':
            # Gera código para os argumentos, se houver
            if len(node.children) > 1:
                for expr in node.children[1].children:
                    self._generate_code(expr)
            
            # Chama o procedimento
            self.code.append(f"CALL {proc_name}")
        else:
            self.errors.append(f"Erro: Procedimento '{proc_name}' não declarado")
    
    def _generate_function_call(self, node):
        """Gera código para chamada de função."""
        func_name = node.children[0].leaf
        
        symbol = self.symtab.lookup(func_name)
        
        if symbol and symbol.kind == 'function':
            # Gera código para os argumentos, se houver
            if len(node.children) > 1:
                for expr in node.children[1].children:
                    self._generate_code(expr)
            
            # Chama a função
            self.code.append(f"CALL {func_name}")
        else:
            self.errors.append(f"Erro: Função '{func_name}' não declarada")
    
    def _new_temp(self):
        """Gera um novo nome de variável temporária."""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def _new_label(self):
        """Gera um novo rótulo (label)."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label