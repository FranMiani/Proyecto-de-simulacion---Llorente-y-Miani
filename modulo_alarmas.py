import sys
import os
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
from parametros import FaseAlarma, NivelAlarma, Params
class ModuloAlarmas(Atomic):
    def __init__(self, name="ModuloAlarmas"):
        super().__init__(name)

        self.i_alarma = Port(str, "i_alarma")
        self.i_confirmacionEnfermero = Port(str, "i_confirmacionEnfermero")
        self.o_notificacionAlarma = Port(str, "o_notificacionAlarma")
        self.add_in_port(self.i_alarma)
        self.add_in_port(self.i_confirmacionEnfermero)
        self.add_out_port(self.o_notificacionAlarma)
        
        self.fase = FaseAlarma.REPOSO
        self.tipo = NivelAlarma.NINGUNA

    def initialize(self):
        self.hold_in("active", float('inf'))

    def exit(self): pass

    def deltint(self):
        if self.fase == FaseAlarma.NOTIFICAR_NUEVA and self.tipo != NivelAlarma.CRITICA:
            self.fase = FaseAlarma.REPOSO
            self.tipo = NivelAlarma.NINGUNA
            self.hold_in("active", float('inf'))
        elif self.fase == FaseAlarma.NOTIFICAR_NUEVA and self.tipo == NivelAlarma.CRITICA:
            self.fase = FaseAlarma.ESPERANDO_30
            self.hold_in("active", Params.ALARMA_ESPERA_INICIAL)
        elif self.fase == FaseAlarma.ESPERANDO_30 and self.tipo == NivelAlarma.CRITICA:
            self.fase = FaseAlarma.ESPERANDO_10
            self.hold_in("active", Params.ALARMA_ESPERA_REPETICION)
        elif self.fase == FaseAlarma.ESPERANDO_10 and self.tipo == NivelAlarma.CRITICA:
            self.hold_in("active", Params.ALARMA_ESPERA_REPETICION)
            
    def deltext(self, e):
        if self.i_alarma:
            self.fase = FaseAlarma.NOTIFICAR_NUEVA
            self.tipo = NivelAlarma(self.i_alarma.get()) 
            self.hold_in("active", 0)
        elif self.i_confirmacionEnfermero:
            self.fase = FaseAlarma.REPOSO
            self.tipo = NivelAlarma.NINGUNA
            self.hold_in("active", float('inf'))

    def lambdaf(self):
        self.o_notificacionAlarma.add(self.tipo.value)