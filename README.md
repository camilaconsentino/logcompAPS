# logcompAPS - BREAD LANGUAGE

# Introdução 
### O que é a máquina (BreadVM)

A **BreadVM** simula o funcionamento real de uma **máquina de fazer pão doméstica**, com estágios automáticos de preparo — mistura, fermentação, crescimento, descanso e forno. Ela possui sensores virtuais de **volume** e **temperatura**, que permitem medir o comportamento da massa ao longo do processo. Diferente de uma simulação genérica, a BreadVM foi concebida como uma máquina **que busca o “pão perfeito”**, isto é, um pão que mantém o volume ideal em cada etapa: cresce de forma equilibrada, assa na temperatura certa e termina com textura e densidade simuladas conforme o código do programa. Cada instrução (como `mix`, `rise`, `bake`) modifica o estado interno da máquina, e as condições no código permitem ajustar o processo para alcançar o resultado ideal.

O compilador lê instruções de alto nível (como mix, rise, bake) e gera código assembly interpretado pela VM. O sistema implementa variáveis (como o sensor volume), estruturas condicionais e loops, cumprindo todos os requisitos da APS. A BreadVM foi criada a partir da MicrowaveVM, adaptada para um contexto culinário. 

**Nota**: há um protótipo Flex/Bison em C na pasta `breadlang/` (entrega parcial #1 e #2). A versão executável da linguagem/VM atualmente é a do compilador Python (`main.py`) + BreadVM (`breadVM.py`).

### Diferenças BreadVM vs MicrowaveVM

- MicrowaveVM: registradores TIME/POWER, instruções como SET, INC, DECJZ, GOTO, PRINT, HALT e um modelo térmico de micro-ondas.

- BreadVM: domínio de pão (volume/temperatura, mistura, fermentação, forno), comandos de alto nível (MIX, RISE, BAKE, WAIT) e comparações com sensores (READ/CMP/Jxx).

- A BreadVM herda a ideia de “assembly textual interpretado”, mas muda o conjunto de instruções para o domínio de panificação.

### Decisões de projeto

- DSL de processo: linguagem explícita de etapas (mistura, crescimento, forno).

- Sensor como variável read-only: volume é lido via READ antes de CMP.

- Controle de fluxo em VM textual: escolhas por labels + GOTO + Jxx.

- Unidades normalizadas: tempo em minutos; volume em ml.

- Separação clara: compilador (alto nível) vs VM (execução), destacando a noção de backend.

### Limitações conhecidas

- O modelo físico da BreadVM é simplificado (crescimento/redução determinísticos).

- Ainda não há tipos (somente números/strings/sensor volume).

- Comparações suportadas: <, >, ==, != (expansão para <=, >= é trivial).

- Não há funções/receitas aninhadas; foco em script linear com blocos.

### Organizacao do repositorio
```/
├─ breadlang/                 # (opcional/legado) versão Flex/Bison em C
│  ├─ lexer.l, parser.y, ast.c/.h, main.c, Makefile, ...
│  └─ examples/
├─ EBNF.md                    # Gramática da linguagem (EBNF)
├─ main.py                    # Compilador em Python → gera .asm para BreadVM
├─ breadVM.py                 # Máquina Virtual que interpreta o .asm
├─ receita.bread              # Exemplo de programa em alto nível
├─ receita.asm                # Assembly gerado pelo compilador
└─ README.md                  # Este arquivo
```

# Visao geral

- **Comandos de alto nível:** add, mix, rise, bake, wait, print.

- **Sensores:** volume (lido da cuba) — usado em condições/loops.

- **Controle de fluxo:** if/else, while.

- O compilador gera labels e saltos no assembly (GOTO, JLT, JGT, JE, JNE).

### Pipeline
```
Programa .bread  ──▶  Parser/AST (Python)  ──▶  Generate()  ──▶  .asm
                                                             │
                                                             ▼
                                                      BreadVM (execução)
```

# EBNF
Versao resumida do arquivo `EBNF.md` (entrar la para mais detalhes)

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
### OBS
Na implementação atual de compilador, o built-in usado como sensor é volume (lido via READ R_VOL SENSOR_VOL). Unidades (g, ml, m) são normalizadas em ml para volume e minutos para tempo (no assembly são números simples).


# VM

## Instrucoes:
| Instrução                | Semântica resumida                                             |
| ------------------------ | -------------------------------------------------------------- |
| `SET R_TMP n`            | Define registrador temporário com constante                    |
| `READ R_VOL SENSOR_VOL`  | Lê o sensor de volume (ml) para `R_VOL`                        |
| `ADD VOL n`              | Incrementa volume interno simulado                             |
| `MIX`                    | Mistura a massa (aumenta homogeneidade / volume levemente)     |
| `RISE f`                 | Fermenta até atingir `f ×` o volume atual                      |
| `WAIT m`                 | Passa `m` minutos (crescimentos/decays internos são simulados) |
| `BAKE t`                 | Assa até atingir temperatura `t` °C; reduz volume levemente    |
| `CMP R_VOL R_TMP`        | Compara `R_VOL` com `R_TMP`                                    |
| `JLT / JGT / JE / JNE L` | Salta para `L` se `<`, `>`, `==`, `!=` (respectivamente)       |
| `GOTO L`                 | Salto incondicional                                            |
| `PRINT "texto"`          | Imprime string literal                                         |
| `PRINT VOL`              | Imprime valor do volume (ml)                                   |
| `label:`                 | Define rótulo                                                  |
| `HALT`                   | Finaliza execução                                              |

**Sensores read-only:** SENSOR_VOL (volume), SENSOR_TEMP (temperatura).

**Registradores auxiliares:** R_VOL, R_TMP (convenções usadas na geração de código).

A simulação física da BreadVM inclui crescimento durante WAIT/RISE e aquecimento/retração em BAKE. É um modelo simples, suficiente para demonstrar semântica.

## Mapeamento da linguagem:

| Comando BreadLang            | Assembly gerado (exemplo)                            |
| ---------------------------- | ---------------------------------------------------- |
| `add farinha, 500 g`         | `ADD VOL 500`                                        |
| `mix`                        | `MIX`                                                |
| `rise 2`                     | `RISE 2`                                             |
| `bake 180`                   | `BAKE 180`                                           |
| `wait 30 m`                  | `WAIT 30`                                            |
| `print("texto")`             | `PRINT "texto"`                                      |
| `print(volume)`              | `PRINT VOL`                                          |
| `while (volume < 200) {...}` | gera `loop_/end_` + `READ/CMP/JLT/GOTO`              |
| `if (volume > 300) {...}`    | gera `READ/CMP/JGT` + blocos `else_/end_` com labels |


# Como rodar

1. Gerar assembly a partir do programa de alto nível (gera `receita.asm`):

```
python3 main.py receita.bread
```


2. Executar o assembly na VM:
```
python3 breadVM.py receita.asm
```

3. Saída esperada:
```
Mistura realizada — volume homogêneo.
Massa cresceu até 2.0× o volume inicial.
Assado a 180 °C concluído.
VOL: 153.73
=== Programa finalizado ===
Estado final: {'VOL': 153.72..., 'TEMP': 182.41..., 'TIMER': 0.0, 'MIXER': 0}
```