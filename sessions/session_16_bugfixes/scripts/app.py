"""
Main application class using PySide6 (Qt).
Manages the GUI and coordinates with Unity via IPC.
"""

import sys
import logging
import asyncio
import os
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMenuBar,
    QMenu,
    QTabWidget,
    QSlider,
    QGroupBox,
    QCheckBox,
    QMessageBox,
    QTextEdit,
    QLineEdit,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QIcon

# Load .env file at startup
from dotenv import load_dotenv

load_dotenv()

from ..ipc.unity_bridge import UnityBridge
from ..utils.config import Config
from ..ai.chat_engine import get_chat_engine
from ..ai.emotion_analyzer import get_emotion_analyzer

logger = logging.getLogger(__name__)


class DiscordSignals(QObject):
    """
    Signaux Qt pour communication thread-safe entre Discord bot et GUI.

    Le bot Discord tourne dans un thread séparé avec asyncio, donc toutes
    les updates de l'UI doivent passer par ces signaux.
    """

    # Signal émis quand le statut de connexion change
    status_changed = Signal(bool, str)  # (connected, bot_name)

    # Signal émis quand un message est reçu/traité
    message_received = Signal(str, str, str)  # (timestamp, username, message)

    # Signal émis quand les statistiques sont mises à jour
    stats_updated = Signal(dict)  # stats_dict

    # Signal émis en cas d'erreur
    error_occurred = Signal(str)  # error_message

    # Signal émis quand une émotion est détectée
    emotion_detected = Signal(str, float)  # (emotion, intensity)


class DiscordBotThread(QThread):
    """
    Thread dédié pour exécuter le bot Discord avec asyncio.

    Discord.py utilise asyncio qui n'est pas compatible avec l'event loop Qt.
    Ce thread crée son propre event loop asyncio pour le bot.
    """

    def __init__(self, token: str, unity_bridge=None, parent: Optional[QObject] = None):
        """
        Initialise le thread Discord.

        Args:
            token: Token Discord bot
            unity_bridge: UnityBridge instance à partager avec le bot
            parent: Widget parent Qt (optionnel)
        """
        super().__init__(parent)
        self.token = token
        self.unity_bridge = unity_bridge
        self.signals = DiscordSignals()
        self.bot = None
        self._stop_requested = False

    def run(self):
        """
        Méthode principale du thread (exécutée dans thread séparé).
        Lance le bot Discord avec asyncio.
        """
        try:
            # Importer ici pour éviter problèmes d'imports circulaires
            from src.discord_bot.bot import KiraDiscordBot

            # Créer bot Discord avec les signals pour communication GUI
            # et l'instance UnityBridge partagée
            logger.info("🚀 Démarrage du bot Discord dans thread séparé...")
            self.bot = KiraDiscordBot(
                gui_signals=self.signals, unity_bridge=self.unity_bridge
            )

            # Émettre signal de démarrage
            self.signals.status_changed.emit(False, "Connexion en cours...")

            # Lancer bot avec asyncio (bloquant jusqu'à arrêt)
            asyncio.run(self._run_bot())

        except Exception as e:
            error_msg = f"❌ Erreur démarrage bot Discord : {e}"
            logger.error(error_msg)
            self.signals.error_occurred.emit(error_msg)
            self.signals.status_changed.emit(False, "Erreur")

    async def _run_bot(self):
        """
        Coroutine pour lancer le bot avec gestion de l'arrêt propre.
        """
        try:
            # Hook sur on_ready pour émettre signal
            original_on_ready = self.bot.on_ready

            async def wrapped_on_ready():
                await original_on_ready()
                # Bot connecté !
                status = self.bot.get_status()
                self.signals.status_changed.emit(
                    status["connected"], status.get("bot_name", "Bot Discord")
                )
                logger.info(f"✅ Bot Discord connecté : {status.get('bot_name')}")

            self.bot.on_ready = wrapped_on_ready

            # Hook sur on_message pour émettre signals
            original_on_message = self.bot.on_message

            async def wrapped_on_message(message):
                await original_on_message(message)
                # Émettre signal pour update GUI
                if message.author != self.bot.user:
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.signals.message_received.emit(
                        timestamp,
                        message.author.name,
                        message.content[:100],  # Limiter à 100 chars
                    )

            self.bot.on_message = wrapped_on_message

            # Lancer bot
            await self.bot.start(self.token)

        except Exception as e:
            logger.error(f"❌ Erreur dans bot Discord : {e}")
            self.signals.error_occurred.emit(str(e))

    def stop_bot(self):
        """
        Arrête le bot Discord proprement.
        """
        self._stop_requested = True

        if self.bot and self.bot.is_ready():
            logger.info("⏹️ Arrêt du bot Discord...")

            # Créer une tâche pour arrêter le bot dans son event loop
            async def close_bot():
                await self.bot.close()

            # Exécuter dans le event loop du bot
            if self.bot.loop and not self.bot.loop.is_closed():
                asyncio.run_coroutine_threadsafe(close_bot(), self.bot.loop)

        # Attendre fin du thread (avec timeout)
        self.wait(5000)  # 5 secondes max


class MainWindow(QMainWindow):
    """Main application window."""

    # Custom signals for thread-safe UI updates
    message_received = Signal(str, str, str)  # sender, message, color
    emotion_updated = Signal(str)  # emotion_text
    expression_changed = Signal(str, float)  # expression_id, value (0-100)
    stats_updated = Signal()
    chat_input_ready = Signal()  # Signal pour réactiver l'input de chat

    def __init__(self):
        super().__init__()

        # Fix Windows taskbar icon - DOIT être défini AVANT la création de l'UI
        if sys.platform == "win32":
            try:
                import ctypes

                app_id = "WorklyHQ.Workly.DesktopApp.1.0"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                logger.info(f"✅ Windows App User Model ID défini : {app_id}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de définir App User Model ID : {e}")

        self.config = Config()
        self.unity_bridge = UnityBridge()
        self.vrm_loaded = False  # Track if VRM model is loaded

        # Initialize AI components as None (will be loaded on demand)
        self.chat_engine = None
        self.emotion_analyzer = None
        self.ai_available = False
        logger.info(
            "💡 AI components not initialized. Use 'Charger IA' button to load them."
        )

        # Initialize Discord components
        self.discord_thread = None
        self.discord_running = False

        # Initialize chat message counter for current session
        self.current_session_messages = 0

        # Connect signals (emotion_updated will be connected after create_chat_tab)
        self.message_received.connect(self.append_chat_message)
        self.stats_updated.connect(self.update_chat_stats)
        self.chat_input_ready.connect(self.enable_chat_input)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Workly Control Panel")
        self.setGeometry(100, 100, 900, 700)

        # Set window icon
        icon_path = (
            Path(__file__).parent.parent.parent / "assets" / "icons" / "workly.ico"
        )
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            logger.info(f"✅ Icône de fenêtre définie : {icon_path}")
        else:
            logger.warning(f"⚠️ Icône non trouvée : {icon_path}")

        # Create menu bar
        self.create_menu_bar()

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Header
        header = QLabel("Workly Control Panel")
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
        self.create_chat_tab()
        self.create_discord_tab()  # NEW: Discord control tab
        self.create_expressions_tab()
        self.create_animations_tab()
        self.create_logs_tab()  # NEW: Logs tab

        # Status timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Check every second

    def create_connexion_tab(self):
        """Create the Unity connexion tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Unity connection buttons
        unity_group = QGroupBox("🔌 Connexion Unity")
        unity_layout = QVBoxLayout()
        unity_group.setLayout(unity_layout)

        button_layout = QHBoxLayout()

        self.connect_btn = QPushButton("Connexion à Unity")
        self.connect_btn.clicked.connect(self.connect_unity)
        button_layout.addWidget(self.connect_btn)

        self.load_vrm_btn = QPushButton("Charger modèle VRM")
        self.load_vrm_btn.clicked.connect(self.toggle_vrm_model)
        self.load_vrm_btn.setEnabled(False)
        button_layout.addWidget(self.load_vrm_btn)

        unity_layout.addLayout(button_layout)
        layout.addWidget(unity_group)

        # AI/LLM loading section
        ai_group = QGroupBox("🤖 Modèle IA (LLM)")
        ai_layout = QVBoxLayout()
        ai_group.setLayout(ai_layout)

        # AI status label
        self.ai_status_label = QLabel("Statut IA : Non chargé")
        self.ai_status_label.setStyleSheet("font-size: 13px; padding: 5px;")
        ai_layout.addWidget(self.ai_status_label)

        # GPU profile label (shows current profile and details)
        self.gpu_profile_label = QLabel("Profil GPU : -")
        self.gpu_profile_label.setStyleSheet(
            "font-size: 12px; padding: 5px; color: #888; font-style: italic;"
        )
        ai_layout.addWidget(self.gpu_profile_label)

        # Load AI button
        ai_button_layout = QHBoxLayout()
        self.load_ai_btn = QPushButton("📥 Charger IA (Zephyr-7B)")
        self.load_ai_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        )
        self.load_ai_btn.clicked.connect(self.load_ai_model)
        ai_button_layout.addWidget(self.load_ai_btn)

        self.unload_ai_btn = QPushButton("🗑️ Décharger IA")
        self.unload_ai_btn.setEnabled(False)
        self.unload_ai_btn.clicked.connect(self.unload_ai_model)
        ai_button_layout.addWidget(self.unload_ai_btn)

        ai_layout.addLayout(ai_button_layout)

        # Info label
        info_label = QLabel(
            "💡 Le modèle IA (Zephyr-7B) est requis pour le chat.\n"
            "Chargement : ~15-30 secondes | Mémoire : ~4-6 GB VRAM"
        )
        info_label.setStyleSheet("font-size: 11px; color: #888; font-style: italic;")
        info_label.setWordWrap(True)
        ai_layout.addWidget(info_label)

        layout.addWidget(ai_group)

        layout.addStretch()

        self.tabs.addTab(tab, "Connexion")

    def create_chat_tab(self):
        """Create the AI Chat tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Chat header with info
        header_layout = QHBoxLayout()
        chat_icon = QLabel("💬")
        chat_icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(chat_icon)

        chat_title = QLabel("Discuter avec Kira")
        chat_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(chat_title)
        header_layout.addStretch()

        # Emotion indicator
        self.current_emotion_label = QLabel("😐 Neutre")
        self.current_emotion_label.setStyleSheet(
            "font-size: 14px; padding: 8px 15px; "
            "background-color: #3a3a3a; border-radius: 8px; "
            "border: 1px solid #555; color: #e0e0e0;"
        )
        header_layout.addWidget(self.current_emotion_label)

        layout.addLayout(header_layout)

        # Chat messages area
        from PySide6.QtWidgets import QTextEdit, QLineEdit

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """
        )
        self.chat_display.setPlaceholderText(
            "Les messages de conversation apparaîtront ici...\n\n"
            "💡 Astuce : Les émotions de Kira s'afficheront automatiquement "
            "sur l'avatar VRM en temps réel !"
        )
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Écrivez votre message ici...")
        self.chat_input.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                font-size: 13px;
                border: 2px solid #444;
                border-radius: 5px;
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """
        )
        self.chat_input.returnPressed.connect(self.send_chat_message)
        input_layout.addWidget(self.chat_input)

        self.send_btn = QPushButton("📤 Envoyer")
        self.send_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868A8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        )
        self.send_btn.clicked.connect(self.send_chat_message)
        input_layout.addWidget(self.send_btn)

        # Disable chat input by default (AI not loaded)
        self.chat_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.chat_input.setPlaceholderText(
            "⚠️ Chargez d'abord l'IA dans l'onglet Connexion"
        )

        layout.addLayout(input_layout)

        # Stats area
        stats_layout = QHBoxLayout()
        self.chat_stats_label = QLabel("Messages : 0")
        self.chat_stats_label.setStyleSheet("font-size: 11px; color: gray;")
        stats_layout.addWidget(self.chat_stats_label)

        # Typing indicator
        self.typing_indicator = QLabel("")
        self.typing_indicator.setStyleSheet(
            "font-size: 11px; color: #4CAF50; font-style: italic;"
        )
        stats_layout.addWidget(self.typing_indicator)

        stats_layout.addStretch()

        clear_btn = QPushButton("🗑️ Effacer l'historique")
        clear_btn.setStyleSheet("font-size: 11px;")
        clear_btn.clicked.connect(self.clear_chat_history)
        stats_layout.addWidget(clear_btn)

        layout.addLayout(stats_layout)

        # Connect emotion_updated signal now that current_emotion_label exists
        self.emotion_updated.connect(self.current_emotion_label.setText)
        # Connect expression_changed signal to update sliders
        self.expression_changed.connect(self.update_expression_slider)

        self.tabs.addTab(tab, "💬 Chat")

    def create_discord_tab(self):
        """Create the Discord bot control tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Discord header
        header_layout = QHBoxLayout()
        discord_icon = QLabel("🤖")
        discord_icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(discord_icon)

        discord_title = QLabel("Contrôle Bot Discord")
        discord_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(discord_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # === SECTION: Bot Control ===
        control_group = QGroupBox("Contrôle du Bot")
        control_layout = QVBoxLayout()
        control_group.setLayout(control_layout)

        # Connection status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Statut:"))
        self.discord_status_label = QLabel("🔴 Déconnecté")
        self.discord_status_label.setStyleSheet(
            "font-size: 14px; padding: 5px 10px; "
            "background-color: #3a3a3a; border-radius: 5px; "
            "border: 1px solid #555; color: #e0e0e0;"
        )
        status_layout.addWidget(self.discord_status_label)
        status_layout.addStretch()
        control_layout.addLayout(status_layout)

        # Start/Stop buttons
        buttons_layout = QHBoxLayout()

        self.discord_start_btn = QPushButton("▶️ Démarrer Bot Discord")
        self.discord_start_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """
        )
        self.discord_start_btn.clicked.connect(self.start_discord_bot)
        buttons_layout.addWidget(self.discord_start_btn)

        self.discord_stop_btn = QPushButton("⏹️ Arrêter Bot Discord")
        self.discord_stop_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """
        )
        self.discord_stop_btn.clicked.connect(self.stop_discord_bot)
        self.discord_stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.discord_stop_btn)

        control_layout.addLayout(buttons_layout)

        layout.addWidget(control_group)

        # === SECTION: Discord Messages ===
        messages_group = QGroupBox("Derniers Messages Discord")
        messages_layout = QVBoxLayout()
        messages_group.setLayout(messages_layout)

        self.discord_messages_display = QTextEdit()
        self.discord_messages_display.setReadOnly(True)
        self.discord_messages_display.setMaximumHeight(150)
        self.discord_messages_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """
        )
        messages_layout.addWidget(self.discord_messages_display)

        layout.addWidget(messages_group)

        # === SECTION: Discord Statistics ===
        stats_group = QGroupBox("Statistiques Discord")
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)

        self.discord_stats_label = QLabel("Aucune statistique disponible")
        self.discord_stats_label.setStyleSheet("font-size: 12px; color: #bbb;")
        stats_layout.addWidget(self.discord_stats_label)

        layout.addWidget(stats_group)

        layout.addStretch()

        self.tabs.addTab(tab, "🤖 Discord")

    def start_discord_bot(self):
        """Start the Discord bot in a separate thread."""
        # Check if AI is available
        if not self.ai_available:
            QMessageBox.warning(
                self,
                "IA Non Disponible",
                "Le bot Discord nécessite que l'IA soit chargée.\n\n"
                "Allez dans l'onglet 'Connexion' et cliquez sur 'Charger IA' d'abord.",
            )
            return

        # CRITICAL: Reload .env to ensure latest token is loaded
        from dotenv import load_dotenv

        load_dotenv(override=True)  # override=True forces reload even if already loaded

        # Get token from environment variable
        import os

        token = os.getenv("DISCORD_TOKEN", "").strip()

        # Debug log (showing only first 20 chars for security)
        if token:
            logger.info(f"🔑 Token Discord chargé : {token[:20]}...")
        else:
            logger.warning("⚠️ Aucun token Discord trouvé dans .env")

        if not token:
            QMessageBox.warning(
                self,
                "Token Manquant",
                "Le token Discord n'est pas configuré dans le fichier .env\n\n"
                "Créez un fichier .env à la racine du projet avec :\n"
                "DISCORD_TOKEN=votre_token_ici",
            )
            return

        # Check if bot is already running
        if self.discord_running:
            QMessageBox.information(
                self, "Bot Déjà Actif", "Le bot Discord est déjà en cours d'exécution."
            )
            return

        logger.info("🚀 Démarrage du bot Discord...")

        # Update UI
        self.discord_status_label.setText("🟡 Connexion en cours...")
        self.discord_start_btn.setEnabled(False)
        self.discord_stop_btn.setEnabled(True)

        # Create and start thread (pass unity_bridge to share with bot)
        self.discord_thread = DiscordBotThread(token, unity_bridge=self.unity_bridge)

        # Connect signals
        self.discord_thread.signals.status_changed.connect(
            self.on_discord_status_changed
        )
        self.discord_thread.signals.message_received.connect(
            self.on_discord_message_received
        )
        self.discord_thread.signals.stats_updated.connect(self.on_discord_stats_updated)
        self.discord_thread.signals.error_occurred.connect(self.on_discord_error)
        self.discord_thread.signals.emotion_detected.connect(
            self.on_discord_emotion_detected
        )

        # Start thread
        self.discord_thread.start()
        self.discord_running = True

        logger.info("✅ Thread Discord démarré")

    def stop_discord_bot(self):
        """Stop the Discord bot."""
        if not self.discord_running or not self.discord_thread:
            return

        logger.info("⏹️ Arrêt du bot Discord...")

        # Update UI
        self.discord_status_label.setText("🟡 Déconnexion en cours...")
        self.discord_stop_btn.setEnabled(False)

        # Stop thread
        self.discord_thread.stop_bot()
        self.discord_thread = None
        self.discord_running = False

        # Update UI
        self.discord_status_label.setText("🔴 Déconnecté")
        self.discord_start_btn.setEnabled(True)

        logger.info("✅ Bot Discord arrêté")

    def on_discord_status_changed(self, connected: bool, bot_name: str):
        """Handle Discord bot status changes (Qt slot)."""
        if connected:
            self.discord_status_label.setText(f"🟢 Connecté : {bot_name}")
            self.discord_status_label.setStyleSheet(
                "font-size: 14px; padding: 5px 10px; "
                "background-color: #2e7d32; border-radius: 5px; "
                "border: 1px solid #4caf50; color: #e0e0e0;"
            )
        else:
            self.discord_status_label.setText(f"🔴 {bot_name}")
            self.discord_status_label.setStyleSheet(
                "font-size: 14px; padding: 5px 10px; "
                "background-color: #3a3a3a; border-radius: 5px; "
                "border: 1px solid #555; color: #e0e0e0;"
            )

    def on_discord_message_received(self, timestamp: str, username: str, message: str):
        """Handle Discord messages (Qt slot)."""
        # Format message
        formatted = f"[{timestamp}] <b>{username}</b>: {message}"

        # Append to display (limit to 50 messages)
        current_text = self.discord_messages_display.toPlainText()
        lines = current_text.split("\n")

        if len(lines) >= 50:
            # Remove oldest message
            lines = lines[-49:]

        # Add new message
        self.discord_messages_display.append(formatted)

    def on_discord_stats_updated(self, stats: dict):
        """Handle Discord statistics updates (Qt slot)."""
        messages_processed = stats.get("messages_processed", 0)
        responses_sent = stats.get("responses_sent", 0)
        guilds = stats.get("guilds", 0)
        uptime = stats.get("uptime_seconds", 0)

        stats_text = (
            f"Messages reçus: {messages_processed} | "
            f"Réponses envoyées: {responses_sent} | "
            f"Serveurs: {guilds} | "
            f"Uptime: {int(uptime)}s"
        )

        self.discord_stats_label.setText(stats_text)

    def on_discord_error(self, error_message: str):
        """Handle Discord errors (Qt slot)."""
        logger.error(f"❌ Erreur Discord : {error_message}")

        QMessageBox.critical(
            self,
            "Erreur Bot Discord",
            f"Une erreur s'est produite :\n\n{error_message}",
        )

        # Reset UI
        self.discord_status_label.setText("🔴 Erreur")
        self.discord_start_btn.setEnabled(True)
        self.discord_stop_btn.setEnabled(False)
        self.discord_running = False

    def on_discord_emotion_detected(self, emotion: str, intensity: float):
        """Handle emotion detected from Discord bot (Qt slot).

        Args:
            emotion: Emotion detected ('joy', 'angry', 'sorrow', 'surprised', 'fun', 'neutral')
            intensity: Intensity 0-100
        """
        logger.info(f"🎭 Émotion Discord reçue : {emotion} ({intensity:.1f}%)")

        # Map emotion to expression_id for GUI sliders
        emotion_to_expr = {
            "joy": "joy",
            "angry": "angry",
            "sorrow": "sorrow",
            "surprised": "surprised",
            "fun": "fun",
            "neutral": None,  # Neutral doesn't update sliders
        }

        expr_id = emotion_to_expr.get(emotion)
        if expr_id:
            # Update slider in Expressions tab
            self.update_expression_slider(expr_id, intensity)

        # Update emotion label in Chat tab
        emotion_emoji = {
            "joy": "😊",
            "angry": "😠",
            "sorrow": "😢",
            "surprised": "😲",
            "fun": "😄",
            "neutral": "😐",
        }
        emotion_name = {
            "joy": "Joyeux",
            "angry": "En colère",
            "sorrow": "Triste",
            "surprised": "Surpris",
            "fun": "Amusé",
            "neutral": "Neutre",
        }

        emoji = emotion_emoji.get(emotion, "😐")
        name = emotion_name.get(emotion, "Neutre")
        self.emotion_updated.emit(f"{emoji} {name} ({int(intensity)}%)")

    def set_discord_token(self):
        """Open dialog to set Discord bot token."""
        # Get current token from environment
        current_token = os.getenv("DISCORD_TOKEN", "")

        # Show input dialog
        token, ok = QInputDialog.getText(
            self,
            "Définir Token Bot Discord",
            "Entrez le token Discord de votre bot :\n\n"
            "(Le token sera sauvegardé dans le fichier .env)",
            QLineEdit.EchoMode.Password,
            current_token,
        )

        if ok and token.strip():
            # Save to .env file
            env_path = Path(__file__).parent.parent.parent / ".env"

            try:
                # Read existing .env content
                env_content = ""
                if env_path.exists():
                    with open(env_path, "r", encoding="utf-8") as f:
                        env_content = f.read()

                # Update or add DISCORD_TOKEN
                if "DISCORD_TOKEN=" in env_content:
                    # Replace existing token
                    lines = env_content.split("\n")
                    for i, line in enumerate(lines):
                        if line.startswith("DISCORD_TOKEN="):
                            lines[i] = f"DISCORD_TOKEN={token.strip()}"
                            break
                    env_content = "\n".join(lines)
                else:
                    # Add new token line
                    if not env_content.endswith("\n"):
                        env_content += "\n"
                    env_content += f"\n# DISCORD BOT\nDISCORD_TOKEN={token.strip()}\n"

                # Write back to .env
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(env_content)

                # Update environment variable
                os.environ["DISCORD_TOKEN"] = token.strip()

                logger.info("✅ Token Discord sauvegardé dans .env")

                QMessageBox.information(
                    self,
                    "Token Sauvegardé",
                    "Le token Discord a été sauvegardé avec succès !\n\n"
                    "Vous pouvez maintenant démarrer le bot depuis l'onglet Discord.",
                )

            except Exception as e:
                logger.error(f"❌ Erreur lors de la sauvegarde du token : {e}")
                QMessageBox.critical(
                    self,
                    "Erreur de Sauvegarde",
                    f"Impossible de sauvegarder le token :\n\n{e}",
                )

    def manage_auto_reply_channels(self):
        """Open dialog to manage Discord auto-reply channels."""
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Gérer Salons Auto-Reply Discord")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(450)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Checkbox pour activer/désactiver auto-reply
        discord_config = self.config.get("discord", {})
        auto_reply_enabled = discord_config.get("auto_reply_enabled", True)

        enable_checkbox = QCheckBox(
            "✅ Activer l'auto-reply dans les salons configurés"
        )
        enable_checkbox.setChecked(auto_reply_enabled)
        enable_checkbox.setStyleSheet(
            "font-size: 13px; font-weight: bold; padding: 10px;"
        )
        layout.addWidget(enable_checkbox)

        # Instructions
        instructions = QLabel(
            "Configurez les salons Discord où le bot répondra automatiquement.\n\n"
            "Pour obtenir l'ID d'un salon :\n"
            "1. Activez le Mode Développeur dans Discord (Paramètres → Avancés)\n"
            "2. Clic droit sur le salon → Copier l'identifiant"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # List widget for channels
        channels_list = QListWidget()
        channels_list.setStyleSheet(
            """
            QListWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
        """
        )

        # Load current channels from config
        discord_config = self.config.get("discord", {})
        auto_reply_channels = discord_config.get("auto_reply_channels", [])

        for channel_id in auto_reply_channels:
            channels_list.addItem(str(channel_id))

        layout.addWidget(channels_list)

        # Buttons for add/remove
        buttons_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Ajouter Salon")
        add_btn.clicked.connect(lambda: self._add_channel_to_list(channels_list))
        buttons_layout.addWidget(add_btn)

        remove_btn = QPushButton("➖ Retirer Salon")
        remove_btn.clicked.connect(
            lambda: self._remove_channel_from_list(channels_list)
        )
        buttons_layout.addWidget(remove_btn)

        layout.addLayout(buttons_layout)

        # Dialog buttons (OK/Cancel)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(
            lambda: self._save_channels(channels_list, enable_checkbox, dialog)
        )
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog
        dialog.exec()

    def _add_channel_to_list(self, list_widget: QListWidget):
        """Add a channel ID to the list."""
        channel_id, ok = QInputDialog.getText(
            self, "Ajouter Salon Discord", "Entrez l'ID du salon Discord :"
        )

        if ok and channel_id.strip():
            # Validate it's a number
            try:
                int(channel_id.strip())
                list_widget.addItem(channel_id.strip())
                logger.info(f"✅ Salon Discord ajouté : {channel_id.strip()}")
            except ValueError:
                QMessageBox.warning(
                    self, "ID Invalide", "L'ID du salon doit être un nombre."
                )

    def _remove_channel_from_list(self, list_widget: QListWidget):
        """Remove selected channel from the list."""
        current_item = list_widget.currentItem()

        if current_item:
            list_widget.takeItem(list_widget.row(current_item))
            logger.info(f"✅ Salon Discord retiré : {current_item.text()}")
        else:
            QMessageBox.information(
                self, "Aucune Sélection", "Veuillez sélectionner un salon à retirer."
            )

    def _save_channels(
        self, list_widget: QListWidget, enable_checkbox: QCheckBox, dialog: QDialog
    ):
        """Save channels and auto-reply state to config.json."""
        # Collect all channel IDs
        auto_reply_channels = []
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            try:
                channel_id = int(item.text())
                auto_reply_channels.append(channel_id)
            except ValueError:
                logger.warning(f"⚠️ ID salon invalide ignoré : {item.text()}")

        # Get auto-reply enabled state
        auto_reply_enabled = enable_checkbox.isChecked()

        # Update config
        self.config.set("discord.auto_reply_enabled", auto_reply_enabled)
        self.config.set("discord.auto_reply_channels", auto_reply_channels)
        self.config.save()

        # Recharger la config du bot Discord si connecté
        if (
            hasattr(self, "discord_manager")
            and self.discord_manager
            and self.discord_manager.bot
        ):
            self.discord_manager.bot.auto_reply_enabled = auto_reply_enabled
            self.discord_manager.bot.auto_reply_channels = auto_reply_channels
            logger.info(
                f"✅ Config bot Discord rechargée : auto_reply={auto_reply_enabled}, "
                f"{len(auto_reply_channels)} salons"
            )

        logger.info(
            f"✅ Config Discord sauvegardée : auto_reply={auto_reply_enabled}, "
            f"{len(auto_reply_channels)} salons"
        )

        status_text = "activée" if auto_reply_enabled else "désactivée"
        QMessageBox.information(
            self,
            "Configuration Sauvegardée",
            f"La configuration Discord a été sauvegardée avec succès !\n\n"
            f"Auto-reply : {status_text}\n"
            f"Nombre de salons configurés : {len(auto_reply_channels)}\n\n"
            f"✅ La configuration du bot a été rechargée automatiquement.",
        )

        dialog.accept()

    def update_gpu_profile_display(self):
        """
        Met à jour l'affichage du profil GPU actuel dans l'interface.
        """
        if not self.ai_available or not self.chat_engine:
            return

        try:
            from src.ai.config import GPU_PROFILES

            # Récupérer le profil actuel depuis ModelManager
            current_profile = self.chat_engine.model_manager.config.gpu_profile

            # Résoudre "auto" si nécessaire
            if current_profile == "auto":
                from src.ai.config import get_initial_gpu_profile

                current_profile = get_initial_gpu_profile()

            # Récupérer les infos du profil
            profile_info = GPU_PROFILES.get(current_profile, {})
            profile_name = profile_info.get("name", current_profile)
            n_gpu_layers = profile_info.get("n_gpu_layers", 0)
            vram_estimate = profile_info.get("vram_estimate", "N/A")

            # Déterminer la couleur selon le profil
            profile_colors = {
                "performance": "#4CAF50",  # Vert
                "balanced": "#FFC107",  # Orange
                "cpu_fallback": "#F44336",  # Rouge
            }
            color = profile_colors.get(current_profile, "#888")

            # Mettre à jour le label
            label_text = f"Profil GPU : {profile_name} (layers: {n_gpu_layers}, VRAM: {vram_estimate})"
            self.gpu_profile_label.setText(label_text)
            self.gpu_profile_label.setStyleSheet(
                f"font-size: 12px; padding: 5px; color: {color}; font-weight: bold;"
            )

            logger.debug(f"GPU profile display updated: {current_profile}")

        except Exception as e:
            logger.error(f"Error updating GPU profile display: {e}")
            self.gpu_profile_label.setText("Profil GPU : Erreur de détection")

    def manage_ia_profiles(self):
        """
        Dialog pour gérer et changer les profils GPU de l'IA.
        """
        from src.ai.config import GPU_PROFILES

        # Créer le dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Profils IA - Gestion GPU")
        dialog.setMinimumWidth(600)
        dialog.setMaximumHeight(700)  # Limiter la hauteur

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Instructions
        instructions = QLabel(
            "Choisissez le profil GPU pour le modèle IA (Zephyr-7B).\n"
            "Le profil détermine combien de layers sont chargées sur le GPU.\n\n"
            "⚠️ Changer le profil rechargera le modèle (15-30 secondes)."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "font-size: 12px; padding: 10px; background-color: #2b2b2b; border-radius: 5px;"
        )
        layout.addWidget(instructions)

        # Profil actuel
        if self.ai_available and self.chat_engine:
            current_profile = self.chat_engine.model_manager.config.gpu_profile
            if current_profile == "auto":
                from src.ai.config import get_initial_gpu_profile

                current_profile = get_initial_gpu_profile()
        else:
            # Si IA non chargée, lire depuis config.json
            current_profile = self.config.get("ai.gpu_profile", "balanced")
            if current_profile == "auto":
                from src.ai.config import get_initial_gpu_profile

                current_profile = get_initial_gpu_profile()

        current_label = QLabel(
            f"📊 Profil actuel : {GPU_PROFILES[current_profile]['name']}"
        )
        current_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 10px;"
        )
        layout.addWidget(current_label)

        # Liste des profils disponibles avec scroll
        from PySide6.QtWidgets import QScrollArea

        profiles_group = QGroupBox("Profils Disponibles")

        # Widget scrollable pour les profils
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        scroll_widget = QWidget()
        profiles_layout = QVBoxLayout()
        scroll_widget.setLayout(profiles_layout)

        from PySide6.QtWidgets import QRadioButton, QButtonGroup

        # Button group pour sélection exclusive
        button_group = QButtonGroup(dialog)

        # Ajouter profil "auto" en premier
        profile_order = ["auto", "performance", "balanced", "cpu_fallback"]

        for profile_id in profile_order:
            # Gérer le profil "auto" spécialement (pas dans GPU_PROFILES)
            if profile_id == "auto":
                profile = {
                    "name": "Auto (Détection Automatique)",
                    "description": "Détecte automatiquement le meilleur profil selon votre GPU",
                    "n_gpu_layers": "Auto",
                    "n_ctx": "Auto",
                    "n_batch": "Auto",
                    "vram_estimate": "Auto-détecté",
                    "speed_estimate": "Variable",
                    "recommended_for": "Laisse le système choisir le profil optimal selon VRAM disponible",
                }
            else:
                profile = GPU_PROFILES[profile_id]

            # Container pour chaque profil
            profile_container = QWidget()
            profile_layout = QVBoxLayout()
            profile_container.setLayout(profile_layout)

            # Radio button avec nom du profil
            radio = QRadioButton(f"{profile['name']}")
            radio.setStyleSheet("font-size: 13px; font-weight: bold;")

            # Cocher le profil actuel
            if profile_id == current_profile:
                radio.setChecked(True)

            button_group.addButton(radio)
            radio.setProperty("profile_id", profile_id)  # Stocker l'ID

            profile_layout.addWidget(radio)

            # Description détaillée
            details_text = (
                f"{profile['description']}\n\n"
                f"• GPU Layers: {profile['n_gpu_layers']}\n"
                f"• Context: {profile['n_ctx']} tokens\n"
                f"• Batch Size: {profile['n_batch']}\n"
                f"• VRAM: {profile['vram_estimate']}\n"
                f"• Vitesse: {profile['speed_estimate']}\n"
                f"• Recommandé pour: {profile['recommended_for']}"
            )

            details_label = QLabel(details_text)
            details_label.setWordWrap(True)
            details_label.setStyleSheet(
                "font-size: 11px; color: #aaa; padding-left: 25px; margin-bottom: 10px;"
            )
            profile_layout.addWidget(details_label)

            # Séparateur
            from PySide6.QtWidgets import QFrame

            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            profile_layout.addWidget(line)

            profiles_layout.addWidget(profile_container)

        # Configurer le scroll area
        scroll_area.setWidget(scroll_widget)

        # Layout du group box
        group_layout = QVBoxLayout()
        group_layout.addWidget(scroll_area)
        profiles_group.setLayout(group_layout)

        layout.addWidget(profiles_group)

        # Buttons (OK/Cancel)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(
            lambda: self._apply_gpu_profile_change(
                dialog, button_group, current_profile
            )
        )
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Afficher le dialog
        dialog.exec()

    def _apply_gpu_profile_change(
        self, dialog: QDialog, button_group, old_profile: str
    ):
        """
        Applique le changement de profil GPU.

        Args:
            dialog: Dialog à fermer
            button_group: QButtonGroup avec les radio buttons
            old_profile: Profil actuel avant changement
        """
        # Récupérer le profil sélectionné
        selected_button = button_group.checkedButton()
        if not selected_button:
            dialog.reject()
            return

        new_profile = selected_button.property("profile_id")

        # Si pas de changement, fermer simplement
        if new_profile == old_profile:
            logger.info("Aucun changement de profil GPU")
            dialog.accept()
            return

        logger.info(f"Changement profil GPU : {old_profile} → {new_profile}")

        # Sauvegarder dans config.json
        self.config.set("ai.gpu_profile", new_profile)
        self.config.save()

        # Si l'IA est déjà chargée, proposer de recharger
        if self.ai_available and self.chat_engine:
            from PySide6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                "Recharger le modèle ?",
                f"Le profil GPU a été changé de '{old_profile}' vers '{new_profile}'.\n\n"
                "Voulez-vous recharger le modèle maintenant avec le nouveau profil ?\n"
                "(Cela prendra 15-30 secondes)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Afficher message de rechargement
                self.ai_status_label.setText("⏳ Rechargement avec nouveau profil...")
                QApplication.processEvents()

                try:
                    # Décharger le modèle actuel
                    logger.info("Déchargement du modèle actuel...")
                    self.chat_engine.model_manager.unload_model()

                    # Recharger la config
                    from src.ai.config import AIConfig

                    self.chat_engine.model_manager.config = AIConfig.from_json()

                    # Recharger le modèle avec le nouveau profil
                    logger.info(f"Rechargement avec profil '{new_profile}'...")
                    if not self.chat_engine.model_manager.load_model():
                        raise RuntimeError("Échec du rechargement du modèle")

                    # Mettre à jour l'affichage
                    self.update_gpu_profile_display()
                    self.ai_status_label.setText("✅ IA rechargée avec nouveau profil")
                    self.ai_status_label.setStyleSheet(
                        "font-size: 13px; padding: 5px; color: #4CAF50;"
                    )

                    logger.info(f"✅ Modèle rechargé avec profil '{new_profile}'")

                    QMessageBox.information(
                        self,
                        "Profil Appliqué",
                        f"Le modèle a été rechargé avec le profil '{new_profile}' !",
                    )

                except Exception as e:
                    logger.error(f"❌ Erreur rechargement modèle : {e}")
                    self.ai_status_label.setText("❌ Erreur de rechargement")
                    self.ai_status_label.setStyleSheet(
                        "font-size: 13px; padding: 5px; color: #f44336;"
                    )

                    QMessageBox.critical(
                        self,
                        "Erreur de Rechargement",
                        f"Impossible de recharger le modèle :\n\n{e}\n\n"
                        "Le profil a été sauvegardé mais n'est pas encore actif.\n"
                        "Redémarrez l'application pour l'appliquer.",
                    )
        else:
            # IA pas encore chargée, juste informer
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "Profil Sauvegardé",
                f"Le profil GPU '{new_profile}' a été sauvegardé.\n\n"
                "Il sera appliqué au prochain chargement de l'IA.",
            )

        dialog.accept()

    def send_chat_message(self):
        """Send a chat message to Kira."""
        # Check if AI is available
        if not self.ai_available:
            self.append_chat_message(
                "Système",
                "❌ Fonctionnalité IA non disponible. Installez llama-cpp-python pour activer le chat.",
                "#EF5350",  # Rouge clair pour fond sombre
            )
            return

        message = self.chat_input.text().strip()

        if not message:
            return

        # Clear input immediately
        self.chat_input.clear()

        # Disable send button during processing
        self.send_btn.setEnabled(False)
        self.chat_input.setEnabled(False)

        # Display user message
        self.append_chat_message(
            "Vous", message, "#64B5F6"
        )  # Bleu clair pour fond sombre

        # Show typing indicator
        self.typing_indicator.setText("✍️ Kira écrit...")

        # Process in background thread to avoid freezing UI
        import threading

        def process_message():
            try:
                # Generate response using ChatEngine
                response = self.chat_engine.chat(
                    user_input=message, user_id="desktop_user"
                )

                # Analyze emotion
                emotion_result = self.emotion_analyzer.analyze(
                    text=response.response, user_id="kira"
                )

                # Emit signal to display Kira's response (thread-safe)
                self.message_received.emit(
                    "Kira", response.response, "#CE93D8"
                )  # Violet clair pour fond sombre

                # Update emotion display
                emotion_emoji = {
                    "joy": "😊",
                    "angry": "😠",
                    "sorrow": "😢",
                    "surprised": "😲",
                    "fun": "😄",
                    "neutral": "😐",
                }
                emotion_name = {
                    "joy": "Joyeux",
                    "angry": "En colère",
                    "sorrow": "Triste",
                    "surprised": "Surpris",
                    "fun": "Amusé",
                    "neutral": "Neutre",
                }

                emoji = emotion_emoji.get(emotion_result.emotion, "😐")
                name = emotion_name.get(emotion_result.emotion, "Neutre")
                intensity = int(emotion_result.intensity)

                self.emotion_updated.emit(f"{emoji} {name} ({intensity}%)")

                # Send emotion to Unity VRM if connected and loaded
                if self.unity_bridge.is_connected() and self.vrm_loaded:
                    vrm_data = self.emotion_analyzer.get_vrm_blendshape(
                        emotion_result.emotion, emotion_result.intensity
                    )

                    if vrm_data and vrm_data.get("recommended", False):
                        blendshape = vrm_data["blendshape"]
                        value = vrm_data["value"]

                        # Map emotion names to expression IDs
                        expression_map = {
                            "Joy": "joy",
                            "Angry": "angry",
                            "Sorrow": "sorrow",
                            "Surprised": "surprised",
                            "Fun": "fun",
                        }

                        expr_id = expression_map.get(blendshape)
                        if expr_id:
                            self.unity_bridge.set_expression(expr_id, value)
                            logger.info(f"Set VRM expression: {expr_id} = {value:.2f}")

                            # Update slider in Expressions tab (convert 0-1 to 0-100)
                            slider_value = value * 100.0
                            self.expression_changed.emit(expr_id, slider_value)

                # Update stats
                self.stats_updated.emit()

            except Exception as e:
                logger.error(f"Error processing chat message: {e}", exc_info=True)
                self.message_received.emit(
                    "Système", f"❌ Erreur : {str(e)}", "#EF5350"
                )  # Rouge clair
            finally:
                # Re-enable input via signal (thread-safe)
                self.chat_input_ready.emit()

        thread = threading.Thread(target=process_message, daemon=True)
        thread.start()

    def enable_chat_input(self):
        """Réactive l'input de chat après le traitement d'un message.

        Cette méthode est appelée via le signal chat_input_ready pour garantir
        que la réactivation se fait dans le thread principal Qt.
        """
        # Hide typing indicator
        self.typing_indicator.setText("")

        # Re-enable input controls
        self.send_btn.setEnabled(True)
        self.chat_input.setEnabled(True)
        self.chat_input.setFocus()

    def append_chat_message(self, sender: str, message: str, color: str):
        """Append a message to the chat display.

        Args:
            sender: Name of the sender
            message: Message content
            color: Color for the sender name (hex code)
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format message with HTML (colors adapted for dark theme)
        html = f"""
        <div style='margin-bottom: 10px;'>
            <span style='color: {color}; font-weight: bold;'>{sender}</span>
            <span style='color: #888; font-size: 11px;'> ({timestamp})</span><br>
            <span style='color: #e0e0e0;'>{message}</span>
        </div>
        """

        self.chat_display.append(html)

        # Incrémenter le compteur seulement pour "Vous" et "Kira", pas "Système"
        if sender in ["Vous", "Kira"]:
            self.current_session_messages += 1
            self.update_chat_stats()

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def update_chat_stats(self):
        """Update chat statistics display."""
        # Affiche le nombre de messages de la session actuelle (GUI uniquement)
        self.chat_stats_label.setText(f"Messages : {self.current_session_messages}")

    def clear_chat_history(self):
        """Clear chat history."""
        reply = QMessageBox.question(
            self,
            "Effacer l'historique",
            "Voulez-vous vraiment effacer tout l'historique de conversation ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear display
            self.chat_display.clear()

            # Reset session message counter
            self.current_session_messages = 0

            # Clear engine memory (if available)
            if self.ai_available:
                self.chat_engine.clear_user_history("desktop_user")
                self.emotion_analyzer.clear_user_history("kira")

            # Update stats
            self.update_chat_stats()

            # Reset emotion display
            self.current_emotion_label.setText("😐 Neutre")

            logger.info("Chat history cleared")

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
            ("fun", "😄 Fun (Amusé)"),
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
                lambda value, eid=expr_id, lbl=value_label, orig_text=expr_label: self.on_expression_slider_change(
                    eid, lbl, orig_text, value
                )
            )

            expr_layout.addWidget(slider)

            # Store references
            self.expression_sliders[expr_id] = slider
            self.expression_labels[expr_id] = value_label

            expressions_layout.addWidget(expr_container)

        layout.addWidget(expressions_group)

        # Reset button for expressions
        reset_layout = QHBoxLayout()
        reset_btn = QPushButton("⚙️ Réinitialiser toutes les expressions")
        reset_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        reset_btn.clicked.connect(self.reset_all_expressions)
        reset_layout.addStretch()
        reset_layout.addWidget(reset_btn)
        reset_layout.addStretch()
        layout.addLayout(reset_layout)

        layout.addStretch()

        self.tabs.addTab(tab, "Expressions")

    def create_animations_tab(self):
        """Create the animations control tab (auto-blink + head movements)."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Auto-blink control
        blink_group = QGroupBox("👁️ Clignement Automatique")
        blink_layout = QVBoxLayout()
        blink_group.setLayout(blink_layout)

        # Checkbox to enable/disable auto-blink
        self.auto_blink_checkbox = QCheckBox(
            "Activer le clignement automatique des yeux"
        )
        self.auto_blink_checkbox.setStyleSheet("font-size: 14px;")

        # Load saved state from config
        auto_blink_enabled = self.config.get("avatar.auto_blink.enabled", False)
        self.auto_blink_checkbox.setChecked(auto_blink_enabled)

        # Connect checkbox to handler
        self.auto_blink_checkbox.stateChanged.connect(self.on_auto_blink_toggle)

        blink_layout.addWidget(self.auto_blink_checkbox)

        # Info label
        blink_info = QLabel(
            "L'avatar clignera des yeux toutes les 2-5 secondes de manière aléatoire."
        )
        blink_info.setStyleSheet("font-size: 11px; color: gray; font-style: italic;")
        blink_info.setWordWrap(True)
        blink_layout.addWidget(blink_info)

        layout.addWidget(blink_group)

        # Head movement control
        head_group = QGroupBox("🎭 Mouvements de Tête Automatiques")
        head_layout = QVBoxLayout()
        head_group.setLayout(head_layout)

        # Checkbox to enable/disable head movements
        self.auto_head_movement_checkbox = QCheckBox(
            "Activer les mouvements de tête automatiques"
        )
        self.auto_head_movement_checkbox.setStyleSheet("font-size: 14px;")

        # Load saved state from config
        auto_head_enabled = self.config.get("avatar.auto_head_movement.enabled", True)
        self.auto_head_movement_checkbox.setChecked(auto_head_enabled)

        # Connect checkbox to handler
        self.auto_head_movement_checkbox.stateChanged.connect(
            self.on_auto_head_movement_toggle
        )

        head_layout.addWidget(self.auto_head_movement_checkbox)

        # Frequency slider (controls max_interval: 3-10s)
        freq_container = QVBoxLayout()
        self.head_freq_label = QLabel("⏱️ Fréquence des mouvements: 7.0s")
        self.head_freq_label.setStyleSheet("font-size: 12px;")
        freq_container.addWidget(self.head_freq_label)

        self.head_freq_slider = QSlider(Qt.Horizontal)
        self.head_freq_slider.setMinimum(30)  # 3.0s
        self.head_freq_slider.setMaximum(100)  # 10.0s
        self.head_freq_slider.setValue(70)  # 7.0s default
        self.head_freq_slider.setTickPosition(QSlider.TicksBelow)
        self.head_freq_slider.setTickInterval(10)

        # Load saved value
        saved_max_interval = self.config.get(
            "avatar.auto_head_movement.max_interval", 7.0
        )
        self.head_freq_slider.setValue(int(saved_max_interval * 10))

        # Connect slider to handler
        self.head_freq_slider.valueChanged.connect(
            lambda val: self.on_head_movement_param_change(
                self.head_freq_label,
                "⏱️ Fréquence des mouvements: {:.1f}s",
                val / 10.0,
                "max_interval",
            )
        )

        freq_container.addWidget(self.head_freq_slider)

        freq_info = QLabel("Intervalle maximum entre deux mouvements (3-10 secondes)")
        freq_info.setStyleSheet("font-size: 10px; color: gray; font-style: italic;")
        freq_info.setWordWrap(True)
        freq_container.addWidget(freq_info)

        head_layout.addLayout(freq_container)

        # Amplitude slider (controls max_angle: 2-10°)
        amp_container = QVBoxLayout()
        self.head_amp_label = QLabel("📐 Amplitude des mouvements: 5.0°")
        self.head_amp_label.setStyleSheet("font-size: 12px;")
        amp_container.addWidget(self.head_amp_label)

        self.head_amp_slider = QSlider(Qt.Horizontal)
        self.head_amp_slider.setMinimum(20)  # 2.0°
        self.head_amp_slider.setMaximum(100)  # 10.0°
        self.head_amp_slider.setValue(50)  # 5.0° default
        self.head_amp_slider.setTickPosition(QSlider.TicksBelow)
        self.head_amp_slider.setTickInterval(10)

        # Load saved value
        saved_max_angle = self.config.get("avatar.auto_head_movement.max_angle", 5.0)
        self.head_amp_slider.setValue(int(saved_max_angle * 10))

        # Connect slider to handler
        self.head_amp_slider.valueChanged.connect(
            lambda val: self.on_head_movement_param_change(
                self.head_amp_label,
                "📐 Amplitude des mouvements: {:.1f}°",
                val / 10.0,
                "max_angle",
            )
        )

        amp_container.addWidget(self.head_amp_slider)

        amp_info = QLabel("Angle maximum de rotation de la tête (2-10 degrés)")
        amp_info.setStyleSheet("font-size: 10px; color: gray; font-style: italic;")
        amp_info.setWordWrap(True)
        amp_container.addWidget(amp_info)

        head_layout.addLayout(amp_container)

        # Info label for head movements
        head_info_label = QLabel(
            "L'avatar bougera légèrement la tête de manière aléatoire pour paraître plus vivant."
        )
        head_info_label.setStyleSheet(
            "font-size: 11px; color: gray; font-style: italic;"
        )
        head_info_label.setWordWrap(True)
        head_layout.addWidget(head_info_label)

        layout.addWidget(head_group)

        # Transition speed control
        speed_group = QGroupBox("⚡ Contrôle des Transitions")
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
        speed_slider.setMaximum(100)  # Maps to 10.0 (fastest)
        speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        speed_slider.setTickInterval(
            10
        )  # Ticks at: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100

        # Block signals during initialization to prevent premature commands
        speed_slider.blockSignals(True)
        speed_slider.setValue(30)  # Maps to 3.0 (default - Normal speed) - ON A TICK!
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
        speed_desc_layout.addStretch(12)  # Space before "3.0 (Normal)"

        # Center label (normal at 3.0) - positioned at tick 30
        center_label = QLabel("3.0 (Normal)")
        center_label.setStyleSheet(
            "font-size: 11px; color: #4A90E2; font-weight: bold;"
        )
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

        # Reset button for animations
        reset_anim_layout = QHBoxLayout()
        reset_anim_btn = QPushButton("⚙️ Réinitialiser les animations")
        reset_anim_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        reset_anim_btn.clicked.connect(self.reset_animations)
        reset_anim_layout.addStretch()
        reset_anim_layout.addWidget(reset_anim_btn)
        reset_anim_layout.addStretch()
        layout.addLayout(reset_anim_layout)

        layout.addStretch()

        self.tabs.addTab(tab, "Animations")

    def create_logs_tab(self):
        """Create the logs display tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        logs_icon = QLabel("📋")
        logs_icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(logs_icon)

        logs_title = QLabel("Logs Application")
        logs_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(logs_title)
        header_layout.addStretch()

        # Clear button
        clear_logs_btn = QPushButton("🗑️ Effacer les logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(clear_logs_btn)

        layout.addLayout(header_layout)

        # Logs display area
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """
        )
        self.logs_display.setPlaceholderText(
            "Les logs de l'application apparaîtront ici en temps réel...\n\n"
            "💡 Utilisez cet onglet pour diagnostiquer les problèmes ou suivre l'activité."
        )
        layout.addWidget(self.logs_display)

        # Info label
        info_layout = QHBoxLayout()
        info_label = QLabel(
            "💡 Les logs sont automatiquement limités aux 1000 dernières lignes"
        )
        info_label.setStyleSheet("font-size: 11px; color: #888; font-style: italic;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        self.tabs.addTab(tab, "📋 Logs")

        # Setup logging handler to capture logs
        self._setup_log_handler()

    def _setup_log_handler(self):
        """Configure un handler pour capturer les logs et les afficher dans l'UI."""

        class QtLogHandler(logging.Handler):
            """Handler qui envoie les logs vers le QTextEdit."""

            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                self.max_lines = 1000  # Limite pour éviter surcharge mémoire

                # Formatter avec couleurs
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    datefmt="%H:%M:%S",
                )
                self.setFormatter(formatter)

            def emit(self, record):
                """Émet un log vers le widget."""
                try:
                    msg = self.format(record)

                    # Déterminer la couleur selon le niveau
                    if record.levelno >= logging.ERROR:
                        color = "#f44336"  # Rouge
                    elif record.levelno >= logging.WARNING:
                        color = "#ff9800"  # Orange
                    elif record.levelno >= logging.INFO:
                        color = "#4caf50"  # Vert
                    else:
                        color = "#2196f3"  # Bleu (DEBUG)

                    # Formater avec HTML pour les couleurs
                    html_msg = f'<span style="color: {color};">{msg}</span>'

                    # Ajouter au widget (thread-safe via Qt)
                    self.text_widget.append(html_msg)

                    # Limiter le nombre de lignes
                    current_text = self.text_widget.toPlainText()
                    lines = current_text.split("\n")
                    if len(lines) > self.max_lines:
                        # Garder seulement les N dernières lignes
                        self.text_widget.clear()
                        self.text_widget.setHtml(
                            "<br>".join(
                                [
                                    f'<span style="color: {color};">{line}</span>'
                                    for line in lines[-self.max_lines :]
                                ]
                            )
                        )

                    # Auto-scroll vers le bas
                    cursor = self.text_widget.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.text_widget.setTextCursor(cursor)

                except Exception:
                    pass  # Ignorer les erreurs du handler pour éviter récursion

        # Créer et ajouter le handler au logger root
        self.log_handler = QtLogHandler(self.logs_display)
        self.log_handler.setLevel(logging.DEBUG)  # Capturer tous les niveaux

        # Ajouter au logger root pour capturer tous les logs
        logging.getLogger().addHandler(self.log_handler)

        logger.info("📋 Logs handler activé - Les logs apparaîtront dans l'onglet Logs")

    def clear_logs(self):
        """Efface les logs affichés."""
        self.logs_display.clear()
        logger.info("🗑️ Logs effacés")

    def on_expression_slider_change(
        self, expression_id: str, label: QLabel, original_text: str, value: int
    ):
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

    def update_expression_slider(self, expression_id: str, value: float):
        """Update expression slider programmatically (from detected emotions).

        Args:
            expression_id: ID of the expression (e.g., "joy")
            value: Value 0-100 (intensity percentage)
        """
        if expression_id in self.expression_sliders:
            slider = self.expression_sliders[expression_id]
            label = self.expression_labels[expression_id]

            # Block signals temporarily to avoid triggering on_expression_slider_change
            slider.blockSignals(True)
            slider.setValue(int(value))
            slider.blockSignals(False)

            # Update label manually
            expressions_display = {
                "joy": "😊 Joy (Joyeux)",
                "angry": "😠 Angry (En colère)",
                "sorrow": "😢 Sorrow (Triste)",
                "surprised": "😲 Surprised (Surpris)",
                "fun": "😄 Fun (Amusé)",
            }
            original_text = expressions_display.get(expression_id, expression_id)
            label.setText(f"{original_text}: {int(value)}%")

            logger.debug(f"Updated slider {expression_id} to {value:.1f}%")

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

    def reset_animations(self):
        """Reset animation settings to defaults."""
        # Blink: disabled (False)
        self.auto_blink_checkbox.setChecked(False)
        self.config.set("avatar.auto_blink.enabled", False)

        # Head movement: enabled (True), freq=7.0s, amp=5.0°
        self.auto_head_movement_checkbox.setChecked(True)
        self.head_freq_slider.setValue(70)  # 7.0s
        self.head_amp_slider.setValue(50)  # 5.0°
        self.config.set("avatar.auto_head_movement.enabled", True)
        self.config.set("avatar.auto_head_movement.max_interval", 7.0)
        self.config.set("avatar.auto_head_movement.max_angle", 5.0)

        self.config.save()

        # Send to Unity if connected
        if self.unity_bridge.is_connected() and self.vrm_loaded:
            self.unity_bridge.set_auto_blink(False)
            self.unity_bridge.set_auto_head_movement(True, 3.0, 7.0, 5.0)

        logger.info("Reset animations to defaults")

    def reset_options(self):
        """Reset options to defaults."""
        # Transition speed: 3.0 (Normal) - slider value 30
        self.speed_slider.setValue(30)
        self.on_speed_slider_change(30)  # Update label and send to Unity

        self.config.save()

        logger.info("Reset options to defaults")

    def on_auto_blink_toggle(self, state: int):
        """Handle auto-blink checkbox state change.

        Args:
            state: Checkbox state (Qt.CheckState.Checked or Qt.CheckState.Unchecked)
        """
        enabled = state == Qt.CheckState.Checked.value

        # Save state to config
        self.config.set("avatar.auto_blink.enabled", enabled)
        self.config.save()

        logger.info(f"Auto-blink {'enabled' if enabled else 'disabled'}")

        # Send command to Unity only if connected AND VRM is loaded
        if self.unity_bridge.is_connected() and self.vrm_loaded:
            self.unity_bridge.set_auto_blink(enabled)
            logger.debug(f"Sent auto_blink command: {enabled}")
        elif not self.vrm_loaded:
            # Warn user that VRM must be loaded
            logger.warning("Cannot set auto-blink: VRM not loaded")
            # We keep the checkbox state saved for when VRM is loaded

    def on_auto_head_movement_toggle(self, state: int):
        """Handle auto head movement checkbox state change.

        Args:
            state: Checkbox state (Qt.CheckState.Checked or Qt.CheckState.Unchecked)
        """
        enabled = state == Qt.CheckState.Checked.value

        # Save state to config
        self.config.set("avatar.auto_head_movement.enabled", enabled)
        self.config.save()

        logger.info(f"Auto head movement {'enabled' if enabled else 'disabled'}")

        # Send command to Unity only if connected AND VRM is loaded
        if self.unity_bridge.is_connected() and self.vrm_loaded:
            # Get current parameter values from sliders
            min_interval = 3.0  # Fixed minimum
            max_interval = self.head_freq_slider.value() / 10.0
            max_angle = self.head_amp_slider.value() / 10.0

            self.unity_bridge.set_auto_head_movement(
                enabled, min_interval, max_interval, max_angle
            )
            logger.debug(
                f"Sent auto_head_movement command: enabled={enabled}, interval=[{min_interval}-{max_interval}]s, angle={max_angle}°"
            )
        elif not self.vrm_loaded:
            logger.warning("Cannot set auto head movement: VRM not loaded")
            # We keep the checkbox state saved for when VRM is loaded

    def on_head_movement_param_change(
        self, label: QLabel, label_format: str, value: float, param_type: str
    ):
        """Handle head movement parameter slider change.

        Args:
            label: QLabel to update with new value
            label_format: Format string for label text (with {:.1f} placeholder)
            value: Slider value (converted to float: 3.0-10.0s or 2.0-10.0°)
            param_type: Type of parameter ("max_interval" or "max_angle")
        """
        # Update label with current value
        label.setText(label_format.format(value))

        # Save to config
        config_key = f"avatar.auto_head_movement.{param_type}"
        self.config.set(config_key, value)
        self.config.save()

        logger.debug(f"Updated head movement {param_type} to {value:.1f}")

        # Send updated parameters to Unity if enabled and connected
        if (
            self.unity_bridge.is_connected()
            and self.vrm_loaded
            and self.auto_head_movement_checkbox.isChecked()
        ):

            # Get all current values
            min_interval = 3.0  # Fixed minimum
            max_interval = self.head_freq_slider.value() / 10.0
            max_angle = self.head_amp_slider.value() / 10.0

            # Send command with updated parameters
            self.unity_bridge.set_auto_head_movement(
                True, min_interval, max_interval, max_angle
            )
            logger.debug(
                f"Sent updated head movement params: interval=[{min_interval}-{max_interval}]s, angle={max_angle}°"
            )

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

        # Options menu
        options_menu = menubar.addMenu("Options")

        # IA submenu
        ia_menu = options_menu.addMenu("IA")

        # Profils IA
        ia_profiles_action = ia_menu.addAction("Profils IA...")
        ia_profiles_action.triggered.connect(self.manage_ia_profiles)

        ia_menu.addSeparator()

        # Memory submenu
        memory_menu = ia_menu.addMenu("Mémoire")

        reset_memory_action = memory_menu.addAction("Réinitialiser mémoire...")
        reset_memory_action.triggered.connect(self.reset_database)

        # Discord submenu
        discord_menu = options_menu.addMenu("Discord")

        set_token_action = discord_menu.addAction("Définir Token Bot Discord...")
        set_token_action.triggered.connect(self.set_discord_token)

        manage_channels_action = discord_menu.addAction("Gérer Salons Auto-Reply...")
        manage_channels_action.triggered.connect(self.manage_auto_reply_channels)

        # Help menu
        help_menu = menubar.addMenu("Aide")

        discord_action = help_menu.addAction("💬 Rejoindre Discord...")
        discord_action.triggered.connect(self.open_discord)

        help_menu.addSeparator()

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

    def load_ai_model(self):
        """Load AI/LLM model (ChatEngine + EmotionAnalyzer)."""
        try:
            # Show loading message
            self.ai_status_label.setText("⏳ Chargement du modèle IA...")
            self.load_ai_btn.setEnabled(False)
            QApplication.processEvents()  # Update UI

            logger.info("Loading AI components...")

            # Try to import and initialize AI components
            from src.ai.chat_engine import get_chat_engine
            from src.ai.emotion_analyzer import get_emotion_analyzer

            # Get instances
            self.chat_engine = get_chat_engine()
            self.emotion_analyzer = get_emotion_analyzer()

            # IMPORTANT: Load the LLM model into VRAM/RAM
            logger.info("Loading LLM model into GPU/CPU...")
            self.ai_status_label.setText("⏳ Chargement du modèle sur GPU...")
            QApplication.processEvents()  # Update UI

            if not self.chat_engine.model_manager.load_model():
                raise RuntimeError("Échec du chargement du modèle LLM")

            self.ai_available = True

            # Update UI
            self.ai_status_label.setText("✅ IA chargée : Zephyr-7B prêt")
            self.ai_status_label.setStyleSheet(
                "font-size: 13px; padding: 5px; color: #4CAF50;"
            )
            self.load_ai_btn.setEnabled(False)
            self.unload_ai_btn.setEnabled(True)

            # Update GPU profile label
            self.update_gpu_profile_display()

            # Enable chat input if on chat tab
            if hasattr(self, "chat_input"):
                self.chat_input.setEnabled(True)
                self.send_btn.setEnabled(True)
                self.chat_input.setPlaceholderText("Écrivez votre message ici...")

            logger.info("✅ AI components loaded successfully!")

            # Show success message
            self.append_chat_message(
                "Système",
                "✅ Modèle IA chargé avec succès ! Vous pouvez maintenant discuter avec Kira.",
                "#4CAF50",
            )

        except ImportError as e:
            error_msg = (
                "❌ Impossible de charger l'IA : llama-cpp-python n'est pas installé.\n\n"
                "Pour installer :\n"
                "pip install llama-cpp-python\n\n"
                f"Détails : {str(e)}"
            )
            self.ai_status_label.setText("❌ IA non disponible")
            self.ai_status_label.setStyleSheet(
                "font-size: 13px; padding: 5px; color: #f44336;"
            )
            self.load_ai_btn.setEnabled(True)
            logger.error(f"ImportError loading AI: {e}")

            # Show error dialog
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Erreur de chargement IA", error_msg)

        except Exception as e:
            error_msg = f"❌ Erreur lors du chargement de l'IA : {str(e)}"
            self.ai_status_label.setText("❌ Erreur de chargement")
            self.ai_status_label.setStyleSheet(
                "font-size: 13px; padding: 5px; color: #f44336;"
            )
            self.load_ai_btn.setEnabled(True)
            logger.error(f"Error loading AI: {e}")

            # Show error dialog
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Erreur de chargement IA", error_msg)

    def unload_ai_model(self):
        """Unload AI/LLM model to free memory."""
        try:
            logger.info("Unloading AI components...")

            # Unload LLM model from VRAM/RAM first
            if self.chat_engine and self.chat_engine.model_manager:
                logger.info("Unloading LLM model from GPU/CPU...")
                self.chat_engine.model_manager.unload_model()

            # Clear references
            self.chat_engine = None
            self.emotion_analyzer = None
            self.ai_available = False

            # Update UI
            self.ai_status_label.setText("Statut IA : Non chargé")
            self.ai_status_label.setStyleSheet("font-size: 13px; padding: 5px;")
            self.load_ai_btn.setEnabled(True)
            self.unload_ai_btn.setEnabled(False)

            # Reset GPU profile label
            self.gpu_profile_label.setText("Profil GPU : -")
            self.gpu_profile_label.setStyleSheet(
                "font-size: 12px; padding: 5px; color: #888; font-style: italic;"
            )

            # Disable chat input
            if hasattr(self, "chat_input"):
                self.chat_input.setEnabled(False)
                self.send_btn.setEnabled(False)
                self.chat_input.setPlaceholderText(
                    "⚠️ Chargez d'abord l'IA dans l'onglet Connexion"
                )

            logger.info("✅ AI components unloaded successfully!")

            # Show info message
            self.append_chat_message(
                "Système",
                "ℹ️ Modèle IA déchargé. Cliquez sur 'Charger IA' pour le recharger.",
                "#FF9800",
            )

        except Exception as e:
            logger.error(f"Error unloading AI: {e}")

    def reset_database(self):
        """Reset SQLite database (delete all conversations, emotions, facts)."""
        from PySide6.QtWidgets import QMessageBox
        import os
        import shutil
        from datetime import datetime

        # Confirmation dialog
        reply = QMessageBox.warning(
            self,
            "Réinitialiser la base de données",
            "⚠️ Cette action va supprimer TOUTES les données :\n\n"
            "• Conversations\n"
            "• Émotions\n"
            "• Faits extraits\n"
            "• Embeddings\n"
            "• Résumés\n\n"
            "Cette action est IRRÉVERSIBLE !\n\n"
            "Voulez-vous continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        try:
            logger.info("🔄 Réinitialisation de la base de données...")

            db_path = "data/memory/workly.db"
            db_dir = "data/memory"

            # Create backup before deletion
            if os.path.exists(db_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join(db_dir, "backups")
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, f"workly_backup_{timestamp}.db")

                shutil.copy2(db_path, backup_path)
                logger.info(f"💾 Backup créé : {backup_path}")

            # Delete database files
            db_files = [db_path, f"{db_path}-shm", f"{db_path}-wal"]
            for db_file in db_files:
                if os.path.exists(db_file):
                    os.remove(db_file)
                    logger.info(f"🗑️ Supprimé : {db_file}")

            # Reinitialize database if AI is loaded
            if self.chat_engine and self.chat_engine.memory_manager:
                logger.info("🔄 Réinitialisation du MemoryManager...")
                # Recreate database
                from src.ai.database import Database

                db = Database(db_path)
                db.create_schema()
                logger.info("✅ Nouvelle base de données créée")

            # Success message
            QMessageBox.information(
                self,
                "Base de données réinitialisée",
                "✅ La base de données a été réinitialisée avec succès !\n\n"
                f"💾 Un backup a été créé dans data/memory/backups/\n\n"
                "Vous pouvez continuer à utiliser l'application normalement.",
            )

            logger.info("✅ Base de données réinitialisée avec succès !")

        except Exception as e:
            error_msg = f"❌ Erreur lors de la réinitialisation : {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de réinitialiser la base de données :\n\n{str(e)}",
            )

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
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
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
                    f"Le modèle par défaut est introuvable :\n{file_path}\n\nVeuillez définir un nouveau modèle par défaut.",
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

                def send_initial_settings():
                    time.sleep(2.5)  # Wait 2.5 seconds for VRM to fully initialize

                    # Send transition speed
                    if hasattr(self, "speed_slider"):
                        value = self.speed_slider.value()
                        speed = value / 10.0  # Direct mapping
                        speed = max(0.1, min(10.0, speed))
                        self.unity_bridge.set_transition_speed(speed)
                        logger.info(f"Set initial transition speed to {speed:.1f}")

                    # Send auto-blink state
                    if hasattr(self, "auto_blink_checkbox"):
                        enabled = self.auto_blink_checkbox.isChecked()
                        self.unity_bridge.set_auto_blink(enabled)
                        logger.info(f"Set initial auto-blink to {enabled}")

                    # Send auto head movement state
                    if hasattr(self, "auto_head_movement_checkbox"):
                        enabled = self.auto_head_movement_checkbox.isChecked()
                        min_interval = 3.0
                        max_interval = self.head_freq_slider.value() / 10.0
                        max_angle = self.head_amp_slider.value() / 10.0
                        self.unity_bridge.set_auto_head_movement(
                            enabled, min_interval, max_interval, max_angle
                        )
                        logger.info(
                            f"Set initial auto head movement to {enabled} (interval=[{min_interval}-{max_interval}]s, angle={max_angle}°)"
                        )

                threading.Thread(target=send_initial_settings, daemon=True).start()
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
            "Fichiers VRM (*.vrm);;Tous les fichiers (*.*)",
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
                "Utilisez le bouton 'Charger modèle VRM' pour le charger automatiquement.",
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
            "Fichiers VRM (*.vrm);;Tous les fichiers (*.*)",
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
                if hasattr(self, "speed_slider"):
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

                # Reset VRM state when Unity disconnects
                if self.vrm_loaded:
                    self.vrm_loaded = False
                    self.load_vrm_btn.setText("Charger modèle VRM")
                    logger.info("Unity disconnected - VRM state reset")

    def open_discord(self):
        """Open Discord invite link in browser."""
        import webbrowser

        webbrowser.open("https://discord.gg/3Cpyxg29B4")
        logger.info("Opening Discord invite link")

    def show_about(self):
        """Show about dialog."""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About Workly",
            "Workly v0.17.0-alpha\n\n"
            "Interactive VRM Desktop Companion\n"
            "Hybrid Unity + Python Application\n\n"
            "© 2025 WorklyHQ\n\n"
            "💬 Rejoignez notre communauté Discord :\n"
            "https://discord.gg/3Cpyxg29B4",
        )

    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Application closing...")
        self.unity_bridge.disconnect()
        self.config.save()
        event.accept()


class WorklyApp:
    """Main application wrapper."""

    def __init__(self, argv):
        """Initialize the application.

        Args:
            argv: Command line arguments
        """
        self.app = QApplication(argv)
        self.app.setApplicationName("Workly")
        self.app.setOrganizationName("WorklyHQ")

        self.main_window = MainWindow()

    def run(self):
        """Run the application.

        Returns:
            Exit code
        """
        self.main_window.show()
        return self.app.exec()
