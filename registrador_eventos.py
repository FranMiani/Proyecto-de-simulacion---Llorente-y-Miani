import matplotlib.pyplot as plt
import sys
import os
from parametros import NivelAlarma

# 1. Le decimos a Python que agregue la carpeta anterior al "radar" de búsqueda
ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Atomic, Port
class RegistradorEventos(Atomic):
    
    alarmas = 0
    confirmaciones = 0
    def agregar_traza(self, evento):
        if evento != "": 
            self.traza.append((self.reloj_global, evento))

    def __init__(self, name="RegistradorEventos"):
        super().__init__(name)

        self.i_caudal_real = Port(float, "i_caudal_real")
        self.i_ajustar_caudal = Port(float, "i_ajustarCaudal")
        self.i_detener_bomba = Port(str, "i_detenerBomba")
        self.i_alarma = Port(str, "i_alarma")
        self.i_confirmacion = Port(str, "i_confirmacion")
        self.i_desvio_corregido = Port(bool,"i_desvio_corregido")

        self.add_in_port(self.i_caudal_real)
        self.add_in_port(self.i_ajustar_caudal)
        self.add_in_port(self.i_detener_bomba)
        self.add_in_port(self.i_alarma)
        self.add_in_port(self.i_confirmacion)
        self.add_in_port(self.i_desvio_corregido)
        
        self.o_registro = Port(str, "o_registro")

        self.add_out_port(self.o_registro)

        
        self.mensaje = ""
        self.sigma = float('inf')
        
        self.reloj_global = 0.0
        self.historial_tiempos_caudal = []
        self.historial_valores_caudal = []
        self.historial_tiempos_alarma = []
        self.historial_valores_alarma = []
        self.historial_tiempos_caudal_real = []
        self.historial_valores_caudal_real = []
        self.contador_detenciones = 0
        self.t_ultima_alarma_media = None
        self.tiempos_respuesta_desvio = []
        self.t_ultima_alarma_baja = None
        self.tiempos_respuesta_bolsa = []
        self.traza = []
        

    def initialize(self):
        self.mensaje = ""
        self.reloj_global = 0.0
        self.passivate()

    def exit(self):
        pass

    def deltint(self):
        self.mensaje = ""
        self.passivate()

    def deltext(self, e):
        self.reloj_global += e

        # Evaluamos qué puerto trajo el evento 
        if self.i_ajustar_caudal:
            valor = self.i_ajustar_caudal.get()
            self.mensaje = f"Ajuste de caudal a: {valor}"
            
            # Guardamos el dato crudo para el gráfico
            self.historial_tiempos_caudal.append(self.reloj_global)
            self.historial_valores_caudal.append(valor)
            # Guardamos el evento en la traza de ejecucion
            self.agregar_traza(self.mensaje)
            
            self.hold_in("active", 0.0) # Transición inmediata (sigma = 0)

        if self.i_detener_bomba:
            self.mensaje = "Detencion de bomba"
            self.contador_detenciones += 1
            # Si se detiene la bomba, el caudal cae a cero
            self.historial_tiempos_caudal.append(self.reloj_global)
            self.historial_valores_caudal.append(0.0)
            
            # Guardamos el evento en la traza de ejecucion
            self.agregar_traza(self.mensaje)
            
            self.hold_in("active", 0.0)

        if self.i_alarma:
            self.alarmas += 1
            print("alarmas", self.alarmas)
            nivel = self.i_alarma.get()
            self.mensaje = f"Alarma: {nivel}"

            if nivel == NivelAlarma.MEDIA.value:
                self.t_ultima_alarma_media = self.reloj_global
            
            if nivel == NivelAlarma.BAJA.value:
                self.t_ultima_alarma_baja = self.reloj_global
            
            # Guardamos el nivel de alarma y el tiempo exacto
            self.historial_tiempos_alarma.append(self.reloj_global)
            self.historial_valores_alarma.append(nivel)
            
            # Guardamos el evento en la traza de ejecucion
            self.agregar_traza(self.mensaje)
            
            self.hold_in("active", 0.0)

        if self.i_caudal_real:
            valor = self.i_caudal_real.get()
        
            self.historial_tiempos_caudal_real.append(self.reloj_global)
            self.historial_valores_caudal_real.append(valor)
        
            self.mensaje = f"Caudal real: {valor}"

            # Guardamos el evento en la traza de ejecucion
            self.agregar_traza(self.mensaje)
            
            self.hold_in("active", 0.0)

        if self.i_confirmacion:
            _ = self.i_confirmacion.get() # Consumimos el evento
            print("confirmaciones", self.confirmaciones)
            self.confirmaciones += 1
            
            if self.t_ultima_alarma_baja is not None:
                tiempo = (self.reloj_global - self.t_ultima_alarma_baja)
                self.tiempos_respuesta_bolsa.append(tiempo)
                self.t_ultima_alarma_baja = None

            # 1. Definimos el mensaje
            self.mensaje = "Confirmacion de enfermero"
            # 2. Lo guardamos en la traza
            self.agregar_traza(self.mensaje)
            # 3. Forzamos la transición
            self.hold_in("active", 0.0)
            
        if self.i_desvio_corregido:
            _ = self.i_desvio_corregido.get() # Consumimos el evento
            
            if self.t_ultima_alarma_media is not None:
                tiempo = (self.reloj_global - self.t_ultima_alarma_media)
                self.tiempos_respuesta_desvio.append(tiempo)
                self.t_ultima_alarma_media = None

            # 1. Definimos el mensaje
            self.mensaje = "Desvio corregido"
            # 2. Lo guardamos en la traza
            self.agregar_traza(self.mensaje)
            # 3. Forzamos la transición
            self.hold_in("active", 0.0)
        
        
    def lambdaf(self):
        # print(f"Disparando salida desde: {self.name}")
        # Equivalente a: case out = (registro, mensaje); if (mensaje != " ")
        if self.mensaje != "":
            self.o_registro.add(self.mensaje)
