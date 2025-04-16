program intervalo_dotdot;

var
    numeros: array[1..5] of integer;
    i: integer;
    

begin
    writeln('Atribuindo valores ao array:');
    for i := 2 to 6 do
    begin
        numeros[i] := i * 2;
        writeln('numeros[', i, '] = ', numeros[i]);
    end;

    writeln('Imprimindo valores do array de trás para frente:');
    for i := 4 downto 0 do
        writeln('numeros[', i, '] = ', numeros[i]);

    halt;
end.
