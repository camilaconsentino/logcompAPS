%{
#include <stdio.h>
#include <stdlib.h>

/* Habilite isto se quiser imprimir uma "AST" mais tarde */
void* make_node(const char* tag, void* a, void* b, void* c);
void  free_tree(void* n);
void  dump_tree(void* n, int ind);

extern int yylineno;
int yylex(void);
void yyerror(const char* s);

void* g_root = NULL;  /* para guardar a árvore/raiz se quiser */
%}

%define parse.error verbose

/* Tipos que yylval pode carregar */
%union {
  double    num;
  char*     ident;
  char*     str;
  void*     node;
}

/* Tokens (sem valor ou com valor) */
%token ADD MIX RISE BAKE WAIT
%token IF ELSE WHILE PRINT
%token VOLUME

%token LPAREN RPAREN SEMI COMMA COLON
%token ASSIGN MUL
%token EQ NEQ LT GT LE GE

%token <num>   NUMBER
%token <ident> IDENT
%token <str>   STRING

%token UNIT_G UNIT_ML UNIT_UN
%token M_UNIT

/* Tipos associados às regras (se for montar AST) */
%type  <node> program recipe items statement simple_stmt step quantity time
%type  <node> if_stmt while_stmt assign_stmt print_stmt
%type  <node> cond simple term factor

/* Precedência (apenas o necessário) */
%left EQ NEQ LT GT LE GE
%left MUL

%%

program
  : /* vazio */               { g_root = NULL; }
  | program recipe            { /* anexaria à raiz se tivesse árvore de receitas */ }
  ;

recipe
  : IDENT LPAREN items RPAREN { /* aqui você poderia criar nó "RECIPE" com $1 e $3 */ }
  ;

items
  : /* vazio */
  | items statement
  ;

statement
  : simple_stmt SEMI
  ;

simple_stmt
  : step
  | assign_stmt
  | while_stmt
  | print_stmt
  | if_stmt
  ;

if_stmt
  : IF LPAREN cond RPAREN COLON simple_stmt COMMA ELSE COLON simple_stmt
  ;

while_stmt
  : WHILE LPAREN cond RPAREN COLON simple_stmt
  ;

assign_stmt
  : IDENT ASSIGN simple
    { /* var = expr */ }
  ;

print_stmt
  : PRINT LPAREN STRING RPAREN
    { /* print("...") */ }
  ;

step
  : ADD IDENT                        { /* add ident (sem qty) */ }
  | ADD IDENT COMMA quantity         { /* add ident, qty */ }
  | MIX                              { /* mix */ }
  | RISE time                        { /* rise time */ }
  | BAKE time                        { /* bake time */ }
  | WAIT time                        { /* wait time */ }
  ;

quantity
  : NUMBER                           { /* 500 */ }
  | NUMBER UNIT_G                    { /* 500 g */ }
  | NUMBER UNIT_ML                   { /* 300 ml */ }
  | NUMBER UNIT_UN                   { /* 5 un */ }
  ;

time
  : NUMBER                           { /* 40 */ }
  | NUMBER M_UNIT                    { /* 40 m */ }
  ;

cond
  : simple EQ  simple
  | simple NEQ simple
  | simple LT  simple
  | simple GT  simple
  | simple LE  simple
  | simple GE  simple
  ;

simple
  : term
  ;

term
  : factor
  | term MUL factor
  ;

factor
  : NUMBER
  | IDENT
  | VOLUME
  | LPAREN simple RPAREN
  ;

%%

void yyerror(const char* s){
  fprintf(stderr, "[parser] erro na linha %d: %s\n", yylineno, s);
}
