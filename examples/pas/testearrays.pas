program ArrayComZero;
var
  dados: array[0..3] of integer;
  i: integer;
begin
  writeln('Introduza 4 valores:');
  for i := 0 to 3 do
    readln(dados[i]);

  writeln('Valores lidos:');
  for i := 0 to 3 do
    writeln(dados[i]);
end.
