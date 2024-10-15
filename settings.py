# settings.py

import json
import os
import logging

class AppSettings:
    """
    AppSettings manages application settings, providing methods to get and set various configuration options.
    Settings are stored in a JSON file for persistence.
    """

    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser("~"), '.sfv_checker_settings.json')
        self.settings = {}
        self.load_settings()

        # General Settings
        self.checksum_algorithm = self.settings.get('checksum_algorithm', 'CRC32')
        self.default_directory = self.settings.get('default_directory', os.path.expanduser("~"))
        self.logging_enabled = self.settings.get('logging_enabled', True)
        self.log_file_path = self.settings.get('log_file_path', 'sfv_checker_debug.log')
        self.log_format = self.settings.get('log_format', 'TXT')
        self.auto_save_logs = self.settings.get('auto_save_logs', False)
        self.default_sfv_filename = self.settings.get('default_sfv_filename', 'checksum')

        # Advanced Settings
        self.output_path_type = self.settings.get('output_path_type', 'Relative')
        self.delimiter = self.settings.get('delimiter', 'Space')
        self.custom_delimiter = self.settings.get('custom_delimiter', ' ')
        self.auto_verify = self.settings.get('auto_verify', False)
        self.detailed_logging = self.settings.get('detailed_logging', False)
        self.checksum_comparison_mode = self.settings.get('checksum_comparison_mode', 'Full')
        self.num_threads = self.settings.get('num_threads', 4)
        self.exclude_file_types = self.settings.get('exclude_file_types', [])

        # Notifications Settings
        self.enable_notifications = self.settings.get('enable_notifications', True)

        # Updates Settings
        self.check_for_updates = self.settings.get('check_for_updates', True)

        # Appearance Settings
        self.theme = self.settings.get('theme', 'Dark')
        self.font_size = self.settings.get('font_size', 12)
        self.language = self.settings.get('language', 'English')

        # History Settings
        self.recent_files_limit = self.settings.get('recent_files_limit', 10)
        self.history = self.settings.get('history', [])
        

    def load_settings(self):
        """
        Load settings from the JSON file.
        """
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                logging.debug("Settings loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
                self.settings = {}
        else:
            logging.info("Settings file not found. Using default settings.")
            self.settings = {}

    def save_settings(self):
        """
        Save settings to the JSON file.
        """
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logging.debug("Settings saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    # Getter and Setter methods for each setting

    # General Settings
    def get_checksum_algorithm(self):
        return self.checksum_algorithm

    def set_checksum_algorithm(self, value):
        self.checksum_algorithm = value
        self.settings['checksum_algorithm'] = value
        self.save_settings()

    def get_default_directory(self):
        return self.default_directory

    def set_default_directory(self, value):
        self.default_directory = value
        self.settings['default_directory'] = value
        self.save_settings()

    def get_logging_enabled(self):
        return self.logging_enabled

    def set_logging_enabled(self, value):
        self.logging_enabled = value
        self.settings['logging_enabled'] = value
        self.save_settings()

    def get_log_file_path(self):
        return self.log_file_path

    def set_log_file_path(self, value):
        self.log_file_path = value
        self.settings['log_file_path'] = value
        self.save_settings()

    def get_log_format(self):
        return self.log_format

    def set_log_format(self, value):
        self.log_format = value
        self.settings['log_format'] = value
        self.save_settings()

    def get_auto_save_logs(self):
        return self.auto_save_logs

    def set_auto_save_logs(self, value):
        self.auto_save_logs = value
        self.settings['auto_save_logs'] = value
        self.save_settings()

    def get_default_sfv_filename(self):
        return self.default_sfv_filename

    def set_default_sfv_filename(self, value):
        self.default_sfv_filename = value
        self.settings['default_sfv_filename'] = value
        self.save_settings()

    # Advanced Settings
    def get_output_path_type(self):
        return self.output_path_type

    def set_output_path_type(self, value):
        self.output_path_type = value
        self.settings['output_path_type'] = value
        self.save_settings()

    def get_delimiter(self):
        return self.delimiter

    def set_delimiter(self, value):
        self.delimiter = value
        self.settings['delimiter'] = value
        self.save_settings()

    def get_custom_delimiter(self):
        return self.custom_delimiter

    def set_custom_delimiter(self, value):
        self.custom_delimiter = value
        self.settings['custom_delimiter'] = value
        self.save_settings()

    def get_auto_verify(self):
        return self.auto_verify

    def set_auto_verify(self, value):
        self.auto_verify = value
        self.settings['auto_verify'] = value
        self.save_settings()

    def get_detailed_logging(self):
        return self.detailed_logging

    def set_detailed_logging(self, value):
        self.detailed_logging = value
        self.settings['detailed_logging'] = value
        self.save_settings()

    def get_checksum_comparison_mode(self):
        return self.checksum_comparison_mode

    def set_checksum_comparison_mode(self, value):
        self.checksum_comparison_mode = value
        self.settings['checksum_comparison_mode'] = value
        self.save_settings()

    def get_num_threads(self):
        return self.num_threads

    def set_num_threads(self, value):
        self.num_threads = value
        self.settings['num_threads'] = value
        self.save_settings()

    def get_exclude_file_types(self):
        return self.exclude_file_types

    def set_exclude_file_types(self, value):
        self.exclude_file_types = value
        self.settings['exclude_file_types'] = value
        self.save_settings()

    # Notifications Settings
    def get_enable_notifications(self):
        return self.enable_notifications

    def set_enable_notifications(self, value):
        self.enable_notifications = value
        self.settings['enable_notifications'] = value
        self.save_settings()

    # Updates Settings
    def get_check_for_updates(self):
        return self.check_for_updates

    def set_check_for_updates(self, value):
        self.check_for_updates = value
        self.settings['check_for_updates'] = value
        self.save_settings()

    # Appearance Settings
    def get_theme(self):
        return self.theme

    def set_theme(self, value):
        self.theme = value
        self.settings['theme'] = value
        self.save_settings()

    def get_font_size(self):
        return self.font_size

    def set_font_size(self, value):
        self.font_size = value
        self.settings['font_size'] = value
        self.save_settings()

    def get_language(self):
        return self.language

    def set_language(self, value):
        self.language = value
        self.settings['language'] = value
        self.save_settings()

    # History Settings
    def get_recent_files_limit(self):
        return self.recent_files_limit

    def set_recent_files_limit(self, value):
        self.recent_files_limit = value
        self.settings['recent_files_limit'] = value
        self.save_settings()

    def get_history(self):
        return self.history

    def add_history_entry(self, entry):
        self.history.append(entry)
        # Limit the history based on recent_files_limit
        self.history = self.history[-self.recent_files_limit:]
        self.settings['history'] = self.history
        self.save_settings()

    def clear_history(self):
        self.history = []
        self.settings['history'] = self.history
        self.save_settings()
