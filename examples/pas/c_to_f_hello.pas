program c_to_f_hello;

uses crt;

procedure PrintHello;
begin
    writeln('Hello, World!');
end;

procedure CelsiusToFahrenheit;
var
    celsius, fahrenheit: real;
begin
    writeln('Digite a temperatura em Celsius:');
    readln(celsius);
    fahrenheit := (celsius * 9/5) + 32;
    writeln('Temperatura em Fahrenheit: ', fahrenheit:0:2);
end;

begin
    clrscr;
    PrintHello;
    writeln;
    CelsiusToFahrenheit;
end.
