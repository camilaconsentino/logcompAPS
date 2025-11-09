# BreadVM.py
# Máquina Virtual para a Linguagem de Pão / Massa
# Adaptada da MicrowaveVM

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import math

Register = str


@dataclass
class Instr:
    op: str
    args: Tuple[str, ...]


class BreadVM:
    """
    VM para simular uma máquina de pão.

    Registradores:
      VOL   – volume atual da massa (ml)
      TEMP  – temperatura interna da cuba (°C)
      TIMER – temporizador (minutos)
      MIXER – estado do misturador (0/1)

    Sensores readonly:
      SENSOR_VOL, SENSOR_TEMP

    Instruções:
      SET R n           ; define valor numérico
      ADD R n           ; soma constante
      MUL R n           ; multiplica constante
      READ R SENSOR     ; lê sensor -> registrador
      WAIT n            ; simula passagem de n minutos
      MIX               ; mistura (aumenta volume)
      RISE n            ; crescimento controlado (aguarda até atingir fator n)
      BAKE n            ; aquece até n °C e reduz volume
      PRINT msg|R       ; imprime literal ou registrador
      HALT              ; encerra execução
      LABEL:            ; define ponto de salto
      GOTO label        ; salto incondicional
    """

    def __init__(self):
        # registradores mutáveis
        self.registers: Dict[Register, float] = {
            "VOL": 100.0,     # volume inicial (ml)
            "TEMP": 25.0,     # temperatura ambiente (°C)
            "TIMER": 0.0,
            "MIXER": 0.0,
        }
        # sensores (read-only)
        self.sensors: Dict[str, float] = {
            "SENSOR_VOL": 100.0,
            "SENSOR_TEMP": 25.0,
        }
        self.program: List[Instr] = []
        self.labels: Dict[str, int] = {}
        self.pc: int = 0
        self.halted: bool = False
        self.steps: int = 0

    # ----------------------------------------------------------
    # Carregamento e montagem do programa
    # ----------------------------------------------------------
    def load_program(self, source: str):
        self.program.clear()
        self.labels.clear()
        self.pc = 0
        self.halted = False
        self.steps = 0

        lines = source.splitlines()
        # 1ª passagem: coleta labels
        idx = 0
        for raw in lines:
            line = raw.split(";", 1)[0].strip()
            if not line:
                continue
            if line.endswith(":"):
                label = line[:-1].strip()
                if not label:
                    raise ValueError("Rótulo vazio.")
                if label in self.labels:
                    raise ValueError(f"Rótulo duplicado: {label}")
                self.labels[label] = idx
            else:
                idx += 1

        # 2ª passagem: parse das instruções
        for raw in lines:
            line = raw.split(";", 1)[0].strip()
            if not line or line.endswith(":"):
                continue
            tokens = line.replace(",", " ").split()
            op = tokens[0].upper()
            args = tuple(tokens[1:])
            self.program.append(Instr(op, args))

    # ----------------------------------------------------------
    # Execução
    # ----------------------------------------------------------
    def run(self, max_steps: Optional[int] = None):
        while not self.halted:
            if max_steps and self.steps >= max_steps:
                raise RuntimeError("Limite de passos atingido.")
            self.step()

    def step(self):
        if self.halted:
            return
        if not (0 <= self.pc < len(self.program)):
            self.halted = True
            return

        instr = self.program[self.pc]
        self.steps += 1
        op = instr.op
        args = instr.args

        def reg(r: str) -> str:
            return r.upper()

        # --- instruções aritméticas ---
        if op == "SET":
            r, n = reg(args[0]), float(args[1])
            self.registers[r] = n
            self.pc += 1

        elif op == "ADD":
            r, n = reg(args[0]), float(args[1])
            self.registers[r] += n
            self.pc += 1

        elif op == "MUL":
            r, n = reg(args[0]), float(args[1])
            self.registers[r] *= n
            self.pc += 1

        elif op == "READ":
            r, s = reg(args[0]), args[1].upper()
            if s not in self.sensors:
                raise ValueError(f"Sensor desconhecido: {s}")
            self.registers[r] = self.sensors[s]
            self.pc += 1

        elif op == "WAIT":
            n = float(args[0])
            self._simulate_wait(n)
            self.pc += 1

        elif op == "MIX":
            self._simulate_mix()
            self.pc += 1

        elif op == "RISE":
            factor = float(args[0])
            self._simulate_rise(factor)
            self.pc += 1

        elif op == "BAKE":
            temp = float(args[0])
            self._simulate_bake(temp)
            self.pc += 1

        elif op == "PRINT":
            if not args:
                print()
            elif args[0].upper() in self.registers:
                r = reg(args[0])
                print(f"{r}: {self.registers[r]:.2f}")
            else:
                print(" ".join(args))
            self.pc += 1

        elif op == "GOTO":
            label = args[0]
            if label not in self.labels:
                raise ValueError(f"Rótulo desconhecido: {label}")
            self.pc = self.labels[label]

        elif op == "HALT":
            print("=== Programa finalizado ===")
            self.halted = True

        else:
            raise ValueError(f"Instrução desconhecida: {op}")

    # ----------------------------------------------------------
    # Simulação dos efeitos físicos
    # ----------------------------------------------------------
    def _simulate_wait(self, minutes: float):
        """Durante espera, temperatura decai e volume cresce lentamente."""
        decay = max(0.95, 1 - minutes * 0.01)
        growth = 1 + minutes * 0.02
        self.registers["TEMP"] *= decay
        self.registers["VOL"] *= growth
        self._update_sensors()

    def _simulate_mix(self):
        """Mistura: ativa misturador e aumenta o volume levemente."""
        self.registers["MIXER"] = 1
        self.registers["VOL"] *= 1.05
        self.registers["MIXER"] = 0
        self._update_sensors()
        print("Mistura realizada — volume homogêneo.")

    def _simulate_rise(self, factor: float):
        """Crescimento até multiplicar o volume atual pelo fator."""
        target = self.registers["VOL"] * factor
        while self.registers["VOL"] < target:
            self._simulate_wait(1)
        print(f"Massa cresceu até {factor:.1f}× o volume inicial.")

    def _simulate_bake(self, target_temp: float):
        """Aquecimento até a temperatura indicada e leve redução de volume."""
        while self.registers["TEMP"] < target_temp:
            self.registers["TEMP"] += 5
            self.registers["VOL"] *= 0.99
        print(f"Assado a {target_temp:.0f} °C concluído.")
        self._update_sensors()

    def _update_sensors(self):
        self.sensors["SENSOR_VOL"] = self.registers["VOL"]
        self.sensors["SENSOR_TEMP"] = self.registers["TEMP"]

    # ----------------------------------------------------------
    # Estado
    # ----------------------------------------------------------
    def state(self) -> Dict[str, float]:
        return dict(self.registers)

    def reset(self):
        self.__init__()


# Exemplo de uso
if __name__ == "__main__":
    example = """
        MIX
        READ VOL SENSOR_VOL
        RISE 2
        BAKE 180
        PRINT VOL
        HALT
    """
    vm = BreadVM()
    vm.load_program(example)
    vm.run()
    print("Estado final:", vm.state())
