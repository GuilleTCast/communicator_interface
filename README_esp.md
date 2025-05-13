# Interfaz de Comunicación

## Descripción
Este proyecto es una interfaz gráfica desarrollada en Python para la comunicación y control de dispositivos mediante comandos seriales. Utiliza bibliotecas como `customtkinter` para la interfaz gráfica, `matplotlib` para la visualización de datos y `pyserial` para la comunicación serial.

## Características principales
- **Selección de dispositivos**: Permite seleccionar dispositivos conectados a puertos seriales.
- **Adquisición de datos**: Configuración y adquisición de datos en tiempo real desde el dispositivo.
- **Visualización gráfica**: Gráficos en tiempo real de los datos adquiridos.
- **Exportación de datos**: Exporta los datos adquiridos a un archivo para análisis posterior.

## Requisitos
- Python >= 3.12
- Dependencias del proyecto:
  - `customtkinter`
  - `matplotlib`
  - `pyserial`
  - `datetime`

## Instalación
1. Clona este repositorio o descarga los archivos.
2. Asegúrate de tener Python 3.12 o superior instalado.
3. Instala las dependencias ejecutando:
   ```bash
   pip install -r requirements.txt
   ```
4. Si estás utilizando `uv`, instala el proyecto en modo editable:
   ```bash
   uv pip install -e .
   ```

## Uso
1. Ejecuta el archivo principal `main.py`:
   ```bash
   python main.py
   ```
2. Interactúa con la interfaz gráfica para seleccionar dispositivos, configurar parámetros y visualizar datos.

## Estructura del proyecto
```
communicator_interface/
├── main.py                # Archivo principal de la aplicación
├── pyproject.toml         # Configuración del proyecto
├── README.md              # Documentación del proyecto
├── helpers/               # Módulos auxiliares
│   ├── __init__.py
│   ├── gui_commands.py    # Comandos relacionados con la interfaz gráfica
│   ├── plot_commands.py   # Comandos relacionados con los gráficos
│   └── serial_commands.py # Comandos relacionados con la comunicación serial
```

## Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
