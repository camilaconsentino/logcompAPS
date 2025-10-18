# MAQUINA DE PAO/MASSA

## Exemplo entrada
```
pao_branco(
  add farinha, 500 g;
  add agua, 300 ml;
  add fermento, 5 g;
  mix;

  vol_inicial = volume;
  while (volume <= vol_inicial * 2): wait 1 m;

  vol_inicial = volume;
  while (volume <= vol_inicial * 1.4): bake 1 m;

  vol = volume;
  wait 30 m;

  if (volume < vol * 0.90): print("jogar fora"), else: print("perfeito");
)

```

1️. adiciona farinha (500 g), água (300 ml) e fermento (5 g).

2️. realiza um mix para homogeneizar a massa.

3️. mede o volume inicial da massa e salva em vol_inicial.

4️. enquanto o volume for menor ou igual ao dobro do inicial → espera 1 minuto e mede de novo.

5️. quando a massa dobra, atualiza vol_inicial = volume.

6️. enquanto o volume for menor ou igual a 1,4 × o novo volume → assa por 1 minuto a cada ciclo (simula o crescimento no forno).

7️. salva vol = volume (volume final após o forno).

8️. espera 30 minutos para o pão estabilizar.

9️. se o volume cair para menos de 90% do que tinha após o forno → imprime “jogar fora” (indicando que o pão murchou demais).


## EBNF 
```
PROGRAM    = { RECIPE } ;

RECIPE     = IDENT, "(", { ITEM }, ")" ;
ITEM       = SIMPLE_STMT, ";" | IF_STMT ;

(* --- statements ---*)
IF_STMT    = "if", "(", COND, ")", ":", SIMPLE_STMT, ",", "else", ":", SIMPLE_STMT, ";" ;

SIMPLE_STMT = STEP
            | ASSIGN_STMT
            | WHILE_STMT
            | PRINT_STMT ;

WHILE_STMT = "while", "(", COND, ")", ":", SIMPLE_STMT ;

ASSIGN_STMT = IDENT, "=", SIMPLE ;

PRINT_STMT  = "print", "(", STRING, ")" ;

(* --- steps --- *)
STEP       = ADD_STEP | MIX_STEP | RISE_STEP | BAKE_STEP | WAIT_STEP ;

ADD_STEP   = "add", IDENT, [ ",", QUANTITY ] ;
MIX_STEP   = "mix" ;
RISE_STEP  = "rise", TIME ;
BAKE_STEP  = "bake" ;
WAIT_STEP  = "wait" ;

QUANTITY   = NUMBER, [ UNIT_Q ] ;
UNIT_Q     = "g" | "ml" | "un" ;
TIME       = NUMBER, [ "m" ] ;

(* --- expressões mínimas --- *)
COND       = SIMPLE, COMP_OP, SIMPLE ;
COMP_OP    = "==" | "!=" | "<" | ">" | "<=" | ">=" ;

SIMPLE     = TERM ;
TERM       = FACTOR, { "*", FACTOR } ;
FACTOR     = NUMBER | IDENT | BUILTIN ;

BUILTIN    = "volume" ;

IDENT      = LETTER, { LETTER | DIGIT | "_" } ;
NUMBER     = DIGIT, { DIGIT }, [ ".", DIGIT, { DIGIT } ] ;
STRING     = "\"", { any_char_except_quote }, "\"" ;

LETTER     = "A" | ... | "Z" | "a" | ... | "z" ;
DIGIT      = "0" | ... | "9" ;

```

## Símbolos não terminais (parsers)

PROGRAM → várias receitas

RECIPE → um bloco com nome e lista de STATEMENTs

STATEMENT (genérico) → pode ser STEP, ASSIGN_STMT, IF_STMT, WHILE_STMT, PRINT_STMT

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ASSIGN_STMT → IDENT "=" SIMPLE

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IF_STMT → if "(" COND ")" ":" STATEMENT

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;WHILE_STMT → while "(" COND ")" ":" STATEMENT

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PRINT_STMT → print "(" STRING ")"

STEP (domínio) → pode ser ADD_STEP, MIX_STEP, RISE_STEP, BAKE_STEP, WAIT_STEP

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ADD_STEP → "add" IDENT [ "," QUANTITY ]

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;MIX_STEP → "mix"

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;RISE_STEP → "rise" TIME

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BAKE_STEP → "bake" TIME

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;WAIT_STEP → "wait" TIME

QUANTITY → NUMBER [ UNIT_Q ]

TIME → NUMBER [ M_UNIT ]  (ex.: 40 ou 40 m)

COND → SIMPLE COMP_OP SIMPLE  (comparação simples, sem and/or/not)

SIMPLE → TERM  (apenas multiplicação)

TERM → FACTOR { "*" FACTOR }

FACTOR → NUMBER | IDENT | "volume"  (volume é built-in dinâmico)

## Símbolos terminais (tokens)

### palavras reservadas

ADD → "add"

MIX → "mix"

RISE → "rise"

BAKE → "bake"

WAIT → "wait"

IF → "if"

WHILE → "while"

PRINT → "print"

VOLUME → "volume"  (built-in de leitura de sensor)

### símbolos de estrutura

LPAREN → "("
RPAREN → ")"
SEMI → ";"
COMMA → ","
COLON → ":"

### operadores

ASSIGN → "="
COMP_OP → "==" | "!= | "<" | ">" | "<=" | ">="
MUL → "*"

### literais

IDENT → nomes (ex.: farinha, agua, pao_branco, vol_inicial, vol)
NUMBER → números inteiros ou decimais (ex.: 500, 1.4, 0.90)
STRING → textos entre aspas (ex.: "jogar fora")

### unidades

UNIT_Q → "g" | "ml" | "un"
M_UNIT → "m"  (minutos para TIME)

### +++

EOF → fim do arquivo





















## Simbolos nao terminais (parsers)
`PROGRAM` → várias receitas

`RECIPE` → um bloco com nome e lista de passos

`STEP` (genérico) → pode ser ADD_STEP, MIX_STEP, RISE_STEP, BAKE_STEP, WAIT_STEP (subclasses)


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ADD_STEP` → "add" IDENT [ "," QUANTITY ]

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`MIX_STEP` → "mix"

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`RISE_STEP` → "rise" NUMBER

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`BAKE_STEP` → "bake" NUMBER

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`WAIT_STEP` → "wait" NUMBER

`QUANTITY` → NUMBER [ UNIT_Q ]

## Simbolos terminais (tokens)

**palavras reservadas**

`ADD` → "add"

`MIX` → "mix"

`RISE` → "rise"

`BAKE` → "bake"

`WAIT` → "wait"

**símbolos de estrutura**

`LPAREN` → "("

`RPAREN` → ")"

`SEMI` → ";"

`COMMA` → ","

**literais**

`IDENT` → nomes (farinha, agua, pao_branco, etc.)

`NUMBER` → números inteiros (500, 40, 60)

`UNIT_Q` → "g" | "ml" | "un" (se você quiser manter unidades de quantidade)

**+++**

`EOF` → fim do arquivo 