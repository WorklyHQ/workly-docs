"""
Tests unitaires pour l'interface GUI Discord (Phase 10)

Tests pour :
- Création de l'onglet Discord
- Contrôle start/stop du bot
- Signaux Qt pour communication thread-safe
- Configuration Discord save/load
- Affichage messages (max 50)
- Statistiques Discord
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Import classes to test
from src.gui.app import MainWindow, DiscordSignals, DiscordBotThread


class TestDiscordSignals(unittest.TestCase):
    """Tests pour la classe DiscordSignals"""
    
    @classmethod
    def setUpClass(cls):
        """Setup Qt application (une seule fois pour tous les tests)"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def test_signals_creation(self):
        """Test création des signaux Discord"""
        signals = DiscordSignals()
        
        # Vérifier que tous les signaux existent
        self.assertTrue(hasattr(signals, 'status_changed'))
        self.assertTrue(hasattr(signals, 'message_received'))
        self.assertTrue(hasattr(signals, 'stats_updated'))
        self.assertTrue(hasattr(signals, 'error_occurred'))
    
    def test_signal_emission(self):
        """Test émission des signaux"""
        signals = DiscordSignals()
        
        # Mock receivers
        status_received = []
        message_received = []
        stats_received = []
        error_received = []
        
        def on_status(connected, bot_name):
            status_received.append((connected, bot_name))
        
        def on_message(timestamp, username, message):
            message_received.append((timestamp, username, message))
        
        def on_stats(stats):
            stats_received.append(stats)
        
        def on_error(error):
            error_received.append(error)
        
        # Connect signals
        signals.status_changed.connect(on_status)
        signals.message_received.connect(on_message)
        signals.stats_updated.connect(on_stats)
        signals.error_occurred.connect(on_error)
        
        # Emit signals
        signals.status_changed.emit(True, "Kira#1234")
        signals.message_received.emit("12:34:56", "User", "Hello")
        signals.stats_updated.emit({'messages': 10})
        signals.error_occurred.emit("Test error")
        
        # Verify
        self.assertEqual(len(status_received), 1)
        self.assertEqual(status_received[0], (True, "Kira#1234"))
        
        self.assertEqual(len(message_received), 1)
        self.assertEqual(message_received[0], ("12:34:56", "User", "Hello"))
        
        self.assertEqual(len(stats_received), 1)
        self.assertEqual(stats_received[0], {'messages': 10})
        
        self.assertEqual(len(error_received), 1)
        self.assertEqual(error_received[0], "Test error")


class TestDiscordBotThread(unittest.TestCase):
    """Tests pour la classe DiscordBotThread"""
    
    @classmethod
    def setUpClass(cls):
        """Setup Qt application"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def test_thread_creation(self):
        """Test création du thread Discord"""
        thread = DiscordBotThread("fake_token")
        
        self.assertIsNotNone(thread.signals)
        self.assertEqual(thread.token, "fake_token")
        self.assertIsNone(thread.bot)
        self.assertFalse(thread._stop_requested)
    
    def test_thread_properties(self):
        """Test propriétés du thread"""
        thread = DiscordBotThread("test_token_123")
        
        # Check signals object
        self.assertIsInstance(thread.signals, DiscordSignals)
        
        # Check token
        self.assertEqual(thread.token, "test_token_123")
        
        # Check initial state
        self.assertFalse(thread._stop_requested)


class TestMainWindowDiscord(unittest.TestCase):
    """Tests pour l'intégration Discord dans MainWindow"""
    
    @classmethod
    def setUpClass(cls):
        """Setup Qt application"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Setup before each test"""
        self.window = MainWindow()
    
    def tearDown(self):
        """Cleanup after each test"""
        if self.window:
            self.window.close()
            self.window = None
    
    def test_discord_tab_exists(self):
        """Test que l'onglet Discord existe"""
        # Find Discord tab
        discord_tab_found = False
        
        for i in range(self.window.tabs.count()):
            if "Discord" in self.window.tabs.tabText(i):
                discord_tab_found = True
                break
        
        self.assertTrue(discord_tab_found, "Onglet Discord non trouvé")
    
    def test_discord_components_exist(self):
        """Test que tous les composants Discord existent"""
        # Status label
        self.assertTrue(hasattr(self.window, 'discord_status_label'))
        
        # Buttons
        self.assertTrue(hasattr(self.window, 'discord_start_btn'))
        self.assertTrue(hasattr(self.window, 'discord_stop_btn'))
        
        # Messages display
        self.assertTrue(hasattr(self.window, 'discord_messages_display'))
        
        # Stats label
        self.assertTrue(hasattr(self.window, 'discord_stats_label'))
    
    def test_discord_initial_state(self):
        """Test état initial des composants Discord"""
        # Stop button should be disabled initially
        self.assertFalse(self.window.discord_stop_btn.isEnabled())
        
        # Start button should be enabled
        self.assertTrue(self.window.discord_start_btn.isEnabled())
        
        # Discord thread should be None
        self.assertIsNone(self.window.discord_thread)
        
        # Discord running should be False
        self.assertFalse(self.window.discord_running)
    
    def test_start_discord_bot_without_ai(self):
        """Test démarrage du bot sans IA chargée"""
        # Ensure AI is not available
        self.window.ai_available = False
        
        # Mock QMessageBox to avoid blocking
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            # Try to start bot
            self.window.start_discord_bot()
            
            # Verify warning was shown
            self.assertTrue(mock_warning.called)
        
        # Verify bot was not started
        self.assertIsNone(self.window.discord_thread)
        self.assertFalse(self.window.discord_running)
    
    def test_start_discord_bot_without_token(self):
        """Test démarrage du bot sans token (depuis .env)"""
        # Set AI as available
        self.window.ai_available = True
        
        # Mock os.getenv to return empty token
        with patch('os.getenv', return_value=""):
            # Mock QMessageBox to avoid blocking
            with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
                # Try to start bot
                self.window.start_discord_bot()
                
                # Verify warning was shown
                self.assertTrue(mock_warning.called)
        
        # Verify bot was not started
        self.assertIsNone(self.window.discord_thread)
        self.assertFalse(self.window.discord_running)
    
    def test_discord_status_changed_connected(self):
        """Test changement de statut Discord (connecté)"""
        # Call slot
        self.window.on_discord_status_changed(True, "Kira#1234")
        
        # Verify UI updated
        self.assertIn("Connecté", self.window.discord_status_label.text())
        self.assertIn("Kira#1234", self.window.discord_status_label.text())
    
    def test_discord_status_changed_disconnected(self):
        """Test changement de statut Discord (déconnecté)"""
        # Call slot
        self.window.on_discord_status_changed(False, "Déconnecté")
        
        # Verify UI updated
        self.assertIn("Déconnecté", self.window.discord_status_label.text())
    
    def test_discord_message_received(self):
        """Test réception de message Discord"""
        # Clear display
        self.window.discord_messages_display.clear()
        
        # Receive message
        self.window.on_discord_message_received("12:34:56", "TestUser", "Hello World")
        
        # Verify message displayed
        text = self.window.discord_messages_display.toPlainText()
        self.assertIn("12:34:56", text)
        self.assertIn("TestUser", text)
        self.assertIn("Hello World", text)
    
    def test_discord_stats_updated(self):
        """Test mise à jour des statistiques Discord"""
        stats = {
            'messages_processed': 42,
            'responses_sent': 35,
            'guilds': 2,
            'uptime_seconds': 3600
        }
        
        # Update stats
        self.window.on_discord_stats_updated(stats)
        
        # Verify stats displayed
        text = self.window.discord_stats_label.text()
        self.assertIn("42", text)  # messages_processed
        self.assertIn("35", text)  # responses_sent
        self.assertIn("2", text)   # guilds
        self.assertIn("3600", text) # uptime
    
    def test_discord_error_occurred(self):
        """Test gestion d'erreur Discord"""
        # Mock QMessageBox to avoid blocking
        with patch('PySide6.QtWidgets.QMessageBox.critical') as mock_critical:
            # Trigger error
            self.window.on_discord_error("Test error message")
            
            # Verify error dialog was shown
            self.assertTrue(mock_critical.called)
        
        # Verify UI state
        self.assertIn("Erreur", self.window.discord_status_label.text())


if __name__ == '__main__':
    unittest.main()
