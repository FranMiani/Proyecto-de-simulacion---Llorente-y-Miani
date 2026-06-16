from ..xdevs.models import Atomic, Port

class ActuadorDeBomba(Atomic):
    def __init__(self, name"ActuadorDeBomba"):
        super().__init__(name)

        self.i_ajustar_caudal = Port(float, "i_ajustar_caudal")
        self.i_detener_bomba = Port(str, "i_detener_bomba")

        self.o_caudal_actual = Port(float, "o_caudal_actual")

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
        self.o_caudal_actual.add(self.caudal_objetivo)

        
