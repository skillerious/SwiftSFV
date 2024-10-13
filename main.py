# main.py

import sys
import os
import hashlib
import zlib
import csv
import logging
import time

from PyQt6.QtCore import (
    Qt, QRunnable, QThreadPool, pyqtSlot, QObject, pyqtSignal
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout,
    QLabel, QPushButton, QTextEdit, QProgressBar,
    QMessageBox, QFileDialog, QLineEdit, QHBoxLayout, QCheckBox,
    QComboBox, QSizePolicy, QSpacerItem, QListWidget, QStackedWidget
)
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont, QAction

from settings import AppSettings
from settings_dialog import SettingsDialog

# Configure Logging
logging.basicConfig(
    filename='sfv_checker_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global Exception Handler
def exception_hook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(None, "Critical Error", f"An unexpected error occurred:\n{exc_value}")
    sys.exit(1)

sys.excepthook = exception_hook

# Signals Class for Tasks
class Signals(QObject):
    progress = pyqtSignal(int)  # Emitting progress percentage
    message = pyqtSignal(str)   # Emitting messages/status updates
    result = pyqtSignal(object) # Emitting results (e.g., SFV content, verification results)
    finished = pyqtSignal()     # Emitting when task is finished

# ChecksumTask for Generating SFV
class ChecksumTask(QRunnable):
    def __init__(self, files, algorithm):
        super().__init__()
        self.files = files
        self.algorithm = algorithm
        self.signals = Signals()
        logging.debug(f"Initialized ChecksumTask with {len(self.files)} files using {self.algorithm} algorithm.")
    
    @pyqtSlot()
    def run(self):
        logging.debug("ChecksumTask.run() started.")
        if not self.files:
            logging.warning("No files to process.")
            self.signals.message.emit("No files to process.")
            self.signals.finished.emit()
            return
        
        sfv_content = ""
        total_files = len(self.files)
        
        for idx, file in enumerate(self.files, 1):
            try:
                file_path = os.path.abspath(file)
                logging.debug(f"Processing file: {file_path}")
                
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                if not os.path.isfile(file_path):
                    raise ValueError(f"Path is not a file: {file_path}")
                
                checksum = self.calculate_checksum(file_path)
                logging.debug(f"Calculated checksum: {checksum} for file: {file_path}")
                
                relative_path = os.path.relpath(file_path)
                sfv_entry = f"{relative_path} {checksum}\n"
                sfv_content += sfv_entry
                
                # Emit progress
                progress = int((idx / total_files) * 100)
                self.signals.progress.emit(progress)
                self.signals.message.emit(f"Processed {idx}/{total_files}: {relative_path}")
                
            except Exception as e:
                logging.error(f"Error processing {file}: {e}")
                sfv_entry = f"{os.path.basename(file)} ERROR: {e}\n"
                sfv_content += sfv_entry
                # Still emit progress
                progress = int((idx / total_files) * 100)
                self.signals.progress.emit(progress)
                self.signals.message.emit(f"Error processing {file}: {e}")
        
        # Emit the final SFV content
        self.signals.result.emit(sfv_content)
        logging.debug("ChecksumTask.run() completed. Emitting result and finished signals.")
        self.signals.finished.emit()
    
    def calculate_checksum(self, file_path):
        logging.debug(f"Calculating checksum for {file_path} using {self.algorithm}")
        if self.algorithm == 'CRC32':
            try:
                checksum = 0
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        checksum = zlib.crc32(chunk, checksum)
                return f"{checksum & 0xFFFFFFFF:08X}"
            except Exception as e:
                logging.error(f"Error calculating CRC32 for {file_path}: {e}")
                return 'ERROR'
        else:
            hash_obj = getattr(hashlib, self.algorithm.lower(), None)
            if not hash_obj:
                logging.error(f"Unsupported algorithm: {self.algorithm}")
                return 'UNKNOWN_ALGORITHM'
            hash_instance = hash_obj()
            try:
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        hash_instance.update(chunk)
                return hash_instance.hexdigest().upper()
            except Exception as e:
                logging.error(f"Error reading file {file_path} for checksum calculation: {e}")
                return 'ERROR'

# VerificationTask for Verifying SFV
class VerificationTask(QRunnable):
    def __init__(self, sfv_file, algorithm, log_enabled, log_file_path, log_format='TXT'):
        super().__init__()
        self.sfv_file = sfv_file
        self.algorithm = algorithm
        self.log_enabled = log_enabled
        self.log_file_path = log_file_path
        self.log_format = log_format
        self.signals = Signals()
        logging.debug(f"Initialized VerificationTask for SFV file: {self.sfv_file} with algorithm: {self.algorithm}")
    
    @pyqtSlot()
    def run(self):
        try:
            logging.debug("VerificationTask.run() started.")
            with open(self.sfv_file, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            logging.error(f"Failed to open SFV file: {e}")
            self.signals.result.emit(f"Failed to open SFV file: {e}")
            self.signals.finished.emit()
            return
    
        total_files = len(lines)
        if total_files == 0:
            self.signals.message.emit("SFV file is empty.")
            self.signals.finished.emit()
            return
    
        results = []
        output = ''
        for idx, line in enumerate(lines, 1):
            parts = line.rstrip().rsplit(' ', 1)
            if len(parts) != 2:
                output += f"Invalid line in SFV: {line}\n"
                results.append({'filename': parts[0] if parts else 'Unknown', 'status': 'Invalid line'})
                self.update_progress(idx, total_files)
                continue
            filename, expected_checksum = parts
    
            file_path = os.path.abspath(filename)
            if not os.path.isfile(file_path):
                output += f"{filename}: File not found\n"
                results.append({'filename': filename, 'status': 'File not found'})
                self.update_progress(idx, total_files)
                continue
            try:
                checksum = self.calculate_checksum(file_path)
                logging.debug(f"Expected Checksum: {expected_checksum}")
                logging.debug(f"Actual Checksum: {checksum}")
                if checksum.upper() == expected_checksum.upper():
                    output += f"{filename}: OK\n"
                    results.append({'filename': filename, 'status': 'OK'})
                else:
                    output += f"{filename}: MISMATCH (Expected {expected_checksum}, Got {checksum})\n"
                    results.append({'filename': filename, 'status': 'MISMATCH'})
                self.update_progress(idx, total_files)
            except Exception as e:
                output += f"{filename}: ERROR {e}\n"
                results.append({'filename': filename, 'status': f'ERROR {e}'})
                self.update_progress(idx, total_files)
    
        self.signals.result.emit(results)
        if self.log_enabled:
            self.save_log(output)
        self.signals.finished.emit()
        logging.debug("VerificationTask.run() completed. Emitting result and finished signals.")
    
    def calculate_checksum(self, file_path):
        logging.debug(f"Calculating checksum for {file_path} using {self.algorithm}")
        if self.algorithm == 'CRC32':
            try:
                checksum = 0
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        checksum = zlib.crc32(chunk, checksum)
                return f"{checksum & 0xFFFFFFFF:08X}"
            except Exception as e:
                logging.error(f"Error calculating CRC32 for {file_path}: {e}")
                return 'ERROR'
        else:
            hash_obj = getattr(hashlib, self.algorithm.lower(), None)
            if not hash_obj:
                logging.error(f"Unsupported algorithm: {self.algorithm}")
                return 'UNKNOWN_ALGORITHM'
            hash_instance = hash_obj()
            try:
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        hash_instance.update(chunk)
                return hash_instance.hexdigest().upper()
            except Exception as e:
                logging.error(f"Error reading file {file_path} for checksum calculation: {e}")
                return 'ERROR'
    
    def save_log(self, content):
        try:
            if self.log_format == 'CSV':
                with open(self.log_file_path, 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(['Filename', 'Status'])
                    for line in content.splitlines():
                        if ' ERROR' in line or 'MISMATCH' in line or 'File not found' in line or 'Invalid line' in line:
                            parts = line.split(':', 1)
                            filename = parts[0]
                            status = parts[1].strip() if len(parts) > 1 else 'Error'
                            writer.writerow([filename, status])
                        else:
                            parts = line.split(' ', 1)
                            filename = parts[0]
                            status = parts[1] if len(parts) > 1 else 'OK'
                            writer.writerow([filename, status])
            else:
                with open(self.log_file_path, 'w') as log_file:
                    log_file.write(content)
            self.signals.message.emit(f"Log saved to {self.log_file_path}")
            logging.info(f"Log saved to {self.log_file_path}")
        except Exception as e:
            self.signals.message.emit(f"Failed to save log: {e}")
            logging.error(f"Failed to save log: {e}")
    
    def update_progress(self, current, total):
        progress = int((current / total) * 100)
        self.signals.progress.emit(progress)
        self.signals.message.emit(f"Verifying {current}/{total} files...")

# CompareTask for Comparing Files/Directories
class CompareTask(QRunnable):
    def __init__(self, path1, path2, algorithm):
        super().__init__()
        self.path1 = path1
        self.path2 = path2
        self.algorithm = algorithm
        self.signals = Signals()
        logging.debug(f"Initialized CompareTask to compare {self.path1} and {self.path2} using {self.algorithm} algorithm.")
    
    @pyqtSlot()
    def run(self):
        self.signals.message.emit("Comparing files/directories...")
        logging.debug("CompareTask.run() started.")
        if os.path.isfile(self.path1) and os.path.isfile(self.path2):
            result = self.compare_files(self.path1, self.path2)
        elif os.path.isdir(self.path1) and os.path.isdir(self.path2):
            result = self.compare_directories(self.path1, self.path2)
        else:
            result = "Both paths must be either files or directories."
            logging.warning("Comparison paths mismatch: one is file, other is directory.")
            self.signals.message.emit(result)
            self.signals.finished.emit()
            return
    
        self.signals.result.emit(result)
        self.signals.finished.emit()
        logging.debug("CompareTask.run() completed. Emitting result and finished signals.")
    
    def compare_files(self, file1, file2):
        try:
            checksum1 = self.calculate_checksum(file1)
            checksum2 = self.calculate_checksum(file2)
            logging.debug(f"Checksum1: {checksum1}")
            logging.debug(f"Checksum2: {checksum2}")
            if checksum1 == checksum2:
                return "Files are identical."
            else:
                return f"Files differ.\nChecksum1: {checksum1}\nChecksum2: {checksum2}"
        except Exception as e:
            logging.error(f"Error comparing files: {e}")
            return f"Error comparing files: {e}"
    
    def compare_directories(self, dir1, dir2):
        try:
            files1 = self.get_files(dir1)
            files2 = self.get_files(dir2)
            common_files = set(files1.keys()).intersection(set(files2.keys()))
            differences = []
            for file in common_files:
                if files1[file] != files2[file]:
                    differences.append(f"File {file} differs.")
            unique_to_dir1 = set(files1.keys()) - set(files2.keys())
            unique_to_dir2 = set(files2.keys()) - set(files1.keys())
            if unique_to_dir1:
                differences.extend([f"File {file} only in {dir1}" for file in unique_to_dir1])
            if unique_to_dir2:
                differences.extend([f"File {file} only in {dir2}" for file in unique_to_dir2])
            if differences:
                return "\n".join(differences)
            else:
                return "Directories are identical."
        except Exception as e:
            logging.error(f"Error comparing directories: {e}")
            return f"Error comparing directories: {e}"
    
    def get_files(self, directory):
        file_checksums = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    checksum = self.calculate_checksum(filepath)
                    relative_path = os.path.relpath(filepath, directory)
                    file_checksums[relative_path] = checksum
                except Exception:
                    file_checksums[relative_path] = 'ERROR'
        return file_checksums
    
    def calculate_checksum(self, file_path):
        logging.debug(f"Calculating checksum for file: {file_path} using {self.algorithm}")
        if self.algorithm == 'CRC32':
            try:
                checksum = 0
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        checksum = zlib.crc32(chunk, checksum)
                return f"{checksum & 0xFFFFFFFF:08X}"
            except Exception as e:
                logging.error(f"Error calculating CRC32 for {file_path}: {e}")
                return 'ERROR'
        else:
            hash_obj = getattr(hashlib, self.algorithm.lower(), None)
            if not hash_obj:
                logging.error(f"Unsupported algorithm: {self.algorithm}")
                return 'UNKNOWN_ALGORITHM'
            hash_instance = hash_obj()
            try:
                with open(file_path, 'rb') as f:
                    while chunk := f.read(4096):
                        hash_instance.update(chunk)
                return hash_instance.hexdigest().upper()
            except Exception as e:
                logging.error(f"Error reading file {file_path} for checksum calculation: {e}")
                return 'ERROR'

# VerificationResultDialog Class
class VerificationResultDialog(QMessageBox):
    def __init__(self, verification_results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verification Results")
        self.setIcon(QMessageBox.Icon.Information)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        ok_count = sum(1 for result in verification_results if result['status'] == 'OK')
        mismatch_count = sum(1 for result in verification_results if result['status'] == 'MISMATCH')
        error_count = sum(1 for result in verification_results if result['status'].startswith('ERROR'))
        not_found_count = sum(1 for result in verification_results if result['status'] == 'File not found')
        invalid_line_count = sum(1 for result in verification_results if result['status'] == 'Invalid line')
        
        summary = f"""
        <b>Verification Completed:</b><br>
        <ul>
            <li>OK: {ok_count}</li>
            <li>MISMATCH: {mismatch_count}</li>
            <li>File Not Found: {not_found_count}</li>
            <li>Errors: {error_count}</li>
            <li>Invalid Lines: {invalid_line_count}</li>
        </ul>
        """
        self.setText(summary)
        detailed_text = "<br>".join([f"{item['filename']}: {item['status']}" for item in verification_results])
        self.setDetailedText(detailed_text)

# SFVApp Main Window
class SFVApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.load_settings()
        self.init_ui()
        self.history = []
        self.load_history()
        self.threadpool = QThreadPool.globalInstance()
        logging.debug("SFVApp initialized.")
    
    def init_ui(self):
        self.setWindowTitle("SwiftSFV")
        self.resize(1000, 700)
        
        # Apply Dark Theme
        self.apply_dark_theme()
        
        # Determine the base directory and images directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(base_dir, 'images')
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create side menu with icons
        self.side_menu = QFrame()
        self.side_menu.setFixedWidth(200)
        self.side_menu.setStyleSheet("background-color: #34495e;")
        side_menu_layout = QVBoxLayout()
        side_menu_layout.setContentsMargins(0, 0, 0, 0)
        side_menu_layout.setSpacing(0)
        self.side_menu.setLayout(side_menu_layout)
        
        # Define button properties
        button_style = """
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d566e;
            }
            QPushButton:checked {
                background-color: #2c3e50;
            }
        """
        
        # Initialize navigation buttons with icons from 'images' folder
        self.btn_generate = QPushButton("  Generate SFV")
        generate_icon_path = os.path.join(images_dir, 'generate.png')
        if os.path.exists(generate_icon_path):
            self.btn_generate.setIcon(QIcon(generate_icon_path))
        else:
            logging.warning(f"Icon not found: {generate_icon_path}")
            self.btn_generate.setIcon(QIcon())  # Set no icon or a default icon
        self.btn_generate.setCheckable(True)
        self.btn_generate.setStyleSheet(button_style)
        self.btn_generate.clicked.connect(lambda: self.display_page(0))
        side_menu_layout.addWidget(self.btn_generate)
        
        self.btn_verify = QPushButton("  Verify SFV")
        verify_icon_path = os.path.join(images_dir, 'verify.png')
        if os.path.exists(verify_icon_path):
            self.btn_verify.setIcon(QIcon(verify_icon_path))
        else:
            logging.warning(f"Icon not found: {verify_icon_path}")
            self.btn_verify.setIcon(QIcon())
        self.btn_verify.setCheckable(True)
        self.btn_verify.setStyleSheet(button_style)
        self.btn_verify.clicked.connect(lambda: self.display_page(1))
        side_menu_layout.addWidget(self.btn_verify)
        
        self.btn_compare = QPushButton("  Compare Files")
        compare_icon_path = os.path.join(images_dir, 'compare.png')
        if os.path.exists(compare_icon_path):
            self.btn_compare.setIcon(QIcon(compare_icon_path))
        else:
            logging.warning(f"Icon not found: {compare_icon_path}")
            self.btn_compare.setIcon(QIcon())
        self.btn_compare.setCheckable(True)
        self.btn_compare.setStyleSheet(button_style)
        self.btn_compare.clicked.connect(lambda: self.display_page(2))
        side_menu_layout.addWidget(self.btn_compare)
        
        self.btn_history = QPushButton("  History")
        history_icon_path = os.path.join(images_dir, 'history.png')
        if os.path.exists(history_icon_path):
            self.btn_history.setIcon(QIcon(history_icon_path))
        else:
            logging.warning(f"Icon not found: {history_icon_path}")
            self.btn_history.setIcon(QIcon())
        self.btn_history.setCheckable(True)
        self.btn_history.setStyleSheet(button_style)
        self.btn_history.clicked.connect(lambda: self.display_page(3))
        side_menu_layout.addWidget(self.btn_history)
        
        # Spacer to push the settings button to the bottom
        side_menu_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.btn_settings = QPushButton("  Settings")
        settings_icon_path = os.path.join(images_dir, 'settings.png')
        if os.path.exists(settings_icon_path):
            self.btn_settings.setIcon(QIcon(settings_icon_path))
        else:
            logging.warning(f"Icon not found: {settings_icon_path}")
            self.btn_settings.setIcon(QIcon())
        self.btn_settings.setStyleSheet(button_style)
        self.btn_settings.clicked.connect(self.open_settings_dialog)
        side_menu_layout.addWidget(self.btn_settings)
        
        main_layout.addWidget(self.side_menu)
        
        # Create stacked widget for main content
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.create_generate_page(images_dir)
        self.create_verify_page(images_dir)
        self.create_compare_page(images_dir)
        self.create_history_page(images_dir)
        
        # Set initial page
        self.display_page(0)
    
    def apply_dark_theme(self):
        dark_palette = QPalette()

        # Base colors
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

        # Link colors
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        QApplication.instance().setPalette(dark_palette)
        QApplication.instance().setStyle("Fusion")
    
    def create_generate_page(self, images_dir):
        generate_page = QWidget()
        layout = QVBoxLayout()
        generate_page.setLayout(layout)
        
        # File List
        self.file_list_generate = QListWidget()
        self.file_list_generate.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: white;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(QLabel("Files to Generate SFV:"))
        layout.addWidget(self.file_list_generate)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_files_button = QPushButton("Add Files/Folders")
        document_icon_path = os.path.join(images_dir, 'document.png')  # Ensure 'document.png' exists
        if os.path.exists(document_icon_path):
            add_files_button.setIcon(QIcon(document_icon_path))
        else:
            logging.warning(f"Icon not found: {document_icon_path}")
            add_files_button.setIcon(QIcon())
        add_files_button.clicked.connect(self.add_files_generate)
        
        clear_files_button = QPushButton("Clear Files")
        clear_icon_path = os.path.join(images_dir, 'clear_icon.png')  # Ensure 'clear_icon.png' exists
        if os.path.exists(clear_icon_path):
            clear_files_button.setIcon(QIcon(clear_icon_path))
        else:
            logging.warning(f"Icon not found: {clear_icon_path}")
            clear_files_button.setIcon(QIcon())
        clear_files_button.clicked.connect(self.clear_files_generate)
        
        generate_button = QPushButton("Generate SFV")
        generate_icon_path = os.path.join(images_dir, 'generate.png')  # Ensure 'generate.png' exists
        if os.path.exists(generate_icon_path):
            generate_button.setIcon(QIcon(generate_icon_path))
        else:
            logging.warning(f"Icon not found: {generate_icon_path}")
            generate_button.setIcon(QIcon())
        generate_button.clicked.connect(self.generate_sfv)
        
        button_layout.addWidget(add_files_button)
        button_layout.addWidget(clear_files_button)
        button_layout.addWidget(generate_button)
        layout.addLayout(button_layout)
        
        # Output Area
        self.output_area_generate = QTextEdit()
        self.output_area_generate.setReadOnly(True)
        self.output_area_generate.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                color: white;
            }
        """)
        layout.addWidget(QLabel("SFV Content:"))
        layout.addWidget(self.output_area_generate)
        
        # Progress Bar
        self.progress_bar_generate = QProgressBar()
        self.progress_bar_generate.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2980b9;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress_bar_generate)
        
        self.stacked_widget.addWidget(generate_page)
    
    def create_verify_page(self, images_dir):
        verify_page = QWidget()
        layout = QVBoxLayout()
        verify_page.setLayout(layout)
        
        # Select SFV File
        select_layout = QHBoxLayout()
        self.selected_sfv_label = QLabel("No SFV file selected.")
        self.selected_sfv_label.setStyleSheet("color: white;")
        select_sfv_button = QPushButton("Select SFV File")
        verify_icon_path = os.path.join(images_dir, 'verify.png')  # Ensure 'verify.png' exists
        if os.path.exists(verify_icon_path):
            select_sfv_button.setIcon(QIcon(verify_icon_path))
        else:
            logging.warning(f"Icon not found: {verify_icon_path}")
            select_sfv_button.setIcon(QIcon())
        select_sfv_button.clicked.connect(self.select_sfv_file)
        verify_button = QPushButton("Verify SFV")
        if os.path.exists(verify_icon_path):
            verify_button.setIcon(QIcon(verify_icon_path))
        else:
            logging.warning(f"Icon not found: {verify_icon_path}")
            verify_button.setIcon(QIcon())
        verify_button.clicked.connect(lambda: self.verify_sfv(auto=False))
        self.verify_button = verify_button
        self.verify_button.setEnabled(False)
        select_layout.addWidget(self.selected_sfv_label)
        select_layout.addWidget(select_sfv_button)
        select_layout.addWidget(verify_button)
        layout.addLayout(select_layout)
        
        # Output Area
        self.output_area_verify = QTextEdit()
        self.output_area_verify.setReadOnly(True)
        self.output_area_verify.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                color: white;
            }
        """)
        layout.addWidget(QLabel("Verification Results:"))
        layout.addWidget(self.output_area_verify)
        
        # Progress Bar
        self.progress_bar_verify = QProgressBar()
        self.progress_bar_verify.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2980b9;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress_bar_verify)
        
        self.stacked_widget.addWidget(verify_page)
    
    def create_compare_page(self, images_dir):
        compare_page = QWidget()
        layout = QVBoxLayout()
        compare_page.setLayout(layout)
        
        # Paths to Compare
        path1_layout = QHBoxLayout()
        self.path1_edit = QLineEdit()
        self.path1_edit.setPlaceholderText("Select Path 1")
        path1_button = QPushButton("Browse")
        document_icon_path = os.path.join(images_dir, 'document.png')  # Ensure 'document.png' exists
        if os.path.exists(document_icon_path):
            path1_button.setIcon(QIcon(document_icon_path))
        else:
            logging.warning(f"Icon not found: {document_icon_path}")
            path1_button.setIcon(QIcon())
        path1_button.clicked.connect(lambda: self.browse_path(self.path1_edit))
        path1_layout.addWidget(QLabel("Path 1:"))
        path1_layout.addWidget(self.path1_edit)
        path1_layout.addWidget(path1_button)
        layout.addLayout(path1_layout)
        
        path2_layout = QHBoxLayout()
        self.path2_edit = QLineEdit()
        self.path2_edit.setPlaceholderText("Select Path 2")
        path2_button = QPushButton("Browse")
        if os.path.exists(document_icon_path):
            path2_button.setIcon(QIcon(document_icon_path))
        else:
            logging.warning(f"Icon not found: {document_icon_path}")
            path2_button.setIcon(QIcon())
        path2_button.clicked.connect(lambda: self.browse_path(self.path2_edit))
        path2_layout.addWidget(QLabel("Path 2:"))
        path2_layout.addWidget(self.path2_edit)
        path2_layout.addWidget(path2_button)
        layout.addLayout(path2_layout)
        
        # Compare Button
        compare_button = QPushButton("Compare")
        compare_icon_path = os.path.join(images_dir, 'compare.png')  # Ensure 'compare.png' exists
        if os.path.exists(compare_icon_path):
            compare_button.setIcon(QIcon(compare_icon_path))
        else:
            logging.warning(f"Icon not found: {compare_icon_path}")
            compare_button.setIcon(QIcon())
        compare_button.clicked.connect(self.compare_files)
        layout.addWidget(compare_button)
        
        # Output Area
        self.output_area_compare = QTextEdit()
        self.output_area_compare.setReadOnly(True)
        self.output_area_compare.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                color: white;
            }
        """)
        layout.addWidget(QLabel("Comparison Results:"))
        layout.addWidget(self.output_area_compare)
        
        # Progress Bar
        self.progress_bar_compare = QProgressBar()
        self.progress_bar_compare.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2980b9;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress_bar_compare)
        
        self.stacked_widget.addWidget(compare_page)
    
    def create_history_page(self, images_dir):
        history_page = QWidget()
        layout = QVBoxLayout()
        history_page.setLayout(layout)
        
        # History List
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: white;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(QLabel("History:"))
        layout.addWidget(self.history_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        history_icon_path = os.path.join(images_dir, 'history.png')  # Ensure 'history.png' exists
        clear_history_button = QPushButton("Clear History")
        if os.path.exists(history_icon_path):
            clear_history_button.setIcon(QIcon(history_icon_path))
        else:
            logging.warning(f"Icon not found: {history_icon_path}")
            clear_history_button.setIcon(QIcon())
        clear_history_button.clicked.connect(self.clear_history)
        
        copy_history_button = QPushButton("Copy to Clipboard")
        if os.path.exists(history_icon_path):
            copy_history_button.setIcon(QIcon(history_icon_path))
        else:
            logging.warning(f"Icon not found: {history_icon_path}")
            copy_history_button.setIcon(QIcon())
        copy_history_button.clicked.connect(lambda: self.copy_to_clipboard(self.history_list))
        
        button_layout.addWidget(clear_history_button)
        button_layout.addWidget(copy_history_button)
        layout.addLayout(button_layout)
        
        self.stacked_widget.addWidget(history_page)
    
    def display_page(self, index):
        # Uncheck all buttons first
        self.btn_generate.setChecked(False)
        self.btn_verify.setChecked(False)
        self.btn_compare.setChecked(False)
        self.btn_history.setChecked(False)
        # Check the selected button
        if index == 0:
            self.btn_generate.setChecked(True)
        elif index == 1:
            self.btn_verify.setChecked(True)
        elif index == 2:
            self.btn_compare.setChecked(True)
        elif index == 3:
            self.btn_history.setChecked(True)
        self.stacked_widget.setCurrentIndex(index)
    
    # Methods for Generate SFV Page
    def add_files_generate(self):
        options = QFileDialog.Option.ReadOnly | QFileDialog.Option.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Generate SFV", self.default_dir or os.getcwd(), "All Files (*)", options=options
        )
        folders = QFileDialog.getExistingDirectory(
            self, "Select Folder to Generate SFV", self.default_dir or os.getcwd(), options=options
        )
        if files:
            for file in files:
                if not self.file_list_generate.findItems(file, Qt.MatchFlag.MatchExactly):
                    self.file_list_generate.addItem(file)
        if folders:
            for root, dirs, filenames in os.walk(folders):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    if not self.file_list_generate.findItems(filepath, Qt.MatchFlag.MatchExactly):
                        self.file_list_generate.addItem(filepath)
    
    def clear_files_generate(self):
        self.file_list_generate.clear()
        self.output_area_generate.clear()
        self.progress_bar_generate.setValue(0)
    
    def generate_sfv(self):
        files = [self.file_list_generate.item(i).text() for i in range(self.file_list_generate.count())]
        logging.debug(f"generate_sfv called with {len(files)} files.")
        if not files:
            logging.warning("No files selected to generate SFV.")
            QMessageBox.warning(self, "No Files Selected", "Please add files to generate SFV.")
            return
    
        self.disable_ui_generate()
        self.output_area_generate.clear()
        self.statusBar().showMessage("Generating SFV...")
        logging.info("Starting SFV generation task.")
    
        self.task = ChecksumTask(files, self.algorithm)
        self.task.signals.progress.connect(self.progress_bar_generate.setValue)
        self.task.signals.result.connect(self.display_sfv)
        self.task.signals.finished.connect(self.enable_ui_generate)
        self.task.signals.message.connect(self.statusBar().showMessage)
    
        self.threadpool.start(self.task)
        logging.debug("ChecksumTask started in thread pool.")
    
    def disable_ui_generate(self):
        self.side_menu.setEnabled(False)
        self.btn_verify.setEnabled(False)
        self.btn_compare.setEnabled(False)
        self.btn_history.setEnabled(False)
        self.btn_settings.setEnabled(False)
    
    def enable_ui_generate(self):
        self.side_menu.setEnabled(True)
        self.btn_verify.setEnabled(True)
        self.btn_compare.setEnabled(True)
        self.btn_history.setEnabled(True)
        self.btn_settings.setEnabled(True)
        self.statusBar().showMessage("SFV generation completed.")
    
    def display_sfv(self, sfv_content):
        logging.debug("display_sfv called with SFV content.")
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save SFV File", self.default_dir or os.getcwd(), "SFV Files (*.sfv);;All Files (*)"
        )
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    f.write(sfv_content)
                logging.info(f"SFV file saved successfully at {save_path}.")
                QMessageBox.information(self, "Success", "SFV file generated successfully.")
                self.statusBar().showMessage("SFV file saved.")
                self.add_to_history(f"SFV Generated: {save_path} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                logging.error(f"Failed to save SFV file at {save_path}: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save SFV file: {e}")
                self.statusBar().showMessage("Failed to save SFV file.")
        else:
            logging.info("SFV file save dialog was canceled by the user.")
            self.statusBar().showMessage("SFV file generation canceled.")
        
        self.output_area_generate.setPlainText(sfv_content)
        self.progress_bar_generate.setValue(0)
        logging.debug("SFV content displayed and progress bar reset.")
    
    # Methods for Verify SFV Page
    def select_sfv_file(self):
        options = QFileDialog.Option.ReadOnly | QFileDialog.Option.DontUseNativeDialog
        sfv_file, _ = QFileDialog.getOpenFileName(
            self, "Select SFV File to Verify", self.default_dir or os.getcwd(), "SFV Files (*.sfv);;All Files (*)", options=options
        )
        if sfv_file:
            self.selected_sfv_file = sfv_file
            self.selected_sfv_label.setText(f"Selected SFV File: {sfv_file}")
            self.verify_button.setEnabled(True)
            logging.debug(f"Selected SFV file for verification: {sfv_file}")
        else:
            self.selected_sfv_file = None
            self.selected_sfv_label.setText("No SFV file selected.")
            self.verify_button.setEnabled(False)
            logging.debug("No SFV file selected for verification.")
    
    def verify_sfv(self, auto=False):
        if not hasattr(self, 'selected_sfv_file') or not self.selected_sfv_file:
            if not auto:
                QMessageBox.warning(self, "No SFV File", "Please select an SFV file to verify.")
            return
    
        self.disable_ui_verify()
        self.output_area_verify.clear()
        self.statusBar().showMessage("Verifying SFV...")
        logging.info("Starting SFV verification task.")
    
        self.task = VerificationTask(
            self.selected_sfv_file,
            self.algorithm,
            self.settings.get_logging_enabled(),
            self.settings.get_log_file_path(),
            self.settings.get_log_format()
        )
        self.task.signals.progress.connect(self.progress_bar_verify.setValue)
        self.task.signals.result.connect(lambda result: self.display_verification(result, auto))
        self.task.signals.finished.connect(self.enable_ui_verify)
        self.task.signals.message.connect(self.statusBar().showMessage)
    
        self.threadpool.start(self.task)
        logging.debug("VerificationTask started in thread pool.")
    
    def disable_ui_verify(self):
        self.side_menu.setEnabled(False)
        self.btn_generate.setEnabled(False)
        self.btn_compare.setEnabled(False)
        self.btn_history.setEnabled(False)
        self.btn_settings.setEnabled(False)
    
    def enable_ui_verify(self):
        self.side_menu.setEnabled(True)
        self.btn_generate.setEnabled(True)
        self.btn_compare.setEnabled(True)
        self.btn_history.setEnabled(True)
        self.btn_settings.setEnabled(True)
        self.statusBar().showMessage("SFV verification completed.")
    
    def display_verification(self, result, auto):
        logging.debug("display_verification called with verification results.")
        if isinstance(result, list):
            # 'result' is a list of dictionaries with 'filename' and 'status'
            result_str = "\n".join([f"{item['filename']}: {item['status']}" for item in result])
            self.output_area_verify.setPlainText(result_str)
            
            # Show the verification results in a dialog
            dialog = VerificationResultDialog(result, self)
            dialog.exec()
            
            self.show_notification("SFV Verification", "Verification process completed.")
            self.add_to_history(f"SFV Verified: {self.selected_sfv_file} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # Handle unexpected result format
            self.output_area_verify.setPlainText(str(result))
            logging.error("Unexpected result format in display_verification.")
            QMessageBox.warning(self, "Verification Error", "Unexpected verification result format.")
    
        self.statusBar().showMessage("Verification completed.")
        self.progress_bar_verify.setValue(0)
        logging.debug("Verification results displayed and progress bar reset.")
    
    # Methods for Compare Files Page
    def compare_files(self):
        path1 = self.path1_edit.text()
        path2 = self.path2_edit.text()
        if not path1 or not path2:
            QMessageBox.warning(self, "Missing Paths", "Please select both paths to compare.")
            return
        
        self.disable_ui_compare()
        self.output_area_compare.clear()
        self.statusBar().showMessage("Comparing files/directories...")
        logging.info(f"Starting comparison between {path1} and {path2}.")
        
        self.task = CompareTask(
            path1,
            path2,
            self.algorithm
        )
        self.task.signals.progress.connect(self.progress_bar_compare.setValue)
        self.task.signals.result.connect(self.display_comparison)
        self.task.signals.finished.connect(self.enable_ui_compare)
        self.task.signals.message.connect(self.statusBar().showMessage)
        
        self.threadpool.start(self.task)
        logging.debug("CompareTask started in thread pool.")
    
    def disable_ui_compare(self):
        self.side_menu.setEnabled(False)
        self.btn_generate.setEnabled(False)
        self.btn_verify.setEnabled(False)
        self.btn_history.setEnabled(False)
        self.btn_settings.setEnabled(False)
    
    def enable_ui_compare(self):
        self.side_menu.setEnabled(True)
        self.btn_generate.setEnabled(True)
        self.btn_verify.setEnabled(True)
        self.btn_history.setEnabled(True)
        self.btn_settings.setEnabled(True)
        self.statusBar().showMessage("Comparison completed.")
    
    def display_comparison(self, result):
        logging.debug("display_comparison called with comparison results.")
        if isinstance(result, str):
            self.output_area_compare.setPlainText(result)
            self.add_to_history(f"Comparison between {self.path1_edit.text()} and {self.path2_edit.text()} completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # Handle unexpected result format
            self.output_area_compare.setPlainText(str(result))
            logging.error("Unexpected result format in display_comparison.")
            QMessageBox.warning(self, "Comparison Error", "Unexpected comparison result format.")
    
        self.progress_bar_compare.setValue(0)
        logging.debug("Comparison results displayed and progress bar reset.")
    
    # Methods for History Page
    def load_history(self):
        self.history = self.settings.get_history()
        self.history_list.addItems(self.history)
    
    def add_to_history(self, entry):
        self.history.append(entry)
        self.settings.add_history_entry(entry)
        self.history_list.addItem(entry)
    
    def clear_history(self):
        confirm = QMessageBox.question(
            self, "Clear History", "Are you sure you want to clear the history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.history_list.clear()
            self.history = []
            self.settings.clear_history()
            logging.debug("History cleared.")
            QMessageBox.information(self, "History Cleared", "All history entries have been cleared.")
    
    def copy_to_clipboard(self, list_widget):
        clipboard = QApplication.clipboard()
        text = "\n".join([list_widget.item(i).text() for i in range(list_widget.count())])
        clipboard.setText(text)
        QMessageBox.information(self, "Copied", "The history has been copied to the clipboard.")
    
    # Methods for Settings
    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.load_settings()
            self.apply_settings()
            logging.debug("Settings updated and applied.")
    
    def load_settings(self):
        # Load settings from settings.py
        self.algorithm = self.settings.get_checksum_algorithm()
        self.default_dir = self.settings.get_default_directory()
        self.logging_enabled = self.settings.get_logging_enabled()
        self.log_file_path = self.settings.get_log_file_path()
        self.log_format = self.settings.get_log_format()
        logging.debug(f"Loaded settings: algorithm={self.algorithm}, default_dir={self.default_dir}, "
                      f"logging_enabled={self.logging_enabled}, log_file_path={self.log_file_path}, "
                      f"log_format={self.log_format}")
    
    def apply_settings(self):
        # Apply settings (e.g., update default directory paths, logging configurations)
        pass  # Implement as needed
    
    # Notification Method
    def show_notification(self, title, message, icon=QMessageBox.Icon.Information):
        QMessageBox(icon, title, message, QMessageBox.StandardButton.Ok, self).show()
    
    # Methods for Browsing Paths
    def browse_path(self, line_edit):
        options = QFileDialog.Option.ReadOnly | QFileDialog.Option.DontUseNativeDialog
        path = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.default_dir or os.getcwd(), options=options
        )
        if path:
            line_edit.setText(path)

# Main Function
def main():
    app = QApplication(sys.argv)
    window = SFVApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
