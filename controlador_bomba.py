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
        tiempo_proximo = min(self.sigma, self.sigma_bolsa)
        self.hold_in("active", tiempo_proximo)


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

        # --- PRIORIDAD 1: LA BOLSA ---
        if self.sigma_bolsa == min(self.sigma, self.sigma_bolsa):
            print("deltaint bolsa")
            if self.estado_bolsa == EstadoBolsa.ACEPTABLE:
                print("iniciando conteo")
                self.estado_bolsa = EstadoBolsa.FINALIZANDO
                self.sigma_bolsa = Params.CONTROL_TIEMPO_PREVIO_FIN_BOLSA
                
            elif self.estado_bolsa == EstadoBolsa.FINALIZANDO:
                print("fin bolsa")
                self.fase = FaseControlador.ESPERANDO
                self.estado_bolsa = EstadoBolsa.VACIA
                self.sigma = float('inf') 
                self.sigma_bolsa = float('inf')

        # --- PRIORIDAD 2: LAS FASES ---
        elif self.sigma == min(self.sigma, self.sigma_bolsa):
            if self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado > 0:
                self.fase = FaseControlador.INFUNDIENDO
                self.sigma = float('inf')
                
            elif self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado == 0:
                self.fase = FaseControlador.ESPERANDO
                self.sigma = float('inf')
                
            elif self.fase == FaseControlador.DESVIADO:
                self.fase = FaseControlador.EVALUANDO_DESVIO
                self.sigma = 0.0
                
            elif self.fase == FaseControlador.EVALUANDO_DESVIO:
                self.fase = FaseControlador.EVALUANDO_CRITICA
                
                self.sigma = Params.tiempo_detencion_critica(self.caudal_real, self.caudal_indicado)    
                
            elif self.fase == FaseControlador.EVALUANDO_CRITICA:
                print("llegue aca")
                self.fase = FaseControlador.DETENIDO_POR_CRITICA
                self.sigma = 0.0
                
            elif self.fase == FaseControlador.DETENIDO_POR_CRITICA:
                self.sigma = float('inf')
            elif self.fase == FaseControlador.INFUNDIENDO or self.fase == FaseControlador.ESPERANDO:
                self.sigma = float('inf')


        self.aux()

    def deltext(self, e):
        if self.sigma != float('inf'):
            self.sigma -= e
        if self.sigma_bolsa != float('inf'):
            self.sigma_bolsa -= e
        
        if self.i_orden_medica :
            if self.fase != FaseControlador.DETENIDO_POR_CRITICA and self.estado_bolsa != EstadoBolsa.VACIA:
                self.fase = FaseControlador.PROCESANDO_ORDEN
                self.sigma = Params.generar_retardo_orden()
            
            self.caudal_indicado = self.i_orden_medica.get()

            
        elif self.i_sensor_flujo:
            desvio_limite = Params.CONTROL_TOLERANCIA_DESVIO * self.caudal_indicado
            desvio_actual = abs(self.i_sensor_flujo.get() - self.caudal_indicado)
            
            if self.fase == FaseControlador.INFUNDIENDO and desvio_actual > desvio_limite and self.estado_bolsa != EstadoBolsa.VACIA:
                self.fase = FaseControlador.DESVIADO
                
                self.sigma = 5.0
                
                self.desvio_corregido = False
                
            if self.fase in [FaseControlador.EVALUANDO_CRITICA, FaseControlador.EVALUANDO_DESVIO, FaseControlador.DESVIADO] and desvio_actual <= desvio_limite and self.estado_bolsa != EstadoBolsa.VACIA:    
                self.desvio_corregido = True
                
                self.fase = FaseControlador.INFUNDIENDO
                self.sigma = float('inf')
                
            ##if self.fase in [FaseControlador.EVALUANDO_CRITICA, FaseControlador.EVALUANDO_DESVIO, FaseControlador.DESVIADO] and desvio_actual > desvio_limite:
              ##nothing, se mantiene en su fase actual esperando a ver si se corrige o empeora el desvío   
                
                
        elif self.i_fin_bolsa:
            self.i_fin_bolsa.get()  # Solo para consumir el evento, no nos importa su valor
            self.sigma_bolsa = 0.0
            print("Evento: Fin de bolsa detectado por el controlador.")
            
            
        elif self.i_confirmacion:
            self.fase = FaseControlador.PROCESANDO_ORDEN
            self.estado_bolsa = EstadoBolsa.ACEPTABLE
            self.sigma_bolsa = float('inf')
            self.sigma = 0.0
                
        self.aux()
            
            
            

    def lambdaf(self):
        # Identificadores de evento (¿Quién llegó a cero?)
        evento_bolsa = (self.sigma_bolsa != float('inf') and min(self.sigma, self.sigma_bolsa) == self.sigma_bolsa)
        evento_fase = (self.sigma != float('inf') and min(self.sigma, self.sigma_bolsa) == self.sigma)

        # El desvío corregido va por un puerto separado, no interfiere
        if self.desvio_corregido:
            self.o_desvio_corregido.add(True)
            
        # --- PRIORIDAD 1: LA BOLSA (Física) ---
        if evento_bolsa:
            if self.estado_bolsa == EstadoBolsa.FINALIZANDO:
                self.o_detener_bomba.add(ComandoBomba.DETENER.value)
                print("orden detener")
            elif self.estado_bolsa == EstadoBolsa.ACEPTABLE:
                self.o_alarma.add(NivelAlarma.BAJA.value)
                
        # --- PRIORIDAD 2: LAS FASES (Lógica) ---
        # Solo emiten si la bolsa no se adueñó del instante de tiempo
        elif evento_fase:
            if self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado > 0:
                self.o_ajustar_caudal.add(float(self.caudal_indicado))
                
            elif (self.fase == FaseControlador.PROCESANDO_ORDEN and self.caudal_indicado == 0) or self.fase == FaseControlador.EVALUANDO_CRITICA:
                self.o_detener_bomba.add(ComandoBomba.DETENER.value)
                
            elif self.fase == FaseControlador.DESVIADO:
                self.o_alarma.add(NivelAlarma.MEDIA.value)
                
            elif self.fase == FaseControlador.EVALUANDO_DESVIO:
                self.o_ajustar_caudal.add(self.caudal_indicado)  
                
            elif self.fase == FaseControlador.DETENIDO_POR_CRITICA:
                self.o_alarma.add(NivelAlarma.CRITICA.value)