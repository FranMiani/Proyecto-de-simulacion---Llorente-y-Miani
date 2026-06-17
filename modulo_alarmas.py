import matplotlib.pyplot as plt
import sys
import os

# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
class ModuloAlarmas(Atomic):
    def __init__(self, name="ModuloAlarmas"):
        super().__init__(name)

        self.i_alarma = Port(str, "i_alarma")
        self.i_confirmacionEnfermero = Port(str, "i_confirmacionEnfermero")
        self.o_notificacionAlarma = Port(str, "o_notificacionAlarma")
        self.add_in_port(self.i_alarma)
        self.add_in_port(self.i_confirmacionEnfermero)
        self.add_out_port(self.o_notificacionAlarma)
        self.fase = "REPOSO"
        self.tipo = "NINGUNA"

    def initialize(self):
        self.passivate()

    def exit(self):
        pass

    def deltint(self):
        if (self.fase == "NOTIFICAR_NUEVA" and self.tipo != "CRITICA"):
            self.fase="REPOSO"
            self.tipo="NINGUNA"
            self.passivate()
        else:
            if self.fase == "NOTIFICAR_NUEVA" and self.tipo == "CRITICA":
                self.fase="ESPERANDO_30"
                self.tipo="CRITICA"
                self.hold_in("active", 30)
            else:
                if self.fase == "ESPERANDO_30" and self.tipo == "CRITICA":
                    self.fase="ESPERANDO_10"
                    self.tipo="CRITICA"
                    self.hold_in("active", 10)
                else:
                    if self.fase == "ESPERANDO_10" and self.tipo == "CRITICA":
                        self.fase="ESPERANDO_10"
                        self.tipo="CRITICA"
                        self.hold_in("active", 10)
            

    def deltext(self, e):
        if self.i_alarma:
            self.fase = "NOTIFICAR_NUEVA"
            self.tipo = self.i_alarma.get()
            self.hold_in("active", 0)
        if self.i_confirmacionEnfermero:
            self.fase = "REPOSO"
            self.tipo = "NINGUNA"
            self.passivate()
        self.continuef(e)

    def lambdaf(self):
        print(f"Disparando salida desde: {self.name}")
        self.o_notificacionAlarma.add(self.tipo)

