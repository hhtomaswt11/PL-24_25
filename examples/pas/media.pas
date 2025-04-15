program MediaTresNumeros;
var
  a, b, c: integer;
  media: integer;
begin
  writeln('Introduza três números:');
  readln(a);
  readln(b);
  readln(c);
  media := (a + b + c) div 3;
  writeln('A média é: ', media);
end.
