from tkinter import *
from tkinter import messagebox

import serial
import serial.tools.list_ports

from threading import Thread



def scan_ports(device):
    '''
    Scan the available ports and update the combobox with the available ports

    Args:
        device (dict): Dictionary containing the device information and combobox widget
    '''

    # Define the list of available ports and combobox
    device['com_ports'] = serial.tools.list_ports.comports()
    ports_list = [str(port) for port in device['com_ports']]
    device['combobox']['values'] = ports_list

    # selection of the port
    if ports_list:
        device['combobox'].set('Select a port')  # Select the first port by default
    elif device['com_ports'] == []:
        device['combobox'].set('No ports available')
    else:
        messagebox.showerror('Error', 'Unexpected error occurred while scanning ports.')

def initialize_device(app: 'KeithleyApp') -> bool:
    '''
    Initialize the device by sending the reset and clear commands

    Args:
        app (KeithleyApp): KeithleyApp object containing the device information

    Returns:
        bool: True if the device is initialized successfully, False otherwise
    '''

    thread_available: bool = app.data['thread_available']
    device = str(app.device['selected_device'])
    integration_rate = app.int_rate.get()

    devices = [device.device for device in serial.tools.list_ports.comports()]

    if device not in devices and device != '':
        messagebox.showerror('Error', f'Device {device} not found.')
        return False
    elif device == '':
        messagebox.showerror('Error', 'No device selected.')
        return False
    else:
        try:
            send(device,'*RST', thread_available)
            send(device,'*CLS', thread_available)
            send(device,'DISPlay:ENABle 0', thread_available)
            send(device,'SYSTem:ZCHeck 0', thread_available)
            send(device,'SYSTem:ZCORrect 0', thread_available)
            send(device,'*OPC', thread_available)
            send(device, f'NPLC {integration_rate}', thread_available)

        except serial.SerialException as e:
            messagebox.showerror('Error', f'Error initializing device: {e}')
            return False

        return True

def query(serial_com, command, thread_available: bool) -> str:
    '''
    Send a command to the device and return the response
    
    Args:
        serial_com (str): Serial port of the device
        command (str): Command to be sent to the device
    Returns:
        str: Response from the device
    '''
    with serial.Serial(serial_com) as ser:
        ser.write(str.encode(f'{command}\r\n'))
        ser.flush()  # Flush the output buffer to ensure the command is sent immediately
        response = ser.readline().decode('utf-8').strip("b'rn\\").split(',')

    return response[0][:-1]

def send(serial_com: str, command: str, thread_available: bool) -> None:
    '''
    Send a command to the device without expecting a response
    
    Args:
        serial_com (str): Serial port of the device
        command (str): Command to be sent to the device
    '''
    with serial.Serial(serial_com) as ser:
        ser.write(str.encode(f'{command}\r\n'))
        print(f'Command sended: {command}')
        ser.flush()  # Flush the output buffer to ensure the command is sent immediately
