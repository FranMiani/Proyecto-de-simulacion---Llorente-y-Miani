import matplotlib.pyplot as plt
import sys
import os
from parametros import NivelAlarma
import numpy as np

ruta_padre = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_padre)
from xdevs.models import Coupled, Port
from xdevs.sim import Coordinator

from controlador_bomba import ControladorBomba
from registrador_eventos import RegistradorEventos
from generador_ordenes_medicas import GeneradorOrdenesMedicas
from sensor_flujo import SensorDeFlujo
from enfermero import Enfermero
from bolsa import Bolsa
from actuador_bomba import ActuadorDeBomba
from modulo_alarmas import ModuloAlarmas

class SistemaBombaCompleto(Coupled):
    def __init__(self, name="SistemaBomba"):
        super().__init__(name)

        # 1. Instanciamos todos los bloques atómicos
        self.controlador = ControladorBomba("Controlador")
        self.registrador = RegistradorEventos("Registrador")
        self.ordenes = GeneradorOrdenesMedicas("Ordenes")
        self.sensor = SensorDeFlujo("Sensor")
        self.enfermero = Enfermero("Enfermero")
        self.bolsa = Bolsa("Bolsa")
        self.bomba = ActuadorDeBomba("Bomba")
        self.alarma = ModuloAlarmas("Alarmas")

        # 2. Agregamos los bloques a la caja principal
        self.add_component(self.controlador)
        self.add_component(self.registrador)
        self.add_component(self.ordenes)
        self.add_component(self.sensor)
        self.add_component(self.enfermero)
        self.add_component(self.bolsa)
        self.add_component(self.bomba)
        self.add_component(self.alarma)

        # 3. Cableamos las ENTRADAS hacia el Controlador
        self.add_coupling(self.ordenes.o_caudal, self.controlador.i_orden_medica)
        self.add_coupling(self.sensor.o_sensorFlujo, self.controlador.i_sensor_flujo)
        self.add_coupling(self.bolsa.o_finBolsa, self.controlador.i_fin_bolsa)
        self.add_coupling(self.enfermero.o_confirmacion, self.controlador.i_confirmacion)

        # 4. Cableamos las SALIDAS del Controlador hacia el Registrador
        self.add_coupling(self.controlador.o_ajustar_caudal, self.registrador.i_ajustar_caudal)
        self.add_coupling(self.controlador.o_detener_bomba, self.registrador.i_detener_bomba)
        self.add_coupling(self.controlador.o_alarma, self.registrador.i_alarma)
        self.add_coupling(self.bomba.o_caudal_actual,self.registrador.i_caudal_real)
        self.add_coupling(self.controlador.o_desvio_corregido, self.registrador.i_desvio_corregido)

        # 5. Salidas Cotrolador 
        self.add_coupling(self.controlador.o_alarma, self.alarma.i_alarma)
        self.add_coupling(self.controlador.o_ajustar_caudal, self.bomba.i_ajustar_caudal)
        self.add_coupling(self.controlador.o_detener_bomba, self.bomba.i_detener_bomba)

        # 6. Alarma a Enfermero
        self.add_coupling(self.alarma.o_notificacionAlarma, self.enfermero.i_notificacionAlarma)
        
        # 7. Enfermero a Bolsa y Controlador
        self.add_coupling(self.enfermero.o_confirmacion, self.controlador.i_confirmacion)
        self.add_coupling(self.enfermero.o_confirmacion, self.bolsa.i_confirmacion)
        self.add_coupling(self.enfermero.o_confirmacion, self.registrador.i_confirmacion)
        self.add_coupling(self.enfermero.o_confirmacion, self.alarma.i_confirmacionEnfermero)
        # 8. Actuador a Sensor
        self.add_coupling(self.bomba.o_caudal_actual, self.sensor.i_caudalActual)
        
        


if __name__ == '__main__':
    # Inicializamos el modelo superior y el motor
    modelo_top = SistemaBombaCompleto()
    coordinador = Coordinator(modelo_top)

    # Ejecutamos la simulación
    print("--- INICIANDO SIMULACIÓN ---")
    coordinador.initialize()
    coordinador.simulate_time(20000) 
    print("--- SIMULACIÓN FINALIZADA ---")

    # Extraemos las listas de datos guardadas en el Registrador
    t_caudal = modelo_top.registrador.historial_tiempos_caudal
    v_caudal = modelo_top.registrador.historial_valores_caudal
    t_alarma = modelo_top.registrador.historial_tiempos_alarma
    v_alarma = modelo_top.registrador.historial_valores_alarma

    t_indicado = modelo_top.registrador.historial_tiempos_caudal
    v_indicado = modelo_top.registrador.historial_valores_caudal
    t_real = modelo_top.registrador.historial_tiempos_caudal_real
    v_real = modelo_top.registrador.historial_valores_caudal_real
    
    resp_desvio = modelo_top.registrador.tiempos_respuesta_desvio
    resp_bolsa = modelo_top.registrador.tiempos_respuesta_bolsa

    if resp_desvio and resp_bolsa:
        print("\n================ RESUMEN ================")
        print(f"{'Evento':<20}{'Media':>10}{'Min':>10}{'Max':>10}{'Std':>10}")
        
        print(f"{'Desvío':<20}"
              f"{np.mean(resp_desvio):10.2f}"
              f"{np.min(resp_desvio):10.2f}"
              f"{np.max(resp_desvio):10.2f}"
              f"{np.std(resp_desvio):10.2f}")
        
        print(f"{'Fin de bolsa':<20}"
              f"{np.mean(resp_bolsa):10.2f}"
              f"{np.min(resp_bolsa):10.2f}"
          f"{np.max(resp_bolsa):10.2f}"
          f"{np.std(resp_bolsa):10.2f}")
        print("cantidad de resp_bolsa:", len(resp_bolsa))
        print("cantidad de resp_desvio:", len(resp_desvio))
        
    # --- ZONA DE GRÁFICOS (Matplotlib) ---
    # Creamos una figura con 2 subgráficos compartiendo el eje X (tiempo)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Panel 1: Gráfico de Caudal
    # Usamos 'step' para que se mantenga plano entre eventos (comportamiento digital/discreto)
    ax1.step(t_caudal, v_caudal, where='post', color='#1f77b4', linewidth=2, marker='o')
    ax1.set_title("Ajustes de Caudal de la Bomba")
    ax1.set_ylabel("Caudal (ml/h)")
    ax1.grid(True, linestyle='--', alpha=0.7)
    if len(t_alarma) > 0:
        ax2.scatter(t_alarma, v_alarma, color='red', s=100, zorder=5)
        # Usamos los Enums para garantizar consistencia visual
        ax2.set_yticks([NivelAlarma.BAJA.value, NivelAlarma.MEDIA.value, NivelAlarma.CRITICA.value])
    else:
        ax2.text(0.5, 0.5, 'Sin alarmas registradas en este lapso', 
                 horizontalalignment='center', verticalalignment='center', 
                 transform=ax2.transAxes, color='gray')

    ax2.set_title("Registro de Eventos Críticos (Alarmas)")
    ax2.set_xlabel("Tiempo de simulación (segundos)")
    ax2.set_ylabel("Nivel")
    ax2.grid(True, linestyle='--', alpha=0.7)

    # Ajustamos márgenes y mostramos la ventana
    plt.tight_layout()
    plt.show()

    # ========= SEGUNDA FIGURA =========
    plt.figure(figsize=(10,6))
    
    plt.step(t_indicado, v_indicado,
             where='post',
             linewidth=2,
             label='Caudal indicado')
    
    plt.step(t_real, v_real,
             where='post',
             linewidth=2,
             linestyle='--',
             label='Caudal real')
    
    plt.title("Caudal indicado vs caudal real")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Caudal (ml/h)")
    plt.grid(True)
    plt.legend()
    
    plt.show()
