# Inside the TabBrowseRecord methods
import globals  # or import globals as global_vars

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sounddevice as sd
import scipy.io.wavfile as wav
import pygame
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.fft
import soundfile as sf

# Ensure using TkAgg as backend
matplotlib.use('TkAgg')

class TabBrowseRecord:
    def __init__(self, root, tab_control):
        self.root = root
        self.frame = ttk.Frame(tab_control)
        self.filename = None  # Store the current file here
        self.canvas = None  # To hold the matplotlib canvas
        self.setup_ui()

    def setup_ui(self):
        button_width = 15  # Set a uniform width for all buttons
        for i in range(5):
            self.frame.grid_columnconfigure(i, weight=1)  # Distribute extra space equally among columns

        ttk.Button(self.frame, text="Browse", command=self.browse_files, width=button_width).grid(column=0, row=0,
        padx=5, pady=10)
        ttk.Button(self.frame, text="Record", command=self.record_audio, width=button_width).grid(column=1, row=0,
        padx=5,pady=10)
        # ttk.Button(self.frame, text="Play", command=self.play_audio, width=button_width).grid(column=2, row=0, padx=5,
        #pady=10)
        #ttk.Button(self.frame, text="Signal", command=lambda: self.display_plot("signal"), width=button_width).grid(
            #column=3, row=0, padx=5, pady=10)
        #ttk.Button(self.frame, text="Spectrum", command=lambda: self.display_plot("spectrum"), width=button_width).grid(
            #column=4, row=0, padx=5, pady=10)

        # Setup the plotting area
        self.plot_frame = ttk.Frame(self.frame)
        self.plot_frame.grid(column=0, row=2, columnspan=5, sticky="nsew", padx=10, pady=10)
        self.frame.grid_rowconfigure(2, weight=1)  # Allow the plot area to expand vertically

    def browse_files(self):
        filename = filedialog.askopenfilename(title="Select a File",
                                              filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*")))
        if filename:
            self.filename = filename  # Store the filename
            messagebox.showinfo("File Selected", filename)
            globals.CURRENT_AUDIO_FILE = self.filename  # Update global variable
        else:
            messagebox.showinfo("Action", "No file selected.")

    def record_audio(self):
        duration = 10  # seconds
        fs = 44100  # Sample rate
        num_samples = duration * fs
        messagebox.showinfo("Record", "Recording will start after closing this message.")
        recording = sd.rec(int(num_samples), samplerate=fs, channels=2, dtype='float64')
        sd.wait()
        filename = simpledialog.askstring("Save Recording", "Enter a filename to save:", parent=self.root)
        if filename:
            if not filename.endswith(".wav"):
                filename += ".wav"
            directory = "recordings"
            os.makedirs(directory, exist_ok=True)
            filepath = os.path.join(directory, filename)
            wav.write(filepath, fs, recording)
            self.filename = filepath  # Store the filename of the recording
            messagebox.showinfo("Record", f"Recording saved as {filepath}")
            globals.CURRENT_AUDIO_FILE = self.filename  # Update global variable
        else:
            messagebox.showinfo("Record", "Recording was not saved.")

    def play_audio(self):
        if not self.filename:
            messagebox.showinfo("Play Audio", "No audio file selected.")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(self.filename)
        pygame.mixer.music.play()
        messagebox.showinfo("Play Audio", "Playing audio...")

        # Start a new thread to wait for the music to finish playing
        threading.Thread(target=self.wait_for_audio_to_finish).start()

    def wait_for_audio_to_finish(self):
        while pygame.mixer.music.get_busy():  # While the music is playing
            time.sleep(1)  # Wait for 1 second before checking again

        # Once the music has finished playing, show a message box
        # Use 'after' method to ensure the messagebox is called in the main thread
        self.root.after(0, lambda: messagebox.showinfo("Play Audio", "Audio playback finished."))

    def display_plot(self, plot_type):
        if not self.filename:
            messagebox.showinfo("Display", "No file selected.")
            return

        data, samplerate = sf.read(self.filename)
        if data.ndim > 1:
            data = data[:, 0]

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        if plot_type == "signal":
            time = np.linspace(0., len(data) / samplerate, len(data))
            ax.plot(time, data)
            ax.set_title("Time Domain Signal")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Amplitude")
        elif plot_type == "spectrum":
            N = len(data)
            yf = scipy.fft.fft(data)
            xf = np.linspace(0.0, 1.0 / (2.0 * (1 / samplerate)), N // 2)
            ax.plot(xf, 2.0 / N * np.abs(yf[:N // 2]))
            ax.set_title("Spectrum")
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Amplitude")

        self.clear_canvas()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_canvas(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
