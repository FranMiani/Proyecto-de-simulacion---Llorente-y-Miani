from xdevs.models import Atomic, Port
import random

class GeneradorOrdenesMedicas(Atomic):
    def __init__(self, name="GeneradorOrdenesMedicas"):
        super().___init___(name)

        self.o_caudal = Port(float, "Caudal")
        self.add_out_port(self.o_caudal)

        self.caudal_indicado = 100 # Decision: empezamos con caudal - 100

    def initialize(self):
        self.hold_in("active", 0)