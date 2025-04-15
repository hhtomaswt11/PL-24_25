program c_to_f_function;

uses crt;

function CelsiusToFahrenheit(celsius: real): real;
begin
    CelsiusToFahrenheit := (celsius * 9 / 5) + 32;
end;

var
    celsius, fahrenheit: real;

begin
    clrscr;
    writeln('Digite a temperatura em Celsius:');
    readln(celsius);

    fahrenheit := CelsiusToFahrenheit(celsius);

    writeln('Temperatura em Fahrenheit: ', fahrenheit:0:2);
end.
