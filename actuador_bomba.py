import matplotlib.pyplot as plt
import sys
import os

# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
class ActuadorDeBomba(Atomic):
    def __init__(self, name="ActuadorDeBomba"):
        super().__init__(name)

        self.i_ajustar_caudal = Port(float, "i_ajustar_caudal")
        self.i_detener_bomba = Port(str, "i_detener_bomba")
        self.o_caudal_actual = Port(float, "o_caudal_actual")
        self.add_in_port(self.i_ajustar_caudal)
        self.add_in_port(self.i_detener_bomba)
        self.add_out_port(self.o_caudal_actual)
        
        
        self.caudal_objetivo = 0.0

    def initialize(self):
        self.passivate()

    def exit(self):
        pass

    def deltint(self):
        self.passivate()

    def deltext(self, e):
        if self.i_ajustar_caudal:
            self.caudal_objetivo = self.i_ajustar_caudal.get()
    
        if self.i_detener_bomba:
            self.caudal_objetivo = 0.0  #caudal = 0 representa la bomba detenida

        self.hold_in("active", 0.5) #0.5 segundos de latencia

    def lambdaf(self):
        print(f"Disparando salida desde: {self.name}")
        self.o_caudal_actual.add(self.caudal_objetivo)

        
