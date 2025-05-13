from tkinter import *
from customtkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os, serial, datetime, time

# importado de commandos personalizados
from helpers.serial_commands import *
from helpers.plot_commands import *
from helpers.gui_commands import *


class KeithleyApp:
    def __init__(self):
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        self.root = CTk()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root._set_appearance_mode("System")

        self.root.title('Keithley Continuous Measurement')

        self.device = {
            'com_ports': list(),
            'com_device': '',
            'selected_device': '',
            'available_device': None,
        }

        self.device['com_ports'] = serial.tools.list_ports.comports()
        self.ports_list = [f'{port}' for port in self.device['com_ports']]

        self.data = {
            'export_directory': None,
            'export_name': None,
            'sample_name': list(),
            'sample_info': list(),
            'first_time': datetime.datetime.today().timestamp,  # primer tiempo en segundos
            'time_data': list(),
            'current_data': list(),
            'running': False,
            'last_data': None,
            'last_time': None,
            'thread_available': True,
        }

        self.text = {
            'smp_info': StringVar(),
            'smp_name': StringVar(),
            'export_name': StringVar(),
        }

        self.text['smp_name'].set('Sample name')
        self.text['smp_info'].set('Sample info')
        self.text['export_name'].set('Export name')

        self.command_integration = 'NPLC 1.0'

        self.int_rate = DoubleVar()
        self.int_rate.set(1.0)

        self.fig, self.line, self.ax = initialize_plot(self)


        update_plot_colors(self)

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz gráfica."""
        self.root.protocol('WM_DELETE_WINDOW', lambda: closing_app(self))
        
        def closing_app(self):
            """Cierra la aplicación."""
            while not self.data['thread_available']:
                print('Waiting for thread to be available...')
                time.sleep(0.1)
            close_app(self)

        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Reemplazar el frame actual con un CTkScrollableFrame
        frm = CTkScrollableFrame(
            self.root, 
            fg_color='transparent',
            scrollbar_button_color='gray70',
            scrollbar_button_hover_color='gray50',
            width=420,
        )
        frm.grid(padx=10, pady=10, sticky='nsew')
        icol_rows = 0

        ######################################################
        #               Selección del dispositivo            #
        ######################################################
        devices_selection_frame = CTkFrame(frm, fg_color='transparent', border_width=2)
        devices_selection_frame.grid(column=0, row=icol_rows, columnspan=2, pady=10, padx=10)
        icol_rows += 1

        bf_font = CTkFont(family='Arial', weight='bold', size=18)

        CTkLabel(devices_selection_frame,
                 text='Select the device',
                 font=bf_font,
                 width=400,
                 ).grid(column=0, row=0, columnspan=2, pady=5, padx=5)

        self.device_selection_lbl = CTkLabel(devices_selection_frame, text='No device selected')

        self.device['combobox'] = CTkComboBox(
            devices_selection_frame,
            state="readonly",
            command=lambda option: select_device(self, option),
            width=400*0.63,
        )
        self.device['combobox'].configure(values=self.ports_list)
        self.device['combobox'].grid(column=0, row=1, columnspan=1, pady=5, padx=5, sticky='e')
        self.device_selection_lbl.grid(column=0, row=3, columnspan=2, pady=5, padx=5)

        dev_scan_btn = CTkButton(devices_selection_frame,
                                 text='Update',
                                 command=lambda: scan_ports(self.device),
                                 width=10)
        dev_scan_btn.grid(column=1, row=1, pady=5, padx=5, sticky='w')


        ######################################################
        #             Configuración de la gráfica            #
        ######################################################
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(column=3, row=0, padx=5, pady=5, sticky='nsew')

        self.ax.set_xlabel('Time (s)', fontweight='bold')
        self.ax.set_ylabel('Current (A)', fontweight='bold')

        def update_colorplot(event=None):
            """Update the plot colors based on the selected theme."""
            theme = self.root._get_appearance_mode()
            fig: plt.Figure = self.fig
            ax: plt.Axes = self.ax
            line: plt.Line2D = self.line

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

        ######################################################
        #                 Controles del gráfico              #
        ######################################################
        plot_frame = CTkFrame(frm, fg_color='transparent')
        plot_frame.grid(column=0, row=icol_rows, columnspan=2, pady=10, padx=10)
        icol_rows += 1
        
        CTkLabel(plot_frame,
                 text='Acquisition and plot controls',
                 font=bf_font,
                 width=400,
        ).grid(column=0, row=1, columnspan=2, pady=5, padx=5)

        CTkButton(plot_frame,
                  text='Initialize',
                  command=lambda: initialize_with_wait(self),
        ).grid(column=0, row=2, ipady=10, padx=5, pady=5, sticky='e')

        def initialize_with_wait(self):
            '''Initialize the device and set the integration rate.'''
            print('Initializing device...')
            
            try:
                self.int_rate.get()
            except Exception as e: # Error getting integration rate
                print(f'Error getting integration rate: {e}')
                self.int_rate.set(1.0)

            while not self.data['thread_available']:
                print('Waiting for thread to be available...')
                time.sleep(0.1)
            initialize_device(self)

        CTkButton(plot_frame,
                  text= 'Start Acquisition',
                  command=lambda: start_acquisition(self),
        ).grid(column=1, row=2, ipady=10, padx=5, pady=5, sticky='w')

        CTkButton(plot_frame,
                  text= 'Clear Graph',
                  command=lambda: plot_clear(self),
        ).grid(column=0, row=3, ipady=10, padx=5, pady=10, sticky='e')

        CTkButton(plot_frame,
                  text='STOP',
                  command= lambda: stop_plot(self.data),
                  fg_color='red',
        ).grid(column=1, row=3, ipady=10, padx=5, pady=10, sticky='w')

        ######################################################
        #               Configuración del device             #
        ######################################################
        config_frame = CTkFrame(frm, fg_color='transparent')
        icol_rows += 1
        config_frame.grid(column=0, row=icol_rows, columnspan=2, pady=10, padx=10)
        icol_rows += 1

        CTkLabel(config_frame,
                 text="Device configuration",
                 font=bf_font,
                 width=400,
                 ).grid(column=0, row=0, columnspan=3, pady=5, padx=5)

        CTkLabel(config_frame,
                 text="Integration rate:",
                 ).grid(column=0, row=1, pady=5, padx=5, sticky='e')
        self.NPLC_entry = CTkEntry(config_frame,
                 placeholder_text="Integration rate (NPLC)",
                 width=150,
                )
        self.NPLC_entry.grid(column=1, row=1, pady=5, padx=5, sticky='w')

        self.NPLC_entry.configure(textvariable=self.int_rate)

        CTkButton(config_frame,
                  text="Submit",
                  command=lambda: send_new_integration_rate(self, self.NPLC_entry.get()),
                  width= 400*0.63 - 150,
                  ).grid(column=2, row=1, pady=5, padx=5, sticky='w')

        def send_new_integration_rate(self, NPLC):
            '''Send the new integration rate command to the device.'''
            try:
                new_rate = float(NPLC)
                if new_rate <= 0:
                    new_rate = 0.01
            except Exception as e:
                new_rate = 0.01
            self.command_integration = f'NPLC {new_rate}'
            print(f'command = {self.command_integration}')
            while not self.data['thread_available']:
                print('Waiting for thread to be available...')
                time.sleep(0.1)
            send(self.device['selected_device'], self.command_integration, self.data['thread_available'])

        self.last_data_str = StringVar(value="N/A")  # Variable to store the last data point

        CTkLabel(config_frame,
                 text='Last data point:',
                 ).grid(column=0, row=2, pady=5, padx=5, sticky='e')
        CTkLabel(config_frame,
                 textvariable=self.last_data_str,
                 font=CTkFont(family='consolas', size=12, weight="bold"),
                 ).grid(column=1, columnspan=2, row=2, pady=5, padx=5, sticky='w')


        ######################################################
        #                   Exportado de datos               #
        ######################################################
        export_frame = CTkFrame(frm, fg_color='transparent')
        export_frame.grid(column=0, row= icol_rows,columnspan=2, pady=10, padx=10)
        icol_rows += 1

        CTkLabel(export_frame, 
                 text='Export data information', 
                 font=bf_font,
                 width=400
                 ).grid(column=0, row=0, columnspan=2, pady=5, padx=5)
        
        CTkLabel(export_frame,text='Sample name:').grid(column=0, row=1, padx=5, pady=5, sticky='e')
        CTkEntry(export_frame,
                 textvariable=self.text['smp_name'],
                 width=400*0.65,
        ).grid(column=1, row=1, sticky='w')

        CTkLabel(export_frame,text='Sample info:').grid(column=0, row=2, padx=5, pady=5, sticky='e')
        CTkEntry(export_frame,
                 textvariable=self.text['smp_info'],
                 width=400*0.65,
        ).grid(column=1, row=2, sticky='w')
        
        self.export_path_label = CTkLabel(export_frame, text='No path selected')
        export_path_btn = CTkButton(export_frame, 
                                    text='Select path', 
                                    width= 400*0.3,
                                    command= lambda: get_folder_path(self) )

        export_path_btn.grid(column=0, row=3, sticky='e')
        self.export_path_label.grid(column=1, row=3, padx=5, pady=5, sticky='w')

        CTkLabel(export_frame, text='Export filename').grid(column=0, row=4, padx=5, pady=5, sticky='e')

        self.export_name_entry = CTkEntry(export_frame, width=400*0.6, textvariable=self.text['export_name'])
        self.export_name_entry.grid(column=1, row=4, padx=5, pady=5, sticky='w')

        CTkButton(export_frame, text='Export data', 
                  command=lambda: export_data(self), width=400*0.3
                  ).grid(column=0, row=icol_rows, columnspan=2, padx=5, pady=10)
        icol_rows += 1


        #######################################################
        #               Configuración de los bordes           #
        #######################################################

        self.list_frames = [devices_selection_frame, 
                            plot_frame,
                            config_frame, 
                            export_frame]

        def update_borders_color(event=None):
            '''Update the border color of the frames based on the current theme.'''
            border_color = 'white' if self.root._get_appearance_mode() == 'dark' else 'black'
            for frame in self.list_frames:
                frame.configure(border_width=2, border_color=border_color)

        def check_theme_change():
            '''Periodically check for theme changes and update the border color.'''
            update_borders_color()
            update_colorplot()
            self.root.after(500, check_theme_change)  # Check every 500ms

        check_theme_change()  # Start the periodic check


    def run(self):
        '''
        Inicia el bucle principal de la aplicación.
        '''
        self.root.mainloop()


if __name__ == '__main__':
    app = KeithleyApp()
    app.run() 