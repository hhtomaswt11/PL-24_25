program ExemploFunction;

{ Function que calcula área do quadrado }
function AreaQuadrado(lado: integer): integer;
begin
  AreaQuadrado := lado * lado; { Atribuição do resultado }
end;

{ Programa principal }
var
  lado, area: integer;
begin
  write('Digite o lado do quadrado: ');
  readln(lado);
  area := AreaQuadrado(lado); { Chamando a function }
  writeln('Área: ', area);
end.