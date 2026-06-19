import random
import sys
import os
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
# Importamos nuestros parámetros
from parametros import FaseControlador, EstadoBolsa, NivelAlarma, ComandoBomba, Params

class ControladorBomba(Atomic):
    def aux(self):
        self.hold_in("active", min(self.sigma, self.sigma_bolsa))
        
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
        self.o_desvio_corregido = Port(bool, "o_desvio_corregido")

        self.add_out_port(self.o_ajustar_caudal)
        self.add_out_port(self.o_detener_bomba)
        self.add_out_port(self.o_alarma)
        self.add_out_port(self.o_registrar_evento)
        self.add_out_port(self.o_desvio_corregido)

        self.fase = FaseControlador.ESPERANDO
        self.estado_bolsa = EstadoBolsa.ACEPTABLE
        self.caudal_indicado = 0.0
        self.caudal_real = 0.0
        self.sigma_bolsa = float('inf')
        self.sigma = float('inf')
        self.desvio_corregido = False
        
    def initialize(self):
        self.passivate()

    def exit(self):
        pass

    def deltint(self):
        if self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado > 0:
            self.fase = FaseControlador.INFUNDIENDO
            self.passivate()
        elif self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado == 0:
            self.fase = FaseControlador.ESPERANDO
            self.passivate()
        elif self.fase == FaseControlador.DESVIADO:
            self.fase = FaseControlador.EVALUANDO_DESVIO
            self.sigma_bolsa -= self.sigma
            self.sigma = Params.generar_retardo(Params.CONTROL_TIEMPO_EVALUACION)
            self.aux()
        elif self.fase == FaseControlador.EVALUANDO_DESVIO:
            self.fase = FaseControlador.EVALUANDO_CRITICA
            self.sigma_bolsa -= self.sigma
            self.sigma = Params.tiempo_detencion_critica(self.caudal_real, self.caudal_indicado)    
            self.aux()
        elif self.fase == FaseControlador.EVALUANDO_CRITICA:
            self.fase = FaseControlador.DETENIDO_POR_CRITICA
            self.sigma_bolsa -= self.sigma
            self.activate()
        elif self.fase == FaseControlador.DETENIDO_POR_CRITICA:
            self.passivate()
        elif self.sigma_bolsa <= 0 and self.estado_bolsa == EstadoBolsa.ACEPTABLE:
            self.estado_bolsa = EstadoBolsa.FINALIZANDO
            self.sigma_bolsa = Params.CONTROL_TIEMPO_PREVIO_FIN_BOLSA
            self.aux()
        elif self.fase == FaseControlador.ESPERANDO_FIN_BOLSA:
            self.fase = FaseControlador.ESPERANDO
            self.estado_bolsa = EstadoBolsa.VACIA
            self.passivate()

    def deltext(self, e):
        if self.i_orden_medica:
            self.fase = FaseControlador.PROCESANDO_ORDEN
            self.sigma_bolsa -= e
            self.sigma = Params.generar_retardo_orden()
            self.caudal_indicado = self.i_orden_medica.get()
            self.aux()
            
        elif self.i_sensor_flujo:
            desvio_limite = Params.CONTROL_TOLERANCIA_DESVIO * self.caudal_indicado
            desvio_actual = abs(self.i_sensor_flujo.get() - self.caudal_indicado)
            
            if self.fase == FaseControlador.INFUNDIENDO and desvio_actual > desvio_limite:
                self.fase = FaseControlador.DESVIADO
                self.sigma_bolsa -= e
                self.sigma = 0.0
                self.aux()
                self.desvio_corregido = False
                
            if self.fase in [FaseControlador.EVALUANDO_CRITICA, FaseControlador.EVALUANDO_DESVIO, FaseControlador.INFUNDIENDO] and desvio_actual <= desvio_limite:
                if self.fase in [
                        FaseControlador.EVALUANDO_CRITICA,
                        FaseControlador.EVALUANDO_DESVIO]:
                
                    self.desvio_corregido = True
                
                self.fase = FaseControlador.INFUNDIENDO
                self.sigma_bolsa -= e
                self.passivate()
                
            if self.fase in [FaseControlador.EVALUANDO_CRITICA, FaseControlador.EVALUANDO_DESVIO] and desvio_actual > desvio_limite:
                self.sigma_bolsa -= e
                self.sigma -= e
                self.aux()
                
        elif self.i_fin_bolsa:
            self.sigma_bolsa = Params.CONTROL_TIEMPO_PREVIO_FIN_BOLSA
            self.sigma -= e
            self.aux()
            
        elif self.i_confirmacion:
            if self.fase == FaseControlador.DETENIDO_POR_CRITICA:
                self.fase = FaseControlador.PROCESANDO_ORDEN
                self.estado_bolsa = EstadoBolsa.ACEPTABLE
                self.sigma_bolsa = float('inf')
                self.sigma = float('inf')
                self.activate()
            else:
                self.fase = FaseControlador.PROCESANDO_ORDEN
                self.estado_bolsa = EstadoBolsa.ACEPTABLE
                self.sigma_bolsa = float('inf')
                self.sigma = float('inf')
                self.activate()
        else:
            self.sigma_bolsa -= e
            self.sigma -= e
            self.aux()

    def lambdaf(self):
        if self.desvio_corregido:
            self.o_desvio_corregido.add(True)
        if self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado > 0:
            self.o_ajustar_caudal.add(float(self.caudal_indicado))
        if self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado == 0:
            self.o_detener_bomba.add(ComandoBomba.DETENER.value) # .value extrae el string
        if self.fase == FaseControlador.DESVIADO:
            self.o_ajustar_caudal.add(self.caudal_indicado)  
        if self.fase == FaseControlador.EVALUANDO_DESVIO:
            self.o_alarma.add(NivelAlarma.MEDIA.value)
        if self.fase == FaseControlador.DETENIDO_POR_CRITICA:
            self.o_alarma.add(NivelAlarma.CRITICA.value)   
        if self.fase == FaseControlador.EVALUANDO_CRITICA or self.estado_bolsa == EstadoBolsa.FINALIZANDO:
            self.o_detener_bomba.add(ComandoBomba.DETENER.value)
        if self.sigma_bolsa <= 0 and self.estado_bolsa == EstadoBolsa.ACEPTABLE:
            self.o_alarma.add(NivelAlarma.BAJA.value)