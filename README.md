# Communicator Interface

## Description
This project is a graphical interface developed in Python for communication and control of devices via serial commands. It uses libraries such as `customtkinter` for the graphical interface, `matplotlib` for data visualization, and `pyserial` for serial communication.

## Key Features
- **Device Selection**: Allows selecting devices connected to serial ports.
- **Data Acquisition**: Configure and acquire real-time data from the device.
- **Graphical Visualization**: Real-time graphs of the acquired data.
- **Data Export**: Export the acquired data to a file for further analysis.

## Requirements
- Python >= 3.12
- Project dependencies:
  - `customtkinter`
  - `matplotlib`
  - `pyserial`
  - `datetime`

## Installation
1. Clone this repository or download the files.
2. Ensure you have Python 3.12 or higher installed.
3. Install the dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```
4. If you are using `uv`, install the project in editable mode:
   ```bash
   uv pip install -e .
   ```

## Usage
1. Run the main file `main.py`:
   ```bash
   python main.py
   ```
2. Interact with the graphical interface to select devices, configure parameters, and visualize data.

## Project Structure
```
communicator_interface/
├── main.py                # Main application file
├── pyproject.toml         # Project configuration
├── README.md              # Project documentation
├── helpers/               # Auxiliary modules
│   ├── __init__.py
│   ├── gui_commands.py    # Commands related to the graphical interface
│   ├── plot_commands.py   # Commands related to plotting
│   └── serial_commands.py # Commands related to serial communication
```

## Contributions
Contributions are welcome. If you wish to contribute, please open an issue or submit a pull request.

## License
This project is licensed under the GNU General Public License v3.0 (GPLv3). See the `LICENSE` file for details.