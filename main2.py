import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import csv
import os
import ctypes

class MathQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)  # Full screen mode
        self.root.attributes('-topmost', True)
        self.root.bind("<Escape>", self.exit_fullscreen)  # Exit on Escape (for development purposes)
        self.root.bind("<Tab>", self.disable_close)  # Disable Alt+Tab
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close)  # Disable Alt+F4 (close event)

        # Intercept Alt+Tab, Alt+F4 using Windows API
        self.block_shortcuts()

        # Load settings from CSV file
        self.load_settings()

        # Load all PNG files from "math_problems" folder
        self.load_problem_images()

        self.current_question = 0
        self.typed_words = 0
        self.start_typing_time = time.time()
        self.typing_intervals = []

        self.create_widgets()
        self.show_question()

    def load_settings(self):
        # Load min_words and time_limit from config.csv
        config_file = 'config.csv'
        if not os.path.exists(config_file):
            # If the file doesn't exist, create a default one
            with open(config_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["min_words", "1"])   # Default min words
                writer.writerow(["time_limit", "5"])  # Default time limit in seconds
                writer.writerow(["wpm_limit", "30"])  # Default WPM
                writer.writerow(["wpm_td", "10"])  # Default WPM Tracking Duration

        with open(config_file, 'r') as file:
            reader = csv.reader(file)
            config = {rows[0]: int(rows[1]) for rows in reader}

        self.min_words = config.get("min_words", 2)
        self.time_limit = config.get("time_limit", 10)
        self.wpm_limit = config.get("wpm_limit", 30)
        self.wpm_td = config.get("wpm_td", 10)

    def block_shortcuts(self):
        # Use ctypes to block Alt+Tab and Alt+F4
        user32 = ctypes.windll.user32
        user32.BlockInput(True)  # Block all input (keyboard, mouse)
        self.root.after(100, lambda: user32.BlockInput(False))  # Allow input after tkinter initializes

    def load_problem_images(self):
        # Get all PNG files in the "math_problems" folder
        problem_folder = 'math_problems'
        if os.path.exists(problem_folder) and os.path.isdir(problem_folder):
            self.questions = [f for f in os.listdir(problem_folder) if f.endswith('.png')]
            # Prepend folder path to the filenames
            self.questions = [os.path.join(problem_folder, f) for f in self.questions]
        else:
            messagebox.showerror("Error", f"Folder '{problem_folder}' does not exist.")
            self.questions = []

    def create_widgets(self):
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=20)

        self.text_entry = tk.Text(self.root, height=5, width=60)
        self.text_entry.pack(pady=20)
        
        # Disable Copy, Paste, and Cut
        self.text_entry.bind("<Control-c>", lambda e: "break")  # Disable Ctrl+C (copy)
        self.text_entry.bind("<Control-v>", lambda e: "break")  # Disable Ctrl+V (paste)
        self.text_entry.bind("<Control-x>", lambda e: "break")  # Disable Ctrl+X (cut)
        
        # Monitor typing speed
        self.text_entry.bind("<KeyRelease>", self.track_typing_speed)

        self.next_button = tk.Button(self.root, text="Next", command=self.check_input)
        self.next_button.pack(pady=20)

        self.timer_label = tk.Label(self.root, text="Time left: ")
        self.timer_label.pack(pady=20)

    def show_question(self):
        # Load and display the image if available
        img = Image.open(self.questions[self.current_question])
        img = img.resize((400, 400))
        photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=photo)
        self.image_label.image = photo
        self.text_entry.delete(1.0, tk.END)  # Clear text entry field
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        self.elapsed_time = time.time() - self.start_time
        self.time_left = self.time_limit - self.elapsed_time
        if self.time_left > 0:
            self.timer_label.config(text=f"Time left: {int(self.time_left)} seconds")
            self.root.after(1000, self.update_timer)
        else:
            self.next_button.config(state=tk.NORMAL)  # Allow user to move to next question after time limit

    def check_input(self):
        text = self.text_entry.get(1.0, tk.END).strip()
        word_count = len(text.split())
        if word_count >= self.min_words or self.time_left <= 0:
            self.current_question += 1
            if self.current_question < len(self.questions):
                self.show_question()
            else:
                messagebox.showinfo("Completed", "You have completed all questions!")
                self.root.quit()
        else:
            messagebox.showwarning("Insufficient words", f"Please write at least {self.min_words} words.")

    def disable_close(self):
        # Disable the close button (Alt+F4)
        messagebox.showwarning("Warning", "You cannot close this window!")
        
    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)  # Press Escape to exit fullscreen (for dev mode)
        
    def track_typing_speed(self, event=None):
        # Track the time of keypress and the number of words typed
        current_time = time.time()
        text = self.text_entry.get(1.0, tk.END).strip()
        words = text.split()
        self.typed_words = len(words)
        
        # Append the current typing timestamp
        self.typing_intervals.append(current_time)

        # Remove typing intervals older than 10 seconds from the list
        self.typing_intervals = [t for t in self.typing_intervals if current_time - t <= 10]

        # If the number of words typed in the last 10 seconds exceeds self.wpm_limits/6
        if len(words) >= self.wpm_limit/(60/self.wpm_td) and len(self.typing_intervals) >= self.wpm_limit/(60/self.wpm_td):
            # Clear the text box and warn the user
            self.text_entry.delete(1.0, tk.END)
            messagebox.showwarning("Slow down!", "You are typing too fast! Please type at a reasonable pace.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    root.mainloop()
