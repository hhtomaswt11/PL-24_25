program CelsiusParaFahrenheit;
var
  celsius: integer;
  fahrenheit: real;
begin
  writeln('Introduza a temperatura em Celsius:');
  readln(celsius);
  fahrenheit := (celsius * 9 / 5) + 32;
  writeln('Temperatura em Fahrenheit: ', fahrenheit:40:4);
end.
