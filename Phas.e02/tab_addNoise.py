# Assuming globals.py exists and contains:
# CURRENT_AUDIO_FILE = None

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sounddevice as sd
import scipy.io.wavfile as wav
import pygame
import numpy as np
import matplotlib.pyplot as plt
import soundfile
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.fft
import soundfile as sf
import threading
import time
import globals  # Make sure globals.py is correctly referenced


class TabAddNoise:
    def __init__(self, root, tab_control):
        self.root = root
        self.frame = ttk.Frame(tab_control)
        self.filename = None  # Store the current file here
        self.noisy_filename = None  # Store the modified file
        self.canvas = None  # To hold the matplotlib canvas
        self.setup_ui()

    def setup_ui(self):
        button_width = 15
        for i in range(6):
            self.frame.grid_columnconfigure(i, weight=1)

        ttk.Button(self.frame, text="Gaussian", command=lambda: self.add_noise("gaussian"), width=button_width).grid(
            column=0, row=0, padx=5, pady=10)
        ttk.Button(self.frame, text="Breath", command=lambda: self.add_noise("breath"), width=button_width).grid(
            column=1, row=0, padx=5, pady=10)
        ttk.Button(self.frame, text="Play", command=self.play_audio, width=button_width).grid(column=3, row=0, padx=5,
                                                                                              pady=10)
        ttk.Button(self.frame, text="Signal", command=lambda: self.display_plot("signal"), width=button_width).grid(
            column=4, row=0, padx=5, pady=10)
        ttk.Button(self.frame, text="Spectrum", command=lambda: self.display_plot("spectrum"), width=button_width).grid(
            column=5, row=0, padx=5, pady=10)

        self.plot_frame = ttk.Frame(self.frame)
        self.plot_frame.grid(column=0, row=1, columnspan=6, sticky="nsew", padx=10, pady=10)
        self.frame.grid_rowconfigure(1, weight=1)

    def add_noise(self, noise_type):
        filename = globals.CURRENT_AUDIO_FILE
        messagebox.showinfo("File Name", f"{filename}")

        if not filename:
            messagebox.showinfo("Add Noise", "No file selected.")
            return

        data, samplerate = sf.read(filename)

        if noise_type == "gaussian":
            noise = np.random.normal(0, 0.01, data.shape)
            noisy_data = data + noise

        elif noise_type == "breath":
            # Simulate breath noise - this is a placeholder for actual breath noise addition
            noise = np.random.normal(0, 0.02, data.shape)
            noisy_data = data + noise

        # Save the modified file
        noisy_filename = "noisy_" + os.path.basename(filename)
        self.noisy_filename = os.path.join("recordings", noisy_filename)
        globals.NOISY_AUDIO_FILE = self.noisy_filename  # Update global variable

        # sf.write(self.noisy_filename, noisy_data, samplerate)
        try:
            # Attempt to write to the file
            sf.write(self.noisy_filename, noisy_data, samplerate)
        except soundfile.LibsndfileError as e:
            messagebox.showerror("Error", f"Failed to save the noisy file: {e}")
            return  # Exit the method if saving failed

        messagebox.showinfo("Add Noise", f"{noise_type.capitalize()} noise selected and file saved as {noisy_filename}")

    # Implement the play_audio, display_plot, and other auxiliary methods similar to those in TabBrowseRecord
    def play_audio(self):
        if not self.noisy_filename:
            messagebox.showinfo("Play Audio", "No audio file selected.")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(self.noisy_filename)
        pygame.mixer.music.play()
        messagebox.showinfo("Play Audio", "Playing audio...")

        # Start a new thread to wait for the music to finish playing
        threading.Thread(target=self.wait_for_audio_to_finish).start()

        while pygame.mixer.music.get_busy():
            # You can use time.sleep(1) here to wait or tkinter's after method to periodically check
            pygame.time.wait(100)  # Wait a bit for playback to finish, adjust as necessary

        # Stop and unload the music to release the file lock
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # If available, or pygame.mixer.quit()

        # Now the file should be unlocked, and you can proceed with other operations

    def wait_for_audio_to_finish(self):
        while pygame.mixer.music.get_busy():  # While the music is playing
            time.sleep(1)  # Wait for 1 second before checking again

        # Once the music has finished playing, show a message box
        # Use 'after' method to ensure the messagebox is called in the main thread
        self.root.after(0, lambda: messagebox.showinfo("Play Audio", "Audio playback finished."))

    def display_plot(self, plot_type):
        if not self.noisy_filename:
            messagebox.showinfo("Display", "No file selected.")
            return

        data, samplerate = sf.read(self.noisy_filename)
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
