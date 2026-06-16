from xdevs.py.xdevs.models import Atomic, Port
class SensorDeFlujo(Atomic):
    def __init__(self, name="SensorDeFlujo"):
        super().__init__(name)

        self.caudalActual = Port(float, "caudalActual")
        self.sensorFlujo = Port(float, "sensorFlujo")
        self.add_in_port(self.caudalActual)
        self.add_out_port(self.sensorFlujo)

        self.caudal_medido = 0

    def initialize(self):
        self.hold_in("active", 0)

    def exit(self):
        pass

    def deltint(self):
        self.hold_in("active", 1)

    def deltext(self, e):
        self.caudal_medido = self.caudalActual.get()
        self.continuef(e)

    def lambdaf(self):
        self.sensorFlujo.add(self.caudal_medido)
