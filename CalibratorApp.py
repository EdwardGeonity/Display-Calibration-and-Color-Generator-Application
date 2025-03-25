import os
import glob
import tkinter as tk

# Constants for monitor calibration
CALIBRATION_DIR = 'DisplaySettings'
CALIBRATION_FILE = os.path.join(CALIBRATION_DIR, 'UserDisplayCalibration.txt')

# Constants for phone profile settings
CCT_SETTINGS_DIR = 'CCT_Settings'

# Brightness levels for monitor calibration (name, base_value)
brightness_levels = [
    ("black", 0),
    ("dark gray", 64),
    ("gray", 128),
    ("light gray", 192),
    ("white", 255)
]

# Test colors for stage two (mapping: Display Name -> base value)
test_color_values = {
    "Black": 0,
    "Dark Gray": 64,
    "Gray": 128,
    "Light Gray": 192,
    "White": 255
}

def clamp(value, min_val=0, max_val=255):
    """Clamp the value within the specified range and return an integer."""
    return max(min_val, min(int(round(value)), max_val))

def compute_color(base, wb, tint):
    """
    Compute the final color.
    The white balance (wb) correction increases red and decreases blue;
    the tint correction is applied to the green channel.
    """
    r = clamp(base + wb)
    g = clamp(base + tint)
    b = clamp(base - wb)
    return f'#{r:02x}{g:02x}{b:02x}'

def load_calibration_data():
    """Load monitor calibration data from file."""
    calibration_values = {}
    if os.path.exists(CALIBRATION_FILE):
        with open(CALIBRATION_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    level, params = line.split(':')
                    wb, tint = params.split(',')
                    calibration_values[level.strip().lower()] = {
                        'white_balance': float(wb),
                        'tint': float(tint)
                    }
                except Exception as e:
                    print("Error parsing calibration line:", line, e)
    return calibration_values

def save_calibration_data(calibration_values):
    """Save monitor calibration data to file."""
    if not os.path.exists(CALIBRATION_DIR):
        os.makedirs(CALIBRATION_DIR)
    with open(CALIBRATION_FILE, 'w') as f:
        for level, values in calibration_values.items():
            f.write(f"{level}:{values['white_balance']},{values['tint']}\n")
    print("Monitor calibration saved:", calibration_values)

# ------------------ Calibration Stage ------------------
class CalibrationApp:
    def __init__(self, root, finish_callback):
        """
        root: Tk root window, initially full-screen for calibration.
        finish_callback: function to call after calibration is finished.
        """
        self.root = root
        self.finish_callback = finish_callback
        self.calibration_values = {}
        self.current_index = 0
        self.current_level, self.current_base = brightness_levels[self.current_index]
        self.current_wb = 0.0
        self.current_tint = 0.0
        
        # Set the initial background color for the current level
        self.update_background()
        
        # Create an overlay window with controls (always on top)
        self.overlay = tk.Toplevel(self.root)
        self.overlay.title(f"Calibration: {self.current_level.capitalize()}")
        self.overlay.attributes("-topmost", True)
        self.create_controls()
        self.center_overlay()
    
    def create_controls(self):
        """Create sliders and a 'Next' button for calibration."""
        self.wb_scale = tk.Scale(self.overlay, from_=-50.0, to=50.0, resolution=0.1,
                                 orient=tk.HORIZONTAL, label="White Balance Correction",
                                 length=400, command=self.on_wb_change)
        self.wb_scale.set(0.0)
        self.wb_scale.pack(padx=10, pady=10)
        
        self.tint_scale = tk.Scale(self.overlay, from_=-50.0, to=50.0, resolution=0.1,
                                   orient=tk.HORIZONTAL, label="Tint Correction",
                                   length=400, command=self.on_tint_change)
        self.tint_scale.set(0.0)
        self.tint_scale.pack(padx=10, pady=10)
        
        self.next_button = tk.Button(self.overlay, text="Next", command=self.on_next)
        self.next_button.pack(pady=10)
    
    def center_overlay(self):
        """Center the overlay window on the screen."""
        self.overlay.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        overlay_width = self.overlay.winfo_width()
        overlay_height = self.overlay.winfo_height()
        x = (screen_width - overlay_width) // 2
        y = (screen_height - overlay_height) // 2
        self.overlay.geometry(f"+{x}+{y}")
    
    def on_wb_change(self, val):
        try:
            self.current_wb = float(val)
        except ValueError:
            self.current_wb = 0.0
        self.update_background()
    
    def on_tint_change(self, val):
        try:
            self.current_tint = float(val)
        except ValueError:
            self.current_tint = 0.0
        self.update_background()
    
    def update_background(self):
        """Update the main window's background based on the current calibration settings."""
        color = compute_color(self.current_base, self.current_wb, self.current_tint)
        self.root.configure(bg=color)
    
    def on_next(self):
        """Save current calibration settings and move to the next brightness level or finish calibration."""
        self.calibration_values[self.current_level] = {
            'white_balance': self.current_wb,
            'tint': self.current_tint
        }
        self.current_index += 1
        if self.current_index < len(brightness_levels):
            self.current_level, self.current_base = brightness_levels[self.current_index]
            self.current_wb = 0.0
            self.current_tint = 0.0
            self.wb_scale.set(0.0)
            self.tint_scale.set(0.0)
            self.overlay.title(f"Calibration: {self.current_level.capitalize()}")
            self.update_background()
        else:
            # Calibration finished: save data and call the finish callback
            save_calibration_data(self.calibration_values)
            self.overlay.destroy()
            self.finish_callback(self.calibration_values)

# ------------------ Second Stage Setup ------------------
class StageTwoUI:
    def __init__(self, root, calibration_data):
        """
        root: Main window (should be in windowed mode, maximized).
        calibration_data: Dictionary with monitor calibration data.
        """
        self.root = root
        self.calibration_data = calibration_data
        
        # Set up the control panel as a Toplevel window
        self.panel = tk.Toplevel(self.root)
        self.panel.title("Second Stage Setup")
        self.panel.attributes("-topmost", True)
        
        # Variables for selections and adjustments
        self.test_color_var = tk.StringVar(value="Gray")
        self.phone_file_var = tk.StringVar(value="Select Phone Profile File")
        self.phone_profile_var = tk.StringVar(value="Select Phone Profile")
        self.phone_temp_var = tk.StringVar(value="NA")
        self.user_wb_var = tk.DoubleVar(value=0.0)
        self.user_tint_var = tk.DoubleVar(value=0.0)
        
        # Create UI controls
        self.create_widgets()
        self.load_phone_files()
        self.panel.protocol("WM_DELETE_WINDOW", self.on_finish_setup)
        self.update_background()
    
    def create_widgets(self):
        """Create all UI controls for the second stage."""
        # Test Color Selection (row 0)
        tk.Label(self.panel, text="Test Color:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        test_color_options = list(test_color_values.keys())
        self.test_color_menu = tk.OptionMenu(self.panel, self.test_color_var, *test_color_options, command=self.on_test_color_change)
        self.test_color_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Phone Profile File Selection (row 1)
        tk.Label(self.panel, text="Phone Profile File:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.phone_file_menu = tk.OptionMenu(self.panel, self.phone_file_var, "", command=self.on_phone_file_change)
        self.phone_file_menu.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Phone Profile Selection (row 2)
        tk.Label(self.panel, text="Phone Profile:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.phone_profile_menu = tk.OptionMenu(self.panel, self.phone_profile_var, "", command=self.on_phone_profile_change)
        self.phone_profile_menu.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Temperature (Kelvin) Entry (row 3)
        tk.Label(self.panel, text="Temperature (Kelvin):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.phone_temp_entry = tk.Entry(self.panel, textvariable=self.phone_temp_var)
        self.phone_temp_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # User White Balance Correction slider (row 4)
        tk.Label(self.panel, text="User White Balance Correction:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.user_wb_scale = tk.Scale(self.panel, from_=-50.0, to=50.0, resolution=0.1,
                                      orient=tk.HORIZONTAL, variable=self.user_wb_var,
                                      command=self.on_slider_change, length=300)
        self.user_wb_scale.grid(row=4, column=1, padx=5, pady=5)
        
        # User Tint Correction slider (row 5)
        tk.Label(self.panel, text="User Tint Correction:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.user_tint_scale = tk.Scale(self.panel, from_=-50.0, to=50.0, resolution=0.1,
                                        orient=tk.HORIZONTAL, variable=self.user_tint_var,
                                        command=self.on_slider_change, length=300)
        self.user_tint_scale.grid(row=5, column=1, padx=5, pady=5)
        
        # Button to save changes to the selected profile (row 6)
        self.save_profile_button = tk.Button(self.panel, text="Save changes to profile", command=self.on_save_changes)
        self.save_profile_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        
        # Finish setup button (row 7)
        self.finish_button = tk.Button(self.panel, text="Finish setup", command=self.on_finish_setup)
        self.finish_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
    
    def load_phone_files(self):
        """Load list of phone profile files from the CCT_Settings directory."""
        if not os.path.exists(CCT_SETTINGS_DIR):
            os.makedirs(CCT_SETTINGS_DIR)
        files = glob.glob(os.path.join(CCT_SETTINGS_DIR, "*.txt"))
        file_names = [os.path.basename(f) for f in files]
        menu = self.phone_file_menu["menu"]
        menu.delete(0, "end")
        for name in file_names:
            menu.add_command(label=name, command=lambda value=name: self.phone_file_var.set(value))
        if file_names:
            # Set the first file as default and load its profiles
            self.phone_file_var.set(file_names[0])
            self.load_phone_profiles(file_names[0])
        else:
            self.phone_file_var.set("No files found")
    
    def load_phone_profiles(self, filename):
        """Load phone profiles from the selected file."""
        self.phone_profiles = {}  # Dictionary: profile name -> profile data
        filepath = os.path.join(CCT_SETTINGS_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Expected format: ProfileName | Temperature | WBCorrection | TintCorrection
                    parts = [part.strip() for part in line.split("|")]
                    if len(parts) < 4:
                        continue
                    profile_name, temperature, wb_corr, tint_corr = parts[:4]
                    self.phone_profiles[profile_name] = {
                        'temperature': temperature,
                        'wb_correction': float(wb_corr) if wb_corr not in ["", "NA"] else 0.0,
                        'tint_correction': float(tint_corr) if tint_corr not in ["", "NA"] else 0.0
                    }
            # Update the phone profile OptionMenu
            menu = self.phone_profile_menu["menu"]
            menu.delete(0, "end")
            # Updated lambda to call on_phone_profile_change so the temperature gets updated
            for name in self.phone_profiles.keys():
                menu.add_command(label=name, command=lambda value=name: self.on_phone_profile_change(value))
            if self.phone_profiles:
                first_profile = list(self.phone_profiles.keys())[0]
                self.phone_profile_var.set(first_profile)
                self.on_phone_profile_change(first_profile)
            else:
                self.phone_profile_var.set("No profiles")
    
    def on_test_color_change(self, value):
        self.update_background()
    
    def on_phone_file_change(self, value):
        self.load_phone_profiles(value)
        self.update_background()
    
    def on_phone_profile_change(self, value):
        if value in self.phone_profiles:
            profile = self.phone_profiles[value]
            # Update sliders with the stored corrections from the selected profile
            self.user_wb_var.set(profile['wb_correction'])
            self.user_tint_var.set(profile['tint_correction'])
            # Update the temperature field (even if it's "NA")
            self.phone_temp_var.set(profile['temperature'])
        self.update_background()
    
    def on_slider_change(self, value):
        self.update_background()
    
    def update_background(self):
        """
        Update the main window background based on the test color, monitor calibration,
        phone profile corrections (including temperature) and user corrections.
        """
        # Get test color base value
        test_color_name = self.test_color_var.get()
        base = test_color_values.get(test_color_name, 128)
        
        # Get monitor calibration for the test color (using lowercase key)
        calib = self.calibration_data.get(test_color_name.lower(), {'white_balance': 0.0, 'tint': 0.0})
        monitor_wb = calib['white_balance']
        monitor_tint = calib['tint']
        
        # Get phone profile temperature correction from the entry (if not "NA")
        phone_temp_corr = 0.0
        temp_str = self.phone_temp_var.get().strip()
        if temp_str.upper() != "NA" and temp_str != "":
            try:
                temp_val = float(temp_str)
                # Simple conversion: assume 6500K is neutral; adjust proportionally
                phone_temp_corr = (temp_val - 6500) / 100.0
            except:
                phone_temp_corr = 0.0
        
        # Get user corrections from the sliders
        user_wb = self.user_wb_var.get()
        user_tint = self.user_tint_var.get()
        
        # Compute final corrections
        final_wb = monitor_wb + phone_temp_corr + user_wb
        final_tint = monitor_tint + user_tint
        
        final_color = compute_color(base, final_wb, final_tint)
        self.root.configure(bg=final_color)
    
    def on_save_changes(self):
        """Save the changes to the selected phone profile back to its file."""
        phone_file = self.phone_file_var.get()
        if not phone_file or phone_file in ["No files found"]:
            return
        filepath = os.path.join(CCT_SETTINGS_DIR, phone_file)
        # Read all lines from the file
        lines = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                lines = f.readlines()
        # Update the line corresponding to the selected profile
        selected_profile = self.phone_profile_var.get()
        new_lines = []
        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue
            parts = [part.strip() for part in line_strip.split("|")]
            if len(parts) < 4:
                new_lines.append(line)
                continue
            profile_name = parts[0]
            if profile_name == selected_profile:
                # Build new line with updated corrections and temperature (temperature is taken from the entry)
                temperature = self.phone_temp_var.get().strip()
                new_wb = f"{self.user_wb_var.get():.1f}"
                new_tint = f"{self.user_tint_var.get():.1f}"
                new_line = f"{profile_name} | {temperature} | {new_wb} | {new_tint}\n"
                new_lines.append(new_line)
                # Also update in our internal dictionary
                self.phone_profiles[profile_name]['temperature'] = temperature
                self.phone_profiles[profile_name]['wb_correction'] = float(new_wb)
                self.phone_profiles[profile_name]['tint_correction'] = float(new_tint)
            else:
                new_lines.append(line)
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print("Profile changes saved.")
    
    def on_finish_setup(self):
        """Finish the setup by closing the program."""
        self.panel.destroy()
        self.root.destroy()

def run_stage_two(root, calibration_data):
    """
    Transition to the second stage:
      - Switch the main window from full-screen to a windowed (maximized) mode,
        allowing it to be resized, minimized, or moved.
      - Launch the second stage control panel.
    """
    root.attributes("-fullscreen", False)
    try:
        root.state('zoomed')
    except:
        pass
    root.title("Color Generator - Stage Two")
    StageTwoUI(root, calibration_data)

# ------------------ Main Program ------------------
def main():
    root = tk.Tk()
    # If the monitor calibration file exists and is not empty, load calibration data and run stage two
    if os.path.exists(CALIBRATION_FILE) and os.path.getsize(CALIBRATION_FILE) > 0:
        calibration_data = load_calibration_data()
        run_stage_two(root, calibration_data)
        root.mainloop()
    else:
        # Otherwise, run the calibration stage in full-screen mode then proceed to stage two
        root.attributes("-fullscreen", True)
        def finish_calibration(calib_data):
            run_stage_two(root, calib_data)
        CalibrationApp(root, finish_calibration)
        root.mainloop()

if __name__ == '__main__':
    main()
