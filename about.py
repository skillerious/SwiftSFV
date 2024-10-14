# about.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit, QWidget, QSizePolicy, QSpacerItem, QFileDialog
)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor, QDesktopServices
from PyQt6.QtCore import Qt, QUrl
import os
import logging

class AboutDialog(QDialog):
    """
    AboutDialog provides comprehensive information about the SwiftSFV application,
    including its purpose, version, author, license, and other relevant details.
    It features a logo, structured layout, and interactive links.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SwiftSFV")
        self.setFixedSize(500, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        # Determine the base directory and images directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.images_dir = os.path.join(base_dir, 'images')
        self.init_ui()
        
         # Set window icon
        self.set_dialog_icon()

    def init_ui(self):
        """
        Initialize the About dialog UI components with enhanced styling and layout.
        """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Logo
        logo_label = QLabel()
        logo_pixmap = self.load_pixmap('logo1.png')  # Ensure 'logo.png' exists in 'images' directory
        if logo_pixmap:
            logo_pixmap = logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(logo_label)
        else:
            # Placeholder if logo is not found
            placeholder = QLabel("SwiftSFV")
            placeholder.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(placeholder)

        # Application Name
        app_name = QLabel("SwiftSFV")
        app_name.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("color: #2980B9;")
        main_layout.addWidget(app_name)

        # Version Information
        version = QLabel("Version: 1.0.0")
        version.setFont(QFont("Segoe UI", 12))
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #2980B9;")
        main_layout.addWidget(version)

        # Author Information
        author = QLabel("Author: Robin Lee Doak")
        author.setFont(QFont("Segoe UI", 12))
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author.setStyleSheet("color: #2980B9;")
        main_layout.addWidget(author)

        # Description
        description = QLabel(
            "SwiftSFV is a robust file verification tool designed to generate and verify SFV files using various checksum algorithms. "
            "Ensure the integrity of your files with ease."
        )
        description.setFont(QFont("Segoe UI", 10))
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #7f8c8d;")
        main_layout.addWidget(description)

        # Spacer
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # License Information
        license_label = QLabel("License: MIT License")
        license_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_label.setStyleSheet("color: #2980b9; text-decoration: underline;")
        license_label.setCursor(Qt.CursorShape.PointingHandCursor)
        license_label.mousePressEvent = self.open_license_link  # Make it clickable
        main_layout.addWidget(license_label)

        # Documentation Link
        doc_label = QLabel("Documentation")
        doc_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        doc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        doc_label.setStyleSheet("color: #2980b9; text-decoration: underline;")
        doc_label.setCursor(Qt.CursorShape.PointingHandCursor)
        doc_label.mousePressEvent = self.open_documentation_link  # Make it clickable
        main_layout.addWidget(doc_label)

        # GitHub Repository Link
        github_label = QLabel("GitHub Repository")
        github_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        github_label.setStyleSheet("color: #2980b9; text-decoration: underline;")
        github_label.setCursor(Qt.CursorShape.PointingHandCursor)
        github_label.mousePressEvent = self.open_github_link  # Make it clickable
        main_layout.addWidget(github_label)

        # Spacer
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Close Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.setIcon(self.load_icon('close_icon.png'))  # Ensure 'close_icon.png' exists
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        
    def set_dialog_icon(self):
        """
        Set the window icon for the about dialog.
        """
        icon_path = os.path.join(self.images_dir, 'about.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            logging.debug(f"Set about dialog icon to {icon_path}")
        else:
            logging.warning(f"About dialog icon not found: {icon_path}. Using default icon.")

    def load_pixmap(self, pixmap_name):
        """
        Load a pixmap from the images directory.

        Parameters:
            pixmap_name (str): The filename of the pixmap.

        Returns:
            QPixmap or None: The loaded pixmap, or None if not found.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(base_dir, 'images')
        pixmap_path = os.path.join(images_dir, pixmap_name)
        if os.path.exists(pixmap_path):
            return QPixmap(pixmap_path)
        else:
            logging.warning(f"Pixmap not found: {pixmap_path}.")
            return None

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

    def open_license_link(self, event):
        """
        Open the license URL in the default web browser.

        Parameters:
            event: The mouse press event.
        """
        QDesktopServices.openUrl(QUrl("https://github.com/skillerious/SwiftSFV/blob/main/LICENSE"))

    def open_documentation_link(self, event):
        """
        Open the documentation URL in the default web browser.

        Parameters:
            event: The mouse press event.
        """
        QDesktopServices.openUrl(QUrl("https://github.com/skillerious/SwiftSFV/blob/main/README.md"))

    def open_github_link(self, event):
        """
        Open the GitHub repository URL in the default web browser.

        Parameters:
            event: The mouse press event.
        """
        QDesktopServices.openUrl(QUrl("https://github.com/skillerious/SwiftSFV"))
