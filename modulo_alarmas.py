from xdevs.py.xdevs.models import Atomic, Port

class GeneradorOrdenesMedicas(Atomic):
    def __init__(self, name="GeneradorOrdenesMedicas"):
        super().__init__(name)

        self.Alarma = Port(str, "Alarma")
        self.confirmacionEnfermero = Port(str, "confirmacionEnfermero")
        self.notificacionAlarma = Port(str, "notificacionAlarma")
        self.add_in_port(self.Alarma)
        self.add_in_port(self.confirmacionEnfermero)
        self.add_out_port(self.notificacionAlarma)
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
        if self.Alarma:
            self.fase = "NOTIFICAR_NUEVA"
            self.tipo = self.Alarma.get()
            self.hold_in("active", 0)
        if self.confirmacionEnfermero:
            self.fase = "REPOSO"
            self.tipo = "NINGUNA"
            self.passivate()
        self.continuef(e)

    def lambdaf(self):
        self.notificacionAlarma.add(self.tipo)

