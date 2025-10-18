%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "parser.tab.h"

static char* dup_yytext(void) {
    size_t n = yyleng;
    char* s = (char*)malloc(n + 1);
    memcpy(s, yytext, n);
    s[n] = 0;
    return s;
}
%}

%option noyywrap nodefault yylineno

SPACE      [ \t\r]+
NEWLINE    \n
DIGIT      [0-9]
ID_START   [A-Za-z_]
ID_CONT    [A-Za-z0-9_]
IDENT      {ID_START}{ID_CONT}*
NUMBER     {DIGIT}+(\.{DIGIT}+)?

%%

{SPACE}               ;
{NEWLINE}             ;

"("                   { return LPAREN; }
")"                   { return RPAREN; }
";"                   { return SEMI; }
","                   { return COMMA; }
":"                   { return COLON; }
"="                   { return ASSIGN; }
"*"                   { return MUL; }
"=="                  { return EQ; }
"!="                  { return NEQ; }
"<="                  { return LE; }
">="                  { return GE; }
"<"                   { return LT; }
">"                   { return GT; }

\"([^\\\"]|\\.)*\"    { yylval.str = dup_yytext(); return STRING; }

{NUMBER}              { yylval.num = atof(yytext); return NUMBER; }

{IDENT} {
    if (!strcmp(yytext,"add"))    return ADD;
    if (!strcmp(yytext,"mix"))    return MIX;
    if (!strcmp(yytext,"rise"))   return RISE;
    if (!strcmp(yytext,"bake"))   return BAKE;
    if (!strcmp(yytext,"wait"))   return WAIT;
    if (!strcmp(yytext,"if"))     return IF;
    if (!strcmp(yytext,"else"))   return ELSE;
    if (!strcmp(yytext,"while"))  return WHILE;
    if (!strcmp(yytext,"print"))  return PRINT;
    if (!strcmp(yytext,"volume")) return VOLUME;
    if (!strcmp(yytext,"g"))      return UNIT_G;
    if (!strcmp(yytext,"ml"))     return UNIT_ML;
    if (!strcmp(yytext,"un"))     return UNIT_UN;
    if (!strcmp(yytext,"m"))      return M_UNIT;

    yylval.ident = dup_yytext();
    return IDENT;
}

. {
    fprintf(stderr,"[lex] caractere inesperado '%c' (linha %d)\n", *yytext, yylineno);
    return yytext[0];
}

%%
