program ListaDeStrings;

var
  nomes: array[1..5] of string[50];
  i: integer;

begin
  writeln('Insira 5 nomes:');
  
  for i := 1 to 5 do
  begin
    write('Nome ', i, ': ');
    readln(nomes[i]);
  end;

  writeln('Nomes inseridos:');
  
  for i := 1 to 5 do
  begin
    writeln('Nome ', i, ': ', nomes[i]);
  end;
end.
