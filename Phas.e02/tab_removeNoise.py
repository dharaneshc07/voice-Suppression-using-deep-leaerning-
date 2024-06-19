# Assuming globals.py exists and contains:
# CURRENT_AUDIO_FILE = None
# NOISY_AUDIO_FILE = None  # You may want to add this to handle the noisy file globally.

import os
import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.fft
import soundfile as sf
import threading
import time
from scipy.signal import wiener
import numpy as np
import librosa

from skimage.restoration import denoise_nl_means, estimate_sigma
from scipy.io import wavfile
import numpy as np

import globals

class TabRemoveNoise:
    def __init__(self, root, tab_control):
        self.root = root
        self.frame = ttk.Frame(tab_control)
        self.canvas = None  # To hold the matplotlib canvas
        self.cleaned_filename = None  # Store the cleaned file
        self.setup_ui()

    def setup_ui(self):
        button_width = 15
        for i in range(5):
            self.frame.grid_columnconfigure(i, weight=1)

        ttk.Button(self.frame, text="Remove Noise", command=self.remove_noise, width=button_width).grid(column=0, row=0, padx=5, pady=10)
        ttk.Button(self.frame, text="Play", command=self.play_audio, width=button_width).grid(column=1, row=0, padx=5, pady=10)
        ttk.Button(self.frame, text="Signal", command=lambda: self.display_plot("signal"), width=button_width).grid(column=2, row=0, padx=5, pady=10)
        ttk.Button(self.frame, text="Spectrum", command=lambda: self.display_plot("spectrum"), width=button_width).grid(column=3, row=0, padx=5, pady=10)

        self.plot_frame = ttk.Frame(self.frame)
        self.plot_frame.grid(column=0, row=1, columnspan=5, sticky="nsew", padx=10, pady=10)
        self.frame.grid_rowconfigure(1, weight=1)

    def remove_noise(self):
        noisy_filename = globals.NOISY_AUDIO_FILE
        if not noisy_filename:
            messagebox.showinfo("Remove Noise", "No noisy file selected.")
            return

        data, samplerate = sf.read(noisy_filename)

        # Placeholder for noise removal process
        cleaned_data = self.spectral_subtraction(data, samplerate)
        cleaned_data = self.wiener_filter(cleaned_data)

        # cleaned_data = self.your_noise_removal_function(data)  # Implement this function

        # Save the cleaned file
        cleaned_filename = "cleaned_" + os.path.basename(noisy_filename)
        self.cleaned_filename = os.path.join("recordings", cleaned_filename)
        globals.CLEANED_AUDIO_FILE = self.cleaned_filename
        sf.write(self.cleaned_filename, cleaned_data, samplerate)
        messagebox.showinfo("Remove Noise", "Noise removed and file saved as " + cleaned_filename)

    def play_audio(self):
        if not self.cleaned_filename:
            messagebox.showinfo("Play Audio", "No audio file selected.")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(self.cleaned_filename)
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
        if not self.cleaned_filename:
            messagebox.showinfo("Display", "No file selected.")
            return

        data, samplerate = sf.read(self.cleaned_filename)
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

    def wiener_filter(self, data):
        # Apply the Wiener filter
        cleaned_data = wiener(data)
        return cleaned_data

    def spectral_subtraction(self, data, samplerate):
        # Placeholder for Spectral Subtraction
        # This is a very simplified version and might not be effective for all types of noise
        # FFT
        data_fft = np.fft.fft(data)
        frequencies = np.fft.fftfreq(len(data), 1 / samplerate)

        # Estimate noise as the average of the magnitude of the lowest 10% of frequencies
        noise_estimate = np.mean(np.abs(data_fft[frequencies < (0.1 * np.max(frequencies))]))
        # Subtract noise estimate from all frequencies
        cleaned_fft = data_fft - noise_estimate

        # Inverse FFT to get back to time domain
        cleaned_data = np.fft.ifft(cleaned_fft)
        return cleaned_data.real

    def spectral_gating(data, sr, n_fft=2048, hop_length=512, noise_floor=0.1):
        # STFT
        stft = librosa.stft(data, n_fft=n_fft, hop_length=hop_length)
        magnitude, phase = librosa.magphase(stft)

        # Estimate the noise power in each frequency bin
        noise_power = np.mean(np.abs(stft), axis=1) * noise_floor

        # Apply spectral gate
        magnitude_clean = np.maximum(magnitude - noise_power[:, np.newaxis], 0)

        # ISTFT to get back to time domain
        clean_stft = magnitude_clean * phase
        cleaned_data = librosa.istft(clean_stft, hop_length=hop_length)
        return cleaned_data

    def simple_vad(data, sr, frame_length=2048, hop_length=512, energy_threshold=0.02):
        # Calculate the short-time energy of the audio signal
        energy = np.array([sum(abs(data[i:i + frame_length] ** 2)) for i in range(0, len(data), hop_length)])
        vad = (energy > energy_threshold).astype(int)
        return vad


    def non_local_means_denoise(audio_path):
        rate, data = wavfile.read(audio_path)
        data = data.astype(np.float32)

        # Estimate 'sigma' if needed
        sigma_est = np.mean(estimate_sigma(data, multichannel=True))

        # Apply non-local means denoise
        denoised = denoise_nl_means(data, h=1.15 * sigma_est, fast_mode=True,
                                    patch_size=5, patch_distance=6, multichannel=True)
        return rate, denoised.astype(np.int16)
