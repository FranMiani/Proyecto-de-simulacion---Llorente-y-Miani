import matplotlib.pyplot as plt
import sys
import os

# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
import random

class ControladorBomba(Atomic):
    def aux(self):
        self.hold_in("active", min(self.sigma,self.sigma_bolsa))
        
    def __init__(self, name="ControladorBomba"):
        super().__init__(name)

        self.i_orden_medica = Port(float, "i_orden_medica")
        self.i_sensor_flujo = Port(float, "i_sensor_flujo")
        self.i_fin_bolsa = Port(bool, "i_fin_bolsa")
        self.i_confirmacion= Port(str, "i_confirmacion")

        self.add_in_port(self.i_orden_medica)
        self.add_in_port(self.i_sensor_flujo)
        self.add_in_port(self.i_fin_bolsa)
        self.add_in_port(self.i_confirmacion)

        self.o_ajustar_caudal = Port(float, "o_ajustar_caudal")
        self.o_detener_bomba = Port(str, "i_detener_bomba")
        self.o_alarma = Port(str, "o_alarma")
        self.o_registrar_evento = Port(str, "o_registrar_evento")

        self.add_out_port(self.o_ajustar_caudal)
        self.add_out_port(self.o_detener_bomba)
        self.add_out_port(self.o_alarma)
        self.add_out_port(self.o_registrar_evento)


        self.fase = "ESPERANDO"
        self.estado_bolsa = "ACEPTABLE"
        self.caudal_indicado = 0.0
        self.caudal_real = 0.0
        self.sigma_bolsa = 0.0
        self.sigma = 0.0
        
    def initialize(self):
        self.passivate()

    def exit(self):
        pass

    def deltint(self):
        if(self.fase == "PROCESANDO_ORDEN" and self.caudal_indicado > 0):
            self.fase = "INFUNDIENDO"
            self.passivate()
        elif(self.fase == "PROCESANDO_ORDEN" and self.caudal_indicado == 0):
            self.fase = "ESPERANDO"
            self.passivate()
        elif(self.fase == "EVALUANDO_DESVIO"):
            self.fase = "EVALUANDO_CRITICA"
            self.sigm -= self.sigma
            self.sigma =  max(0, 5 - 5*(abs(self.caudal_indicado - self.caudal_real) / self.caudal_indicado))
            self.aux()
        elif(self.fase == "EVALUANDO_CRITICA"):
            self.fase = "DETENIDO_POR_CRITICA"
            self.sigmabolsa -= self.sigma
            self.activate()
        elif(self.fase == "DETENIDO_POR_CRITICA"):
            self.passivate()
        elif(self.sigma_bolsa == 0 and self.estado_bolsa == "ACEPTABLE"):
            self.estado_bolsa = "FINALIZANDO"
            self.sigma_bolsa = 60
            self.aux()
        elif(self.fase == "ESPERANDO_FIN_BOLSA"):
            self.fase = "ESPERANDO"
            self.estado_bolsa = "VACIA"
            self.passivate()

    def deltext(self, e):
        if self.i_orden_medica:
            self.fase = "PROCESANDO_ORDEN"
            self.sigma_bolsa -= e
            ran = random.uniform(0, 3)  #Retardo aleatorio entre la orden y su procesamiento
            self.sigma = ran
            self.caudal_indicado = self.i_orden_medica.get()
            self.aux()
        elif self.i_sensor_flujo:
            if(self.fase == "INFUNDIENDO" and abs (self.i_sensor_flujo.get() - self.caudal_indicado) > (0.1 * self.caudal_indicado)):   #Desvio significativo si > 10%
                self.fase = "EVALUANDO_DESVIO"
                self.sigma_bolsa -= e
                self.sigma = 5
                self.aux()
            if(self.fase in ["EVALUANDO_CRITICA", "EVALUANDO_DESVIO", "INFUNDIENDO"] and abs(self.i_sensor_flujo.get() - self.caudal_indicado) <= (0.1 * self.caudal_indicado)):
                self.fase = "INFUNDIENDO"
                self.sigma_bolsa -= e
                self.passivate()
            if(self.fase in ["EVALUANDO_CRITICA", "EVALUANDO_DESVIO"] and abs(self.i_sensor_flujo.get() - self.caudal_indicado) > (0.1 * self.caudal_indicado)):
                self.sigma_bolsa -= e
                self.sigma -= e
                self.aux()
        elif self.i_fin_bolsa:
            self.sigma_bolsa = 60
            self.sigma -= e
            self.aux()
        elif self.i_confirmacion:
            if self.fase == "DETENIDO_POR_CRITICA":
                self.fase = "ESPERANDO"
                self.sigma_bolsa = float('inf')
                self.sigma = float('inf')
                self.passivate()
            else:
                self.fase = "PROCESANDO_ORDEN"
                self.estado_bolsa = "ACEPTABLE"
                self.sigma_bolsa = float('inf')
                self.sigma = float('inf')
                self.activate()
        else:
            self.sigma_bolsa -= e
            self.sigma -= e
            self.aux()

    def lambdaf(self):
        print(f"Disparando salida desde: {self.name}")
        if self.fase == "PROCESANDO_ORDEN" and self.caudal_indicado > 0:
            self.o_ajustar_caudal.add(self.caudal_indicado)
        if self.fase == "PROCESANDO_ORDEN" and self.caudal_indicado == 0:
            self.o_detener_bomba.add("DETENER")
        if self.fase == "EVALUANDO_DESVIO":
            self.o_alarma.add("MEDIA")  #Alarma de advertencia por desvio temporal de caudal
        if self.fase == "DETENIDO_POR_CRITICA":
            self.o_alarma.add("CRITICA")   #Alarma critica emitida tras confirmar persistencia del desvio
        if self.fase == "EVALUANDO_CRITICA" or self.estado_bolsa == "FINALIZANDO":
            self.o_detener_bomba.add("DETENER")
        if self.sigma_bolsa == 0 and self.estado_bolsa == "ACEPTABLE":
            self.o_alarma.add("BAJA")
        