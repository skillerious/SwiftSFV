# settings.py

import json
import os
import logging
from threading import Lock

class AppSettings:
    _instance = None
    _lock = Lock()

    def __new__(cls, config_file='settings.json'):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AppSettings, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file='settings.json'):
        if self._initialized:
            return
        self.config_file = config_file
        self.settings = {
            "checksum_algorithm": "CRC32",
            "default_directory": os.path.expanduser("~"),
            "logging_enabled": True,
            "log_file_path": "sfv_checker_debug.log",
            "log_format": "TXT",
            "history": [],
            # New Settings
            "output_path_type": "Relative",  # Options: Relative, Absolute
            "delimiter": "Space",             # Options: Space, Tab, Custom
            "custom_delimiter": " ",          # Used if delimiter is Custom
            "auto_verify": False,             # Boolean
            "detailed_logging": False,        # Boolean
            "ui_theme": "Dark",               # Options: Dark, Light
            "font_size": 12                   # Integer
        }
        self.load_settings()
        self._initialized = True

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                logging.debug("Settings loaded successfully.")
            except Exception as e:
                logging.error(f"Error loading settings: {e}")
        else:
            self.save_settings()  # Save defaults if config does not exist
            logging.debug("Settings file not found. Created default settings.")

    def save_settings(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logging.debug("Settings saved successfully.")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")

    # Getter methods
    def get_checksum_algorithm(self):
        return self.settings.get("checksum_algorithm", "CRC32")

    def get_default_directory(self):
        return self.settings.get("default_directory", os.getcwd())

    def get_logging_enabled(self):
        return self.settings.get("logging_enabled", True)

    def get_log_file_path(self):
        return self.settings.get("log_file_path", "sfv_checker_debug.log")

    def get_log_format(self):
        return self.settings.get("log_format", "TXT")

    def get_history(self):
        return self.settings.get("history", [])

    # New Getter Methods
    def get_output_path_type(self):
        return self.settings.get("output_path_type", "Relative")

    def get_delimiter(self):
        return self.settings.get("delimiter", "Space")

    def get_custom_delimiter(self):
        return self.settings.get("custom_delimiter", " ")

    def get_auto_verify(self):
        return self.settings.get("auto_verify", False)

    def get_detailed_logging(self):
        return self.settings.get("detailed_logging", False)

    def get_ui_theme(self):
        return self.settings.get("ui_theme", "Dark")

    def get_font_size(self):
        return self.settings.get("font_size", 12)

    # Setter methods
    def set_checksum_algorithm(self, algorithm):
        self.settings["checksum_algorithm"] = algorithm
        self.save_settings()

    def set_default_directory(self, directory):
        self.settings["default_directory"] = directory
        self.save_settings()

    def set_logging_enabled(self, enabled):
        self.settings["logging_enabled"] = enabled
        self.save_settings()

    def set_log_file_path(self, path):
        self.settings["log_file_path"] = path
        self.save_settings()

    def set_log_format(self, format):
        self.settings["log_format"] = format
        self.save_settings()

    # New Setter Methods
    def set_output_path_type(self, path_type):
        self.settings["output_path_type"] = path_type
        self.save_settings()

    def set_delimiter(self, delimiter):
        self.settings["delimiter"] = delimiter
        self.save_settings()

    def set_custom_delimiter(self, delimiter):
        self.settings["custom_delimiter"] = delimiter
        self.save_settings()

    def set_auto_verify(self, auto):
        self.settings["auto_verify"] = auto
        self.save_settings()

    def set_detailed_logging(self, detailed):
        self.settings["detailed_logging"] = detailed
        self.save_settings()

    def set_ui_theme(self, theme):
        self.settings["ui_theme"] = theme
        self.save_settings()

    def set_font_size(self, size):
        if isinstance(size, int) and 8 <= size <= 24:
            self.settings["font_size"] = size
            self.save_settings()
        else:
            logging.warning(f"Attempted to set invalid font size: {size}")

    # History methods
    def add_history_entry(self, entry):
        self.settings["history"].append(entry)
        self.save_settings()

    def clear_history(self):
        self.settings["history"] = []
        self.save_settings()
