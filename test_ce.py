import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import csv
import glob

class ConfigEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Config Editor")

        # Load current settings from CSV
        self.load_settings()

        # Create GUI components
        self.create_widgets()

    def load_settings(self):
        self.config_file = 'config.csv'

        # Check if the config file exists, if not, show error and close
        if not os.path.exists(self.config_file):
            messagebox.showerror("Error", "Config file not found! Exiting...")
            self.root.quit()

        # Load settings from the config file
        with open(self.config_file, 'r') as file:
            reader = csv.reader(file)
            self.config = {rows[0]: rows[1] for rows in reader}

    def create_widgets(self):
        # Labels and Entry fields for min_words and time_limit
        tk.Label(self.root, text="Minimum Words:").grid(row=0, column=0, padx=10, pady=10)
        self.min_words_var = tk.StringVar(value=self.config['min_words'])
        self.min_words_entry = tk.Entry(self.root, textvariable=self.min_words_var)
        self.min_words_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Time Limit (seconds):").grid(row=1, column=0, padx=10, pady=10)
        self.time_limit_var = tk.StringVar(value=self.config['time_limit'])
        self.time_limit_entry = tk.Entry(self.root, textvariable=self.time_limit_var)
        self.time_limit_entry.grid(row=1, column=1, padx=10, pady=10)

        # Button to open file explorer and select a folder
        self.folder_button = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        self.folder_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Save button
        self.save_button = tk.Button(self.root, text="Save Settings", command=self.save_config)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=10)

    def select_folder(self):
        # Open a file dialog to select a folder
        folder_path = filedialog.askdirectory(title="Select Folder")
        
        if folder_path:
            # Get the current directory where config_editor is located
            current_directory = os.path.dirname(os.path.abspath(__file__))
            destination_folder = os.path.join(current_directory, "math_problems")

            # Ensure "math_problems" folder can be removed and recreated without permission issues
            if os.path.exists(destination_folder):
                try:
                    shutil.rmtree(destination_folder)  # Remove the folder and its contents
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove existing 'math_problems' folder: {str(e)}")
                    return

            # Create a new "math_problems" folder
            try:
                os.makedirs(destination_folder)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create 'math_problems' folder: {str(e)}")
                return

            # Copy only .png files from the selected folder
            try:
                png_files = glob.glob(os.path.join(folder_path, "*.png"))  # List of all .png files
                for file in png_files:
                    shutil.copy(file, destination_folder)  # Copy each .png file to the destination folder

                messagebox.showinfo("Success", f"Copied {len(png_files)} .png files to 'math_problems'.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy files: {str(e)}")

    def save_config(self):
        # Get values from entry fields
        new_min_words = self.min_words_var.get()
        new_time_limit = self.time_limit_var.get()

        # Validate inputs (ensure they are numeric)
        if not new_min_words.isdigit() or not new_time_limit.isdigit():
            messagebox.showerror("Error", "Both values must be numeric!")
            return

        # Save the updated values to the CSV file
        with open(self.config_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["min_words", new_min_words])
            writer.writerow(["time_limit", new_time_limit])

        messagebox.showinfo("Success", "Settings updated successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditorApp(root)
    root.mainloop()
