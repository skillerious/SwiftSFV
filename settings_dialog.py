# settings_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QLineEdit, QPushButton, QFileDialog, QMessageBox, QSpinBox,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont
import os
import logging

from settings import AppSettings

class SettingsDialog(QDialog):
    """
    SettingsDialog provides a user interface for configuring application settings.
    Users can select checksum algorithms, set default directories, manage logging,
    choose UI themes, adjust font sizes, and more.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 600)
        self.settings = AppSettings()
        self.init_ui()

    def init_ui(self):
        """
        Initialize the settings dialog UI components.
        """
        layout = QVBoxLayout()

        # Checksum Algorithm Selection
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Checksum Algorithm:")
        self.algo_combo = QComboBox()
        # Updated list with additional algorithms
        self.algo_combo.addItems([
            "CRC32", "MD5", "SHA1", "SHA224", "SHA256",
            "SHA384", "SHA512", "BLAKE2B", "BLAKE2S"
        ])
        self.algo_combo.setCurrentText(self.settings.get_checksum_algorithm())
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        layout.addLayout(algo_layout)

        # Default Directory Selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Default Directory:")
        self.dir_edit = QLineEdit()
        self.dir_edit.setText(self.settings.get_default_directory())
        dir_browse = QPushButton("Browse")
        dir_browse.setIcon(self.load_icon('document.png'))  # Ensure 'document.png' exists
        dir_browse.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(dir_browse)
        layout.addLayout(dir_layout)

        # Logging Enabled Checkbox
        self.logging_checkbox = QCheckBox("Enable Logging")
        self.logging_checkbox.setChecked(self.settings.get_logging_enabled())
        layout.addWidget(self.logging_checkbox)

        # Log File Path Selection
        log_path_layout = QHBoxLayout()
        log_path_label = QLabel("Log File Path:")
        self.log_path_edit = QLineEdit()
        self.log_path_edit.setText(self.settings.get_log_file_path())
        log_path_browse = QPushButton("Browse")
        log_path_browse.setIcon(self.load_icon('document.png'))  # Reusing 'document.png'
        log_path_browse.clicked.connect(self.browse_log_file)
        log_path_layout.addWidget(log_path_label)
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(log_path_browse)
        layout.addLayout(log_path_layout)

        # Log Format Selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Log Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "CSV"])
        self.format_combo.setCurrentText(self.settings.get_log_format())
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Output Path Type Selection
        path_type_layout = QHBoxLayout()
        path_type_label = QLabel("Output Path Type:")
        self.path_type_combo = QComboBox()
        self.path_type_combo.addItems(["Relative", "Absolute"])
        self.path_type_combo.setCurrentText(self.settings.get_output_path_type())
        path_type_layout.addWidget(path_type_label)
        path_type_layout.addWidget(self.path_type_combo)
        layout.addLayout(path_type_layout)

        # Delimiter Selection with Dynamic Custom Delimiter
        delimiter_layout = QHBoxLayout()
        delimiter_label = QLabel("Delimiter:")
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(["Space", "Tab", "Custom"])
        self.delimiter_combo.setCurrentText(self.settings.get_delimiter())
        self.delimiter_combo.currentTextChanged.connect(self.toggle_custom_delimiter)
        delimiter_layout.addWidget(delimiter_label)
        delimiter_layout.addWidget(self.delimiter_combo)

        self.custom_delimiter_edit = QLineEdit()
        self.custom_delimiter_edit.setText(self.settings.get_custom_delimiter())
        self.custom_delimiter_edit.setEnabled(self.settings.get_delimiter() == "Custom")
        self.custom_delimiter_edit.setPlaceholderText("Enter custom delimiter")
        delimiter_layout.addWidget(self.custom_delimiter_edit)
        layout.addLayout(delimiter_layout)

        # Automatically Verify After Generation Checkbox
        self.auto_verify_checkbox = QCheckBox("Automatically Verify SFV After Generation")
        self.auto_verify_checkbox.setChecked(self.settings.get_auto_verify())
        layout.addWidget(self.auto_verify_checkbox)

        # Detailed Logging Checkbox
        self.detailed_logging_checkbox = QCheckBox("Enable Detailed Logging")
        self.detailed_logging_checkbox.setChecked(self.settings.get_detailed_logging())
        layout.addWidget(self.detailed_logging_checkbox)

        # UI Theme Selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("UI Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get_ui_theme())
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font Size Adjustment
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.settings.get_font_size())
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_spin)
        layout.addLayout(font_size_layout)

        # Spacer to push buttons to the bottom
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Buttons: Save, Cancel, Reset to Defaults
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.setIcon(self.load_icon('save_icon.png'))  # Ensure 'save_icon.png' exists
        save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("Cancel")
        cancel_button.setIcon(self.load_icon('cancel_icon.png'))  # Ensure 'cancel_icon.png' exists
        cancel_button.clicked.connect(self.reject)

        reset_button = QPushButton("Reset to Defaults")
        reset_button.setIcon(self.load_icon('reset_icon.png'))  # Ensure 'reset_icon.png' exists
        reset_button.clicked.connect(self.reset_to_defaults)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(reset_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_icon(self, icon_name):
        """
        Load an icon from the images directory with a fallback to a default icon.

        Parameters:
            icon_name (str): The filename of the icon.

        Returns:
            QIcon: The loaded icon or a default icon if not found.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(base_dir, 'images')
        icon_path = os.path.join(images_dir, icon_name)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            logging.warning(f"Icon not found: {icon_path}. Using default icon.")
            return QIcon()

    def browse_directory(self):
        """
        Open a dialog to browse and select the default directory.
        """
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Default Directory", self.dir_edit.text()
        )
        if dir_path:
            self.dir_edit.setText(dir_path)

    def browse_log_file(self):
        """
        Open a dialog to browse and select the log file path.
        """
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Log File", self.log_path_edit.text(),
            "Log Files (*.log *.txt *.csv);;All Files (*)", options=options
        )
        if file_path:
            self.log_path_edit.setText(file_path)

    def toggle_custom_delimiter(self, text):
        """
        Enable or disable the custom delimiter input based on the selected delimiter option.

        Parameters:
            text (str): The currently selected delimiter option.
        """
        if text == "Custom":
            self.custom_delimiter_edit.setEnabled(True)
        else:
            self.custom_delimiter_edit.setEnabled(False)

    def save_settings(self):
        """
        Validate and save the settings entered by the user.
        """
        # Retrieve values from UI components
        algorithm = self.algo_combo.currentText()
        default_dir = self.dir_edit.text()
        logging_enabled = self.logging_checkbox.isChecked()
        log_file_path = self.log_path_edit.text()
        log_format = self.format_combo.currentText()

        output_path_type = self.path_type_combo.currentText()
        delimiter = self.delimiter_combo.currentText()
        custom_delimiter = self.custom_delimiter_edit.text() if delimiter == "Custom" else " "
        auto_verify = self.auto_verify_checkbox.isChecked()
        detailed_logging = self.detailed_logging_checkbox.isChecked()
        ui_theme = self.theme_combo.currentText()
        font_size = self.font_size_spin.value()

        # Input Validation
        if not os.path.isdir(default_dir):
            QMessageBox.warning(self, "Invalid Directory", "The selected default directory does not exist.")
            return

        if logging_enabled:
            if not log_file_path:
                QMessageBox.warning(self, "Invalid Log File Path", "Please specify a valid log file path.")
                return
            # Validate log file extension based on log format
            if log_format == "CSV" and not log_file_path.lower().endswith('.csv'):
                QMessageBox.warning(self, "Invalid Log File Extension", "Log file must have a .csv extension for CSV format.")
                return
            elif log_format == "TXT" and not log_file_path.lower().endswith(('.txt', '.log')):
                QMessageBox.warning(self, "Invalid Log File Extension", "Log file must have a .txt or .log extension for TXT format.")
                return

        if delimiter == "Custom" and not custom_delimiter:
            QMessageBox.warning(self, "Invalid Delimiter", "Please specify a custom delimiter.")
            return

        # Save settings
        self.settings.set_checksum_algorithm(algorithm)
        self.settings.set_default_directory(default_dir)
        self.settings.set_logging_enabled(logging_enabled)
        self.settings.set_log_file_path(log_file_path)
        self.settings.set_log_format(log_format)

        self.settings.set_output_path_type(output_path_type)
        self.settings.set_delimiter(delimiter)
        self.settings.set_custom_delimiter(custom_delimiter)
        self.settings.set_auto_verify(auto_verify)
        self.settings.set_detailed_logging(detailed_logging)
        self.settings.set_ui_theme(ui_theme)
        self.settings.set_font_size(font_size)

        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
        self.accept()

    def reset_to_defaults(self):
        """
        Reset all settings to their default values.
        """
        confirm = QMessageBox.question(
            self, "Reset to Defaults", "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            # Reset each setting to its default value
            self.algo_combo.setCurrentText("CRC32")
            self.dir_edit.setText(os.getcwd())
            self.logging_checkbox.setChecked(True)
            self.log_path_edit.setText("sfv_checker_debug.log")
            self.format_combo.setCurrentText("TXT")
            self.path_type_combo.setCurrentText("Relative")
            self.delimiter_combo.setCurrentText("Space")
            self.custom_delimiter_edit.setText(" ")
            self.custom_delimiter_edit.setEnabled(False)
            self.auto_verify_checkbox.setChecked(False)
            self.detailed_logging_checkbox.setChecked(False)
            self.theme_combo.setCurrentText("Dark")
            self.font_size_spin.setValue(12)

            # Update settings
            self.settings.set_checksum_algorithm("CRC32")
            self.settings.set_default_directory(os.getcwd())
            self.settings.set_logging_enabled(True)
            self.settings.set_log_file_path("sfv_checker_debug.log")
            self.settings.set_log_format("TXT")

            self.settings.set_output_path_type("Relative")
            self.settings.set_delimiter("Space")
            self.settings.set_custom_delimiter(" ")
            self.settings.set_auto_verify(False)
            self.settings.set_detailed_logging(False)
            self.settings.set_ui_theme("Dark")
            self.settings.set_font_size(12)

            QMessageBox.information(self, "Reset", "All settings have been reset to their default values.")
