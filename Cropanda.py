import librosa
import soundfile as sf
import numpy as np
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD  # Import tkinterdnd2


def detect_and_crop_sounds_improved(input_file, output_dir, onset_threshold_db=-30, sustain_threshold_db=-50, min_duration_sec=0.1, hop_length=512, padding_sec=0.05, progress_var=None, status_label=None):
    """
    Detects and crops sounds using onset detection and dual thresholding.
    """
    try:
        y, sr = librosa.load(input_file, sr=None)
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)

        # 1. Onset Detection
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length, backtrack=False, units='frames')
        onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)

        # 2. Dual Thresholding and Cropping
        sound_events = []
        for onset_time in onset_times:
            onset_sample = int(onset_time * sr)
            onset_frame = librosa.time_to_frames(onset_time, sr=sr, hop_length=hop_length)

            if rms_db[onset_frame] < onset_threshold_db:  continue

            # Track back (start)
            start_sample = onset_sample
            start_frame = onset_frame
            while start_sample > 0 and rms_db[start_frame] > sustain_threshold_db:
                start_sample -= hop_length
                start_frame = max(0, start_frame - 1)
            start_time = max(0, librosa.samples_to_time(start_sample, sr=sr) - padding_sec)
            start_sample = int(start_time * sr)

            # Track forward (end)
            end_sample = onset_sample
            end_frame = onset_frame
            while end_frame < len(rms_db) - 1 and rms_db[end_frame] > sustain_threshold_db:
                end_frame += 1

            end_sample = int(librosa.frames_to_time(end_frame - 1, sr=sr, hop_length=hop_length) * sr)
            end_sample += hop_length // 2

            end_time = min(len(y) / sr, librosa.samples_to_time(end_sample, sr=sr) + padding_sec)
            end_sample = int(end_time * sr)
            duration = end_time - start_time

            if duration < min_duration_sec: continue
            if sound_events and start_sample < sound_events[-1][1]: continue

            sound_events.append((start_sample, end_sample))

        # 3. Save Cropped Sounds
        num_sounds = len(sound_events)
        for i, (start_sample, end_sample) in enumerate(sound_events):
            cropped_audio = y[start_sample:end_sample]
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}_cropped_{i+1:03d}.wav")
            sf.write(output_file, cropped_audio, sr)

            if progress_var:
                progress = (i + 1) / num_sounds * 100
                progress_var.set(progress)
            if status_label:
                status_label.config(text=f"Processing sound {i+1}/{num_sounds}")
        if status_label:
            status_label.config(text=f"Finished. Processed {num_sounds} sounds")

    except Exception as e:
        if status_label:
            status_label.config(text=f"Error: {e}")
        messagebox.showerror("Error", str(e))
        raise


class SoundCropperApp:
    def __init__(self, master):
        self.master = master
        master.title("Cropanda")

        self.input_file = ""

        # --- GUI Elements ---

        # Input File (with Browse button)
        self.input_label = ttk.Label(master, text="Input File:")
        self.input_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_entry = ttk.Entry(master, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        self.input_button = ttk.Button(master, text="Browse...", command=self.browse_input)
        self.input_button.grid(row=0, column=2, padx=5, pady=5)


        # Onset Threshold
        self.onset_threshold_label = ttk.Label(master, text="Onset Threshold (dB):")
        self.onset_threshold_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.onset_threshold_entry = ttk.Entry(master, width=10)
        self.onset_threshold_entry.insert(0, "-30")
        self.onset_threshold_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Sustain Threshold
        self.sustain_threshold_label = ttk.Label(master, text="Sustain Threshold (dB):")
        self.sustain_threshold_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.sustain_threshold_entry = ttk.Entry(master, width=10)
        self.sustain_threshold_entry.insert(0, "-50")
        self.sustain_threshold_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Minimum Duration
        self.min_duration_label = ttk.Label(master, text="Min Duration (s):")
        self.min_duration_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.min_duration_entry = ttk.Entry(master, width=10)
        self.min_duration_entry.insert(0, "0.1")
        self.min_duration_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Padding
        self.padding_label = ttk.Label(master, text="Padding (s):")
        self.padding_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.padding_entry = ttk.Entry(master, width=10)
        self.padding_entry.insert(0, "0.05")
        self.padding_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Process Button
        self.process_button = ttk.Button(master, text="Process", command=self.start_processing)
        self.process_button.grid(row=5, column=1, padx=5, pady=10)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(master, variable=self.progress_var, length=300)
        self.progress_bar.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        # Status Label
        self.status_label = ttk.Label(master, text="")
        self.status_label.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

        # --- Drag and Drop ---
        # Use tkinterdnd2 for drag and drop
        self.master.drop_target_register(DND_FILES)
        self.master.dnd_bind('<<Drop>>', self.handle_drop)

        # Threading
        self.processing_thread = None

    def browse_input(self):
        self.input_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.flac;*.aiff")])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, self.input_file)

    def handle_drop(self, event):
        # Correctly handle file paths from drag-and-drop, including spaces and {}
        file_path = event.data
        # Remove curly braces and any surrounding spaces
        file_path = file_path.strip('{} ').replace('\\','')

        if os.path.isfile(file_path):
            self.input_file = file_path
            self.input_entry.delete(0, tk.END)  # Clear the entry
            self.input_entry.insert(0, self.input_file)  # Show the file
            #self.start_processing() # uncomment this if you want to start processing immediately after drop


    def start_processing(self):
        if self.processing_thread and self.processing_thread.is_alive():
            messagebox.showwarning("Already Processing", "Please wait for the current process to finish.")
            return

        if not self.input_file:
            messagebox.showerror("Error", "No input file provided.")
            return

        try:
            onset_threshold_db = float(self.onset_threshold_entry.get())
            sustain_threshold_db = float(self.sustain_threshold_entry.get())
            min_duration_sec = float(self.min_duration_entry.get())
            padding_sec = float(self.padding_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input for thresholds, duration, or padding.")
            return

        # --- Automatic Output Directory ---
        input_dir = os.path.dirname(self.input_file)
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        output_dir = os.path.join(input_dir, f"{base_name}_set")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.process_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_label.config(text="Starting...")

        self.processing_thread = threading.Thread(
            target=self.run_processing,
            args=(output_dir, onset_threshold_db, sustain_threshold_db, min_duration_sec, padding_sec)
        )
        self.processing_thread.start()

    def run_processing(self, output_dir, onset_threshold_db, sustain_threshold_db, min_duration_sec, padding_sec):
        try:
            detect_and_crop_sounds_improved(
                self.input_file,
                output_dir,
                onset_threshold_db=onset_threshold_db,
                sustain_threshold_db=sustain_threshold_db,
                min_duration_sec=min_duration_sec,
                padding_sec=padding_sec,
                progress_var=self.progress_var,
                status_label=self.status_label
            )
        finally:
            self.master.after(0, self.processing_complete)


    def processing_complete(self):
        self.process_button.config(state=tk.NORMAL)
        if self.status_label["text"].startswith("Finished"):
            messagebox.showinfo("Complete", "Sound cropping complete!")

# --- Main Execution ---
if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD.Tk() instead of tk.Tk()
    app = SoundCropperApp(root)
    root.mainloop()