# Assuming globals.py has been properly set up with necessary global variables
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import globals
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import librosa
from pesq import pesq
from pystoi.stoi import stoi
from scipy.signal import wiener
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import librosa


def calculate_snr(clean_signal, noisy_signal):
    signal_power = np.sum(clean_signal ** 2)
    noise_power = np.sum((clean_signal - noisy_signal) ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    return snr


class TabPerfEvaluation:
    def __init__(self, root, tab_control):
        self.root = root
        self.frame = ttk.Frame(tab_control)
        self.setup_ui()

    def setup_ui(self):
        # Buttons row
        ttk.Button(self.frame, text="Evaluate", command=self.evaluate_audio).grid(column=0, row=0, padx=10, pady=10,
                                                                                  sticky="ew")

        # Plot and metrics row configuration
        self.plot_frame = ttk.Frame(self.frame)
        # self.plot_frame.grid(column=0, row=1, sticky="nsew", padx=5, pady=5)
        # self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_rowconfigure(1, weight=1)

        # Configure the frame to use all available space for the plot and metrics
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)  # Plot row
        self.frame.grid_rowconfigure(2, weight=1)  # Metrics row

        # Plot area
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(column=0, row=1, sticky="nsew", padx=5, pady=5)

        # Metrics display area
        self.metrics_text = tk.Text(self.frame, height=10, width=40)
        self.metrics_text.grid(column=0, row=2, sticky="nsew", padx=5, pady=5)


    def evaluate_audio(self):
        clean_path = globals.CURRENT_AUDIO_FILE
        noisy_path = globals.NOISY_AUDIO_FILE
        cleaned_path = globals.CLEANED_AUDIO_FILE

        if not (clean_path and noisy_path and cleaned_path):
            messagebox.showerror("Error", "Audio files not fully specified.")
            return

        try:
            clean_signal, sr = librosa.load(clean_path, sr=None)
            noisy_signal, _ = librosa.load(noisy_path, sr=None)
            cleaned_signal, _ = librosa.load(cleaned_path, sr=None)

            # Ensure signals are the same length for evaluation
            min_len = min(len(clean_signal), len(noisy_signal), len(cleaned_signal))
            clean_signal = clean_signal[:min_len]
            noisy_signal = noisy_signal[:min_len]
            cleaned_signal = cleaned_signal[:min_len]

            # Update plot
            self.ax.clear()
            times = np.arange(len(clean_signal)) / sr
            self.ax.plot(times, clean_signal, label='Clean', color='blue')
            self.ax.plot(times, cleaned_signal, label='Denoised', color='green')
            self.ax.set(xlabel='Time (s)', ylabel='Amplitude')
            self.ax.legend()
            self.canvas.draw()

            sample_rate = 16000  # Or 8000, depending on your audio files

            snr_before = calculate_snr(clean_signal, noisy_signal)
            snr_after = calculate_snr(clean_signal, cleaned_signal)
            pesq_score = calculate_pesq(clean_signal, cleaned_signal, sample_rate)
            # pesq_score = pesq(sr, clean_signal, cleaned_signal, 'wb')
            stoi_score = stoi(clean_signal, cleaned_signal, sr, extended=False)

            metrics_results = f"SNR before: {snr_before:.2f} dB\n" \
                              f"SNR after: {snr_after:.2f} dB\n" \
                              f"PESQ: {pesq_score:.2f}\n" \
                              f"STOI: {stoi_score:.2f}"
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(tk.END, metrics_results)

            messagebox.showinfo("Evaluation Results", f"SNR before: {snr_before:.2f} dB\n"
                                                      f"SNR after: {snr_after:.2f} dB\n"
                                                      f"PESQ: {pesq_score:.2f}\n"
                                                      f"STOI: {stoi_score:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to evaluate: {e}")

    # In your main application setup, add the evaluation tab to your tab_control
    # and ensure the globals module is correctly handling the audio file paths.
    from pesq import pesq


def calculate_pesq(clean_signal, denoised_signal, sample_rate):
    if sample_rate == 8000:
        mode = 'nb'  # Narrowband
    elif sample_rate == 16000:
        mode = 'wb'  # Wideband
    else:
        raise ValueError("Sample rate must be either 8000 or 16000 Hz.")

    score = pesq(sample_rate, clean_signal, denoised_signal, mode)
    return score
