import matplotlib.pyplot as plt
import sys
import os

# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
import random

class GeneradorOrdenesMedicas(Atomic):
    def __init__(self, name="GeneradorOrdenesMedicas"):
        super().__init__(name)

        self.o_caudal = Port(float, "Caudal")
        self.add_out_port(self.o_caudal)

        self.caudal_indicado = 100.0 # Decision: empezamos con caudal - 100

    def initialize(self):
        self.hold_in("active", 0)

    def exit(self):
        pass

    def deltint(self):

        c = random.uniform(1, 300)

        if c <= 200:
            self.caudal_indicado = c
        else:
            # caudal inválido => detener bomba
            self.caudal_indicado = 0.0

        self.hold_in("active", 60)

    def deltext(self, e):
        # no posee entradas
        pass

    def lambdaf(self):
        print(f"Disparando salida desde: {self.name}")
        self.o_caudal.add(self.caudal_indicado)
