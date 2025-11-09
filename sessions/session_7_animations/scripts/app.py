"""
Main application class using PySide6 (Qt).
Manages the GUI and coordinates with Unity via IPC.
VERSION SESSION 7 - ANIMATIONS & TRANSITIONS
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMenuBar, QMenu,
    QTabWidget, QSlider, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from ..ipc.unity_bridge import UnityBridge
from ..utils.config import Config

logger = logging.getLogger(__name__)

# Fix pour afficher l'icône dans la taskbar Windows
try:
    import ctypes
    # Définir un AppUserModelID unique pour l'application
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Xyon15.DesktopMate.1.0')
except Exception as e:
    logger.warning(f"Impossible de définir AppUserModelID: {e}")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.unity_bridge = UnityBridge()
        self.vrm_loaded = False  # Track if VRM model is loaded
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Desktop-Mate Control Panel")
        self.setGeometry(100, 100, 900, 700)
        
        # Set window icon
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "mura_fond_violet._ico.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            logger.warning(f"Icon not found at {icon_path}")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Header
        header = QLabel("Desktop-Mate Control Panel")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(header)
        
        # Unity connection status
        self.status_label = QLabel("Statut Unity : Non connecté")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_connexion_tab()
        self.create_expressions_tab()
        
        # Status timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Check every second

    def create_connexion_tab(self):
        """Create the Unity connexion tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connexion à Unity")
        self.connect_btn.clicked.connect(self.connect_unity)
        button_layout.addWidget(self.connect_btn)
        
        self.load_vrm_btn = QPushButton("Charger modèle VRM")
        self.load_vrm_btn.clicked.connect(self.toggle_vrm_model)
        self.load_vrm_btn.setEnabled(False)
        button_layout.addWidget(self.load_vrm_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.tabs.addTab(tab, "Connexion")

    def create_expressions_tab(self):
        """Create the facial expressions tab with sliders."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Group box for expressions
        expressions_group = QGroupBox("Expressions Faciales")
        expressions_layout = QVBoxLayout()
        expressions_group.setLayout(expressions_layout)
        
        # Dictionary to store sliders and labels
        self.expression_sliders = {}
        self.expression_labels = {}
        
        # List of expressions with emoji and names
        expressions = [
            ("joy", "😊 Joy (Joyeux)"),
            ("angry", "😠 Angry (En colère)"),
            ("sorrow", "😢 Sorrow (Triste)"),
            ("surprised", "😲 Surprised (Surpris)"),
            ("fun", "😄 Fun (Amusé)")
        ]
        
        # Create slider for each expression
        for expr_id, expr_label in expressions:
            # Container for this expression
            expr_container = QWidget()
            expr_layout = QVBoxLayout()
            expr_container.setLayout(expr_layout)
            
            # Label with current value
            value_label = QLabel(f"{expr_label}: 0%")
            value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            expr_layout.addWidget(value_label)
            
            # Slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(0)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(10)
            
            # Connect slider to handler
            slider.valueChanged.connect(
                lambda value, eid=expr_id, lbl=value_label, orig_text=expr_label: 
                    self.on_expression_slider_change(eid, lbl, orig_text, value)
            )
            
            expr_layout.addWidget(slider)
            
            # Store references
            self.expression_sliders[expr_id] = slider
            self.expression_labels[expr_id] = value_label
            
            expressions_layout.addWidget(expr_container)
        
        layout.addWidget(expressions_group)
        
        # Transition speed control
        speed_group = QGroupBox("Contrôle des Transitions")
        speed_layout = QVBoxLayout()
        speed_group.setLayout(speed_layout)
        
        # Label with current speed (will be updated by slider)
        self.speed_label = QLabel("Vitesse de transition : 3.0 (Normal)")
        self.speed_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        speed_layout.addWidget(self.speed_label)
        
        # Speed slider (left=slow, right=fast)
        # Slider value 10-100 maps directly to 1.0-10.0
        speed_slider = QSlider(Qt.Orientation.Horizontal)
        speed_slider.setMinimum(10)  # Maps to 1.0 (slowest - reasonable minimum)
        speed_slider.setMaximum(100) # Maps to 10.0 (fastest)
        speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        speed_slider.setTickInterval(10)  # Ticks at: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
        
        # Block signals during initialization to prevent premature commands
        speed_slider.blockSignals(True)
        speed_slider.setValue(30)    # Maps to 3.0 (default - Normal speed) - ON A TICK!
        speed_slider.blockSignals(False)
        
        # Store slider reference
        self.speed_slider = speed_slider
        
        # Connect slider to handler AFTER setting initial value
        speed_slider.valueChanged.connect(self.on_speed_slider_change)
        
        # Manually trigger initial label update
        self.on_speed_slider_change(30)
        
        speed_layout.addWidget(speed_slider)
        
        # Add speed descriptions with markers (left=slow, center=normal at 3.0, right=fast)
        speed_desc_layout = QHBoxLayout()
        speed_desc_layout.setSpacing(0)
        speed_desc_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left label (slow) - positioned at the start
        left_label = QLabel("← Plus lent")
        left_label.setStyleSheet("font-size: 11px; color: gray;")
        left_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        speed_desc_layout.addWidget(left_label, stretch=0)
        
        # Stretch to position "3.0 (Normal)" at the right spot
        # Slider range: 10-100 (90 units), 3.0 is at position 30 (20 units from start)
        # Fine-tuned ratio: Slightly more space before to center better
        speed_desc_layout.addStretch(12)  # Space before "3.0 (Normal)"
        
        # Center label (normal at 3.0) - positioned at tick 30
        center_label = QLabel("3.0 (Normal)")
        center_label.setStyleSheet("font-size: 11px; color: #4A90E2; font-weight: bold;")
        center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        speed_desc_layout.addWidget(center_label, stretch=0)
        
        # Stretch to fill the rest of the space
        speed_desc_layout.addStretch(60)  # Space after "3.0 (Normal)"
        
        # Right label (fast) - positioned at the end
        right_label = QLabel("Plus rapide →")
        right_label.setStyleSheet("font-size: 11px; color: gray;")
        right_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        speed_desc_layout.addWidget(right_label, stretch=0)
        
        speed_layout.addLayout(speed_desc_layout)
        
        layout.addWidget(speed_group)
        
        # Reset button
        reset_layout = QHBoxLayout()
        reset_btn = QPushButton("Réinitialiser toutes les expressions")
        reset_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        reset_btn.clicked.connect(self.reset_all_expressions)
        reset_layout.addStretch()
        reset_layout.addWidget(reset_btn)
        reset_layout.addStretch()
        layout.addLayout(reset_layout)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Expressions")

    def on_expression_slider_change(self, expression_id: str, label: QLabel, 
                                    original_text: str, value: int):
        """Handle expression slider value change.
        
        Args:
            expression_id: ID of the expression (e.g., "joy")
            label: QLabel to update with new value
            original_text: Original label text with emoji
            value: Slider value (0-100)
        """
        # Update label with current value
        label.setText(f"{original_text}: {value}%")
        
        # Send to Unity if connected
        if self.unity_bridge.is_connected():
            # Convert 0-100 to 0.0-1.0
            normalized_value = value / 100.0
            self.unity_bridge.set_expression(expression_id, normalized_value)
            logger.debug(f"Set expression {expression_id} to {normalized_value:.2f}")

    def on_speed_slider_change(self, value: int):
        """Handle transition speed slider value change.
        
        Args:
            value: Slider value (10-100) maps directly to speed
                  10 (left) = 1.0 (slowest transition)
                  20 (default) = 2.0 (normal - ON A TICK!)
                  100 (right) = 10.0 (fastest transition)
        """
        # Direct mapping: slider 10-100 to speed 1.0-10.0
        # Unity Lerp: Higher transitionSpeed = faster transition
        speed = value / 10.0
        
        # Clamp to ensure we stay in valid range
        speed = max(0.1, min(10.0, speed))
        
        # Update label with current speed
        # In Unity: Higher transitionSpeed = faster Lerp
        # Range: 1.0-10.0 (since minimum is now 10 on slider)
        # 3.0 is marked as "Normal" in the UI
        if speed <= 1.5:
            speed_text = "Très lent"
        elif speed <= 2.2:
            speed_text = "Lent"
        elif speed <= 4.0:
            speed_text = "Normal"
        elif speed <= 6.5:
            speed_text = "Rapide"
        else:
            speed_text = "Très rapide"
        
        self.speed_label.setText(f"Vitesse de transition : {speed:.1f} ({speed_text})")
        
        # Send to Unity only if connected AND VRM is loaded
        if self.unity_bridge.is_connected() and self.vrm_loaded:
            self.unity_bridge.set_transition_speed(speed)
            logger.debug(f"Set transition speed to {speed:.1f}")

    def reset_all_expressions(self):
        """Reset all expressions to neutral."""
        # Reset all sliders to 0
        for slider in self.expression_sliders.values():
            slider.setValue(0)
        
        # Send reset command to Unity
        if self.unity_bridge.is_connected():
            self.unity_bridge.reset_expressions()
            logger.info("Reset all expressions")

        
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Fichier")
        
        # VRM model management
        set_default_action = file_menu.addAction("Définir modèle par défaut...")
        set_default_action.triggered.connect(self.set_default_model)
        
        use_other_action = file_menu.addAction("Utiliser un autre modèle VRM...")
        use_other_action.triggered.connect(self.load_temporary_model)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Quitter")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Aide")
        about_action = help_menu.addAction("À propos")
        about_action.triggered.connect(self.show_about)
        
    def connect_unity(self):
        """Connect to Unity application."""
        logger.info("Attempting to connect to Unity...")
        if self.unity_bridge.connect():
            self.status_label.setText("Statut Unity : Connecté ✓")
            self.load_vrm_btn.setEnabled(True)
            self.connect_btn.setEnabled(False)
            logger.info("Successfully connected to Unity")
        else:
            self.status_label.setText("Statut Unity : Connexion échouée ✗")
            logger.error("Failed to connect to Unity")
            
    def toggle_vrm_model(self):
        """Toggle between loading and unloading VRM model."""
        if not self.vrm_loaded:
            # Load default VRM model
            default_model = self.config.get("avatar.default_model")
            
            if not default_model:
                # No default model set, ask user to set one
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Aucun modèle par défaut",
                    "Aucun modèle VRM par défaut n'est défini.\n\nVoulez-vous en définir un maintenant ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.set_default_model()
                return
            
            file_path = default_model
            
            # Check if file exists
            from pathlib import Path
            if not Path(file_path).exists():
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Fichier introuvable",
                    f"Le modèle par défaut est introuvable :\n{file_path}\n\nVeuillez définir un nouveau modèle par défaut."
                )
                return
            
            if file_path:
                logger.info(f"Loading VRM model: {file_path}")
                self.unity_bridge.send_command("load_model", {"path": file_path})
                self.vrm_loaded = True  # Mark VRM as loaded
                
                # Change button text to "Unload"
                self.load_vrm_btn.setText("Décharger le modèle")
                
                # After loading VRM, send the current transition speed
                # (Give Unity a moment to load the model)
                import time
                import threading
                def send_speed_after_delay():
                    time.sleep(1.5)  # Wait 1.5 seconds for VRM to load
                    if hasattr(self, 'speed_slider'):
                        value = self.speed_slider.value()
                        speed = value / 10.0  # Direct mapping
                        speed = max(0.1, min(10.0, speed))
                        self.unity_bridge.set_transition_speed(speed)
                        logger.info(f"Set initial transition speed to {speed:.1f}")
                
                threading.Thread(target=send_speed_after_delay, daemon=True).start()
        else:
            # Unload VRM model
            logger.info("Unloading VRM model")
            self.unity_bridge.send_command("unload_model", {})
            self.vrm_loaded = False  # Mark VRM as unloaded
            
            # Change button text back to "Load"
            self.load_vrm_btn.setText("Charger modèle VRM")
            
            # Reset all expression sliders to 0
            for slider in self.expression_sliders.values():
                slider.blockSignals(True)
                slider.setValue(0)
                slider.blockSignals(False)
    
    def set_default_model(self):
        """Open dialog to set the default VRM model."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Définir le modèle VRM par défaut",
            self.config.get("avatar.default_model", ""),
            "Fichiers VRM (*.vrm);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            # Save as default model
            self.config.set("avatar.default_model", file_path)
            self.config.save()
            logger.info(f"Default VRM model set to: {file_path}")
            
            # Show confirmation
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Modèle par défaut défini",
                f"Le modèle par défaut a été défini :\n\n{file_path}\n\n"
                "Utilisez le bouton 'Charger modèle VRM' pour le charger automatiquement."
            )
    
    def load_temporary_model(self):
        """Load a different VRM model temporarily (doesn't change default)."""
        # Get the directory of the default model if set
        default_model = self.config.get("avatar.default_model", "")
        from pathlib import Path
        start_dir = str(Path(default_model).parent) if default_model else ""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Utiliser un autre modèle VRM (temporaire)",
            start_dir,
            "Fichiers VRM (*.vrm);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            # If a model is already loaded, unload it first
            if self.vrm_loaded:
                logger.info("Unloading current model before loading new one")
                self.unity_bridge.send_command("unload_model", {})
                self.vrm_loaded = False
            
            # Load the temporary model
            logger.info(f"Loading temporary VRM model: {file_path}")
            self.unity_bridge.send_command("load_model", {"path": file_path})
            self.vrm_loaded = True
            
            # Change button text to "Unload"
            self.load_vrm_btn.setText("Décharger le modèle")
            
            # Send transition speed after loading
            import time
            import threading
            def send_speed_after_delay():
                time.sleep(1.5)
                if hasattr(self, 'speed_slider'):
                    value = self.speed_slider.value()
                    speed = value / 10.0
                    speed = max(0.1, min(10.0, speed))
                    self.unity_bridge.set_transition_speed(speed)
                    logger.info(f"Set initial transition speed to {speed:.1f}")
            
            threading.Thread(target=send_speed_after_delay, daemon=True).start()
            
    def update_status(self):
        """Update connection status."""
        if self.unity_bridge.is_connected():
            self.status_label.setText("Statut Unity : Connecté ✓")
        else:
            if self.connect_btn.isEnabled() == False:
                self.status_label.setText("Statut Unity : Déconnecté ✗")
                self.connect_btn.setEnabled(True)
                self.load_vrm_btn.setEnabled(False)
                
    def show_about(self):
        """Show about dialog."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About Desktop-Mate",
            "Desktop-Mate v0.1.0\n\n"
            "Interactive VRM Desktop Companion\n"
            "Hybrid Unity + Python Application\n\n"
            "© 2025 Xyon15"
        )
        
    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Application closing...")
        self.unity_bridge.disconnect()
        self.config.save()
        event.accept()


class DesktopMateApp:
    """Main application wrapper."""
    
    def __init__(self, argv):
        """Initialize the application.
        
        Args:
            argv: Command line arguments
        """
        self.app = QApplication(argv)
        self.app.setApplicationName("Desktop-Mate")
        self.app.setOrganizationName("Xyon15")
        
        self.main_window = MainWindow()
        
    def run(self):
        """Run the application.
        
        Returns:
            Exit code
        """
        self.main_window.show()
        return self.app.exec()
