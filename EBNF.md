# MAQUINA DE PAO/MASSA

## Exemplo entradaR
```
pao_branco(
  add farinha, 500 g;
  add agua, 300 ml;
  add fermento, 5 g;
  mix;
  rise 60 m;
  bake 40 m;
)
```

- Cada **RECEITA** tem um *nome* e uma serie de *steps*

- Cada **STEP** eh uma *acao | acao + ingrediente + qntd | acao + int* (nesse caso, int eh o tempo em minutos)

- **QNTD** eh um *inteiro* junto com uma *unidade* (g | ml | un)

- O nome da receita ou do ingrediente sera um IDENT, o compilador sabera diferenciar qual eh o que pelo contexto (o nome de uma receita vem antes de um openpar)

## EBNF 
```
PROGRAM   = { RECIPE } ;

RECIPE    = IDENT, "(", { STEP, ";" }, ")" ;

STEP      = ADD_STEP
          | MIX_STEP
          | RISE_STEP
          | BAKE_STEP
          | WAIT_STEP ;

ADD_STEP  = "add", IDENT, [ ",", QUANTITY ] ;
MIX_STEP  = "mix" ;
RISE_STEP = "rise", NUMBER ;     (* tempo em minutos *)
BAKE_STEP = "bake", NUMBER ;     (* tempo em minutos *)
WAIT_STEP = "wait", NUMBER ;     (* tempo em minutos *)

QUANTITY  = NUMBER, [ UNIT_Q ] ;

UNIT_Q    = "g" | "ml" | "un" ;

IDENT     = LETTER, { LETTER | DIGIT | "_" } ;
NUMBER    = DIGIT, { DIGIT } ;

LETTER    = "A" | ... | "Z" | "a" | ... | "z" ;
DIGIT     = "0" | ... | "9" ;
```

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