import globals  # Import global variables

import tkinter as tk
from tkinter import ttk
from tab_browseRecord import TabBrowseRecord
from tab_addNoise import TabAddNoise
from tab_removeNoise import TabRemoveNoise  # Ensure this is correctly imported
from tab_perfEvaluation import TabPerfEvaluation  # Ensure this is correctly imported

# Global variable to store the current audio file's path
CURRENT_AUDIO_FILE = None
NOISY_AUDIO_FILE = None
CLEANED_AUDIO_FILE = None


def setup_style():
    style = ttk.Style()
    style.theme_use('clam')  # Modern theme
    style.configure("TNotebook", background="#333333", borderwidth=0)
    style.configure("TNotebook.Tab", font=('Arial', 15, 'bold'), padding=[20, 10], background="#555555", foreground="green")
    style.configure("TButton", font=('Arial', 13), background="#606060", foreground="#FFFFFF", borderwidth=1)
    style.configure("TLabel", font=('Arial', 22, 'bold'), background="#404040", foreground="#FFD700")


def main():
    root = tk.Tk()
    root.title("Speech Background Voice Suppression with Deep Learning")
    root.geometry("1000x700")
    setup_style()

    tab_control = ttk.Notebook(root)

    # Initialize tabs
    browse_record_tab = TabBrowseRecord(root, tab_control)
    add_noise_tab = TabAddNoise(root, tab_control)
    remove_noise_tab = TabRemoveNoise(root, tab_control)
    perf_evaluation_tab = TabPerfEvaluation(root, tab_control)

    tab_control.add(browse_record_tab.frame, text="Browse or Record")
    tab_control.add(add_noise_tab.frame, text="select Noise")
    tab_control.add(remove_noise_tab.frame, text="Remove Noise")
    tab_control.add(perf_evaluation_tab.frame, text="Performance Evaluation")

    tab_control.pack(expand=1, fill="both")

    root.mainloop()

if __name__ == "__main__":
    main()
