program ExemploCompleto;

{ Function que calcula fatorial }
function Fatorial(n: integer): integer;
var
  i, resultado: integer;
begin
  resultado := 1;
  for i := 1 to n do
    resultado := resultado * i;
  Fatorial := resultado;
end;

{ Procedure que exibe o fatorial }
procedure ExibirFatorial(num: integer);
begin
  writeln('O fatorial de ', num, ' é: ', Fatorial(num));
end;

{ Programa principal }
var
  numero: integer;
begin
  write('Digite um número: ');
  readln(numero);
  ExibirFatorial(numero); { Chamando procedure que usa function }
end.