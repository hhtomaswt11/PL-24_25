program TesteFuncProc;

function Dobro(x: integer): integer;
begin
    Dobro := x * 2;
end;

procedure MostrarResultado(y: integer);
begin
    writeln('Resultado: ', y);
end;

var
    numero, resultado: integer;
begin
    numero := 5;
    resultado := Dobro(numero);
    MostrarResultado(resultado);
end.
