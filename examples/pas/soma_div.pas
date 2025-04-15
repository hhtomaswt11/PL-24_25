program CalcularExpressaoComDivisao;

var
  resultado: integer;  { Usando Real para permitir a divisão de ponto flutuante }
begin
  { Calculando 4 + 2 * 3 - 2 / 2, respeitando a ordem das operações - 9 output}
  resultado := 4 + 2 * 3 - 2 / 2;

  { Exibindo o resultado }
  WriteLn('O resultado de 4 + 2 * 3 - 2 / 2 é: ', resultado);  { Formatando para 2 casas decimais }
end.
