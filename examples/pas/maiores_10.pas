program ContarMaiores;
var
  v: array[1..6] of integer;
  i, count: integer;
begin
  count := 0;
  writeln('Introduza 6 números:');
  for i := 1 to 6 do
  begin
    readln(v[i]);
    if v[i] > 10 then
      count := count + 1;
  end;
  writeln('Quantidade > 10: ', count);
end.
