program ExemploProcedure;

{ Procedure que cumprimenta o usuário }
procedure Saudacao(nome: string);
begin
  writeln('Olá, ', nome, '!');
  writeln('Bem-vindo ao Pascal!');
end;

{ Programa principal }
var
  nomeUsuario: string;
begin
  write('Digite seu nome: ');
  readln(nomeUsuario);
  Saudacao(nomeUsuario); { Chamando a procedure }
end.