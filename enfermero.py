import matplotlib.pyplot as plt
import sys
import os
from parametros import Params
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
        self.hold_in("active", self.sigma)

    def exit(self):
        pass

    def deltint(self):
        self.sigma = float('inf')
        self.hold_in("active", self.sigma)

    def deltext(self, e):
        if self.i_notificacionAlarma:
            alarma = self.i_notificacionAlarma.get()

            if alarma=="BAJA" and self.sigma== float('inf'):
                self.sigma = Params.generar_tiempo_enfermero_baja()
            elif alarma=="BAJA" and self.sigma!= float('inf'):
                self.sigma = min(self.sigma - e, Params.generar_tiempo_enfermero_baja())
            elif alarma=="CRITICA" and self.sigma== float('inf'):
                self.sigma = Params.generar_tiempo_enfermero_critica()
            elif alarma=="CRITICA" and self.sigma != float('inf'):
                self.sigma = min(self.sigma - e,Params.generar_tiempo_enfermero_critica())
            elif self.sigma != float('inf'):
                self.sigma = self.sigma - e
        if self.sigma != float('inf'):
            self.hold_in("active",self.sigma)



    def lambdaf(self):
        # print(f"Disparando salida desde: {self.name}")
        self.o_confirmacion.add("")