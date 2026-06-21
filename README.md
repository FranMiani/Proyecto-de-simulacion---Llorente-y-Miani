# Proyecto de simulacion. Mateo Llorente y Francisco Miani

Simulacion de una bomba de infusion utilizando el formalismo DEVS e implementada en Python mediante la biblioteca xdevs.py

## Requisitos
- Python 3.10 o superior

## Instalacion y ejecucion

- Clonar el repositorio:
```bash 
git clone https://github.com/FranMiani/Proyecto-de-simulacion---Llorente-y-Miani.git

cd Proyecto-de-simulacion---Llorente-y-Miani
```

- Crear un entorno virtual:
```bash 
python3 -m venv venv
```
- Activar el entorno virtual:
```bash
source venv/bin/activate
```
- Activar el entorno virtual en windows:
```bash
 venv\Scripts\activate
```
- Instalar las dependencias:
```bash
pip install -r requirements.txt
```
- Ejecutar la simulacion:
```bash
python3 simulador.py
```
### Al ejecutar simulador.py se desplegará un menú interactivo por consola que permite modificar fácilmente ciertos parámetros clave de la simulación (como el tiempo total, errores del actuador y demoras del personal).
### Nota: a traves del archivo parametros.py se pueden modificar todos los valores base y límites de entrada para el sistema de simulación, ademas de las funciones que generan valores de gran importancia en la simulacion.
### La traza de simulacion de cada ejecucion se guarda en un archivo traza.txt
