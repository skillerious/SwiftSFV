# SwiftSFV

SwiftSFV is a comprehensive GUI application for generating, verifying, and comparing SFV (Simple File Verification) files, comparing files and directories, and ensuring data integrity. Built with Python and PyQt6, SwiftSFV provides an intuitive interface for managing checksums using CRC32, MD5, SHA-1, and other supported algorithms.

![SwiftSFV Logo](images/logo1.png)

**Developer**: [Robin Doak](https://github.com/skillerious)

**Repository URL**: [https://github.com/skillerious/SwiftSFV](https://github.com/skillerious/SwiftSFV)

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Generating SFV Files](#generating-sfv-files)
  - [Verifying SFV Files](#verifying-sfv-files)
  - [Comparing Files or Directories](#comparing-files-or-directories)
  - [History](#history)
  - [Settings and Preferences](#settings-and-preferences)
- [Error Handling](#error-handling)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Generate SFV files**: Create SFV files for selected files or directories using CRC32, MD5, SHA-1, and other supported checksums.
- **Verify SFV files**: Verify the integrity of files against an existing SFV file.
- **Compare files or directories**: Compare two files or directories to check for differences.
- **Drag-and-Drop Interface**: Easily add files and directories via drag-and-drop.
- **Customizable Settings**: Choose default checksum algorithms, default directories, and logging preferences.
- **History tracking**: Keeps a log of previously performed operations, including generated SFV files, verifications, and comparisons.
- **Session Management**: Save and load sessions to continue work at a later time.
- **Multithreading Support**: Performs tasks using threading to keep the UI responsive.
- **Progress Indicators**: Visual progress bars and status messages for long-running tasks.
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux.
- **Modern UI Design**: Intuitive and user-friendly interface with theme support (Dark and Light).

## Requirements

- Python 3.8+
- PyQt6

## Installation

To install the required dependencies, use:

```sh
pip install PyQt6
```

## Usage

To run the application, execute the `main.py` file:

```sh
python main.py
```

### Generating SFV Files

1. **Navigate to "Generate SFV"**
    - On the sidebar, select **Generate SFV**.

2. **Add Files or Folders**
    - **Drag and Drop**: Drag files or folders into the file list area.
    - **Add Files/Folders Button**: Click the **Add Files/Folders** button to select files or directories via a dialog.

3. **Clear Files (Optional)**
    - Use the **Clear Files** button to remove all files from the list.

4. **Generate SFV**
    - Click the **Generate SFV** button. A progress bar will indicate the task's progress.

5. **Save SFV File**
    - Once generation is complete, you will be prompted to save the SFV file. Choose a location and filename.

6. **View Output**
    - The generated SFV content will be displayed in the output area.

### Verifying SFV Files

1. **Navigate to "Verify SFV"**
    - On the sidebar, select **Verify SFV**.

2. **Select SFV File**
    - Click the **Select SFV File** button and choose an existing SFV file.

3. **Verify SFV**
    - After selecting the SFV file, click the **Verify SFV** button. The application will verify each file listed in the SFV file.

4. **View Results**
    - The verification results will be displayed in the output area, indicating if files are OK, mismatched, or missing.

### Comparing Files or Directories

1. **Navigate to "Compare Files"**
    - On the sidebar, select **Compare Files**.

2. **Select Paths**
    - **Path 1**: Use the **Select Path 1** button to choose the first file or directory.
    - **Path 2**: Use the **Select Path 2** button to choose the second file or directory.

3. **Compare**
    - Click the **Compare** button to start the comparison.

4. **View Comparison Results**
    - The output area will display whether the files or directories are identical or list the differences.

### History

- **View History**
  - Navigate to the **History** section to view a log of all generated SFV files, verifications, and comparisons.
- **Clear History**
  - Use the **Clear History** button to remove all history entries.
- **Copy to Clipboard**
  - Copy the history entries to the clipboard for reference.

### Settings and Preferences

Access the settings by clicking on **Settings > Preferences** in the menu bar.

- **Default Checksum Algorithm**: Choose between CRC32, MD5, SHA-1, and other available algorithms.
- **Theme**: Switch between Dark and Light themes.
- **Default Directory**: Set a default directory for file dialogs.
- **Enable Logging**: Toggle logging of verification results.
- **Log File Path**: Specify the path where log files will be saved.

After adjusting settings, click **Save** to apply changes.

## Screenshots

[![Screenshot-2024-10-13-123924.png](https://i.postimg.cc/WzWh2CV7/Screenshot-2024-10-13-123924.png)](https://postimg.cc/PvDty6PL)

[![Screenshot-2024-10-13-124226.png](https://i.postimg.cc/L5b8dPkC/Screenshot-2024-10-13-124226.png)](https://postimg.cc/kRWmKBpK)

[![Screenshot-2024-10-13-194342.png](https://i.postimg.cc/WbqFbJc0/Screenshot-2024-10-13-194342.png)](https://postimg.cc/SJqNgRsK)

[![Screenshot-2024-10-13-194328.png](https://i.postimg.cc/qvfttMpS/Screenshot-2024-10-13-194328.png)](https://postimg.cc/0bf5FvM0)

## Error Handling

SwiftSFV includes a global exception handler for any unexpected issues. Errors are logged to a file (`sfv_checker_debug.log`) and also displayed in a message box.

## Development

The project uses a modular structure to ensure the separation of GUI, logic, and background tasks.

- **`ChecksumTask`**: A background task for generating SFV files.
- **`VerificationTask`**: A background task for verifying the contents of an SFV file.
- **`CompareTask`**: A background task for comparing two files or directories.

### Contributing

Contributions are welcome! Feel free to submit issues or pull requests for improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any inquiries, you can reach out via the GitHub repository: [https://github.com/skillerious/swiftsfv](https://github.com/skillerious/swiftsfv)

---

**Note**: Ensure you have a directory called `images` containing appropriate icons (`generate.png`, `verify.png`, `compare.png`, etc.) for use in the application. Missing icons will be indicated by warnings in the application log.
