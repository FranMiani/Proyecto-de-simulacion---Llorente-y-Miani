import matplotlib.pyplot as plt
import sys
import os

# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
class RegistradorEventos(Atomic):
    def __init__(self, name="RegistradorEventos"):
        super().__init__(name)

        self.i_caudal_real = Port(float, "i_caudal_real")
        self.i_ajustar_caudal = Port(float, "i_ajustarCaudal")
        self.i_detener_bomba = Port(str, "i_detenerBomba")
        self.i_alarma = Port(str, "i_alarma")

        self.add_in_port(self.i_caudal_real)
        self.add_in_port(self.i_ajustar_caudal)
        self.add_in_port(self.i_detener_bomba)
        self.add_in_port(self.i_alarma)
        self.o_registro = Port(str, "o_registro")

        self.add_out_port(self.o_registro)

        
        self.mensaje = ""
        self.sigma = float('inf')
        
        self.reloj_global = 0.0
        self.historial_tiempos_caudal = []
        self.historial_valores_caudal = []
        self.historial_tiempos_alarma = []
        self.historial_valores_alarma = []
        self.historial_tiempos_caudal_real = []
        self.historial_valores_caudal_real = []

    def initialize(self):
        self.mensaje = ""
        self.reloj_global = 0.0
        self.passivate()

    def exit(self):
        pass

    def deltint(self):
        self.mensaje = ""
        self.passivate()

    def deltext(self, e):
        self.reloj_global += e

        # Evaluamos qué puerto trajo el evento (siguiendo el estilo de tu Controlador)
        if self.i_ajustar_caudal:
            valor = self.i_ajustar_caudal.get()
            self.mensaje = f"Ajuste de caudal a: {valor}"
            
            # Guardamos el dato crudo para el gráfico
            self.historial_tiempos_caudal.append(self.reloj_global)
            self.historial_valores_caudal.append(valor)
            
            self.hold_in("active", 0.0) # Transición inmediata (sigma = 0)

        elif self.i_detener_bomba:
            self.mensaje = "Detencion de bomba"
            
            # Si se detiene la bomba, el caudal cae a cero
            self.historial_tiempos_caudal.append(self.reloj_global)
            self.historial_valores_caudal.append(0.0)
            
            self.hold_in("active", 0.0)

        elif self.i_alarma:
            nivel = self.i_alarma.get()
            self.mensaje = f"Alarma: {nivel}"
            
            # Guardamos el nivel de alarma y el tiempo exacto
            self.historial_tiempos_alarma.append(self.reloj_global)
            self.historial_valores_alarma.append(nivel)
            
            self.hold_in("active", 0.0)

        elif self.i_caudal_real:
            valor = self.i_caudal_real.get()
        
            self.historial_tiempos_caudal_real.append(self.reloj_global)
            self.historial_valores_caudal_real.append(valor)
        
            self.mensaje = f"Caudal real: {valor}"
        
            self.hold_in("active", 0.0)
        
        
    def lambdaf(self):
        print(f"Disparando salida desde: {self.name}")
        # Equivalente a: case out = (registro, mensaje); if (mensaje != " ")
        if self.mensaje != "":
            self.o_registro.add(self.mensaje)