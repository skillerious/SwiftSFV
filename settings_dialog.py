# settings_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QIcon
import os

from settings import AppSettings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)
        self.settings = AppSettings()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Checksum Algorithm
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Checksum Algorithm:")
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["CRC32", "MD5", "SHA1", "SHA256"])
        self.algo_combo.setCurrentText(self.settings.get_checksum_algorithm())
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        layout.addLayout(algo_layout)
        
        # Default Directory
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Default Directory:")
        self.dir_edit = QLineEdit()
        self.dir_edit.setText(self.settings.get_default_directory())
        dir_browse = QPushButton("Browse")
        dir_browse.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(dir_browse)
        layout.addLayout(dir_layout)
        
        # Logging Enabled
        self.logging_checkbox = QCheckBox("Enable Logging")
        self.logging_checkbox.setChecked(self.settings.get_logging_enabled())
        layout.addWidget(self.logging_checkbox)
        
        # Log File Path
        log_path_layout = QHBoxLayout()
        log_path_label = QLabel("Log File Path:")
        self.log_path_edit = QLineEdit()
        self.log_path_edit.setText(self.settings.get_log_file_path())
        log_path_browse = QPushButton("Browse")
        log_path_browse.clicked.connect(self.browse_log_file)
        log_path_layout.addWidget(log_path_label)
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(log_path_browse)
        layout.addLayout(log_path_layout)
        
        # Log Format
        format_layout = QHBoxLayout()
        format_label = QLabel("Log Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "CSV"])
        self.format_combo.setCurrentText(self.settings.get_log_format())
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Default Directory", self.dir_edit.text())
        if dir_path:
            self.dir_edit.setText(dir_path)
    
    def browse_log_file(self):
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Log File", self.log_path_edit.text(), "Log Files (*.log *.txt *.csv)", options=options)
        if file_path:
            self.log_path_edit.setText(file_path)
    
    def save_settings(self):
        algorithm = self.algo_combo.currentText()
        default_dir = self.dir_edit.text()
        logging_enabled = self.logging_checkbox.isChecked()
        log_file_path = self.log_path_edit.text()
        log_format = self.format_combo.currentText()
        
        # Validate inputs
        if not os.path.isdir(default_dir):
            QMessageBox.warning(self, "Invalid Directory", "The selected default directory does not exist.")
            return
        if logging_enabled and not log_file_path:
            QMessageBox.warning(self, "Invalid Log File Path", "Please specify a valid log file path.")
            return
        
        # Save settings
        self.settings.set_checksum_algorithm(algorithm)
        self.settings.set_default_directory(default_dir)
        self.settings.set_logging_enabled(logging_enabled)
        self.settings.set_log_file_path(log_file_path)
        self.settings.set_log_format(log_format)
        
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
        self.accept()
