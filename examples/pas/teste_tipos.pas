program RepetirOlaMundo;

var
  mensagem: string;
  contador, vezes: integer;

begin
  { Inicialização das variáveis }
  mensagem := 'Olá Mundo';
  vezes := 3;

  { Imprimir a mensagem 3 vezes usando while }
  contador := 1;
  while contador <= vezes do
  begin
    writeln(mensagem);
    contador := contador + 1;
  end;
end.    