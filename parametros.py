from enum import Enum
import random
# --- ENUMERACIONES (Lógica de Estados y Mensajes) ---
class FaseControlador(Enum):
    ESPERANDO = "ESPERANDO"
    PROCESANDO_ORDEN = "PROCESANDO_ORDEN"
    INFUNDIENDO = "INFUNDIENDO"
    EVALUANDO_DESVIO = "EVALUANDO_DESVIO"
    EVALUANDO_CRITICA = "EVALUANDO_CRITICA"
    DETENIDO_POR_CRITICA = "DETENIDO_POR_CRITICA"
    DESVIO_CORREGIDO = "DESVIO_CORREGIDO"
    DESVIADO = "DESVIADO"

class EstadoBolsa(Enum):
    ACEPTABLE = "ACEPTABLE"
    FINALIZANDO = "FINALIZANDO"
    VACIA = "VACIA"

class NivelAlarma(Enum):
    NINGUNA = "NINGUNA"
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    CRITICA = "CRITICA"

class FaseAlarma(Enum):
    REPOSO = "REPOSO"
    NOTIFICAR_NUEVA = "NOTIFICAR_NUEVA"
    ESPERANDO_30 = "ESPERANDO_30"
    ESPERANDO_10 = "ESPERANDO_10"

class ComandoBomba(Enum):
    DETENER = "DETENER"

# --- PARÁMETROS NUMÉRICOS DEL SISTEMA ---
class Params:
    TIEMPO_SIMULACION = 20000.0
    ACEPTACION_DESVIO = 0.10
    # Actuador
    ACTUADOR_ERROR_MIN = -0.15
    ACTUADOR_ERROR_MAX = 0.15
    ACTUADOR_LATENCIA = 1.0
    
    # Bolsa
    BOLSA_DURACION_MIN = 1000.0
    BOLSA_DURACION_MAX = 2000.0
    
    # Controlador
    CONTROL_RETARDO_ORDEN_MIN = 0.0
    CONTROL_RETARDO_ORDEN_MAX = 3.0
    CONTROL_TOLERANCIA_DESVIO = 0.10
    CONTROL_TIEMPO_EVALUACION = 10.0
    CONTROL_TIEMPO_PREVIO_FIN_BOLSA = 60.0
    @staticmethod
    def tiempo_detencion_critica(caudal_real, caudal_indicado):
        return max(5, Params.CONTROL_TIEMPO_EVALUACION - (Params.CONTROL_TIEMPO_EVALUACION * (abs(caudal_indicado - caudal_real) / caudal_indicado)))
    @staticmethod
    def generar_retardo_orden():
        return random.uniform(Params.CONTROL_RETARDO_ORDEN_MIN, Params.CONTROL_RETARDO_ORDEN_MAX)
    
    @staticmethod
    def generar_retardo(tiempo_base):
        return random.uniform(tiempo_base * 0.5, tiempo_base * 1.5)


    # Enfermero
    ENFERMERO_TIEMPO_RESP_BAJA_MIN = 70.0
    ENFERMERO_TIEMPO_RESP_BAJA_MAX = 110.0
    ENFERMERO_TIEMPO_RESP_CRITICA_MIN = 20.0
    ENFERMERO_TIEMPO_RESP_CRITICA_MAX = 60.0
    
    # Generador
    GENERADOR_CAUDAL_INICIAL = 100.0
    GENERADOR_TIEMPO_NUEVA_ORDEN = 200.0
    GENERADOR_CAUDAL_MAX_VALIDO = 200.0
    GENERADOR_CAUDAL_MIN = 1.0
    GENERADOR_CAUDAL_MAX = 300.0
    
    # Alarmas
    ALARMA_ESPERA_INICIAL = 30.0
    ALARMA_ESPERA_REPETICION = 10.0
    
    # Sensor
    SENSOR_PERIODO_MUESTREO = 1.
    
    @staticmethod
    def generar_caudal_aleatorio():
        # Tira el dado en tiempo real usando los límites de arriba
        return random.uniform(Params.GENERADOR_CAUDAL_MIN, Params.GENERADOR_CAUDAL_MAX)

    @staticmethod
    def generar_tiempo_nueva_orden():
        return random.uniform(Params.GENERADOR_TIEMPO_NUEVA_ORDEN * 0.5, Params.GENERADOR_TIEMPO_NUEVA_ORDEN * 1.5)

    @staticmethod
    def generar_error_actuador():
        return random.uniform(Params.ACTUADOR_ERROR_MIN, Params.ACTUADOR_ERROR_MAX)

    @staticmethod
    def generar_duracion_bolsa():
        return random.uniform(Params.BOLSA_DURACION_MIN, Params.BOLSA_DURACION_MAX)

    @staticmethod
    def generar_tiempo_enfermero_baja():
        return random.uniform(Params.ENFERMERO_TIEMPO_RESP_BAJA_MIN, Params.ENFERMERO_TIEMPO_RESP_BAJA_MAX)
    
    @staticmethod
    def generar_tiempo_enfermero_critica():
        return random.uniform(Params.ENFERMERO_TIEMPO_RESP_CRITICA_MIN, Params.ENFERMERO_TIEMPO_RESP_CRITICA_MAX)
    
    
