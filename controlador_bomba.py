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
        if (self.estado_bolsa != EstadoBolsa.FINALIZANDO) :
            self.hold_in("active", min(self.sigma, self.sigma_bolsa))
        else :
            self.passivate()

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
        e = min(self.sigma, self.sigma_bolsa)
        
        if self.sigma != float('inf'):
            self.sigma -= e
        if self.sigma_bolsa != float('inf'):
            self.sigma_bolsa -= e

        if self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado > 0 and self.sigma_bolsa > 0:
            self.fase = FaseControlador.INFUNDIENDO
            self.sigma = float('inf')
            
        elif self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado == 0:
            self.fase = FaseControlador.ESPERANDO
            self.sigma = float('inf')
            
            
        elif self.fase == FaseControlador.DESVIADO and self.sigma_bolsa > 0:
            self.fase = FaseControlador.EVALUANDO_DESVIO
            self.sigma = 0.0
            
        elif self.fase == FaseControlador.EVALUANDO_DESVIO and self.sigma_bolsa > 0:
            self.fase = FaseControlador.EVALUANDO_CRITICA
            self.sigma = Params.tiempo_detencion_critica(self.caudal_real, self.caudal_indicado)    
            
        elif self.fase == FaseControlador.EVALUANDO_CRITICA and self.sigma_bolsa > 0:
            self.fase = FaseControlador.DETENIDO_POR_CRITICA
            self.activate()
        elif self.fase == FaseControlador.DETENIDO_POR_CRITICA and self.sigma_bolsa > 0:
            self.sigma = float('inf')
            self.sigma_bolsa = float('inf')
        elif self.sigma_bolsa <= 0 and self.estado_bolsa == EstadoBolsa.ACEPTABLE:
            self.estado_bolsa = EstadoBolsa.FINALIZANDO
            self.sigma_bolsa = Params.CONTROL_TIEMPO_PREVIO_FIN_BOLSA
            
        elif self.estado_bolsa == EstadoBolsa.FINALIZANDO:
            self.fase = FaseControlador.ESPERANDO
            self.estado_bolsa = EstadoBolsa.VACIA
            self.sigma = float('inf')
            self.sigma_bolsa = float('inf')
        self.aux()

    def deltext(self, e):
        if self.sigma != float('inf'):
            self.sigma -= e
        if self.sigma_bolsa != float('inf'):
            self.sigma_bolsa -= e
        
        if self.i_orden_medica:
            self.fase = FaseControlador.PROCESANDO_ORDEN
            self.sigma = Params.generar_retardo_orden()
            self.caudal_indicado = self.i_orden_medica.get()
            
            
        elif self.i_sensor_flujo:
            desvio_limite = Params.CONTROL_TOLERANCIA_DESVIO * self.caudal_indicado
            desvio_actual = abs(self.i_sensor_flujo.get() - self.caudal_indicado)
            
            if self.fase == FaseControlador.INFUNDIENDO and desvio_actual > desvio_limite:
                self.fase = FaseControlador.DESVIADO
                
                self.sigma = 5.0
                
                self.desvio_corregido = False
                
            if self.fase in [FaseControlador.EVALUANDO_CRITICA, FaseControlador.EVALUANDO_DESVIO, FaseControlador.DESVIADO] and desvio_actual <= desvio_limite:    
                self.desvio_corregido = True
                
                self.fase = FaseControlador.INFUNDIENDO
                self.sigma = float('inf')
                
            ##if self.fase in [FaseControlador.EVALUANDO_CRITICA, FaseControlador.EVALUANDO_DESVIO, FaseControlador.DESVIADO] and desvio_actual > desvio_limite:
              ##nothing, se mantiene en su fase actual esperando a ver si se corrige o empeora el desvío   
                
                
        elif self.i_fin_bolsa:
            self.sigma_bolsa = 0.0
            
            
        elif self.i_confirmacion:
            self.fase = FaseControlador.PROCESANDO_ORDEN
            self.estado_bolsa = EstadoBolsa.ACEPTABLE
            self.sigma_bolsa = float('inf')
            self.sigma = float('inf')
            self.activate()
                
        self.aux()
            
            
            

    def lambdaf(self):
        if self.desvio_corregido:
            self.o_desvio_corregido.add(True)
        if self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado > 0:
            self.o_ajustar_caudal.add(float(self.caudal_indicado))
        elif self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado == 0:
            self.o_detener_bomba.add(ComandoBomba.DETENER.value) # .value extrae el string
        elif self.fase == FaseControlador.DESVIADO:
            self.o_alarma.add(NivelAlarma.MEDIA.value)
        elif self.fase == FaseControlador.EVALUANDO_DESVIO:
            self.o_ajustar_caudal.add(self.caudal_indicado)  
        elif self.fase == FaseControlador.DETENIDO_POR_CRITICA:
            self.o_alarma.add(NivelAlarma.CRITICA.value)   
        elif (self.fase == FaseControlador.EVALUANDO_CRITICA and self.sigma != float('inf')) or (self.estado_bolsa == EstadoBolsa.FINALIZANDO and self.sigma != float('inf')):
            self.o_detener_bomba.add(ComandoBomba.DETENER.value)
        elif self.sigma_bolsa <= 0 and self.estado_bolsa == EstadoBolsa.ACEPTABLE:
            self.o_alarma.add(NivelAlarma.BAJA.value)