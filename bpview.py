#!/usr/bin/env python3
import argparse
import tkinter as tk
from tkinter import filedialog
import numpy as np
import adios2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from tkinter import ttk


# Open a file dialog to select a BP file.
def load_bp_file():
    file_path = filedialog.askopenfilename(filetypes=[("BP Files", "*.bp")])  # Select BP file
    if file_path:
        return file_path


# Plot 2D data from a BP file.
def plot_data(bp_file):
    adios = adios2.ADIOS()  # Create ADIOS object
    io = adios.DeclareIO("SimulationOutput")  # Declare IO object
    io.SetEngine("BP5")  # Set engine type to BP5

    # Open the BP file for reading
    fr = io.Open(bp_file, adios2.Mode.ReadRandomAccess)

    root = tk.Tk()
    root.title("BP File Plotter")

    # Left side labels and listbox
    var_label = tk.Label(root, text="Variable, Type, Steps, Dims, Min, Max:")
    var_label.pack(anchor=tk.NW)

    variables = io.AvailableVariables()  # Get available variables in BP file
    var_names = list(variables.keys())  # Extract variable names

    selected_var = var_names[0]  # Set default selected variable to the first one (if available)

    var_listbox = tk.Listbox(root, width=50)
    var_listbox.pack(side=tk.LEFT, anchor=tk.NW, padx=5, pady=5)

    # List variable info with variable in listbox
    for var_name in var_names:
        var = io.InquireVariable(var_name)
        var_info = str(var_name)
        var_info += ",   " + str(variables[var_name]['Type'])
        var_info += ",   " + str(variables[var_name]['AvailableStepsCount'])
        var_info += ",   {" + str(variables[var_name]['Shape']) + "}"
        var_info += ",   " + str(variables[var_name]['Min'])
        var_info += ",   " + str(variables[var_name]['Max'])
        var_listbox.insert(tk.END, var_info)
    

    #var_listbox.select_set(0)  # Select the first variable by default

    # Right side labels and entries
    selection_frame = ttk.Frame(root)
    selection_frame.pack(side=tk.RIGHT, anchor=tk.NE, padx=5, pady=5)

    # Step start
    step_start_label = tk.Label(selection_frame, text="Step start:")
    step_start_label.pack()

    step_start_entry = ttk.Entry(selection_frame)
    step_start_entry.pack()

    # Step count
    step_count_label = tk.Label(selection_frame, text="Step count:")
    step_count_label.pack()

    step_count_entry = ttk.Entry(selection_frame)
    step_count_entry.pack()

    # Selection start
    sel_start_label = tk.Label(selection_frame, text="Selection start:")
    sel_start_label.pack()

    sel_start_entry = ttk.Entry(selection_frame)
    sel_start_entry.pack()

    # Second Selection start
    sec_start_label = tk.Label(selection_frame, text="Second selection start (optional):")
    sec_start_label.pack()

    sec_start_entry = ttk.Entry(selection_frame)
    sec_start_entry.pack()

    # Selection count
    sel_count_label = tk.Label(selection_frame, text="Selection count:")
    sel_count_label.pack()

    sel_count_entry = ttk.Entry(selection_frame)
    sel_count_entry.pack()

    def update_selected_var(event):
        nonlocal selected_var
        selected_var = var_listbox.get(var_listbox.curselection()).split(",")[0].strip()  # Update selected variable based on listbox selection
    var_listbox.bind("<<ListboxSelect>>", update_selected_var)

    var = io.InquireVariable(selected_var)
    shape = var.Shape()
    dim = len(shape)

    # 2 D plotting

    def plot_2d():
        nonlocal fr
        
        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        #Step Selection
        try:
            step_start = int(step_start_entry.get())
        except ValueError:
            step_start = 0

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1
        
        var.SetStepSelection([step_start,step_count])

        try:
            sel_start_str = sel_start_entry.get()
            sel_start = np.array(eval(sel_start_str))
        except (ValueError, SyntaxError):
            sel_start = np.zeros(dim, dtype=int)

        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)

        sel_end = sel_start + sel_count
        
        fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
        gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
        ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

        # Check how dimensions are counted
        count_dim = [0,0]
        triv_dim = [0]*(dim-2)

        j = 0
        k = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                count_dim[j] = i
                j += 1
            else:
                triv_dim[k] = i
                k+=1
        
        data = np.empty([sel_count[count_dim[0]], sel_count[count_dim[1]]], dtype=np.float64)

        var.SetSelection([sel_start, sel_count])

        fr.Get(var, data, adios2.Mode.Sync)
        colorax = ax.imshow(data, origin='lower', interpolation='quadric', extent=[
                    sel_start[count_dim[1]], sel_end[count_dim[1]], sel_start[count_dim[0]], sel_end[count_dim[0]]], cmap=plt.get_cmap('gist_ncar'))
        ax.set_xlabel("axis-" + str(count_dim[0]))
        ax.set_ylabel("axis-" + str(count_dim[1]))

        fig.colorbar(colorax, orientation='horizontal')
        ax.plot([sel_start[count_dim[1]], sel_end[count_dim[1]]], [sel_start[count_dim[0]], sel_start[count_dim[0]]],
                color='black')
        ax.plot([sel_start[count_dim[1]], sel_end[count_dim[1]]], [sel_end[count_dim[0]], sel_end[count_dim[0]]],
                color='black')
        ax.plot([sel_start[count_dim[1]], sel_start[count_dim[1]]], [sel_start[count_dim[0]], sel_end[count_dim[0]]],
                color='black')
        ax.plot([sel_end[count_dim[1]], sel_end[count_dim[1]]], [sel_start[count_dim[0]], sel_end[count_dim[0]]],
                color='black')

        ax.set_title("Data with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_start))
        
        plt.ion()
        plt.show()

    # 2 D Series plotting

    def plot_2d_series():
        nonlocal fr
        
        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        #Step Selection
        try:
            step_start = int(step_start_entry.get())
        except ValueError:
            step_start = 0

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1

        for s in range(step_count):
            step_start_current = step_start + s
            var.SetStepSelection([step_start_current,1])

            try:
                sel_start_str = sel_start_entry.get()
                sel_start = np.array(eval(sel_start_str))
            except (ValueError, SyntaxError):
                sel_start = np.zeros(dim, dtype=int)

            try:
                sel_count_str = sel_count_entry.get()
                sel_count = np.array(eval(sel_count_str))
            except (ValueError, SyntaxError):
                sel_count = np.ones(dim, dtype=int)

            sel_end = sel_start + sel_count
            
            fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
            gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
            ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

            # Check how dimensions are counted
            count_dim = [0,0]
            triv_dim = [0]*(dim-2)

            j = 0
            k = 0
            for i in range(dim):
                if (sel_count[i] != 1):
                    count_dim[j] = i
                    j += 1
                else:
                    triv_dim[k] = i
                    k+=1
            
            data = np.empty([sel_count[count_dim[0]], sel_count[count_dim[1]]], dtype=np.float64)

            var.SetSelection([sel_start, sel_count])

            fr.Get(var, data, adios2.Mode.Sync)
            colorax = ax.imshow(data, origin='lower', interpolation='quadric', extent=[
                        sel_start[count_dim[1]], sel_end[count_dim[1]], sel_start[count_dim[0]], sel_end[count_dim[0]]], cmap=plt.get_cmap('gist_ncar'))
            ax.set_xlabel("axis-" + str(count_dim[0]))
            ax.set_ylabel("axis-" + str(count_dim[1]))

            fig.colorbar(colorax, orientation='horizontal')
            ax.plot([sel_start[count_dim[1]], sel_end[count_dim[1]]], [sel_start[count_dim[0]], sel_start[count_dim[0]]],
                    color='black')
            ax.plot([sel_start[count_dim[1]], sel_end[count_dim[1]]], [sel_end[count_dim[0]], sel_end[count_dim[0]]],
                    color='black')
            ax.plot([sel_start[count_dim[1]], sel_start[count_dim[1]]], [sel_start[count_dim[0]], sel_end[count_dim[0]]],
                    color='black')
            ax.plot([sel_end[count_dim[1]], sel_end[count_dim[1]]], [sel_start[count_dim[0]], sel_end[count_dim[0]]],
                    color='black')

            ax.set_title("Data with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_start_current))
            
            plt.ion()
            plt.show()
            #time.sleep(2)
            #plt.close()

    # 1 D plotting

    def plot_1d():
        nonlocal fr
    
        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        #Step Selection
        try:
            step_start = int(step_start_entry.get())
        except ValueError:
            step_start = 0

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1
        
        var.SetStepSelection([step_start,step_count])

        try:
            sel_start_str = sel_start_entry.get()
            sel_start = np.array(eval(sel_start_str))
        except (ValueError, SyntaxError):
            sel_start = np.zeros(dim, dtype=int)

        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)

        sel_end = sel_start + sel_count
        
        fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
        gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
        ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

        # Check how dimensions are counted
        count_dim = [0]
        triv_dim = [0]*(dim-1)

        j = 0
        k = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                count_dim[j] = i
                j += 1
            else:
                triv_dim[k] = i
                k+=1

        data = np.empty([sel_count[count_dim[0]]], dtype=np.float64)
        var.SetSelection([sel_start, sel_count])

        fr.Get(var, data, adios2.Mode.Sync)
        x_values = np.arange(sel_start[count_dim[0]], sel_end[count_dim[0]])
        ax.plot(x_values, data)
        ax.set_xlabel("x-axis")
        ax.set_ylabel("Values")

        ax.set_title(
            "Data with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_start))

        plt.ion()
        plt.show()

    # 1 D Series plotting

    def plot_1d_series():
        nonlocal fr
    
        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        #Step Selection
        try:
            step_start = int(step_start_entry.get())
        except ValueError:
            step_start = 0

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1
        
        for s in range(step_count):
            step_start_current = step_start + s
            var.SetStepSelection([step_start_current,1])

            try:
                sel_start_str = sel_start_entry.get()
                sel_start = np.array(eval(sel_start_str))
            except (ValueError, SyntaxError):
                sel_start = np.zeros(dim, dtype=int)

            try:
                sel_count_str = sel_count_entry.get()
                sel_count = np.array(eval(sel_count_str))
            except (ValueError, SyntaxError):
                sel_count = np.ones(dim, dtype=int)

            sel_end = sel_start + sel_count
            
            fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
            gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
            ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

            # Check how dimensions are counted
            count_dim = [0]
            triv_dim = [0]*(dim-1)

            j = 0
            k = 0
            for i in range(dim):
                if (sel_count[i] != 1):
                    count_dim[j] = i
                    j += 1
                else:
                    triv_dim[k] = i
                    k+=1

            data = np.empty([sel_count[count_dim[0]]], dtype=np.float64)
            var.SetSelection([sel_start, sel_count])

            fr.Get(var, data, adios2.Mode.Sync)
            x_values = np.arange(sel_start[count_dim[0]], sel_end[count_dim[0]])
            ax.plot(x_values, data)
            ax.set_xlabel("x-axis")
            ax.set_ylabel("Values")

            ax.set_title(
                "Data with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_start_current))

            plt.ion()
            plt.show()

    def plot_1d_v_1d():
        nonlocal fr

        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        #Step Selection
        try:
            step_start = int(step_start_entry.get())
        except ValueError:
            step_start = 0

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1
        
        var.SetStepSelection([step_start,step_count])

        try:
            sel_start_str = sel_start_entry.get()
            sel_start = np.array(eval(sel_start_str))
        except (ValueError, SyntaxError):
            sel_start = np.zeros(dim, dtype=int)

        try:
            sec_start_str = sec_start_entry.get()
            sec_start = np.array(eval(sec_start_str))
        except (ValueError, SyntaxError):
            sec_start = np.zeros(dim, dtype=int)

        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)

        #sel_end_1 = sel_start + sel_count
        #sel_end_2 = sec_start + sel_count
        
        fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
        gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
        ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

        # Check how dimensions are counted
        count_dim = [0]
        triv_dim = [0]*(dim-1)

        j = 0
        k = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                count_dim[j] = i
                j += 1
            else:
                triv_dim[k] = i
                k+=1
        
        y_values = np.empty([sel_count[count_dim[0]]], dtype=np.float64)
        var.SetSelection([sel_start, sel_count])
        fr.Get(var, y_values, adios2.Mode.Sync)

        x_values = np.empty([sel_count[count_dim[0]]], dtype=np.float64)
        var.SetSelection([sec_start, sel_count])
        fr.Get(var, x_values, adios2.Mode.Sync)

        ax.plot(x_values, y_values)
        ax.set_xlabel(str(count_dim[0])+"-axis")
        ax.set_ylabel(str(count_dim[0])+"-axis")

        ax.set_title(
            "Data with start " + str(sel_start) + "and" + str(sec_start) + " with count " + str(sel_count) + ", step " + str(step_start))

        plt.ion()
        plt.show()

    # N D Display

    def display_nd():
        nonlocal fr, var, sel_start_entry, sel_count_entry, step_start_entry
    
        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        #Step Selection
        try:
            step_start = int(step_start_entry.get())
        except ValueError:
            step_start = 0

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1
        
        var.SetStepSelection([step_start,step_count])

        try:
            sel_start_str = sel_start_entry.get()
            sel_start = np.array(eval(sel_start_str))
        except (ValueError, SyntaxError):
            sel_start = np.zeros(dim, dtype=int)

        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)

        # Create a new window for the display
        display_window = tk.Toplevel(root)
        display_window.title("Data Display")

        # Create a text box for displaying the result
        text_box = tk.Text(display_window, width=80, height=20)
        text_box.pack()

        def update_text_box():
            nonlocal text_box, fr, var, sel_start, sel_count, step_start
            var.SetStepSelection([step_start, step_count])
            var.SetSelection([sel_start, sel_count])

            data = np.empty(sel_count, dtype=np.float64)
            fr.Get(var, data, adios2.Mode.Sync)

            data_str = np.array2string(data, precision=5, separator=', ')

            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, data_str)

        update_text_box()


    # Check dimensions of input and then plot accordingly

    def check_and_plot():
        
        # Creates selection count array for checking purposes
        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)

        # Check if there's a second selection start for 1d v 1d plotting
        try:
            sec_start_str = sec_start_entry.get()
            sec_start = np.array(eval(sec_start_str))
            oneD_v_oneD = True
        except (ValueError, SyntaxError):
            oneD_v_oneD = False

        j = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                j += 1

        if(oneD_v_oneD):
            plot_1d_v_1d()

        elif(j == 2):
            plot_2d()
            

        elif(j == 1):
            plot_1d()
            
        else:
            print("Selection dimension not 1 or 2")

    def check_and_plot():
        
        # Creates selection count array for checking purposes
        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)

        # Check if there's a second selection start for 1d v 1d plotting
        try:
            sec_start_str = sec_start_entry.get()
            sec_start = np.array(eval(sec_start_str))
            oneD_v_oneD = True
        except (ValueError, SyntaxError):
            oneD_v_oneD = False

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1


        j = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                j += 1

        if(oneD_v_oneD):
            plot_1d_v_1d()

        elif(step_count != 1 and j == 2):
            plot_2d_series()

        elif(step_count != 1 and j == 1):
            plot_1d_series()

        elif(j == 2):
            plot_2d()
            

        elif(j == 1):
            plot_1d()
            
        else:
            print("Selection dimension not 1 or 2")

    def check_and_display():
        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)

        display_nd()

    var_listbox.bind("<<ListboxSelect>>", update_selected_var)
    
    plot_button = ttk.Button(selection_frame, text="Plot", command=check_and_plot)
    plot_button.pack(side=tk.BOTTOM, padx=5, pady=5)

    display_button = ttk.Button(selection_frame, text="Display", command=check_and_display)
    display_button.pack(side=tk.BOTTOM, padx=5, pady=5)

    root.mainloop()

    fr.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bp_file", help="Path to the BP file", required=True)
    args = parser.parse_args()

    plot_data(args.bp_file)
