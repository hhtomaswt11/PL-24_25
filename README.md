# Processamento de Linguagens - Universidade do Minho

(Ano letivo 2024/2025)

##### Avaliação Final: 

#### Projeto: Compilador Pascal Standard ★

Este projeto foi desenvolvido no âmbito da unidade curricular de **Processamento de Linguagens**, no 2.º semestre do 3.º ano da licenciatura em Engenharia Informática, por:

**Grupo 11**
- Tomás Henrique Alves Melo - A104529
- João Gustavo da Silva Couto Mendes Serrão - A104444
- José Pedro Torres Vasconcelos - A100763

---

## Objetivo

Desenvolver um **compilador funcional para Pascal Standard**, com capacidade de reconhecer, interpretar e traduzir programas Pascal para uma **representação intermédia** ou diretamente para **código de máquina da EWVM**:

> [https://ewvm.epl.di.uminho.pt/](https://ewvm.epl.di.uminho.pt/)

O projeto consolida conceitos fundamentais de compilação: análise léxica, sintática, semântica e geração de código VM.

---

## Etapas do Compilador

### Análise Léxica
- Implementada com `ply.lex`.
- Geração de tokens a partir do código-fonte:
  - Palavras-chave, identificadores, números, operadores, símbolos.

### Análise Sintática
- Implementada com `ply.yacc`.
- Verificação da estrutura gramatical com base nas regras da linguagem.

### Análise Semântica
- Verificação de:
  - Declarações de variáveis;
  - Tipos de dados;
  - Coerência das expressões e comandos.

### Geração de Código
- Tradução para instruções da máquina virtual EWVM.
- Com ou sem uso de representação intermédia.

### Otimização de Código *(Extra)*
- Remoção de redundâncias;
- Otimizações locais/globais (opcional).

### Testes
- Testes unitários e funcionais com múltiplos exemplos em Pascal.
- Comparação entre saída esperada e executada na VM.

---

## Requisitos Funcionais

O compilador deverá processar programas que incluam:

- Declaração de variáveis (`var`);
- Expressões aritméticas (`+`, `-`, `*`, `/`, `mod`);
- Estruturas de controlo (`if`, `while`, `for`);
- Procedimentos e funções (*opcional*);
- Escrita e leitura (`writeln`, `readln`).

---

## Execução 

Para compilar um ficheiro .pas com o compilador desenvolvido: 
```bash
python3 main.py examples/pas/ex1.pas
```
Para rodar o código VM gerado diretamente na máquina virtual desenvolvida:
```bash
python3 vm.py examples/vm/ex1.vm
```

Visualizar estatísticas do programa compilado (avaliação da análise sintática, visualização da Árvore Sintática Abstrata (AST), avaliação da análise semântica ou todos):
```bash
python3 test.py examples/pas/ex1.pas <tokens|ast|semantic|all> 
```


Interface Web, criada para compilar os programas em Pascal Standard, visualizar estatísticas do programa compilado e visualizar o código VM gerado, de forma mais intuitiva e acessível - Mover para a diretoria `web_interface`: 
```
python3 app.py 
```
- A aplicação ficará disponível em http://localhost:5000 por predefinição.

