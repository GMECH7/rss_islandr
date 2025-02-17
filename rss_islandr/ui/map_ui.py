# Create the main Tkinter window
file_ = r"C:\Users\George\Documents\makge\Python\islandr\rss_islandr\rss_islandr\static\map.html"
import subprocess
import sys
import os


class MapUI:
    def __init__(self):
        self.webview_process = None

    def show_map(self):
        """Launch the webview window in a separate process."""
        script_path = os.path.abspath(__file__)  # Path to the current script
        self.webview_process = subprocess.Popen([sys.executable, script_path, "--webview"])

    def close_map(self):
        """Terminate the webview process."""
        if self.webview_process:
            self.webview_process.terminate()
            self.webview_process = None

    def run_webview(self):
        """Run the webview window (to be called in a separate process)."""
        import webview

        webview.create_window(
            "Embedded Map",
            file_,  # Replace with the path to your map.html file
            width=800,
            height=600,
            background_color="#19232d",
        )
        webview.start()


# Entry point for the webview process
if __name__ == "__main__":
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--webview", action="store_true", help="Run webview in a separate process")
    args = parser.parse_args()

    if args.webview:
        # If --webview flag is passed, run the webview window
        map_ui = MapUI()
        map_ui.run_webview()
# import tkinter as tk
# import subprocess
# import sys
# import os


# class MapApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tkinter with Embedded HTML Map")
#         self.root.geometry("800x600")

#         # Create a frame for the map
#         self.map_frame = tk.Frame(root, width=800, height=600)
#         self.map_frame.pack(fill="both", expand=True)

#         # Button to show the map
#         self.btn_show_map = tk.Button(
#             self.map_frame,
#             text="Show Map",
#             command=self.show_map,
#         )
#         self.btn_show_map.pack(pady=10)

#         # Button to close the map
#         self.btn_close_map = tk.Button(
#             self.map_frame,
#             text="Close Map",
#             command=self.close_map,
#             state=tk.DISABLED,  # Disabled until the map is opened
#         )
#         self.btn_close_map.pack(pady=10)

#         # Button to print a test message
#         self.btn_print_test = tk.Button(
#             self.map_frame,
#             text="Print Test",
#             command=self.print_test,
#         )
#         self.btn_print_test.pack(pady=10)

#         # Variable to store the subprocess
#         self.webview_process = None

#     def show_map(self):
#         # Launch webview in a separate process using subprocess
#         script_path = os.path.abspath(__file__)  # Path to the current script
#         self.webview_process = subprocess.Popen([sys.executable, script_path, "--webview"])

#         # Enable the "Close Map" button
#         self.btn_close_map.config(state=tk.NORMAL)

#     def close_map(self):
#         # Terminate the webview process
#         if self.webview_process:
#             self.webview_process.terminate()
#             self.webview_process = None

#         # Disable the "Close Map" button
#         self.btn_close_map.config(state=tk.DISABLED)

#     def print_test(self):
#         # Print a test message to verify GUI responsiveness
#         print("Tkinter GUI is responsive!")

#     def run_webview(self):
#         # This method will run in the separate process
#         import webview

#         webview.create_window(
#             "Embedded Map",
#             file_,  # Replace with the path to your map.html file
#             width=800,
#             height=600,
#         )
#         webview.start()


# # Run the application
# if __name__ == "__main__":
#     import argparse

#     # Parse command-line arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--webview", action="store_true", help="Run webview in a separate process")
#     args = parser.parse_args()

#     if args.webview:
#         # If --webview flag is passed, run the webview window
#         app = MapApp(tk.Tk())
#         app.run_webview()
#     else:
#         # Otherwise, run the Tkinter GUI
#         root = tk.Tk()
#         app = MapApp(root)
#         root.mainloop()
