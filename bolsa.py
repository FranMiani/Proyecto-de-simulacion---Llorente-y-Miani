import matplotlib.pyplot as plt
import sys
import os
from parametros import Params
# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
import random

class Bolsa(Atomic):
    def __init__(self, name="Bolsa"):
        super().__init__(name)
        self.i_confirmacion= Port(str, "i_confirmacion")
        self.o_finBolsa = Port(bool, "o_finBolsa")
        self.add_out_port(self.o_finBolsa)
        self.add_in_port(self.i_confirmacion)
        self.duracionBolsa = Params.generar_duracion_bolsa()

    def initialize(self):
        self.hold_in("active", self.duracionBolsa)

    def exit(self):
        pass

    def deltint(self):
        self.duracionBolsa = float('inf')
        self.passivate()

    def deltext(self, e):
        if self.i_confirmacion:
            if(self.duracionBolsa != float('inf')):
                self.duracionBolsa -= e
                self.continuef(e)
            else:
                self.duracionBolsa = Params.generar_duracion_bolsa()
                print("duracionBolsa", self.duracionBolsa)
                self.hold_in("active", self.duracionBolsa)

    def lambdaf(self):
        # print(f"Disparando salida desde: {self.name}")
        self.o_finBolsa.add(True)