import matplotlib.pyplot as plt
import sys
import os

# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
import random

class Enfermero(Atomic):
    def __init__(self, name="Enfermero"):
        super().__init__(name)
        self.i_notificacionAlarma = Port(str, "i_notificacionAlarma")
        
        self.o_confirmacion= Port(str, "o_confirmacion")
        self.add_out_port(self.o_confirmacion)
        self.add_in_port(self.i_notificacionAlarma)
        self.sigma = float('inf')

    def initialize(self):
        self.passivate()

    def exit(self):
        pass

    def deltint(self):
        self.sigma = float('inf')
        self.passivate()

    def deltext(self, e):
        if self.i_notificacionAlarma:
            alarma = self.i_notificacionAlarma.get()
            if alarma=="BAJA" and self.sigma== float('inf'):
                self.sigma = random.uniform(30,90)
            elif alarma=="CRIITICA" and self.sigma== float('inf'):
                self.sigma = random.uniform(5,10)
            elif alarma=="CRIITICA" and self.sigma != float('inf'):
                self.sigma = min(self.sigma - e,random.uniform(5,10))
            elif self.sigma != float('inf'):
                self.sigma = self.sigma - e
        if self.sigma != float('inf'):
            self.hold_in("active",self.sigma)



    def lambdaf(self):
        print(f"Disparando salida desde: {self.name}")
        self.o_confirmacion.add("")