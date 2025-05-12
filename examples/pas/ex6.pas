program ExemploFunction;

function Soma(a, b: integer): integer;
begin
    Soma := a + b;
end;

var
    num1, num2, resultado: integer;
begin
    writeln('Digite o primeiro número:');
    readln(num1);
    writeln('Digite o segundo número:');
    readln(num2);

    resultado := Soma(num1, num2);
    
    writeln('A soma é: ', resultado);
end.
