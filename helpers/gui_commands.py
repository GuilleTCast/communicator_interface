from .serial_commands import initialize_device
from tkinter import filedialog, messagebox
import numpy as np
from tkinter import *
from customtkinter import *
import serial
import matplotlib.pyplot as plt

from .plot_commands import stop_plot

def update_borders_color(root: CTk, frames: list[CTkFrame]):
    '''
    Update the colors of the frame based on the selected theme

    Args:
        frame (Frame): Frame to update the colors
        theme (str): Selected theme ('dark' or 'light')
    '''
    theme = root._get_appearance_mode()

    border_color = "#2E2E2E" if theme.lower() == 'dark' else "#FFFFFF"

    for frame in frames:
        frame.configure(border_color=border_color)


def select_device(app: 'KeithleyApp', option: str):
    '''
    Selection of the device from the combobox and update the label with the selected device

    Args: 
        device (dict): Dictionary containing the device information and combobox widget
        selected_device_label (Label): Label widget to display the selected device
    '''

    device: dict = app.device
    selected_device_label: Label = app.device_selection_lbl

    devices = [device for device in device['com_ports']]

    for instrument in devices:
        if f'{instrument}' == option:
            device['selected_device'] = instrument.device
            initialize_device(app)
            selected_device_label.configure(text=f"{device['selected_device']} selected")
            # break

def get_folder_path(app: 'KeithleyApp'):
    '''
    Open a file dialog to select the export directory and update the label with the selected path
    
    Args:
        data (dict): Dictionary containing the data to be exported
        export_label (Label): Label to update with the selected path
    '''

    data: dict = app.data
    export_label: Label = app.export_path_label

    selected_folder = filedialog.askdirectory()        
    data['export_directory'] = selected_folder
    export_label.configure(text=selected_folder)

def export_data(app: 'KeithleyApp'):
    '''
    Export the data to a file in the selected directory
    
    Args:
        app (KeithleyApp): KeithleyApp object containing the data to be exported
    '''
    data: dict = app.data
    text: dict = app.text
    export_name_entry: Entry = app.export_name_entry
    device: dict = app.device
    
    requirements = [text['smp_name'].get() not in ('', None),
                    text['smp_info'].get() not in ('', None),
                    text['export_name'].get() not in ('', None),
                    data['export_directory'] not in ('', None),
    ]
    requirement_info = ['Sample name', 'Sample information',
                        'Export name', 'Export directory'
    ]

    fulfilled_list = [requirement_info[i] for i, requirement in enumerate(requirements) if not requirement]

    if not all(requirements):
        messagebox.showerror('Error', f'Please fill in the following fields:\n\t{"\n\t".join(fulfilled_list)}')
    else:
        data['sample_name'] = text['smp_name'].get()
        data['sample_info'] = text['smp_info'].get()
        data['export_name'] = text['export_name'].get()
        rules = [len(data['current_data']) > 0,
                len(data['time_data']) > 0]
        if all(rules):
            final_data = np.hstack((np.array(data['time_data']).reshape(-1, 1),np.array(data['current_data']).reshape(-1, 1)))
            sample_name = ['Sample name:',
                        data['sample_name']
            ]
            sample_info = ['Sample information:',
                        data['sample_info']
            ]

            for device in device['com_ports']:
                print(device)
                if device.device == app.device['selected_device']:
                    print(device)
                    break

            device_info = ['Device information:',
                        device['com_device'],
            ]
            final_comments = '\n'.join([' '.join(sample_name), ' '.join(sample_info), ' '.join(device_info),'\n'])
            final_header = 'Relative time (s)\tCurrent (A)'
            filename_export = os.path.join(app.data['export_directory'], (export_name_entry.get() + '.dat'))
            print(filename_export)
            np.savetxt(filename_export,final_data, delimiter='\t', fmt='%s', header= final_header, comments= final_comments)
        else:
            messagebox.showerror('Error', 'No data to export. Please start the acquisition first.')
            return

def close_app(app: 'KeithleyApp'):
    '''
    Close the application and stop the acquisition if running

    Args:
        data (dict): Dictionary containing the data to be plotted
        device (dict): Dictionary containing the device information
        root (Tk): Tkinter root window
    '''
    its_running: bool = app.data['running']
    device: str = app.device['selected_device']
    root: Tk = app.root

    if its_running:
        stop_plot(app.data)
        serial.Serial(device).close()
    
    plt.close('all')
    root.destroy()