# SwiftSFV

A comprehensive GUI application for generating and verifying SFV (Simple File Verification) files, comparing files and directories, and ensuring data integrity. Built with Python and PyQt6, SwiftSFV provides an intuitive interface for managing checksums using CRC32, MD5, or SHA1 algorithms.

![SwiftSFV Logo](images/app_icon.png)

**Developer**: [Robin Doak](https://github.com/skillerious)

**Repository URL**: [https://github.com/skillerious/SwiftSFV](https://github.com/skillerious/SwiftSFV)

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Generating SFV Files](#generating-sfv-files)
  - [Verifying SFV Files](#verifying-sfv-files)
  - [Comparing Files or Directories](#comparing-files-or-directories)
  - [Settings and Preferences](#settings-and-preferences)
  - [Session Management](#session-management)
  - [Keyboard Shortcuts](#keyboard-shortcuts)
- [Customization](#customization)
  - [Themes](#themes)
  - [Checksum Algorithms](#checksum-algorithms)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Generate SFV Files**: Create SFV files for selected files or directories using CRC32, MD5, or SHA1 checksums.
- **Verify SFV Files**: Verify the integrity of files against an existing SFV file.
- **Compare Files or Directories**: Compare two files or directories to check for differences.
- **Drag-and-Drop Interface**: Easily add files and directories via drag-and-drop.
- **Customizable Settings**: Choose default checksum algorithms, themes (Dark or Light), default directories, and logging preferences.
- **Session Management**: Save and load sessions to continue work at a later time.
- **Multithreading Support**: Performs tasks using threading to keep the UI responsive.
- **Progress Indicators**: Visual progress bars and status messages for long-running tasks.
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux.
- **Modern UI Design**: Intuitive and user-friendly interface with theme support.

## Screenshots

### Generate SFV Files

![Generate SFV](screenshots/generate_sfv.png)

### Verify SFV Files

![Verify SFV](screenshots/verify_sfv.png)

### Compare Files or Directories

![Compare Files](screenshots/compare_files.png)

### Settings Dialog

![Settings](screenshots/settings_dialog.png)

*Note: If the images are not visible, please check the "screenshots" folder in the repository.*

## Prerequisites

- **Python 3.7 or higher**
- **PyQt6 library**
- **Additional Python Modules**:
  - `zlib`
  - `hashlib`
  - `pickle`

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/skillerious/SwiftSFV.git
   cd SwiftSFV
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use 'venv\Scripts\activate'
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If `requirements.txt` is not provided, install PyQt6 manually:

   ```bash
   pip install PyQt6
   ```

4. **Run the Application**

   ```bash
   python SwiftSFV.py
   ```

   Replace `SwiftSFV.py` with the actual filename if different.

## Usage

### Generating SFV Files

1. **Navigate to "Generate SFV"**

   On the sidebar, select **Generate SFV**.

2. **Add Files or Folders**

   - **Drag and Drop**: Drag files or folders into the file list area.
   - **Add Files/Folders Button**: Click the **Add Files/Folders** button to select files or directories via a dialog.

3. **Clear Files (Optional)**

   Use the **Clear Files** button to remove all files from the list.

4. **Generate SFV**

   Click the **Generate SFV** button. A progress bar will indicate the task's progress.

5. **Save SFV File**

   Once generation is complete, you will be prompted to save the SFV file. Choose a location and filename.

6. **View Output**

   The generated SFV content will be displayed in the output area.

### Verifying SFV Files

1. **Navigate to "Verify SFV"**

   On the sidebar, select **Verify SFV**.

2. **Select SFV File**

   Click the **Select SFV File** button and choose an existing SFV file.

3. **Verify SFV**

   After selecting the SFV file, click the **Verify SFV** button. The application will verify each file listed in the SFV file.

4. **View Results**

   The verification results will be displayed in the output area, indicating if files are OK, mismatched, or missing.

### Comparing Files or Directories

1. **Navigate to "Compare Files"**

   On the sidebar, select **Compare Files**.

2. **Select Paths**

   - **Path 1**: Use the **Select Path 1** button to choose the first file or directory.
   - **Path 2**: Use the **Select Path 2** button to choose the second file or directory.

3. **Compare**

   Click the **Compare** button to start the comparison.

4. **View Comparison Results**

   The output area will display whether the files or directories are identical or list the differences.

### Settings and Preferences

Access the settings by clicking on **Settings > Preferences** in the menu bar.

- **Default Checksum Algorithm**: Choose between CRC32, MD5, or SHA1.
- **Theme**: Switch between Dark and Light themes.
- **Default Directory**: Set a default directory for file dialogs.
- **Enable Logging**: Toggle logging of verification results.
- **Log File Path**: Specify the path where log files will be saved.

After adjusting settings, click **Save** to apply changes.

### Session Management

- **Save Session**

  - Go to **Session > Save Session**.
  - Choose a location and filename to save the current session, which includes the file list and selected SFV file.

- **Load Session**

  - Go to **Session > Load Session**.
  - Select a previously saved session file to restore the state.

### Keyboard Shortcuts

- **Add Files/Folders**: `Ctrl + O`
- **Generate SFV**: `Ctrl + G`
- **Verify SFV**: `Ctrl + V`
- **Compare Files**: `Ctrl + C`
- **Open Settings**: `Ctrl + S`
- **Save Session**: `Ctrl + Shift + S`
- **Load Session**: `Ctrl + L`

## Customization

### Themes

SwiftSFV supports Dark and Light themes. You can switch between them in the **Settings** dialog.

- **Dark Theme**: Ideal for low-light environments, reduces eye strain.
- **Light Theme**: Classic appearance with high contrast.

### Checksum Algorithms

Choose your preferred checksum algorithm based on your requirements:

- **CRC32**: Fast but less secure, commonly used for error-checking.
- **MD5**: Moderate speed, better for ensuring data integrity.
- **SHA1**: Slower but more secure, suitable for critical data verification.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

   Click the **Fork** button at the top-right corner of the repository page.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/SwiftSFV.git
   cd SwiftSFV
   ```

3. **Create a Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**

   Implement your feature or bug fix.

5. **Commit Changes**

   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

   Go to the original repository and click **New Pull Request**.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- **PyQt6**: For the powerful GUI framework.
- **Open Source Community**: For the inspiration and continuous support.
- **Contributors**: Thanks to everyone who has contributed to the project.

---

**Disclaimer**: This application is provided "as is" without warranty of any kind. Use at your own risk.
