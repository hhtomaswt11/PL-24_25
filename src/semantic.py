from src.symboltable import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.warnings = []
        self.current_function = None

    def analyze(self, ast):
        if ast is None:
            return False
        self._analyze_node(ast)
        return len(self.errors) == 0

    def _analyze_node(self, node):
        if node is None or not hasattr(node, 'type'):
            return None

        method_name = f"_analyze_{node.type}"
        method = getattr(self, method_name, None)
        if method:
            return method(node)
        else:
            for child in node.children:
                self._analyze_node(child)

    def _analyze_program(self, node):
        return self._analyze_node(node.children[0])

    def _analyze_block(self, node):
        for child in node.children:
            self._analyze_node(child)

    def _analyze_declarations(self, node):
        for child in node.children:
            self._analyze_node(child)

    def _analyze_var_section(self, node):
        for child in node.children:
            self._analyze_node(child)

    # def _analyze_var_declarations(self, node):
    #     for child in node.children:
    #         self._analyze_node(child)
    
    def _analyze_var_declaration(self, node):
        id_list, type_node = node.children
        var_type = type_node.leaf

        for var in id_list.children:
            if type_node.type == "array_type":
                ...
            elif var_type == "string":
                self.symtab.add_symbol(var.leaf, type="string", kind="variable")
            else:
                self.symtab.add_symbol(var.leaf, var_type, kind="variable")


    def _analyze_var_declaration(self, node):
        id_list, type_node = node.children
        var_type = type_node.leaf
        
        if var_type == "string_bounded":
            str_len = type_node.children[0].leaf
            for var in id_list.children:
                self.symtab.add_symbol(var.leaf, type="string", kind="variable", size=int(str_len))
        else:
            for var in id_list.children:
                if type_node.type == "array_type":
                    # Pega informações do array
                    range_node = type_node.children[0]
                    base_type = type_node.children[1].leaf

                    lower_bound = int(range_node.children[0].leaf)
                    upper_bound = int(range_node.children[1].leaf)
                    size = upper_bound - lower_bound + 1

                    self.symtab.add_symbol(
                        var.leaf,
                        type="array",
                        kind="variable",
                        size=size,
                        dimensions=(lower_bound, upper_bound),
                        element_type=base_type
                    )
                else:
                    self.symtab.add_symbol(var.leaf, var_type, kind="variable")

    def _analyze_function_decl(self, node):
        func_id = node.children[0].leaf
        param_list = node.children[1]
        return_type = node.children[2].leaf
        function_body = node.children[3]


        # self.symtab.add_symbol(func_id, type=return_type, kind='function', params=param_list)

        
        # # Guarda a função atual para verificação de retorno
        # previous_function = self.current_function
        # self.current_function = func_id

        # # Entra no novo escopo
        # self.symtab.enter_scope(func_id)
        
        
        # Guarda a função atual antes de qualquer coisa
        previous_function = self.current_function
        self.current_function = func_id

        # Adiciona símbolo da função E entra no escopo
        self.symtab.add_symbol(func_id, type=return_type, kind='function', params=param_list)

                
                
                
        

        # Adiciona parâmetros ao escopo da função
        self._analyze_param_list(param_list, func_id)

        # Analisa o corpo da função
        self._analyze_node(function_body)

        # Verifica se a função tem retorno correto
        has_return = self._check_function_return(function_body, func_id, return_type)
        if not has_return:
            self.errors.append(f"Erro: função '{func_id}' não tem retorno definido ou é do tipo incorreto")

        # Retorna ao escopo anterior
        self.symtab.exit_scope()
        self.current_function = previous_function

    def _analyze_procedure_decl(self, node):
        proc_id = node.children[0].leaf
        param_list = node.children[1]
        procedure_body = node.children[2]

        # Adiciona símbolo do procedimento
        self.symtab.add_symbol(proc_id, type=None, kind='procedure')
        
        # Guarda a função atual para verificação de retorno
        previous_function = self.current_function
        self.current_function = proc_id

        # Entra no novo escopo
        self.symtab.enter_scope(proc_id)

        # Adiciona parâmetros ao escopo do procedimento
        self._analyze_param_list(param_list, proc_id)

        # Analisa o corpo do procedimento
        self._analyze_node(procedure_body)

        # Retorna ao escopo anterior
        self.symtab.exit_scope()
        self.current_function = previous_function

    def _analyze_param_list(self, param_list, func_name):
        """Analisa a lista de parâmetros de uma função ou procedimento"""
        for param in param_list.children:
            param_mode = param.leaf  # 'value' ou 'reference'
            id_list = param.children[0]
            type_node = param.children[1]
            param_type = type_node.leaf
            
            for id_node in id_list.children:
                param_kind = "parameter"
                if param_mode == "reference":
                    param_kind = "reference_parameter"
                
                self.symtab.add_symbol(
                    id_node.leaf, 
                    type=param_type, 
                    kind=param_kind
                )

    def _analyze_compound(self, node):
        return self._analyze_node(node.children[0])

    def _analyze_statement_list(self, node):
        for stmt in node.children:
            self._analyze_node(stmt)

    def _analyze_assignment(self, node):
        var_node = node.children[0]
        expr_node = node.children[1]
        var_type = self._get_expression_type(var_node)
        expr_type = self._get_expression_type(expr_node)
        
        if var_type and expr_type and var_type != expr_type:
            self.errors.append(f"Erro de tipo: não pode atribuir '{expr_type}' a '{var_type}'")

    def _analyze_function_return(self, node):
        """Analisa atribuição de valor de retorno a função"""
        func_id = node.children[0].leaf
        expr_node = node.children[1]
        
        # Verifica se estamos dentro de uma função
        if self.current_function != func_id:
            self.errors.append(f"Erro: atribuição de retorno para '{func_id}' fora do escopo da função")
            return
            
        # Obtém o tipo da função
        func_symbol = self.symtab.lookup(func_id)
        if not func_symbol:
            self.errors.append(f"Erro: função '{func_id}' não declarada")
            return
            
        # Verifica o tipo do valor de retorno
        expr_type = self._get_expression_type(expr_node)
        if expr_type != func_symbol.type:
            self.errors.append(f"Erro: tipo de retorno incompatível. Esperado '{func_symbol.type}', obtido '{expr_type}'")

    def _analyze_return(self, node):
        """Analisa comando de retorno explícito"""
        if not self.current_function:
            self.errors.append("Erro: comando 'return' fora de função ou procedimento")
            return
            
        expr_node = node.children[0] if node.children else None
        func_symbol = self.symtab.lookup(self.current_function)
        
        if func_symbol.kind == 'procedure':
            if expr_node:
                self.errors.append("Erro: procedimento não deve retornar valor")
        elif func_symbol.kind == 'function':
            if not expr_node:
                self.errors.append(f"Erro: função '{self.current_function}' deve retornar um valor")
                return
                
            expr_type = self._get_expression_type(expr_node)
            if expr_type != func_symbol.type:
                self.errors.append(f"Erro: tipo de retorno incompatível. Esperado '{func_symbol.type}', obtido '{expr_type}'")

    def _check_function_return(self, block_node, func_id, return_type):
        """Verifica se uma função retorna o valor correto"""
        # Busca atribuições ao nome da função (Pascal style)
        if block_node.type == "block":
            for child in block_node.children:
                if self._check_function_return(child, func_id, return_type):
                    return True
        elif block_node.type == "compound":
            return self._check_function_return(block_node.children[0], func_id, return_type)
        elif block_node.type == "statement_list":
            for stmt in block_node.children:
                if self._check_function_return(stmt, func_id, return_type):
                    return True
        elif block_node.type == "function_return":
            id_node = block_node.children[0]
            if id_node.leaf == func_id:
                expr_type = self._get_expression_type(block_node.children[1])
                return expr_type == return_type
        elif block_node.type == "return":
            if block_node.children:
                expr_type = self._get_expression_type(block_node.children[0])
                return expr_type == return_type
        return False

    def _analyze_if(self, node):
        cond_type = self._get_expression_type(node.children[0])
        if cond_type != 'boolean':
            self.errors.append("Erro: condição do 'if' deve ser booleana")
        self._analyze_node(node.children[1])
        if len(node.children) > 2:
            self._analyze_node(node.children[2])

    def _analyze_while(self, node):
        cond_type = self._get_expression_type(node.children[0])
        if cond_type != 'boolean':
            self.errors.append("Erro: condição do 'while' deve ser booleana")
        self._analyze_node(node.children[1])

    def _analyze_for(self, node):
        # Verifica se a variável de controle existe
        var_id = node.children[0].leaf
        var_symbol = self.symtab.lookup(var_id)
        if not var_symbol:
            self.errors.append(f"Erro: variável de controle '{var_id}' não declarada")
        elif var_symbol.type != 'integer':
            self.errors.append(f"Erro: variável de controle do 'for' deve ser inteira")
            
        # Verifica os valores inicial e final
        init_type = self._get_expression_type(node.children[1])
        final_type = self._get_expression_type(node.children[2])
        
        if init_type != 'integer':
            self.errors.append("Erro: valor inicial do 'for' deve ser inteiro")
        if final_type != 'integer':
            self.errors.append("Erro: valor final do 'for' deve ser inteiro")
            
        # Analisa o corpo do loop
        self._analyze_node(node.children[3])

    def _analyze_procedure_call(self, node):
        proc_name = node.children[0].leaf
        proc_symbol = self.symtab.lookup(proc_name)
        
        if not proc_symbol:
            self.errors.append(f"Erro: procedimento '{proc_name}' não declarado")
            return
            
        if proc_symbol.kind != 'procedure':
            self.errors.append(f"Erro: '{proc_name}' não é um procedimento")
            return
            
        # Verifica os argumentos se houver
        if len(node.children) > 1:
            arg_list = node.children[1]
            self._check_call_arguments(proc_name, proc_symbol, arg_list)

    def _analyze_function_call(self, node):
        func_name = node.children[0].leaf
        func_symbol = self.symtab.lookup(func_name)
        
        if not func_symbol:
            self.errors.append(f"Erro: função '{func_name}' não declarada")
            return None
            
        if func_symbol.kind != 'function':
            self.errors.append(f"Erro: '{func_name}' não é uma função")
            return None
            
        # Verifica os argumentos se houver
        if len(node.children) > 1:
            arg_list = node.children[1]
            self._check_call_arguments(func_name, func_symbol, arg_list)
            
        return func_symbol.type

    def _analyze_function_call_stmt(self, node):
        """Analisa chamada de função usada como statement"""
        func_call = node.children[0]
        return self._analyze_function_call(func_call)
 
    def _check_call_arguments(self, call_name, call_symbol, arg_list):
        """Verifica se os argumentos da chamada correspondem aos parâmetros declarados"""
        if not hasattr(call_symbol, 'params') or not call_symbol.params:
            if arg_list and len(arg_list.children) > 0:
                self.errors.append(f"Erro: '{call_name}' não espera argumentos")
            return

        params = call_symbol.params.children
        args = arg_list.children

        # Conta o total de argumentos esperados (cada id em cada param conta como 1)
        expected_args = sum(len(param.children[0].children) for param in params)
        actual_args = len(args)

        if expected_args != actual_args:
            self.errors.append(f"Erro: '{call_name}' espera {expected_args} argumentos, mas recebeu {actual_args}")
            return

        # Verificação um a um
        arg_index = 0
        for param in params:
            param_ids = param.children[0].children  # Lista de ids como [ASTNode(id), ...]
            param_type_node = param.children[1]
            param_type = param_type_node.leaf
            is_reference = (param.leaf == 'reference')

            for _ in param_ids:
                arg = args[arg_index]
                arg_type = self._get_expression_type(arg)

                if arg_type != param_type:
                    self.errors.append(f"Erro: argumento {arg_index+1} de '{call_name}' deve ser do tipo '{param_type}', mas recebeu '{arg_type}'")

                if is_reference and arg.type != 'variable':
                    self.errors.append(f"Erro: argumento {arg_index+1} de '{call_name}' deve ser uma variável (passagem por referência)")

                arg_index += 1

    
 
 
    def _analyze_length_function(self, node):
        """Analisa chamada para função 'length' (intrínseca)"""
        expr = node.children[0]
        expr_type = self._get_expression_type(expr)
        
        if expr_type != 'string' and expr_type != 'array':
            self.errors.append("Erro: função 'length' espera string ou array")
            
        return 'integer'

    def _analyze_string_access(self, node):
        """Analisa acesso a caractere de string"""
        str_id = node.children[0].leaf
        str_symbol = self.symtab.lookup(str_id)
        
        if not str_symbol:
            self.errors.append(f"Erro: string '{str_id}' não declarada")
            return None
            
        if str_symbol.type != 'string':
            self.errors.append(f"Erro: '{str_id}' não é uma string")
            return None
            
        index_expr = node.children[1]
        index_type = self._get_expression_type(index_expr)
        
        if index_type != 'integer':
            self.errors.append("Erro: índice de string deve ser inteiro")
            
        return 'char_type'

    def _analyze_writeln(self, node):
        if node.children:
            expr_list = node.children[0]
            for expr in expr_list.children:
                self._analyze_node(expr)

    def _analyze_readln(self, node):
        if node.children:
            var_node = node.children[0]
            if var_node.type == 'variable':
                if self.symtab.lookup(var_node.leaf) is None:
                    self.errors.append(f"Erro: variável '{var_node.leaf}' não declarada")
            else:
                self._analyze_node(var_node)
    
    def _analyze_binary_op(self, node):
        left_type = self._get_expression_type(node.children[0])
        right_type = self._get_expression_type(node.children[1])
        op = node.leaf.lower()

        if op in ['=', '<>', '<', '>', '<=', '>=']:
            # Operações relacionais retornam boolean
            if left_type != right_type:
                # Permite comparar 'char' com string literal como '1'
                if not (left_type == 'char' and right_type == 'string') and not (left_type == 'string' and right_type == 'char'):
                    self.errors.append(f"Erro: comparação entre tipos diferentes ({left_type} e {right_type})")

            return 'boolean'

        elif op in ['and', 'or']:
            if left_type != 'boolean' or right_type != 'boolean':
                self.errors.append("Erro: operador lógico com operandos não booleanos")
            return 'boolean'
        
        elif op in ['+', '-', '*', 'div', 'mod', '/']:
            if op in ['div', 'mod']:
                if left_type != 'integer' or right_type != 'integer':
                    self.errors.append("Erro: operação 'div' ou 'mod' requer operandos do tipo inteiro")
                return 'integer'
            elif op == '/':
                if left_type not in ['integer', 'real'] or right_type not in ['integer', 'real']:
                    self.errors.append("Erro: operação '/' requer operandos do tipo inteiro ou real")
                if left_type == 'real' or right_type == 'real':
                    return 'real'
                else:
                    return 'integer'
            else:
                if left_type not in ['integer', 'real'] or right_type not in ['integer', 'real']:
                    self.errors.append("Erro: operação aritmética requer operandos do tipo inteiro ou real")
                if left_type == 'real' or right_type == 'real':
                    return 'real'
                else:
                    return 'integer'
        else:
            self.errors.append(f"Erro: operador binário desconhecido '{op}'")
            return None

    def _analyze_unary_op(self, node):
        expr_type = self._get_expression_type(node.children[0])
        op = node.leaf.lower()
        
        if op == 'not':
            if expr_type != 'boolean':
                self.errors.append("Erro: operador 'not' requer operando booleano")
            return 'boolean'
        elif op in ['+', '-']:
            if expr_type not in ['integer', 'real']:
                self.errors.append(f"Erro: operador unário '{op}' requer operando numérico")
            return expr_type
        else:
            self.errors.append(f"Erro: operador unário desconhecido '{op}'")
            return None

    def _get_expression_type(self, node):
        if node is None:
            return None
            
        if node.type == 'integer':
            return 'integer'
        elif node.type == 'real':
            return 'real'
        elif node.type == 'formatted_output':
            return self._get_expression_type(node.children[0])
        elif node.type == 'boolean':
            return 'boolean'
        elif node.type == 'string':
            return 'string'
        elif node.type == 'variable':
            symbol = self.symtab.lookup(node.leaf)
            if symbol:
                return symbol.type
            else:
                self.errors.append(f"Erro: variável '{node.leaf}' não declarada")
                return None
            
        elif node.type == 'array_access':
            array_name = node.leaf
            array_info = self.symtab.lookup(array_name) 
            
            if array_info is None:
                self.errors.append(f"Erro: variável '{array_name}' não declarada")
                return None

            # Verifica se o array foi corretamente identificado
            if not hasattr(array_info, "element_type") or array_info.element_type is None:
                self.errors.append(f"Erro: '{array_name}' não é um array")
                return None

            # Verificar se índice é inteiro
            index_type = self._get_expression_type(node.children[0])
            if index_type != 'integer':
                self.errors.append(f"Erro: índice do array '{array_name}' deve ser inteiro")

            return array_info.element_type
            
        elif node.type == 'string_access':
            return self._analyze_string_access(node)
            
        elif node.type == 'function_call':
            return self._analyze_function_call(node)
            
        elif node.type == 'length_function':
            # return self._analyze_length_function(node)
            return 'integer'
            
        elif node.type == 'binary_op':
            return self._analyze_binary_op(node)
            
        elif node.type == 'unary_op':
            return self._analyze_unary_op(node)
            
        return None