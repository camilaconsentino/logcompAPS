#include <stdio.h>

int yyparse(void);
void yyerror(const char* s);

int main(void){
    int rc = yyparse();
    if (rc == 0) {
        puts("[ok] parse concluído.");
        return 0;
    } else {
        puts("[fail] erro de parse.");
        return 1;
    }
}
