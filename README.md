# Display-Calibration-and-Color-Generator-Application
# Display Calibration and Color Generator Application

This Python application provides a two-stage process for monitor calibration and color generation using Tkinter for the GUI. Here's what it does and how to use it:

![Display](https://github.com/user-attachments/assets/4e23421b-fda1-4802-b51c-a1dfe41f7e9b)
![Profiles](https://github.com/user-attachments/assets/7434311c-65db-49c6-a683-f3ec897d4030)

## Purpose
The app helps users:
1. Calibrate their monitor's color display across different brightness levels
2. Generate and adjust colors based on phone profiles and temperature settings

## How It Works

### Stage 1: Monitor Calibration
- Runs in full-screen mode
- Guides users through calibrating 5 brightness levels (black, dark gray, gray, light gray, white)
- For each level, users adjust:
  - White balance (red/blue adjustment)
  - Tint (green adjustment)
- Saves calibration data to `DisplaySettings/UserDisplayCalibration.txt`

### Stage 2: Color Generation
- Runs in windowed (maximized) mode
- Allows users to:
  - Select test colors
  - Choose phone profile files
  - Select specific phone profiles
  - Adjust temperature (Kelvin)
  - Fine-tune white balance and tint
- Saves profile adjustments back to the phone profile files

## Key Features
- Simple slider-based interface
- Persistent storage of calibration and profile data
- Dynamic background color updates
- Phone profile management system

## How to Use It

### First Run (Calibration)
1. Run the script - it will start in full-screen calibration mode
2. For each brightness level:
   - Adjust the sliders until the screen looks neutral
   - Click "Next" to proceed
3. After completing all levels, it automatically transitions to stage two

### Subsequent Runs
- If calibration data exists, it skips directly to stage two
- In stage two:
  - Select a test color to display
  - Choose a phone profile file (from CCT_Settings directory)
  - Select a specific profile
  - Adjust temperature if needed
  - Fine-tune with the sliders
  - Save changes to profiles as needed

## GitHub Upload Instructions

1. **Repository Structure**:
   ```
   DisplayCalibrator/
   ├── DisplaySettings/          (auto-created)
   ├── CCT_Settings/             (auto-created)
   ├── CalibratorApp.py          (main script)
   ├── README.md                 (documentation)
   ├── requirements.txt          (dependencies)
   └── LICENSE                   (choose appropriate license)
   ```

2. **README.md Content**:
   ```markdown
   # Display Calibrator and Color Generator

   A Python application for monitor calibration and color generation.

   ## Features
   - Monitor calibration across 5 brightness levels
   - Phone profile management
   - Temperature-based color adjustments
   - Real-time color preview

   ## Requirements
   - Python 3.x
   - tkinter (usually included with Python)

   ## Installation
   ```
   git clone [your-repo-url]
   cd DisplayCalibrator
   ```

   ## Usage
   Run the application:
   ```
   python CalibratorApp.py
   ```

   Follow the on-screen instructions for calibration and color adjustment.

   ## File Structure
   - `DisplaySettings/`: Stores monitor calibration data
   - `CCT_Settings/`: Stores phone profile data
   ```

3. **requirements.txt**:
   ```
   # Only needed if you add dependencies later
   ```

4. **License**:
   - Choose an appropriate license (MIT is common for open-source projects)
   - Create a LICENSE file with the license text

5. **Upload Process**:
   - Create a new repository on GitHub
   - Initialize locally:
     ```
     git init
     git add .
     git commit -m "Initial commit"
     git remote add origin [your-repo-url]
     git push -u origin master
     ```

## Additional Recommendations
1. Consider adding screenshots to the README
2. Add more detailed usage instructions
3. Include information about the file formats for phone profiles
4. Consider adding error handling for file operations
5. You might want to add a requirements.txt file even if it's empty now, for future dependencies

The application is self-contained and doesn't require external dependencies beyond Python's standard library (tkinter), making it easy to distribute and run.
