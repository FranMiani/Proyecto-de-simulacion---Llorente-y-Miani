
import matplotlib.pyplot as plt
import sys
import os
from parametros import Params
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
class SensorDeFlujo(Atomic):
    def __init__(self, name="SensorDeFlujo"):
        super().__init__(name)

        self.i_caudalActual = Port(float, "i_caudalActual")
        self.o_sensorFlujo = Port(float, "o_sensorFlujo")
        self.add_in_port(self.i_caudalActual)
        self.add_out_port(self.o_sensorFlujo)

        self.caudal_medido = 0.0

    def initialize(self):
        self.hold_in("active", 0)

    def exit(self):
        pass

    def deltint(self):
        self.hold_in("active", Params.SENSOR_PERIODO_MUESTREO)

    def deltext(self, e):
        self.caudal_medido = self.i_caudalActual.get()
        self.continuef(e)

    def lambdaf(self):
        # print(f"Disparando salida desde: {self.name}")
        self.o_sensorFlujo.add(self.caudal_medido)
