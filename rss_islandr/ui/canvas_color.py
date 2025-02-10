import tkinter as tk


# Function to calculate risk based on dropdown value
def risk_calc(value: float):

    value = float(value)
    if value <= 0.1:
        return "green"
    elif 0.1 < value <= 0.3:
        return "yellow"
    else:
        return "red"  # Low risk, so red light


# Function to update light color
def update_light(value):
    # Call risk_calc to get the color based on dropdown value
    color = risk_calc(value)
    # Update the light color on the canvas
    canvas.itemconfig(light, fill=color)


# Create main window
root = tk.Tk()
root.title("Light Indicator")

# Dropdown options
options = [1.0, 0.8, 0.55, 0.45, 0.25, 0.15, 0.02]
selected_value = tk.StringVar()
selected_value.set(options[0])  # Default value

# Create the dropdown menu
dropdown = tk.OptionMenu(root, selected_value, *options, command=update_light)
dropdown.pack(pady=10)

# Create canvas for light indicator
canvas = tk.Canvas(root, width=50, height=50)
canvas.pack()
light = canvas.create_oval(5, 5, 45, 45, fill="red")  # Default red

# Run the GUI loop
root.mainloop()
