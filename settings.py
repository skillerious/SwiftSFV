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
            "output_path_type": "Relative",   # Options: Relative, Absolute
            "delimiter": "Space",             # Options: Space, Tab, Custom
            "custom_delimiter": " ",          # Used if delimiter is Custom
            "auto_verify": False,             # Boolean
            "detailed_logging": False,        # Boolean
            "ui_theme": "Dark",               # Options: Dark, Light
            "font_size": 12,                  # Integer
            "language": "English",
            # New Settings
            "recent_files_limit": 10,             # Integer
            "enable_notifications": True,         # Boolean
            "default_sfv_filename": "checksum",   # String
            "check_for_updates": True,            # Boolean
            "checksum_comparison_mode": "Full",   # Options: Quick, Full
            "num_threads": 4,                     # Integer
            "auto_save_logs": False,              # Boolean
            "backup_original_sfv": True,          # Boolean
            "exclude_file_types": [],             # List of strings (file extensions)
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

    def get_language(self):
        return self.settings.get("language", "English")

    def get_recent_files_limit(self):
        return self.settings.get("recent_files_limit", 10)

    def get_enable_notifications(self):
        return self.settings.get("enable_notifications", True)

    def get_default_sfv_filename(self):
        return self.settings.get("default_sfv_filename", "checksum")

    def get_check_for_updates(self):
        return self.settings.get("check_for_updates", True)

    def get_checksum_comparison_mode(self):
        return self.settings.get("checksum_comparison_mode", "Full")

    def get_num_threads(self):
        return self.settings.get("num_threads", 4)

    def get_auto_save_logs(self):
        return self.settings.get("auto_save_logs", False)

    def get_backup_original_sfv(self):
        return self.settings.get("backup_original_sfv", True)

    def get_exclude_file_types(self):
        return self.settings.get("exclude_file_types", [])

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

    def set_language(self, language):
        self.settings["language"] = language
        self.save_settings()

    def set_recent_files_limit(self, limit):
        if isinstance(limit, int) and limit > 0:
            self.settings["recent_files_limit"] = limit
            self.save_settings()
        else:
            logging.warning(f"Attempted to set invalid recent files limit: {limit}")

    def set_enable_notifications(self, enable):
        self.settings["enable_notifications"] = enable
        self.save_settings()

    def set_default_sfv_filename(self, filename):
        self.settings["default_sfv_filename"] = filename
        self.save_settings()

    def set_check_for_updates(self, check):
        self.settings["check_for_updates"] = check
        self.save_settings()

    def set_checksum_comparison_mode(self, mode):
        if mode in ["Quick", "Full"]:
            self.settings["checksum_comparison_mode"] = mode
            self.save_settings()
        else:
            logging.warning(f"Attempted to set invalid checksum comparison mode: {mode}")

    def set_num_threads(self, num):
        if isinstance(num, int) and num > 0:
            self.settings["num_threads"] = num
            self.save_settings()
        else:
            logging.warning(f"Attempted to set invalid number of threads: {num}")

    def set_auto_save_logs(self, auto_save):
        self.settings["auto_save_logs"] = auto_save
        self.save_settings()

    def set_backup_original_sfv(self, backup):
        self.settings["backup_original_sfv"] = backup
        self.save_settings()

    def set_exclude_file_types(self, file_types):
        if isinstance(file_types, list):
            self.settings["exclude_file_types"] = file_types
            self.save_settings()
        else:
            logging.warning(f"Attempted to set invalid exclude file types: {file_types}")

    # History methods
    def add_history_entry(self, entry):
        self.settings["history"].append(entry)
        # Enforce recent files limit
        if len(self.settings["history"]) > self.get_recent_files_limit():
            self.settings["history"] = self.settings["history"][-self.get_recent_files_limit():]
        self.save_settings()

    def clear_history(self):
        self.settings["history"] = []
        self.save_settings()
