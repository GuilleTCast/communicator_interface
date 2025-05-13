from tkinter import *
from tkinter import messagebox
import matplotlib.pyplot as plt
import datetime, time

from threading import Thread

from .serial_commands import query

def update_plot_colors(app: 'KeythleyApp'):
    '''
    Update the plot colors based on the selected theme
    
    Args:
        app (KeithleyApp): KeithleyApp object containing the plot information
    '''
    theme = app.root._get_appearance_mode()
    fig: plt.Figure = app.fig
    ax: plt.Axes = app.ax
    line: plt.Line2D = app.line

    if theme.lower() == 'dark':
        bg_color = "#2E2E2E"  # Fondo oscuro
        text_color = "#FFFFFF"  # Texto blanco
        line_color = "#FF5733"  # Línea naranja
    else:
        bg_color = "#FFFFFF"  # Fondo claro
        text_color = "#000000"  # Texto negro
        line_color = "#007BFF"  # Línea azul

    # Configurar colores del gráfico
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)
    ax.tick_params(colors=text_color)
    ax.spines['top'].set_color(text_color)
    ax.spines['bottom'].set_color(text_color)
    ax.spines['left'].set_color(text_color)
    ax.spines['right'].set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.xaxis.offsetText.set_color(text_color)
    ax.yaxis.offsetText.set_color(text_color)
    ax.title.set_color(text_color)

    # Actualizar la línea del gráfico (si existe)
    if line:
        line.set_color(line_color)

    # Redibujar el gráfico
    fig.canvas.draw_idle()

def initialize_plot(app: 'KeithleyApp') -> tuple[plt.Figure, plt.Line2D, plt.Axes]:
    '''
    Initialize the plot with empty data and set the labels and title
    
    Args:
        app (KeithleyApp): KeithleyApp object containing the plot information

    Returns:
        fig (Figure): Figure object to plot the data
        line (Line2D): Line object to update the data
        ax (Axes): Axes object to plot the data
    '''
    
    fig, ax = plt.subplots()
    fig: plt.Figure
    ax: plt.Axes

    line, = ax.plot([],[])
    ax.set_title(f'Real time data')
    ax.set_xlabel(f'Time (s)', fontweight='bold')
    ax.set_ylabel(f'Current (A)', fontweight='bold')

    return fig, line, ax

def update_data(data: dict) -> tuple[plt.Line2D, plt.Axes, plt.Figure]:
    '''
    Update the data with the current time and current data

    Args:
        data (dict): Dictionary containing the data to be plotted

    returns:
        x_data (list): List of time data
        y_data (list): List of current data
    ''' 

    date_formatted = datetime.datetime.now()	
    now_time = date_formatted.timestamp() # tiempo actual en segundos

    if len(data['time_data']) == 0:
        data['first_time'] = now_time
        relative_time = now_time - data['first_time']    #dato de tiempo relativo
        data['time_data'].append(relative_time)
    else:
        relative_time = now_time - data['first_time']    #dato de tiempo relativo
        data['time_data'].append(relative_time)
    
    x_data = data['time_data']
    y_data = data['current_data']

    return x_data, y_data

def start_acquisition(app: 'KeithleyApp'):
    '''
    Start the acquisition of data from the device and update the plot
    this function runs in a separate thread to avoid blocking the GUI
    and allows the user to stop the acquisition at any time

    Args:
        app (KeithleyApp): KeithleyApp object containing the data and plot information

    '''
    if app.device['selected_device'] == '':
        messagebox.showerror('Error', 'No device selected')
        return None, None, None
    
    data: dict = app.data
    fig: plt.Figure = app.fig
    ax: plt.Axes = app.ax
    last_data: float = app.data['last_data']
    last_time: float = app.data['last_time']
    last_data_string: Label = app.last_data_str
    
    def acquisition():
        data['running'] = True
        while data['running']:
            # Adquisición de datos
            device = str(app.device['selected_device'])
            if data['thread_available']:
                data['thread_available'] = False
                last_data = float(query(device, 'READ?', data['thread_available']))  # leer el valor de corriente
                data['thread_available'] = True
                data['current_data'].append(last_data)         # dato de corriente
                data['last_data'] = last_data                   # store last data
            data['last_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # store last time

            last_data_string.set(f'{last_data: .4e} A ({data["last_time"]})')

            x_data, y_data = update_data(data)
            # print(f'Time: {x_data[-1]: 5.4f}, Current: {y_data[-1]: #.4g} A')

            # Actualizar gráfico
            plot_title, x_label, y_label = ax.get_title(), ax.get_xlabel(), ax.get_ylabel()
            ax.clear()
            ax.set_title(f'{plot_title}')
            ax.set_xlabel(f'{x_label}', fontweight='bold')
            ax.set_ylabel(f'{y_label}', fontweight='bold')

            update_plot_colors(app)

            ax.plot(x_data, y_data)
            fig.canvas.draw_idle()  # Redraw the canvas

            time.sleep(0.01)  # Sleep for 10 ms to avoid high CPU usage

    # Crear y arrancar el hilo
    try:
        acquisition_thread = Thread(target=acquisition)
        acquisition_thread.daemon = True  # Permitir que el hilo se cierre al cerrar la aplicación
        acquisition_thread.start()

    except Exception as e:
        messagebox.showerror('Error', f'Error starting acquisition thread: {e}')            

def plot_clear(app: 'KeithleyApp'):
    '''
    Clear the plot data and redraw the canvas
    
    Args:
        app (KeithleyApp): KeithleyApp object containing the data and plot information
    '''
    data: dict = app.data
    fig: plt.Figure = app.fig
    ax: plt.Axes = app.ax
    last_data_string: Label = app.last_data_str

    data['time_data'] = []
    data['current_data'] = []

    plot_title = ax.get_title()
    x_label = ax.get_xlabel()
    y_label = ax.get_ylabel()

    ax.clear()
    ax.plot([],[])
    ax.relim()
    ax.autoscale_view()

    ax.set_title(f'{plot_title}')
    ax.set_xlabel(f'{x_label}', fontweight='bold')
    ax.set_ylabel(f'{y_label}', fontweight='bold')

    update_plot_colors(app)

    last_data_string.set("N/A")

    fig.canvas.draw()

def stop_plot(data: dict):
    '''
    Stop the acquisition of data from the device and update the plot
    
    Args:
        data (dict): Dictionary containing the data to be plotted
    '''
    data['running'] = False    