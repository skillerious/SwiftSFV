# settings_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QLineEdit, QPushButton, QFileDialog, QMessageBox, QSpinBox,
    QSpacerItem, QSizePolicy, QGroupBox, QTabWidget, QWidget
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
        self.setFixedSize(600, 600)
        self.settings = AppSettings()
        # Determine the base directory and images directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.images_dir = os.path.join(base_dir, 'images')
        self.init_ui()
        
    # Set window icon
        self.set_dialog_icon()

    def set_dialog_icon(self):
        """
        Set the window icon for the settings dialog.
        """
        icon_path = os.path.join(self.images_dir, 'settings.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            logging.debug(f"Set settings dialog icon to {icon_path}")
        else:
            logging.warning(f"Settings dialog icon not found: {icon_path}. Using default icon.")

    def init_ui(self):
        """
        Initialize the settings dialog UI components.
        """
        main_layout = QVBoxLayout()

        # Create Tab Widget
        tabs = QTabWidget()
        tabs.addTab(self.create_general_tab(), "General")
        tabs.addTab(self.create_advanced_tab(), "Advanced")
        tabs.addTab(self.create_notifications_tab(), "Notifications")
        tabs.addTab(self.create_updates_tab(), "Updates")
        tabs.addTab(self.create_appearance_tab(), "Appearance")
        tabs.addTab(self.create_history_tab(), "History")
        main_layout.addWidget(tabs)

        # Buttons: Save, Cancel, Reset to Defaults
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_button = QPushButton("Save")
        save_button.setIcon(self.load_icon('save_icon.png'))  # Ensure 'save_icon.png' exists
        save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("Cancel")
        cancel_button.setIcon(self.load_icon('cancel_icon.png'))  # Ensure 'cancel_icon.png' exists
        cancel_button.clicked.connect(self.reject)

        reset_button = QPushButton("Reset to Defaults")
        reset_button.setIcon(self.load_icon('reset_icon.png'))  # Ensure 'reset_icon.png' exists
        reset_button.clicked.connect(self.reset_to_defaults)

        button_layout.addWidget(reset_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def create_general_tab(self):
        """
        Create the General settings tab.
        """
        general_tab = QWidget()
        layout = QVBoxLayout()

        # Checksum Settings Group
        checksum_group = QGroupBox("Checksum Settings")
        checksum_layout = QVBoxLayout()

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
        algo_label.setToolTip("Select the checksum algorithm to use for generating and verifying checksums.")
        self.algo_combo.setToolTip("Select the checksum algorithm.")
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.algo_combo)
        checksum_layout.addLayout(algo_layout)

        # Default Directory Selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Default Directory:")
        self.dir_edit = QLineEdit()
        self.dir_edit.setText(self.settings.get_default_directory())
        dir_browse = QPushButton("Browse")
        dir_browse.setIcon(self.load_icon('folder.png'))  # Ensure 'folder.png' exists
        dir_browse.clicked.connect(self.browse_directory)
        dir_label.setToolTip("Set the default directory for opening and saving files.")
        self.dir_edit.setToolTip("Default directory path.")
        dir_browse.setToolTip("Browse for default directory.")
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(dir_browse)
        checksum_layout.addLayout(dir_layout)

        # Default SFV Filename
        sfv_filename_layout = QHBoxLayout()
        sfv_filename_label = QLabel("Default SFV Filename:")
        self.sfv_filename_edit = QLineEdit()
        self.sfv_filename_edit.setText(self.settings.get_default_sfv_filename())
        sfv_filename_label.setToolTip("Specify the default filename for generated SFV files.")
        self.sfv_filename_edit.setToolTip("Enter default SFV filename without extension.")
        sfv_filename_layout.addWidget(sfv_filename_label)
        sfv_filename_layout.addWidget(self.sfv_filename_edit)
        checksum_layout.addLayout(sfv_filename_layout)

        checksum_group.setLayout(checksum_layout)
        layout.addWidget(checksum_group)

        # Logging Settings Group
        logging_group = QGroupBox("Logging Settings")
        logging_layout = QVBoxLayout()

        # Logging Enabled Checkbox
        self.logging_checkbox = QCheckBox("Enable Logging")
        self.logging_checkbox.setChecked(self.settings.get_logging_enabled())
        self.logging_checkbox.setToolTip("Enable or disable logging of application activities.")
        logging_layout.addWidget(self.logging_checkbox)

        # Log File Path Selection
        log_path_layout = QHBoxLayout()
        log_path_label = QLabel("Log File Path:")
        self.log_path_edit = QLineEdit()
        self.log_path_edit.setText(self.settings.get_log_file_path())
        log_path_browse = QPushButton("Browse")
        log_path_browse.setIcon(self.load_icon('folder.png'))  # Reusing 'folder.png'
        log_path_browse.clicked.connect(self.browse_log_file)
        log_path_label.setToolTip("Set the file path where logs will be saved.")
        self.log_path_edit.setToolTip("Log file path.")
        log_path_browse.setToolTip("Browse for log file.")
        log_path_layout.addWidget(log_path_label)
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(log_path_browse)
        logging_layout.addLayout(log_path_layout)

        # Log Format Selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Log Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "CSV"])
        self.format_combo.setCurrentText(self.settings.get_log_format())
        format_label.setToolTip("Select the format for log files.")
        self.format_combo.setToolTip("Log file format.")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        logging_layout.addLayout(format_layout)

        # Auto-Save Logs
        self.auto_save_logs_checkbox = QCheckBox("Auto-Save Logs")
        self.auto_save_logs_checkbox.setChecked(self.settings.get_auto_save_logs())
        self.auto_save_logs_checkbox.setToolTip("Automatically save logs without prompting.")
        logging_layout.addWidget(self.auto_save_logs_checkbox)

        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)

        layout.addStretch()
        general_tab.setLayout(layout)
        return general_tab

    def create_advanced_tab(self):
        """
        Create the Advanced settings tab.
        """
        advanced_tab = QWidget()
        layout = QVBoxLayout()

        # Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()

        # Output Path Type Selection
        path_type_layout = QHBoxLayout()
        path_type_label = QLabel("Output Path Type:")
        self.path_type_combo = QComboBox()
        self.path_type_combo.addItems(["Relative", "Absolute"])
        self.path_type_combo.setCurrentText(self.settings.get_output_path_type())
        path_type_label.setToolTip("Choose whether to use relative or absolute paths in SFV files.")
        self.path_type_combo.setToolTip("Select path type for SFV entries.")
        path_type_layout.addWidget(path_type_label)
        path_type_layout.addWidget(self.path_type_combo)
        output_layout.addLayout(path_type_layout)

        # Delimiter Selection with Dynamic Custom Delimiter
        delimiter_layout = QHBoxLayout()
        delimiter_label = QLabel("Delimiter:")
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(["Space", "Tab", "Custom"])
        self.delimiter_combo.setCurrentText(self.settings.get_delimiter())
        self.delimiter_combo.currentTextChanged.connect(self.toggle_custom_delimiter)
        delimiter_label.setToolTip("Select the delimiter used between file paths and checksums in SFV files.")
        self.delimiter_combo.setToolTip("Select delimiter type.")
        delimiter_layout.addWidget(delimiter_label)
        delimiter_layout.addWidget(self.delimiter_combo)

        self.custom_delimiter_edit = QLineEdit()
        self.custom_delimiter_edit.setText(self.settings.get_custom_delimiter())
        self.custom_delimiter_edit.setEnabled(self.settings.get_delimiter() == "Custom")
        self.custom_delimiter_edit.setPlaceholderText("Enter custom delimiter")
        self.custom_delimiter_edit.setToolTip("Specify a custom delimiter.")
        delimiter_layout.addWidget(self.custom_delimiter_edit)
        output_layout.addLayout(delimiter_layout)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Additional Settings Group
        additional_group = QGroupBox("Additional Settings")
        additional_layout = QVBoxLayout()

        # Automatically Verify After Generation Checkbox
        self.auto_verify_checkbox = QCheckBox("Automatically Verify SFV After Generation")
        self.auto_verify_checkbox.setChecked(self.settings.get_auto_verify())
        self.auto_verify_checkbox.setToolTip("Automatically verify files after generating an SFV file.")
        additional_layout.addWidget(self.auto_verify_checkbox)

        # Detailed Logging Checkbox
        self.detailed_logging_checkbox = QCheckBox("Enable Detailed Logging")
        self.detailed_logging_checkbox.setChecked(self.settings.get_detailed_logging())
        self.detailed_logging_checkbox.setToolTip("Enable detailed logging for debugging purposes.")
        additional_layout.addWidget(self.detailed_logging_checkbox)

        # Checksum Comparison Mode
        checksum_mode_layout = QHBoxLayout()
        checksum_mode_label = QLabel("Checksum Comparison Mode:")
        self.checksum_mode_combo = QComboBox()
        self.checksum_mode_combo.addItems(["Quick", "Full"])
        self.checksum_mode_combo.setCurrentText(self.settings.get_checksum_comparison_mode())
        checksum_mode_label.setToolTip("Select between quick or full checksum comparison.")
        self.checksum_mode_combo.setToolTip("Quick compares file size and modification date; Full computes checksums.")
        checksum_mode_layout.addWidget(checksum_mode_label)
        checksum_mode_layout.addWidget(self.checksum_mode_combo)
        additional_layout.addLayout(checksum_mode_layout)

        # Number of Threads
        num_threads_layout = QHBoxLayout()
        num_threads_label = QLabel("Number of Threads:")
        self.num_threads_spin = QSpinBox()
        self.num_threads_spin.setRange(1, 32)
        self.num_threads_spin.setValue(self.settings.get_num_threads())
        num_threads_label.setToolTip("Set the number of threads for checksum calculations.")
        self.num_threads_spin.setToolTip("Set number of threads (1-32).")
        num_threads_layout.addWidget(num_threads_label)
        num_threads_layout.addWidget(self.num_threads_spin)
        additional_layout.addLayout(num_threads_layout)

        # Exclude File Types
        exclude_types_layout = QHBoxLayout()
        exclude_types_label = QLabel("Exclude File Types:")
        self.exclude_types_edit = QLineEdit()
        self.exclude_types_edit.setText(", ".join(self.settings.get_exclude_file_types()))
        exclude_types_label.setToolTip("Specify file extensions to exclude, separated by commas (e.g., .tmp, .bak).")
        self.exclude_types_edit.setToolTip("Enter file extensions to exclude.")
        exclude_types_layout.addWidget(exclude_types_label)
        exclude_types_layout.addWidget(self.exclude_types_edit)
        additional_layout.addLayout(exclude_types_layout)

        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)

        layout.addStretch()
        advanced_tab.setLayout(layout)
        return advanced_tab

    def create_notifications_tab(self):
        """
        Create the Notifications settings tab.
        """
        notifications_tab = QWidget()
        layout = QVBoxLayout()

        # Notifications Settings Group
        notifications_group = QGroupBox("Notifications Settings")
        notifications_layout = QVBoxLayout()

        # Enable Notifications Checkbox
        self.enable_notifications_checkbox = QCheckBox("Enable Desktop Notifications")
        self.enable_notifications_checkbox.setChecked(self.settings.get_enable_notifications())
        self.enable_notifications_checkbox.setToolTip("Enable or disable desktop notifications for operations.")
        notifications_layout.addWidget(self.enable_notifications_checkbox)

        notifications_group.setLayout(notifications_layout)
        layout.addWidget(notifications_group)

        layout.addStretch()
        notifications_tab.setLayout(layout)
        return notifications_tab

    def create_updates_tab(self):
        """
        Create the Updates settings tab.
        """
        updates_tab = QWidget()
        layout = QVBoxLayout()

        # Updates Settings Group
        updates_group = QGroupBox("Updates Settings")
        updates_layout = QVBoxLayout()

        # Check for Updates Checkbox
        self.check_updates_checkbox = QCheckBox("Automatically Check for Updates")
        self.check_updates_checkbox.setChecked(self.settings.get_check_for_updates())
        self.check_updates_checkbox.setToolTip("Enable or disable automatic checking for application updates.")
        updates_layout.addWidget(self.check_updates_checkbox)

        updates_group.setLayout(updates_layout)
        layout.addWidget(updates_group)

        layout.addStretch()
        updates_tab.setLayout(layout)
        return updates_tab

    def create_appearance_tab(self):
        """
        Create the Appearance settings tab.
        """
        appearance_tab = QWidget()
        layout = QVBoxLayout()

        # UI Theme Selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("UI Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get_ui_theme())
        theme_label.setToolTip("Select the UI theme.")
        self.theme_combo.setToolTip("Choose between dark and light themes.")
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font Size Adjustment
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.settings.get_font_size())
        font_size_label.setToolTip("Adjust the font size of the application.")
        self.font_size_spin.setToolTip("Set font size.")
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_spin)
        layout.addLayout(font_size_layout)

        # Language Selection
        language_layout = QHBoxLayout()
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French"])  # Example languages
        self.language_combo.setCurrentText(self.settings.get_language())
        language_label.setToolTip("Select the application language.")
        self.language_combo.setToolTip("Choose language.")
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)

        layout.addStretch()
        appearance_tab.setLayout(layout)
        return appearance_tab

    def create_history_tab(self):
        """
        Create the History settings tab.
        """
        history_tab = QWidget()
        layout = QVBoxLayout()

        # History Settings Group
        history_group = QGroupBox("History Settings")
        history_layout = QVBoxLayout()

        # Recent Files Limit
        recent_files_layout = QHBoxLayout()
        recent_files_label = QLabel("Recent Files Limit:")
        self.recent_files_spin = QSpinBox()
        self.recent_files_spin.setRange(1, 100)
        self.recent_files_spin.setValue(self.settings.get_recent_files_limit())
        recent_files_label.setToolTip("Set the maximum number of recent files/directories to keep in history.")
        self.recent_files_spin.setToolTip("Set recent files limit.")
        recent_files_layout.addWidget(recent_files_label)
        recent_files_layout.addWidget(self.recent_files_spin)
        history_layout.addLayout(recent_files_layout)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        layout.addStretch()
        history_tab.setLayout(layout)
        return history_tab

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
        auto_save_logs = self.auto_save_logs_checkbox.isChecked()

        default_sfv_filename = self.sfv_filename_edit.text()

        output_path_type = self.path_type_combo.currentText()
        delimiter = self.delimiter_combo.currentText()
        custom_delimiter = self.custom_delimiter_edit.text() if delimiter == "Custom" else " "
        auto_verify = self.auto_verify_checkbox.isChecked()
        detailed_logging = self.detailed_logging_checkbox.isChecked()

        checksum_comparison_mode = self.checksum_mode_combo.currentText()
        num_threads = self.num_threads_spin.value()
        exclude_file_types = [ext.strip() for ext in self.exclude_types_edit.text().split(',') if ext.strip()]

        enable_notifications = self.enable_notifications_checkbox.isChecked()
        check_for_updates = self.check_updates_checkbox.isChecked()

        ui_theme = self.theme_combo.currentText()
        font_size = self.font_size_spin.value()
        language = self.language_combo.currentText()

        recent_files_limit = self.recent_files_spin.value()

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

        if not default_sfv_filename:
            QMessageBox.warning(self, "Invalid SFV Filename", "Please specify a default SFV filename.")
            return

        # Save settings
        self.settings.set_checksum_algorithm(algorithm)
        self.settings.set_default_directory(default_dir)
        self.settings.set_logging_enabled(logging_enabled)
        self.settings.set_log_file_path(log_file_path)
        self.settings.set_log_format(log_format)
        self.settings.set_auto_save_logs(auto_save_logs)
        self.settings.set_default_sfv_filename(default_sfv_filename)

        self.settings.set_output_path_type(output_path_type)
        self.settings.set_delimiter(delimiter)
        self.settings.set_custom_delimiter(custom_delimiter)
        self.settings.set_auto_verify(auto_verify)
        self.settings.set_detailed_logging(detailed_logging)
        self.settings.set_checksum_comparison_mode(checksum_comparison_mode)
        self.settings.set_num_threads(num_threads)
        self.settings.set_exclude_file_types(exclude_file_types)

        self.settings.set_enable_notifications(enable_notifications)
        self.settings.set_check_for_updates(check_for_updates)

        self.settings.set_ui_theme(ui_theme)
        self.settings.set_font_size(font_size)
        self.settings.set_language(language)

        self.settings.set_recent_files_limit(recent_files_limit)

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
            self.dir_edit.setText(os.path.expanduser("~"))
            self.logging_checkbox.setChecked(True)
            self.log_path_edit.setText("sfv_checker_debug.log")
            self.format_combo.setCurrentText("TXT")
            self.auto_save_logs_checkbox.setChecked(False)
            self.sfv_filename_edit.setText("checksum")

            self.path_type_combo.setCurrentText("Relative")
            self.delimiter_combo.setCurrentText("Space")
            self.custom_delimiter_edit.setText(" ")
            self.custom_delimiter_edit.setEnabled(False)
            self.auto_verify_checkbox.setChecked(False)
            self.detailed_logging_checkbox.setChecked(False)
            self.checksum_mode_combo.setCurrentText("Full")
            self.num_threads_spin.setValue(4)
            self.exclude_types_edit.setText("")

            self.enable_notifications_checkbox.setChecked(True)
            self.check_updates_checkbox.setChecked(True)

            self.theme_combo.setCurrentText("Dark")
            self.font_size_spin.setValue(12)
            self.language_combo.setCurrentText("English")

            self.recent_files_spin.setValue(10)

            # Update settings
            self.settings.set_checksum_algorithm("CRC32")
            self.settings.set_default_directory(os.path.expanduser("~"))
            self.settings.set_logging_enabled(True)
            self.settings.set_log_file_path("sfv_checker_debug.log")
            self.settings.set_log_format("TXT")
            self.settings.set_auto_save_logs(False)
            self.settings.set_default_sfv_filename("checksum")

            self.settings.set_output_path_type("Relative")
            self.settings.set_delimiter("Space")
            self.settings.set_custom_delimiter(" ")
            self.settings.set_auto_verify(False)
            self.settings.set_detailed_logging(False)
            self.settings.set_checksum_comparison_mode("Full")
            self.settings.set_num_threads(4)
            self.settings.set_exclude_file_types([])

            self.settings.set_enable_notifications(True)
            self.settings.set_check_for_updates(True)

            self.settings.set_ui_theme("Dark")
            self.settings.set_font_size(12)
            self.settings.set_language("English")

            self.settings.set_recent_files_limit(10)

            QMessageBox.information(self, "Reset", "All settings have been reset to their default values.")

