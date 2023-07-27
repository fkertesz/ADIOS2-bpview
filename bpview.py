#!/usr/bin/env python3
import argparse
import tkinter as tk
from tkinter import filedialog
import numpy as np
import adios2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
from tkinter import scrolledtext


# Load BP file
def load_bp_file():
    file_path = filedialog.askopenfilename(filetypes=[("BP Files", "*.bp")])  # Select BP file
    if file_path:
        return file_path


# Read BP file and create window and selections.
def show_file(bp_file):
    adios = adios2.ADIOS()  # Create ADIOS object
    io = adios.DeclareIO("SimulationOutput")  # Declare IO object

    # Open the BP file for reading
    fr = io.Open(bp_file, adios2.Mode.ReadRandomAccess)

    root = tk.Tk()
    root.title("BPView")

    # Top frame
    top_frame = ttk.Frame(root)
    top_frame.pack(side=tk.TOP, padx=5, pady=5)

    # Left frame
    left_frame = ttk.Frame(top_frame)
    left_frame.pack(side=tk.LEFT)

    # Variable frame
    var_frame = ttk.Frame(left_frame)
    var_frame.pack(side=tk.LEFT, padx=5, pady=5)

    #Button frame
    b_frame = ttk.Frame(var_frame)
    b_frame.pack(side=tk.TOP, padx=5, pady=5)

    # Left side labels and listbox
    var_label = tk.Label(var_frame, text="Variable, Type, Steps, Dims, Min, Max:")
    var_label.pack(anchor=tk.NW)

    variables = io.AvailableVariables()  # Get available variables in BP file
    var_names = list(variables.keys())  # Extract variable names

    selected_var = var_names[0]  # Set default selected variable to the first one (if available)

    var_listbox = tk.Listbox(var_frame, width=50)
    var_listbox.pack(side=tk.LEFT, anchor=tk.NW, padx=5, pady=5)

    #Scrollbar
    scrollbar = tk.Scrollbar(var_frame, orient="vertical", command=var_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    var_listbox.config(yscrollcommand=scrollbar.set)

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

    # Required selection frame
    first_frame = ttk.Frame(left_frame)
    first_frame.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=5)

    # Selected variable label
    selected_var_label = tk.Label(first_frame, text="Variable: "+ selected_var)
    selected_var_label.pack()

    # Step start
    step_start_label = tk.Label(first_frame, text="Step start:")
    step_start_label.pack()

    step_start_entry = ttk.Entry(first_frame)
    step_start_entry.insert(0, "0")
    step_start_entry.pack()

    # Step count
    step_count_label = tk.Label(first_frame, text="Step count:")
    step_count_label.pack()

    step_count_entry = ttk.Entry(first_frame)
    step_count_entry.insert(0, "1")
    step_count_entry.pack()

    # Selection start
    sel_start_label = tk.Label(first_frame, text="Selection start:")
    sel_start_label.pack()

    var = io.InquireVariable(selected_var)
    shape = var.Shape()
    dim = len(shape)
    zeros_str = "["
    for d in range(dim):
        zeros_str += "0"
        if d != dim - 1:
            zeros_str += ", "
    zeros_str += "]"

    sel_start_entry = ttk.Entry(first_frame)
    sel_start_entry.insert(0, zeros_str)
    sel_start_entry.pack()

    # Selection count
    sel_count_label = tk.Label(first_frame, text="Selection count:")
    sel_count_label.pack()

    ones_str = "["
    for d in range(dim):
        ones_str += "1"
        if d != dim - 1:
            ones_str += ", "
    ones_str += "]"

    sel_count_entry = ttk.Entry(first_frame)
    sel_count_entry.insert(0, ones_str)
    sel_count_entry.pack()

        # Update selected variable when clicked on
    def update_selected_var(event):
        nonlocal selected_var
        selected_var_index = var_listbox.curselection()
        if selected_var_index:

            selected_var = var_listbox.get(var_listbox.curselection()).split(",")[0].strip()  # Update selected variable based on listbox selection

            # Update selected variable label
            selected_var_label.config(text="Variable: " + selected_var)

            # Update selection start and count default entries based on selected variable
            var = io.InquireVariable(selected_var)
            shape = var.Shape()
            dim = len(shape)

            zeros_str = "["
            for d in range(dim):
                zeros_str += "0"
                if d != dim - 1:
                    zeros_str += ", "
            zeros_str += "]"

            ones_str = "["
            for d in range(dim):
                ones_str += "1"
                if d != dim - 1:
                    ones_str += ", "
            ones_str += "]"

            sel_start_entry.delete(0, tk.END)
            sel_start_entry.insert(0, zeros_str)

            sel_count_entry.delete(0, tk.END)
            sel_count_entry.insert(0, ones_str)

    var_listbox.bind("<<ListboxSelect>>", update_selected_var)

    #SPEC stuff, not visible yet
    # Selection 1
    button1 = ttk.Button(b_frame, text="Selection 1")
    
    # Selection 2
    button2 = ttk.Button(b_frame, text="Selection 2")
    
    # Bottom frame
    right_frame = ttk.Frame(top_frame)

    variables = io.AvailableVariables()  # Get available variables in BP file
    var_names = list(variables.keys())  # Extract variable names

    spec_selected_var = selected_var  # Set default second selected variable to first selected variable

    spec_var_listbox = tk.Listbox(var_frame, width=50)

    #Spec scrollbar
    spec_scrollbar = tk.Scrollbar(var_frame, orient="vertical", command=spec_var_listbox.yview)
    spec_var_listbox.config(yscrollcommand=spec_scrollbar.set)

    # List variable info with variable in listbox
    for var_name in var_names:
        spec_var = io.InquireVariable(var_name)
        spec_var_info = str(var_name)
        spec_var_info += ",   " + str(variables[var_name]['Type'])
        spec_var_info += ",   " + str(variables[var_name]['AvailableStepsCount'])
        spec_var_info += ",   {" + str(variables[var_name]['Shape']) + "}"
        spec_var_info += ",   " + str(variables[var_name]['Min'])
        spec_var_info += ",   " + str(variables[var_name]['Max'])
        spec_var_listbox.insert(tk.END, spec_var_info)

    # Right side labels and entries
    second_frame = ttk.Frame(right_frame)

    # Second selected variable label
    spec_selected_var_label = tk.Label(second_frame, text="2nd Variable: "+ spec_selected_var)

    # Step start
    spec_step_start_label = tk.Label(second_frame, text="Step start:")

    spec_step_start_entry = ttk.Entry(second_frame)
    spec_step_start_entry.insert(0, str(step_start_entry.get()))

    # Step count
    spec_step_count_label = tk.Label(second_frame, text=("Step count:\n SAME AS LEFT"))

    # Selection start
    spec_sel_start_label = tk.Label(second_frame, text="Selection start:")

    spec_var = io.InquireVariable(selected_var)
    spec_shape = spec_var.Shape()
    spec_dim = len(spec_shape)

    spec_sel_start_entry = ttk.Entry(second_frame)
    spec_sel_start_entry.insert(0, str(sel_start_entry.get()))

    # Selection count
    spec_sel_count_label = tk.Label(second_frame, text="Selection count:")

    spec_sel_count_entry = ttk.Entry(second_frame)
    spec_sel_count_entry.insert(0, str(sel_count_entry.get()))

    global select1

    # Selection1 button
    def button1_com():
        global select1
        if select1 == False:
            spec_var_listbox.pack_forget()
            var_listbox.pack()
        select1 = True
        style.configure('Button1.TButton', font=("TkDefaultFont", 12, "bold"))
        style.configure('Button2.TButton', font=("TkDefaultFont", 12))
     
    button1.config(command=button1_com)

    # Selection2 button
    def button2_com():
        global select1
        if select1:
            var_listbox.pack_forget()
            spec_var_listbox.pack()
        select1 = False
        style.configure('Button1.TButton', font=("TkDefaultFont", 12))
        style.configure('Button2.TButton', font=("TkDefaultFont", 12, "bold"))

    button2.config(command=button2_com)


    # Update selected variable and automatic entries when clicked on
    def spec_update_selected_var(event):
        nonlocal spec_selected_var
        spec_selected_var_index = spec_var_listbox.curselection()
        if spec_selected_var_index:
            spec_selected_var =spec_var_listbox.get(spec_var_listbox.curselection()).split(",")[0].strip()  # Update selected variable based on listbox selection

            spec_selected_var_label.config(text="2nd Variable: " + spec_selected_var)  # Update selected variable label

            spec_var = io.InquireVariable(spec_selected_var)
            spec_shape = spec_var.Shape()
            spec_dim = len(spec_shape)

            spec_zeros_str = "["
            for sd in range(spec_dim):
                spec_zeros_str += "0"
                if sd != spec_dim - 1:
                    spec_zeros_str += ", "
            spec_zeros_str += "]"

            spec_ones_str = "["
            for sd in range(spec_dim):
                spec_ones_str += "1"
                if sd != spec_dim - 1:
                    spec_ones_str += ", "
            spec_ones_str += "]"

            spec_sel_start_entry.delete(0, tk.END)
            spec_sel_start_entry.insert(0, spec_zeros_str)

            spec_sel_count_entry.delete(0, tk.END)
            spec_sel_count_entry.insert(0, spec_ones_str)

    spec_var_listbox.bind("<<ListboxSelect>>", spec_update_selected_var)


        # 2 1D plots
    def plot_1d_v_1d():
        nonlocal fr

        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        spec_var = io.InquireVariable(spec_selected_var)
        spec_shape = spec_var.Shape()
        spec_dim = len(spec_shape)

        #First Selection
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

        #Second Selection
        try:
            spec_step_start = int(spec_step_start_entry.get())
        except ValueError:
            spec_step_start = 0
        
        spec_var.SetStepSelection([spec_step_start,step_count])

        try:
            spec_sel_start_str = spec_sel_start_entry.get()
            spec_sel_start = np.array(eval(spec_sel_start_str))
        except (ValueError, SyntaxError):
            spec_sel_start = np.zeros(spec_dim, dtype=int)

        try:
            spec_sel_count_str = spec_sel_count_entry.get()
            spec_sel_count = np.array(eval(spec_sel_count_str))
        except (ValueError, SyntaxError):
            spec_sel_count = np.ones(spec_dim, dtype=int)
        
        if step_count == 1:
            window = tk.Tk()
            window.title("1D v 1D Plot")

            plot_frame = ttk.Frame(window)
            plot_frame.pack(side=tk.TOP, padx=5, pady=5)

            fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
            gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
            ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

            # Check how dimensions are counted
            count_dim = [0]

            j = 0
            for i in range(dim):
                if (sel_count[i] != 1):
                    count_dim[j] = i
                    j += 1

            # Second - check how dimensions are counted
            spec_count_dim = [0]

            spec_j = 0
            for spec_i in range(spec_dim):
                if (spec_sel_count[spec_i] != 1):
                    spec_count_dim[spec_j] = spec_i
                    spec_j += 1
            
            # Plot the values against each other
            y_values = np.empty([sel_count[count_dim[0]]], dtype=np.float64)
            var.SetSelection([sel_start, sel_count])
            fr.Get(var, y_values, adios2.Mode.Sync)

            x_values = np.empty([spec_sel_count[spec_count_dim[0]]], dtype=np.float64)
            spec_var.SetSelection([spec_sel_start, spec_sel_count])
            fr.Get(spec_var, x_values, adios2.Mode.Sync)

            ax.plot(x_values, y_values)
            ax.set_xlabel(str(spec_count_dim[0])+"-axis")
            ax.set_ylabel(str(count_dim[0])+"-axis")

            ax.set_title(
                "Data from variables " + selected_var + " and " + spec_selected_var + " with starts " + str(sel_start) + " and " + str(spec_sel_start) + "\n with counts " + str(sel_count) + " and " + str(spec_sel_count) + ", steps " + str(step_start) + " and " + str(spec_step_start))

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        else:
            # Check how dimensions are counted
            count_dim = [0]

            j = 0
            for i in range(dim):
                if (sel_count[i] != 1):
                    count_dim[j] = i
                    j += 1

            # Second - check how dimensions are counted
            spec_count_dim = [0]

            spec_j = 0
            for spec_i in range(spec_dim):
                if (spec_sel_count[spec_i] != 1):
                    spec_count_dim[spec_j] = spec_i
                    spec_j += 1

            window = tk.Tk()
            window.title("1D Plot")

            plot_frame = ttk.Frame(window)
            plot_frame.pack(side=tk.TOP, padx=5, pady=5)

            butts_frame = ttk.Frame(window)
            butts_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

            forw_button = ttk.Button(butts_frame, text="Next")
            forw_button.pack(side=tk.RIGHT)

            back_button = ttk.Button(butts_frame, text="Previous")
            back_button.pack(side=tk.LEFT)

            global step_1
            step_1 = step_start
            global step_2
            step_2 = spec_step_start

            # Plot function
            def plspec():
                # Destroy previous plot if exists
                if len(plot_frame.winfo_children()) > 0:
                    for widget in plot_frame.winfo_children():
                        widget.destroy()

                global step_1
                var.SetStepSelection([step_1,1])

                global step_2
                spec_var.SetStepSelection([step_2,1])
                
                fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
                gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
                ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

                # Plot the values against each other
                y_values = np.empty([sel_count[count_dim[0]]], dtype=np.float64)
                var.SetSelection([sel_start, sel_count])
                fr.Get(var, y_values, adios2.Mode.Sync)

                x_values = np.empty([spec_sel_count[spec_count_dim[0]]], dtype=np.float64)
                spec_var.SetSelection([spec_sel_start, spec_sel_count])
                fr.Get(spec_var, x_values, adios2.Mode.Sync)

                ax.plot(x_values, y_values)
                ax.set_xlabel(str(spec_count_dim[0])+"-axis")
                ax.set_ylabel(str(count_dim[0])+"-axis")

                ax.set_title(
                    "Data from variables " + selected_var + " and " + spec_selected_var + " with starts " + str(sel_start) + " and " + str(spec_sel_start) + "\n with counts " + str(sel_count) + " and " + str(spec_sel_count) + ", steps " + str(step_1) + " and " + str(step_2))
                canvas = FigureCanvasTkAgg(fig, master=plot_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Go forward one step
            def forw():
                global step_1
                step_1 += 1
                global step_2
                step_2 += 1
                plspec()
                
                if step_1 == step_start + step_count - 1:
                    forw_button.config(state=tk.DISABLED)
                elif step_1 == step_start + 1:
                    back_button.config(state=tk.NORMAL)

            # Go back one step
            def back():
                global step_1
                step_1 -= 1
                global step_2
                step_2 -= 1
                plspec()

                if step_1 == step_start:
                    back_button.config(state=tk.DISABLED)
                elif step_1 == step_start + step_count - 2:
                    forw_button.config(state=tk.NORMAL)

            forw_button.config(command=forw)
            back_button.config(command=back)

            # Initial plot
            plspec()
            back_button.config(state=tk.DISABLED)


    #Hide button
    hide_button = tk.Button(second_frame, text="Hide")

    # Value false if more options are hidden, true if shown and plotting 1d v 1d
    global spec
    spec = False

    style = ttk.Style()
    style.configure('Button1.TButton', font=("TkDefaultFont", 12))
    style.configure('Button2.TButton', font=("TkDefaultFont", 12, "bold"))

    # Shows more options
    def spec_plot_show():
        global spec
        spec = True

        global select1
        select1 = False

        spec_selected_var = selected_var
        spec_selected_var_label.config(text="2nd Variable: " + spec_selected_var)  # Update selected variable label

        spec_step_start_entry.delete(0, tk.END)
        spec_step_start_entry.insert(0, str(step_start_entry.get()))

        spec_sel_start_entry.delete(0, tk.END)
        spec_sel_start_entry.insert(0, str(sel_start_entry.get()))

        spec_sel_count_entry.delete(0, tk.END)
        spec_sel_count_entry.insert(0, str(sel_count_entry.get()))

        button1.pack(side=tk.LEFT)
        button1.config(style='Button1.TButton')
        
        button2.pack(side=tk.RIGHT)
        button2.config(style='Button2.TButton')
        
        right_frame.pack(side=tk.RIGHT)

        var_listbox.pack_forget()

        spec_var_listbox.pack(side=tk.LEFT, anchor=tk.NW, padx=5, pady=5)

        scrollbar.pack_forget()

        spec_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        second_frame.pack(side=tk.TOP, padx=5, pady=5)

        spec_selected_var_label.pack()

        spec_step_start_label.pack()

        spec_step_start_entry.pack()

        spec_step_count_label.pack()

        spec_sel_start_label.pack()

        spec_sel_start_entry.pack()

        spec_sel_count_label.pack()

        spec_sel_count_entry.pack() 

        hide_button.pack(side=tk.BOTTOM)  

        spec_button.config(state=tk.DISABLED)

    # Hide more options
    def spec_plot_hide():
        global spec
        spec = False

        button1.pack_forget()
        
        button2.pack_forget()
        
        right_frame.pack_forget()

        spec_var_listbox.pack_forget()

        var_listbox.pack(side=tk.LEFT, anchor=tk.NW, padx=5, pady=5)

        spec_scrollbar.pack_forget()

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        second_frame.pack_forget()

        spec_selected_var_label.pack_forget()

        spec_step_start_label.pack_forget()

        spec_step_start_entry.pack_forget()

        spec_step_count_label.pack_forget()

        spec_sel_start_label.pack_forget()

        spec_sel_start_entry.pack_forget()

        spec_sel_count_label.pack_forget()

        spec_sel_count_entry.pack_forget()  

        hide_button.pack_forget() 

        spec_button.config(state=tk.NORMAL)
    
    hide_button.config(command=spec_plot_hide)

    # 2D plot

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
        
        window = tk.Tk()
        window.title("2D Plot")

        plot_frame = ttk.Frame(window)
        plot_frame.pack(side=tk.TOP, padx=5, pady=5)

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

        ax.set_title("Data from variable " + selected_var + " with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_start))
        
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # 2D Series plot

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

        # Check how dimensions are counted
        count_dim = [0,0]

        j = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                count_dim[j] = i
                j += 1

        window = tk.Tk()
        window.title("2D Series Plot")

        plot_frame = ttk.Frame(window)
        plot_frame.pack(side=tk.TOP, padx=5, pady=5)

        butts_frame = ttk.Frame(window)
        butts_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

        forw_button = ttk.Button(butts_frame, text="Next")
        forw_button.pack(side=tk.RIGHT)

        back_button = ttk.Button(butts_frame, text="Previous")
        back_button.pack(side=tk.LEFT)

        global step_2d
        step_2d = step_start

        # Plot function
        def pl2ds():
            # Destroy previous plot if exists
            if len(plot_frame.winfo_children()) > 0:
                for widget in plot_frame.winfo_children():
                    widget.destroy()

            global step_2d
            var.SetStepSelection([step_2d,1])

            data = np.empty([sel_count[count_dim[0]], sel_count[count_dim[1]]], dtype=np.float64)

            var.SetSelection([sel_start, sel_count])

            fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
            gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
            ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

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

            ax.set_title("Data from variable " + selected_var + " with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_2d))
            
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Go forward one step
        def forw():
            global step_2d
            step_2d += 1
            pl2ds()
            
            if step_2d == step_start + step_count -1:
                forw_button.config(state=tk.DISABLED)
            elif step_2d == step_start + 1:
                back_button.config(state=tk.NORMAL)

        # Go back one step
        def back():
            global step_2d
            step_2d -= 1
            pl2ds()

            if step_2d == step_start:
                back_button.config(state=tk.DISABLED)
            elif step_2d == step_start + step_count - 2:
                forw_button.config(state=tk.NORMAL)

        forw_button.config(command=forw)
        back_button.config(command=back)

        # Initial plot    
        pl2ds()
        back_button.config(state=tk.DISABLED)

    # 1D plot

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

        window = tk.Tk()
        window.title("1D Plot")

        plot_frame = ttk.Frame(window)
        plot_frame.pack(side=tk.TOP, padx=5, pady=5)
        
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
            "Data from variable " + selected_var + " with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_start))

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # 1D Series plot

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

        # Check how dimensions are counted
        count_dim = [0]

        j = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                count_dim[j] = i
                j += 1

        window = tk.Tk()
        window.title("1D Plot")

        plot_frame = ttk.Frame(window)
        plot_frame.pack(side=tk.TOP, padx=5, pady=5)

        butts_frame = ttk.Frame(window)
        butts_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

        forw_button = ttk.Button(butts_frame, text="Next")
        forw_button.pack(side=tk.RIGHT)

        back_button = ttk.Button(butts_frame, text="Previous")
        back_button.pack(side=tk.LEFT)

        global step_1d
        step_1d = step_start

        # Plot function
        def pl1ds():
            # Destroy previous plot if exists
            if len(plot_frame.winfo_children()) > 0:
                for widget in plot_frame.winfo_children():
                    widget.destroy()

            global step_1d
            var.SetStepSelection([step_1d,1])
            
            fig = plt.figure(figsize=(8, 8))  # Create a new figure for the plot
            gs = gridspec.GridSpec(1, 1)  # Create a 1x1 grid for the plot layout
            ax = fig.add_subplot(gs[0, 0])  # Add a subplot to the figure

            data = np.empty([sel_count[count_dim[0]]], dtype=np.float64)
            var.SetSelection([sel_start, sel_count])

            fr.Get(var, data, adios2.Mode.Sync)
            x_values = np.arange(sel_start[count_dim[0]], sel_end[count_dim[0]])
            ax.plot(x_values, data)
            ax.set_xlabel("x-axis")
            ax.set_ylabel("Values")

            ax.set_title(
                "Data from variable " + selected_var + " with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_1d))

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Go forward one step
        def forw():
            global step_1d
            step_1d += 1
            pl1ds()
            
            if step_1d == step_start + step_count - 1:
                forw_button.config(state=tk.DISABLED)
            elif step_1d == step_start + 1:
                back_button.config(state=tk.NORMAL)

        # Go back one step
        def back():
            global step_1d
            step_1d -= 1
            pl1ds()

            if step_1d == step_start:
                back_button.config(state=tk.DISABLED)
            elif step_1d == step_start + step_count - 2:
                forw_button.config(state=tk.NORMAL)

        forw_button.config(command=forw)
        back_button.config(command=back)

        # Initial plot
        pl1ds()
        back_button.config(state=tk.DISABLED)

    # nD Display

    def display_nd():
        nonlocal fr
    
        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        # Step Selection
        try:
            step_start = int(step_start_entry.get())
        except ValueError:
            step_start = 0

        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1

        # Selection
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

        text_frame = ttk.Frame(display_window)
        text_frame.pack(side=tk.TOP, padx=5, pady=5)

        # Create a text box for displaying the result
        text_box = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=80, height=20)
        text_box.pack(fill=tk.BOTH, expand=True)

        


        def update_text_box():
            nonlocal text_box, fr, var, sel_start, sel_count, step_start, step_count

            data_str = "Data from variable " + selected_var + " with start " + str(sel_start) + " and count " + str(sel_count) + ", step " + str(step_start) + " with step count " + str(step_count) + "\n\n"
            for s in range(step_count):
                
                var.SetStepSelection([step_start+s, 1])
                var.SetSelection([sel_start, sel_count])

                data = np.empty(sel_count, dtype=np.float64)
                fr.Get(var, data, adios2.Mode.Sync)

                data_str += np.array2string(data, precision=5, separator=', ') + "\n"

            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, data_str)

        update_text_box()

    # Check dimensions, steps, and if more options displayed and plot data accordingly
    def check_and_plot():
        var = io.InquireVariable(selected_var)
        shape = var.Shape()
        dim = len(shape)

        # Creates selection count array for checking purposes
        try:
            sel_count_str = sel_count_entry.get()
            sel_count = np.array(eval(sel_count_str))
        except (ValueError, SyntaxError):
            sel_count = np.ones(dim, dtype=int)


        try:
            step_count = int(step_count_entry.get())
        except ValueError:
            step_count = 1

        j = 0
        for i in range(dim):
            if (sel_count[i] != 1):
                j += 1
        global spec
        

        if spec:
            plot_1d_v_1d()

        elif(step_count != 1 and j == 2):
            plot_2d_series()

        elif(step_count != 1 and j == 1):
            plot_1d_series()

        elif(step_count == 1 and j == 2):
            plot_2d()
            

        elif(step_count == 1 and j == 1):
            plot_1d()
            
        else:
            print("Selection dimension not 1 or 2")

    # Displays data if display button clicked
    def check_and_display():

        display_nd()
    
    # Buttons' frame
    button_frame = ttk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, anchor=tk.S, padx=5, pady=5)

    # 1D v 1D special button for more options
    spec_button = ttk.Button(button_frame, text="More options", command=spec_plot_show)
    spec_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Plot button
    plot_button = ttk.Button(button_frame, text="Plot", command=check_and_plot)
    plot_button.pack(side=tk.LEFT, padx=5, pady=5)
    # Display button
    display_button = ttk.Button(button_frame, text="Display", command=check_and_display)
    display_button.pack(side=tk.LEFT, padx=5, pady=5)

    root.mainloop()

    fr.Close()

# Execute code if running in main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bp_file", "-b", help="Path to the BP file", required=True)
    args = parser.parse_args()

    show_file(args.bp_file)
