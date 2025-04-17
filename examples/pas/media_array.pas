program MediaArray;
var
  notas: array[1..4] of real;
  i: integer;
  soma, media: real;
begin
  soma := 0.0;
  writeln('Introduza 4 notas:');
  for i := 1 to 4 do
  begin
    readln(notas[i]);
    soma := soma + notas[i];
  end;
  media := soma / 4;
  writeln('Média: ', media:5:2);
end.
