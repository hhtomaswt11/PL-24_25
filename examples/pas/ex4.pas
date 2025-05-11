program SomaArray;
var
    numeros: array[1..5] of integer;
    i, j, soma, soma2: integer;
begin
    soma := 0;
    writeln('Introduza 5 números inteiros:');
    for i := 1 to 5 do
    begin
    readln(numeros[i]);
    soma := soma + numeros[i];
    for j := 1 to i do
    begin
    	soma2 := soma2 + numeros[j];
    end;
end;
    writeln('A soma dos números é: ', soma);
    writeln('A soma2 dos números é: ', soma2);
end.
