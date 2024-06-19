import tkinter as tk
from tkinter import ttk, messagebox

from tkinter import filedialog

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

import pygame

import numpy as np
import scipy.fft
import matplotlib.pyplot as plt
from tkinter import filedialog
import soundfile as sf


# Placeholder functions for button actions
def browse_files():
    messagebox.showinfo("Action", "Browse files...")

    filename = filedialog.askopenfilename(title="Select a File",
                                          filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*")))
    if filename:
        messagebox.showinfo("File Selected", filename)
    else:
        messagebox.showinfo("Action", "No file selected.")


def record_audio():
    messagebox.showinfo("Action", "Record audio...")

    fs = 44100  # Sample rate
    duration = 15  # seconds
    messagebox.showinfo("Action", "Recording for 5 seconds...")
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='float64')
    sd.wait()  # Wait until recording is finished
    output_filename = "recording.wav"
    wav.write(output_filename, fs, myrecording)  # Save as WAV file
    messagebox.showinfo("Action", f"Audio recorded and saved as {output_filename}")


def play_audio():
    messagebox.showinfo("Action", "Play audio...")

    # Let the user choose an audio file
    filename = filedialog.askopenfilename(title="Select an Audio File",
                                          filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*")))
    if not filename:  # User cancelled the dialog
        messagebox.showinfo("Action", "No audio file selected.")
        return

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load the selected audio file
    pygame.mixer.music.load(filename)

    # Play the audio
    pygame.mixer.music.play()

    # Show a message box that the audio is playing
    messagebox.showinfo("Action", "Playing audio...")

    # This will not wait for the audio to finish playing.
    # If you want the application to wait, you could add a loop to check if the music is playing.


def add_gaussian_noise():
    messagebox.showinfo("Action", "Gaussian noise added...")


def add_breath_noise():
    messagebox.showinfo("Action", "Breath noise added...")


def apply_wiener_filter():
    messagebox.showinfo("Action", "Wiener filter applied...")


def apply_spectral_gating():
    messagebox.showinfo("Action", "Spectral gating applied...")


def display_time_domain_signal():
    messagebox.showinfo("Action", "Time Domain Signal displayed...")

    filename = filedialog.askopenfilename(title="Select an Audio File",
                                          filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*")))
    if not filename:  # User cancelled the dialog
        messagebox.showinfo("Action", "No audio file selected.")
        return

    # Load audio file
    data, samplerate = sf.read(filename)
    # Assuming mono or taking only the first channel if stereo
    if data.ndim > 1:
        data = data[:, 0]

    # Time vector
    time = np.linspace(0., len(data) / samplerate, len(data))

    # Plot time domain signal
    plt.figure(figsize=(10, 4))
    plt.plot(time, data)
    plt.title("Time Domain Signal")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.show()


def display_spectrum():
    messagebox.showinfo("Action", "Spectrum displayed...")

    filename = filedialog.askopenfilename(title="Select an Audio File",
                                          filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*")))
    if not filename:  # User cancelled the dialog
        messagebox.showinfo("Action", "No audio file selected.")
        return

    # Load audio file
    data, samplerate = sf.read(filename)
    # Assuming mono or taking only the first channel if stereo
    if data.ndim > 1:
        data = data[:, 0]

    # FFT
    N = len(data)
    yf = scipy.fft.fft(data)
    xf = np.linspace(0.0, 1.0 / (2.0 * (1 / samplerate)), N // 2)

    # Plot spectrum
    plt.figure(figsize=(10, 4))
    plt.plot(xf, 2.0 / N * np.abs(yf[:N // 2]))
    plt.title("Spectrum")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.show()


def display_time_domain_signal_noisy_and_clean():
    messagebox.showinfo("Action", "Time Domain Signal Noisy and Clean displayed...")


def display_metric_parameters():
    messagebox.showinfo("Action", "Metric Parameters displayed...")


def exit_application():
    if messagebox.askokcancel("Exit", "Do you really wish to exit?"):
        root.destroy()


# Initialize main application window
root = tk.Tk()
root.title("Speech Background Voice Suppression with Deep Learning")
root.geometry("1000x700")

# Style configuration
style = ttk.Style(root)
style.theme_use('clam')  # Modern theme
style.configure("TNotebook", background="#333333", borderwidth=0)
style.configure("TNotebook.Tab", font=('Arial', 15, 'bold'), padding=[20, 10], background="#555555",
                foreground="#FFD700")
style.configure("TButton", font=('Arial', 13), background="#606060", foreground="#FFFFFF", borderwidth=1)
style.configure("TLabel", font=('Arial', 22, 'bold'), background="#404040", foreground="#FFD700")

# Create Tab Control
tab_control = ttk.Notebook(root)
tab_names = ['Browse and Record', 'Play', 'Add Noise', 'Remove Noise', 'Display Result']
tabs = {name: ttk.Frame(tab_control) for name in tab_names}

for name, frame in tabs.items():
    tab_control.add(frame, text=name)
tab_control.pack(expand=1, fill="both")

# Tab 1: Browse and Record
ttk.Label(tabs['Browse and Record'], text="Browse and Record").grid(column=0, row=0, padx=10, pady=10, columnspan=2)
ttk.Button(tabs['Browse and Record'], text="Browse", command=browse_files).grid(column=0, row=1, padx=10, pady=10)
ttk.Button(tabs['Browse and Record'], text="Record", command=record_audio).grid(column=1, row=1, padx=10, pady=10)

# Tab 2: Play
ttk.Label(tabs['Play'], text="Play and Display").grid(column=0, row=0, padx=10, pady=10, columnspan=3)
ttk.Button(tabs['Play'], text="Play", command=play_audio).grid(column=0, row=1, padx=10, pady=10)
ttk.Button(tabs['Play'], text="Display Time Domain Signal", command=display_time_domain_signal).grid(column=1, row=1,
                                                                                                     padx=10, pady=10)
ttk.Button(tabs['Play'], text="Display Spectrum", command=display_spectrum).grid(column=2, row=1, padx=10, pady=10)

# Tab 3: Add Noise
ttk.Label(tabs['Add Noise'], text="Add Noise").grid(column=0, row=0, padx=10, pady=10, columnspan=2)
ttk.Button(tabs['Add Noise'], text="Gaussian Noise", command=add_gaussian_noise).grid(column=0, row=1, padx=10, pady=10)
ttk.Button(tabs['Add Noise'], text="Breath Noise", command=add_breath_noise).grid(column=1, row=1, padx=10, pady=10)

# Tab 4: Remove Noise
ttk.Label(tabs['Remove Noise'], text="Remove Noise").grid(column=0, row=0, padx=10, pady=10, columnspan=2)
ttk.Button(tabs['Remove Noise'], text="Wiener Filter", command=apply_wiener_filter).grid(column=0, row=1, padx=10,
                                                                                         pady=10)
ttk.Button(tabs['Remove Noise'], text="Spectral Gating", command=apply_spectral_gating).grid(column=1, row=1, padx=10,
                                                                                             pady=10)

# Tab 5: Display Result
ttk.Label(tabs['Display Result'], text="Display Results").grid(column=0, row=0, padx=10, pady=10, columnspan=2)
ttk.Button(tabs['Display Result'], text="Display Time Domain Signal Noisy and Clean",
           command=display_time_domain_signal_noisy_and_clean).grid(column=0, row=1, padx=10, pady=10)
ttk.Button(tabs['Display Result'], text="Display Metric Parameters", command=display_metric_parameters).grid(column=1,
                                                                                                             row=1,
                                                                                                             padx=10,
                                                                                                             pady=10)

# Exit Button
ttk.Button(root, text="Exit", command=exit_application).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

root.mainloop()
