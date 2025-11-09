# main.py
# Compilador da Linguagem da Máquina de Pão (BreadLang)
# Gera assembly para a BreadVM
import sys
from abc import ABC, abstractmethod

# ============================================================
# Infraestrutura de geração de código
# ============================================================
class Code:
    instructions = []

    @staticmethod
    def reset():
        Code.instructions = []

    @staticmethod
    def append(line: str):
        if not line.endswith("\n"):
            line += "\n"
        Code.instructions.append(line)

    @staticmethod
    def dump(filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            for line in Code.instructions:
                f.write(line)


# ============================================================
# Tabela de símbolos
# ============================================================
class SymbolTable(dict):
    pass


# ============================================================
# Tokens e Lexer
# ============================================================
class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value


class Lexer:
    RESERVED = {
        "add": "ADD",
        "mix": "MIX",
        "rise": "RISE",
        "bake": "BAKE",
        "wait": "WAIT",
        "print": "PRINT",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "volume": "VOLUME",
    }

    def __init__(self, src: str):
        self.src = src
        self.pos = 0
        self.next = None

    def select_next(self):
        s = self.src
        while self.pos < len(s) and s[self.pos].isspace():
            self.pos += 1
        if self.pos >= len(s):
            self.next = Token("EOF", "")
            return

        c = s[self.pos]

        # strings
        if c == '"':
            self.pos += 1
            val = ""
            while self.pos < len(s) and s[self.pos] != '"':
                val += s[self.pos]
                self.pos += 1
            self.pos += 1
            self.next = Token("STRING", val)
            return

        # números
        if c.isdigit():
            val = ""
            while self.pos < len(s) and (s[self.pos].isdigit() or s[self.pos] == "."):
                val += s[self.pos]
                self.pos += 1
            self.next = Token("NUMBER", float(val))
            return

        # palavras
        if c.isalpha():
            ident = ""
            while self.pos < len(s) and (s[self.pos].isalnum() or s[self.pos] == "_"):
                ident += s[self.pos]
                self.pos += 1
            kind = Lexer.RESERVED.get(ident.lower(), "IDENT")
            self.next = Token(kind, ident)
            return

        # operadores compostos (==, !=)
        if c in ["=", "!"]:
            if self.pos + 1 < len(s) and s[self.pos + 1] == "=":
                if c == "=":
                    self.next = Token("EQ", "==")
                else:
                    self.next = Token("NEQ", "!=")
                self.pos += 2
                return

        # operadores simples e símbolos
        symbols = {
            "(": "LPAREN", ")": "RPAREN",
            "{": "LBRACE", "}": "RBRACE",
            ":": "COLON", ";": "SEMI", ",": "COMMA",
            "=": "ASSIGN",
            "<": "LT", ">": "GT",
        }
        if c in symbols:
            self.next = Token(symbols[c], c)
            self.pos += 1
            return

        # segurança extra: captura < ou > colados
        if c in "<>":
            self.next = Token("LT" if c == "<" else "GT", c)
            self.pos += 1
            return

        raise Exception(f"Caractere inválido: {c}")


# ============================================================
# AST Nodes
# ============================================================
class Node(ABC):
    def __init__(self, value=None, children=None):
        self.value = value
        self.children = children or []

    @abstractmethod
    def generate(self, st: SymbolTable): ...


# --- Valores e Expressões ---
class Number(Node):
    def generate(self, st): return self.value


class Volume(Node):
    def generate(self, st):
        Code.append("READ R_VOL SENSOR_VOL")
        return "R_VOL"


class Comparison(Node):
    """Representa uma comparação: left < right, etc."""
    def generate(self, st):
        left = self.children[0].generate(st)
        right = self.children[1].generate(st)
        op = self.value
        lbl = str(id(self))
        #Code.append("READ R_VOL SENSOR_VOL")  # leitura do sensor
        Code.append(f"SET R_TMP {right}")
        if op == "<":
            Code.append("CMP R_VOL R_TMP")
            Code.append(f"JLT cond_true_{lbl}")
        elif op == ">":
            Code.append("CMP R_VOL R_TMP")
            Code.append(f"JGT cond_true_{lbl}")
        elif op == "==":
            Code.append("CMP R_VOL R_TMP")
            Code.append(f"JE cond_true_{lbl}")
        elif op == "!=":
            Code.append("CMP R_VOL R_TMP")
            Code.append(f"JNE cond_true_{lbl}")
        return lbl


# --- Comandos da Linguagem ---
class AddStep(Node):
    def generate(self, st):
        qty = self.children[0].value if self.children else 0
        Code.append(f"ADD VOL {qty}")


class MixStep(Node):
    def generate(self, st): Code.append("MIX")


class RiseStep(Node):
    def generate(self, st): Code.append(f"RISE {self.value}")


class BakeStep(Node):
    def generate(self, st): Code.append(f"BAKE {self.value}")


class WaitStep(Node):
    def generate(self, st): Code.append(f"WAIT {self.value}")


class Print(Node):
    def generate(self, st):
        if isinstance(self.children[0], String):
            Code.append(f'PRINT "{self.children[0].value}"')
        else:
            Code.append("PRINT VOL")


class String(Node):
    def generate(self, st): Code.append(f'PRINT "{self.value}"')


# --- Controle de Fluxo ---
class If(Node):
    def generate(self, st):
        lbl = str(id(self))
        cond_lbl = self.children[0].generate(st)
        Code.append(f"GOTO else_{lbl}")
        Code.append(f"cond_true_{cond_lbl}:")
        self.children[1].generate(st)
        Code.append(f"GOTO end_{lbl}")
        Code.append(f"else_{lbl}:")
        if len(self.children) > 2 and self.children[2]:
            self.children[2].generate(st)
        Code.append(f"end_{lbl}:")


class While(Node):
    def generate(self, st):
        lbl = str(id(self))
        Code.append(f"loop_{lbl}:")
        cond_lbl = self.children[0].generate(st)
        Code.append(f"GOTO end_{lbl}")
        Code.append(f"cond_true_{cond_lbl}:")
        self.children[1].generate(st)
        Code.append(f"GOTO loop_{lbl}")
        Code.append(f"end_{lbl}:")


# --- Blocos ---
class Block(Node):
    def generate(self, st):
        for c in self.children:
            c.generate(st)


# ============================================================
# Parser
# ============================================================
class Parser:
    @staticmethod
    def parse(src: str):
        lex = Lexer(src)
        lex.select_next()
        block = Block()
        while lex.next.kind != "EOF":
            block.children.append(Parser.parse_statement(lex))
        return block

    @staticmethod
    def parse_condition(lex: Lexer):
        # consome o primeiro token (espera 'volume')
        if lex.next.kind != "VOLUME":
            raise Exception("Esperado 'volume' na condição")
        left = Volume()
        lex.select_next()  # avança para o operador

        # agora lê o operador (<, >, ==, !=)
        op_token = lex.next
        if op_token.kind not in ("LT", "GT", "EQ", "NEQ"):
            raise Exception("Esperado operador de comparação (<, >, ==, !=)")
        op = op_token.value
        lex.select_next()

        # agora lê o número
        if lex.next.kind == "NUMBER":
            right = Number(lex.next.value)
            lex.select_next()
        else:
            raise Exception("Esperado número após operador de comparação")

        return Comparison(op, [left, right])


    @staticmethod
    def parse_statement(lex: Lexer):
        k = lex.next.kind

        if k == "ADD":
            lex.select_next()
            qty = None
            if lex.next.kind == "IDENT": lex.select_next()
            if lex.next.kind == "COMMA":
                lex.select_next()
                if lex.next.kind == "NUMBER":
                    qty = Number(lex.next.value)
                    lex.select_next()
            if lex.next.kind == "SEMI": lex.select_next()
            return AddStep(None, [qty] if qty else [])

        if k == "MIX":
            lex.select_next()
            if lex.next.kind == "SEMI": lex.select_next()
            return MixStep()

        if k == "RISE":
            lex.select_next()
            val = 0
            if lex.next.kind == "NUMBER":
                val = lex.next.value
                lex.select_next()
            if lex.next.kind == "SEMI": lex.select_next()
            return RiseStep(val)

        if k == "BAKE":
            lex.select_next()
            val = 0
            if lex.next.kind == "NUMBER":
                val = lex.next.value
                lex.select_next()
            if lex.next.kind == "SEMI": lex.select_next()
            return BakeStep(val)

        if k == "WAIT":
            lex.select_next()
            val = 0
            if lex.next.kind == "NUMBER":
                val = lex.next.value
                lex.select_next()
            if lex.next.kind == "SEMI": lex.select_next()
            return WaitStep(val)

        if k == "PRINT":
            lex.select_next()
            if lex.next.kind != "LPAREN": raise Exception("Esperado '(' após print")
            lex.select_next()
            msg = None
            if lex.next.kind == "STRING":
                msg = String(lex.next.value)
                lex.select_next()
            if lex.next.kind != "RPAREN": raise Exception("Esperado ')'")
            lex.select_next()
            if lex.next.kind == "SEMI": lex.select_next()
            return Print(None, [msg])

        if k == "IF":
            lex.select_next()
            if lex.next.kind != "LPAREN": raise Exception("Esperado '('")
            lex.select_next()
            cond = Parser.parse_condition(lex)
            if lex.next.kind != "RPAREN": raise Exception("Esperado ')'")
            lex.select_next()
            if lex.next.kind != "LBRACE": raise Exception("Esperado '{'")
            lex.select_next()
            then_block = Block()
            while lex.next.kind != "RBRACE":
                then_block.children.append(Parser.parse_statement(lex))
            lex.select_next()
            else_block = None
            if lex.next.kind == "ELSE":
                lex.select_next()
                if lex.next.kind != "LBRACE": raise Exception("Esperado '{'")
                lex.select_next()
                else_block = Block()
                while lex.next.kind != "RBRACE":
                    else_block.children.append(Parser.parse_statement(lex))
                lex.select_next()
            return If(None, [cond, then_block, else_block])

        if k == "WHILE":
            lex.select_next()
            if lex.next.kind != "LPAREN": raise Exception("Esperado '('")
            lex.select_next()
            cond = Parser.parse_condition(lex)
            if lex.next.kind != "RPAREN": raise Exception("Esperado ')'")
            lex.select_next()
            if lex.next.kind != "LBRACE": raise Exception("Esperado '{'")
            lex.select_next()
            body = Block()
            while lex.next.kind != "RBRACE":
                body.children.append(Parser.parse_statement(lex))
            lex.select_next()
            return While(None, [cond, body])

        raise Exception(f"Comando inesperado: {k}")


# ============================================================
# Geração de Assembly
# ============================================================
def write_asm_from_ast(ast_root: Node, filename: str):
    Code.reset()
    st = SymbolTable()
    ast_root.generate(st)
    Code.append("HALT")
    out = filename.rsplit(".", 1)[0] + ".asm"
    Code.dump(out)
    print(f"[ok] Assembly gerado em: {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <arquivo.bread>")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "r", encoding="utf-8") as f:
        src = f.read()

    ast = Parser.parse(src)
    write_asm_from_ast(ast, filename)
