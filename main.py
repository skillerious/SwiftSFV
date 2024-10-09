import sys
import os
import zlib
import hashlib
import pickle
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTextEdit, QLabel, QProgressBar,
    QMessageBox, QStatusBar, QListWidget, QListWidgetItem, QStackedWidget,
    QStyleFactory, QMenu, QDialog, QFormLayout, QLineEdit,
    QComboBox, QCheckBox, QToolButton
)
from PyQt6.QtGui import (
    QPalette, QColor, QIcon, QFont, QPixmap, QAction
)
from PyQt6.QtCore import (
    Qt, QThreadPool, QRunnable, pyqtSlot, QObject, pyqtSignal, QSettings
)

class Signals(QObject):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    result = pyqtSignal(str)
    finished = pyqtSignal()

class ChecksumTask(QRunnable):
    def __init__(self, files, algorithm):
        super().__init__()
        self.files = files
        self.algorithm = algorithm
        self.signals = Signals()

    @pyqtSlot()
    def run(self):
        total_files = len(self.files)
        if total_files == 0:
            self.signals.message.emit("No files selected for SFV generation.")
            self.signals.finished.emit()
            return

        sfv_content = ''
        for idx, file in enumerate(self.files):
            try:
                file_path = os.path.abspath(file)
                with open(file_path, 'rb') as f:
                    data = f.read()
                    checksum = self.calculate_checksum(data)
                    relative_path = os.path.relpath(file_path)
                    sfv_content += f"{relative_path} {checksum}\n"
            except Exception as e:
                sfv_content += f"{os.path.basename(file)} ERROR: {e}\n"
            progress = int((idx + 1) / total_files * 100)
            self.signals.progress.emit(progress)
            self.signals.message.emit(f"Processing {idx + 1}/{total_files} files...")
        self.signals.result.emit(sfv_content)
        self.signals.finished.emit()

    def calculate_checksum(self, data):
        if self.algorithm == 'CRC32':
            return f"{zlib.crc32(data) & 0xFFFFFFFF:08X}"
        elif self.algorithm == 'MD5':
            return hashlib.md5(data).hexdigest().upper()
        elif self.algorithm == 'SHA1':
            return hashlib.sha1(data).hexdigest().upper()
        else:
            return 'UNKNOWN_ALGORITHM'

class VerificationTask(QRunnable):
    def __init__(self, sfv_file, algorithm, log_enabled, log_file_path):
        super().__init__()
        self.sfv_file = sfv_file
        self.algorithm = algorithm
        self.log_enabled = log_enabled
        self.log_file_path = log_file_path
        self.signals = Signals()

    @pyqtSlot()
    def run(self):
        try:
            with open(self.sfv_file, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            self.signals.result.emit(f"Failed to open SFV file: {e}")
            self.signals.finished.emit()
            return

        total_files = len(lines)
        if total_files == 0:
            self.signals.message.emit("SFV file is empty.")
            self.signals.finished.emit()
            return

        output = ''
        for idx, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) != 2:
                output += f"Invalid line in SFV: {line}\n"
                continue
            filename, expected_checksum = parts
            file_path = os.path.abspath(filename)
            if not os.path.isfile(file_path):
                output += f"{filename}: File not found\n"
                continue
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    checksum = self.calculate_checksum(data)
                    if checksum.upper() == expected_checksum.upper():
                        output += f"{filename}: OK\n"
                    else:
                        output += f"{filename}: MISMATCH (Expected {expected_checksum}, Got {checksum})\n"
                progress = int((idx + 1) / total_files * 100)
                self.signals.progress.emit(progress)
                self.signals.message.emit(f"Verifying {idx + 1}/{total_files} files...")
            except Exception as e:
                output += f"{filename}: ERROR {e}\n"
        self.signals.result.emit(output)
        if self.log_enabled:
            self.save_log(output)
        self.signals.finished.emit()

    def calculate_checksum(self, data):
        if self.algorithm == 'CRC32':
            return f"{zlib.crc32(data) & 0xFFFFFFFF:08X}"
        elif self.algorithm == 'MD5':
            return hashlib.md5(data).hexdigest().upper()
        elif self.algorithm == 'SHA1':
            return hashlib.sha1(data).hexdigest().upper()
        else:
            return 'UNKNOWN_ALGORITHM'

    def save_log(self, content):
        try:
            with open(self.log_file_path, 'w') as log_file:
                log_file.write(content)
            self.signals.message.emit(f"Log saved to {self.log_file_path}")
        except Exception as e:
            self.signals.message.emit(f"Failed to save log: {e}")

class CompareTask(QRunnable):
    def __init__(self, path1, path2, algorithm):
        super().__init__()
        self.path1 = path1
        self.path2 = path2
        self.algorithm = algorithm
        self.signals = Signals()

    @pyqtSlot()
    def run(self):
        self.signals.message.emit("Comparing files/directories...")
        if os.path.isfile(self.path1) and os.path.isfile(self.path2):
            result = self.compare_files(self.path1, self.path2)
        elif os.path.isdir(self.path1) and os.path.isdir(self.path2):
            result = self.compare_directories(self.path1, self.path2)
        else:
            result = "Both paths must be either files or directories."
        self.signals.result.emit(result)
        self.signals.finished.emit()

    def compare_files(self, file1, file2):
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                data1 = f1.read()
                data2 = f2.read()
                checksum1 = self.calculate_checksum(data1)
                checksum2 = self.calculate_checksum(data2)
                if checksum1 == checksum2:
                    return "Files are identical."
                else:
                    return f"Files differ.\nChecksum1: {checksum1}\nChecksum2: {checksum2}"
        except Exception as e:
            return f"Error comparing files: {e}"

    def compare_directories(self, dir1, dir2):
        files1 = self.get_files(dir1)
        files2 = self.get_files(dir2)
        common_files = set(files1.keys()).intersection(set(files2.keys()))
        differences = []
        for file in common_files:
            if files1[file] != files2[file]:
                differences.append(f"File {file} differs.")
        if differences:
            return "\n".join(differences)
        else:
            return "Directories are identical."

    def get_files(self, directory):
        file_checksums = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, 'rb') as f:
                    data = f.read()
                    checksum = self.calculate_checksum(data)
                    relative_path = os.path.relpath(filepath, directory)
                    file_checksums[relative_path] = checksum
        return file_checksums

    def calculate_checksum(self, data):
        if self.algorithm == 'CRC32':
            return f"{zlib.crc32(data) & 0xFFFFFFFF:08X}"
        elif self.algorithm == 'MD5':
            return hashlib.md5(data).hexdigest().upper()
        elif self.algorithm == 'SHA1':
            return hashlib.sha1(data).hexdigest().upper()
        else:
            return 'UNKNOWN_ALGORITHM'

class DraggableListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setSpacing(5)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                self.add_files_recursive(filepath)
            event.accept()
        else:
            event.ignore()

    def add_files_recursive(self, path):
        if os.path.isfile(path):
            self.addItem(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    self.addItem(os.path.join(root, file))

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        # Checksum Algorithm
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(['CRC32', 'MD5', 'SHA1'])
        layout.addRow("Default Checksum Algorithm:", self.algorithm_combo)

        # Theme Selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Dark', 'Light'])
        layout.addRow("Theme:", self.theme_combo)

        # Default Directory
        dir_layout = QHBoxLayout()
        self.default_dir_edit = QLineEdit()
        self.dir_picker_button = QToolButton()
        self.dir_picker_button.setIcon(QIcon("images/folder_icon.png"))
        self.dir_picker_button.clicked.connect(self.pick_default_directory)
        dir_layout.addWidget(self.default_dir_edit)
        dir_layout.addWidget(self.dir_picker_button)
        layout.addRow("Default Directory:", dir_layout)

        # Enable Logging
        self.logging_checkbox = QCheckBox("Enable Logging")
        layout.addRow(self.logging_checkbox)

        # Log File Path
        log_layout = QHBoxLayout()
        self.log_file_edit = QLineEdit()
        self.log_file_button = QToolButton()
        self.log_file_button.setIcon(QIcon("images/file_icon.png"))
        self.log_file_button.clicked.connect(self.pick_log_file)
        log_layout.addWidget(self.log_file_edit)
        log_layout.addWidget(self.log_file_button)
        layout.addRow("Log File Path:", log_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

        self.load_settings()

    def pick_default_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Default Directory")
        if directory:
            self.default_dir_edit.setText(directory)

    def pick_log_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Log File", "", "Log Files (*.log);;All Files (*)")
        if file_path:
            self.log_file_edit.setText(file_path)

    def load_settings(self):
        settings = QSettings("MyCompany", "SFVChecker")
        algorithm = settings.value("algorithm", 'CRC32')
        theme = settings.value("theme", 'Dark')
        default_dir = settings.value("default_dir", '')
        logging_enabled = settings.value("logging_enabled", False, type=bool)
        log_file_path = settings.value("log_file_path", '')

        self.algorithm_combo.setCurrentText(algorithm)
        self.theme_combo.setCurrentText(theme)
        self.default_dir_edit.setText(default_dir)
        self.logging_checkbox.setChecked(logging_enabled)
        self.log_file_edit.setText(log_file_path)

    def save_settings(self):
        settings = QSettings("MyCompany", "SFVChecker")
        settings.setValue("algorithm", self.algorithm_combo.currentText())
        settings.setValue("theme", self.theme_combo.currentText())
        settings.setValue("default_dir", self.default_dir_edit.text())
        settings.setValue("logging_enabled", self.logging_checkbox.isChecked())
        settings.setValue("log_file_path", self.log_file_edit.text())
        self.accept()

class SFVApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python SFV Checker")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('images/app_icon.png'))
        self.threadpool = QThreadPool()
        self.init_ui()
        self.load_settings()
        self.apply_styles()
        self.show()

    def init_ui(self):
        # Menu Bar
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")
        settings_action = QAction(QIcon("images/settings_icon.png"), "Preferences", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

        session_menu = menubar.addMenu("Session")
        save_session_action = QAction(QIcon("images/save_icon.png"), "Save Session", self)
        save_session_action.triggered.connect(self.save_session)
        load_session_action = QAction(QIcon("images/load_icon.png"), "Load Session", self)
        load_session_action.triggered.connect(self.load_session)
        session_menu.addAction(save_session_action)
        session_menu.addAction(load_session_action)

        # Central Widget and Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sidebar Navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)
        self.sidebar.addItem(QListWidgetItem(QIcon("images/generate_icon.png"), "Generate SFV"))
        self.sidebar.addItem(QListWidgetItem(QIcon("images/verify_icon.png"), "Verify SFV"))
        self.sidebar.addItem(QListWidgetItem(QIcon("images/compare_icon.png"), "Compare Files"))
        self.sidebar.currentRowChanged.connect(self.display_page)
        main_layout.addWidget(self.sidebar)

        # Stacked Widget for Pages
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Page 1: Generate SFV
        self.page_generate = QWidget()
        self.init_generate_page()
        self.pages.addWidget(self.page_generate)

        # Page 2: Verify SFV
        self.page_verify = QWidget()
        self.init_verify_page()
        self.pages.addWidget(self.page_verify)

        # Page 3: Compare Files
        self.page_compare = QWidget()
        self.init_compare_page()
        self.pages.addWidget(self.page_compare)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Set default page
        self.sidebar.setCurrentRow(0)

    def init_generate_page(self):
        layout = QVBoxLayout(self.page_generate)

        # Instructions Label
        instruction_label = QLabel("Drag and drop files or folders here or click 'Add Files' to select files for SFV generation.")
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)

        # File List
        self.file_list = DraggableListWidget()
        layout.addWidget(self.file_list)

        # Buttons Layout
        button_layout = QHBoxLayout()
        self.add_files_button = QPushButton(QIcon("images/add_icon.png"), "Add Files/Folders")
        self.add_files_button.clicked.connect(self.add_files)
        self.clear_files_button = QPushButton(QIcon("images/clear_icon.png"), "Clear Files")
        self.clear_files_button.clicked.connect(self.clear_files)
        button_layout.addWidget(self.add_files_button)
        button_layout.addWidget(self.clear_files_button)
        layout.addLayout(button_layout)

        # Generate Button
        self.generate_button = QPushButton(QIcon("images/generate_icon.png"), "Generate SFV")
        self.generate_button.clicked.connect(self.generate_sfv)
        layout.addWidget(self.generate_button)

        # Output Area
        self.output_area_generate = QTextEdit()
        self.output_area_generate.setReadOnly(True)
        self.output_area_generate.setFont(QFont("Consolas", 10))
        layout.addWidget(self.output_area_generate)

        # Progress Bar
        self.progress_bar_generate = QProgressBar()
        layout.addWidget(self.progress_bar_generate)

    def init_verify_page(self):
        layout = QVBoxLayout(self.page_verify)

        # Instructions Label
        instruction_label = QLabel("Select an SFV file to verify the listed files.")
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)

        # Select SFV Button
        self.select_sfv_button = QPushButton(QIcon("images/open_icon.png"), "Select SFV File")
        self.select_sfv_button.clicked.connect(self.select_sfv_file)
        layout.addWidget(self.select_sfv_button)

        # Selected SFV File Label
        self.selected_sfv_label = QLabel("No SFV file selected.")
        layout.addWidget(self.selected_sfv_label)

        # Verify Button
        self.verify_button = QPushButton(QIcon("images/verify_icon.png"), "Verify SFV")
        self.verify_button.clicked.connect(self.verify_sfv)
        self.verify_button.setEnabled(False)
        layout.addWidget(self.verify_button)

        # Output Area
        self.output_area_verify = QTextEdit()
        self.output_area_verify.setReadOnly(True)
        self.output_area_verify.setFont(QFont("Consolas", 10))
        layout.addWidget(self.output_area_verify)

        # Progress Bar
        self.progress_bar_verify = QProgressBar()
        layout.addWidget(self.progress_bar_verify)

    def init_compare_page(self):
        layout = QVBoxLayout(self.page_compare)

        # Instructions Label
        instruction_label = QLabel("Select two files or directories to compare.")
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)

        # Path Selection Layout
        path_layout = QHBoxLayout()

        # Path 1
        self.path1_edit = QLineEdit()
        self.path1_button = QPushButton(QIcon("images/folder_icon.png"), "Select Path 1")
        self.path1_button.clicked.connect(self.select_path1)
        path_layout.addWidget(self.path1_edit)
        path_layout.addWidget(self.path1_button)

        # Path 2
        self.path2_edit = QLineEdit()
        self.path2_button = QPushButton(QIcon("images/folder_icon.png"), "Select Path 2")
        self.path2_button.clicked.connect(self.select_path2)
        path_layout.addWidget(self.path2_edit)
        path_layout.addWidget(self.path2_button)

        layout.addLayout(path_layout)

        # Compare Button
        self.compare_button = QPushButton(QIcon("images/compare_icon.png"), "Compare")
        self.compare_button.clicked.connect(self.compare_paths)
        layout.addWidget(self.compare_button)

        # Output Area
        self.output_area_compare = QTextEdit()
        self.output_area_compare.setReadOnly(True)
        self.output_area_compare.setFont(QFont("Consolas", 10))
        layout.addWidget(self.output_area_compare)

    def select_path1(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File or Directory", self.default_dir, "All Files (*)")
        if path:
            self.path1_edit.setText(path)

    def select_path2(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File or Directory", self.default_dir, "All Files (*)")
        if path:
            self.path2_edit.setText(path)

    def compare_paths(self):
        path1 = self.path1_edit.text()
        path2 = self.path2_edit.text()
        if not path1 or not path2:
            QMessageBox.warning(self, "Paths Missing", "Please select both paths to compare.")
            return

        self.disable_ui_compare()
        self.output_area_compare.clear()
        self.status_bar.showMessage("Comparing paths...")

        self.task = CompareTask(path1, path2, self.algorithm)
        self.task.signals.result.connect(self.display_comparison)
        self.task.signals.message.connect(self.status_bar.showMessage)
        self.task.signals.finished.connect(self.enable_ui_compare)

        self.threadpool.start(self.task)

    def display_comparison(self, result):
        self.output_area_compare.setPlainText(result)
        self.status_bar.showMessage("Comparison completed.")

    def disable_ui_compare(self):
        self.compare_button.setEnabled(False)
        self.path1_button.setEnabled(False)
        self.path2_button.setEnabled(False)
        self.sidebar.setEnabled(False)

    def enable_ui_compare(self):
        self.compare_button.setEnabled(True)
        self.path1_button.setEnabled(True)
        self.path2_button.setEnabled(True)
        self.sidebar.setEnabled(True)
        self.status_bar.showMessage("Ready.")

    def display_page(self, index):
        self.pages.setCurrentIndex(index)

    def add_files(self):
        options = QFileDialog.Option.ReadOnly
        options |= QFileDialog.Option.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files or Folders", self.default_dir, "All Files (*)", options=options
        )
        for file in files:
            self.file_list.add_files_recursive(file)

    def clear_files(self):
        self.file_list.clear()

    def generate_sfv(self):
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not files:
            QMessageBox.warning(self, "No Files Selected", "Please add files to generate SFV.")
            return

        self.disable_ui_generate()
        self.output_area_generate.clear()
        self.status_bar.showMessage("Generating SFV...")

        self.task = ChecksumTask(files, self.algorithm)
        self.task.signals.progress.connect(self.progress_bar_generate.setValue)
        self.task.signals.result.connect(self.display_sfv)
        self.task.signals.message.connect(self.status_bar.showMessage)
        self.task.signals.finished.connect(self.enable_ui_generate)

        self.threadpool.start(self.task)

    def display_sfv(self, sfv_content):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save SFV File", self.default_dir, "SFV Files (*.sfv);;All Files (*)"
        )
        if save_path:
            try:
                with open(save_path, 'w') as f:
                    f.write(sfv_content)
                QMessageBox.information(self, "Success", "SFV file generated successfully.")
                self.status_bar.showMessage("SFV file saved.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save SFV file: {e}")
                self.status_bar.showMessage("Failed to save SFV file.")
        else:
            self.status_bar.showMessage("SFV file generation canceled.")

        self.output_area_generate.setPlainText(sfv_content)
        self.progress_bar_generate.setValue(0)

    def disable_ui_generate(self):
        self.generate_button.setEnabled(False)
        self.add_files_button.setEnabled(False)
        self.clear_files_button.setEnabled(False)
        self.sidebar.setEnabled(False)

    def enable_ui_generate(self):
        self.generate_button.setEnabled(True)
        self.add_files_button.setEnabled(True)
        self.clear_files_button.setEnabled(True)
        self.sidebar.setEnabled(True)
        self.status_bar.showMessage("Ready.")

    def select_sfv_file(self):
        sfv_file, _ = QFileDialog.getOpenFileName(
            self, "Open SFV File", self.default_dir, "SFV Files (*.sfv);;All Files (*)"
        )
        if sfv_file:
            self.selected_sfv_file = sfv_file
            self.selected_sfv_label.setText(f"Selected SFV File: {os.path.basename(sfv_file)}")
            self.verify_button.setEnabled(True)
        else:
            self.selected_sfv_label.setText("No SFV file selected.")
            self.verify_button.setEnabled(False)

    def verify_sfv(self):
        if not hasattr(self, 'selected_sfv_file'):
            QMessageBox.warning(self, "No SFV File", "Please select an SFV file to verify.")
            return

        self.disable_ui_verify()
        self.output_area_verify.clear()
        self.status_bar.showMessage("Verifying SFV...")

        self.task = VerificationTask(self.selected_sfv_file, self.algorithm, self.logging_enabled, self.log_file_path)
        self.task.signals.progress.connect(self.progress_bar_verify.setValue)
        self.task.signals.result.connect(self.display_verification)
        self.task.signals.message.connect(self.status_bar.showMessage)
        self.task.signals.finished.connect(self.enable_ui_verify)

        self.threadpool.start(self.task)

    def display_verification(self, result):
        self.output_area_verify.setPlainText(result)
        self.progress_bar_verify.setValue(0)
        self.status_bar.showMessage("Verification completed.")

    def disable_ui_verify(self):
        self.verify_button.setEnabled(False)
        self.select_sfv_button.setEnabled(False)
        self.sidebar.setEnabled(False)

    def enable_ui_verify(self):
        self.verify_button.setEnabled(True)
        self.select_sfv_button.setEnabled(True)
        self.sidebar.setEnabled(True)
        self.status_bar.showMessage("Ready.")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.load_settings()
            self.apply_styles()

    def load_settings(self):
        settings = QSettings("MyCompany", "SFVChecker")
        self.algorithm = settings.value("algorithm", 'CRC32')
        theme = settings.value("theme", 'Dark')
        self.default_dir = settings.value("default_dir", '')
        self.logging_enabled = settings.value("logging_enabled", False, type=bool)
        self.log_file_path = settings.value("log_file_path", '')

        if theme == 'Dark':
            self.theme = 'dark'
        else:
            self.theme = 'light'

    def apply_styles(self):
        if self.theme == 'dark':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        # Set Font
        font = QFont("Segoe UI", 10)
        self.setFont(font)

    def apply_dark_theme(self):
        # Dark Theme Palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#2b2b2b"))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2b2b2b"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor("#2b2b2b"))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor("#2980b9"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#2980b9"))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        self.setPalette(palette)

        # Apply Style Sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: white;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #2980b9;
            }
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QLabel {
                color: white;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
            }
            QProgressBar {
                background-color: #1e1e1e;
                color: white;
                border: none;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2980b9;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: white;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: white;
            }
        """)

    def apply_light_theme(self):
        # Light Theme Palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor("#f0f0f0"))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor("#007acc"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#007acc"))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        self.setPalette(palette)

        # Apply Style Sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QListWidget {
                background-color: #ffffff;
                color: black;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #3399ff;
            }
            QLabel {
                color: black;
            }
            QTextEdit {
                background-color: #ffffff;
                color: black;
            }
            QProgressBar {
                background-color: #ffffff;
                color: black;
                border: none;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
            QStatusBar {
                background-color: #ffffff;
                color: black;
            }
            QMessageBox {
                background-color: #f0f0f0;
                color: black;
            }
        """)

    def save_session(self):
        session_data = {
            'file_list': [self.file_list.item(i).text() for i in range(self.file_list.count())],
            'selected_sfv_file': getattr(self, 'selected_sfv_file', None)
        }
        session_file, _ = QFileDialog.getSaveFileName(self, "Save Session", self.default_dir, "Session Files (*.session);;All Files (*)")
        if session_file:
            with open(session_file, 'wb') as f:
                pickle.dump(session_data, f)
            QMessageBox.information(self, "Success", "Session saved successfully.")

    def load_session(self):
        session_file, _ = QFileDialog.getOpenFileName(self, "Load Session", self.default_dir, "Session Files (*.session);;All Files (*)")
        if session_file:
            with open(session_file, 'rb') as f:
                session_data = pickle.load(f)
            self.file_list.clear()
            for file in session_data.get('file_list', []):
                self.file_list.addItem(file)
            self.selected_sfv_file = session_data.get('selected_sfv_file', None)
            if self.selected_sfv_file:
                self.selected_sfv_label.setText(f"Selected SFV File: {os.path.basename(self.selected_sfv_file)}")
                self.verify_button.setEnabled(True)
            else:
                self.selected_sfv_label.setText("No SFV file selected.")
                self.verify_button.setEnabled(False)
            QMessageBox.information(self, "Success", "Session loaded successfully.")

    def closeEvent(self, event):
        self.threadpool.waitForDone()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setOrganizationName("MyCompany")
    app.setApplicationName("SFVChecker")
    window = SFVApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
