"""
Tests d'intégration complets - Session 14 Phase 5

Valide l'intégration de tous les modules des Phases 1-4 :
- Phase 1: MemoryManager, ConversationSummarizer, FactExtractor
- Phase 2: PersonalityEngine
- Phase 3: EmotionAnalyzer, EmotionMemory
- Phase 4: ContextAnalyzer

Tests sans LLM réel (mode simulation)
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.ai.chat_engine import ChatEngine, ChatResponse
from src.ai.config import AIConfig
from src.ai.memory import ConversationMemory


@pytest.fixture
def temp_storage():
    """Créer dossier temporaire pour tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_model_manager():
    """Mock ModelManager pour éviter chargement modèle."""
    mock = MagicMock()
    mock.is_loaded = True
    mock.generate.return_value = "Bonjour ! Comment puis-je t'aider ?"
    return mock


@pytest.fixture
def basic_config():
    """Configuration basique pour tests."""
    return AIConfig(
        model_path="dummy",
        system_prompt="Tu es Kira, une assistante virtuelle.",
        temperature=0.7,
        max_tokens=200,
        context_limit=10,
    )


class TestChatEngineBasicMode:
    """Tests ChatEngine mode basique (enable_advanced_ai=False)."""
    
    def test_initialization_basic_mode(self, basic_config, mock_model_manager):
        """Test : Initialisation mode basique."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=False
        )
        
        assert engine.config == basic_config
        assert engine.model_manager == mock_model_manager
        assert engine.enable_advanced_ai is False
        
        # Phase 3 & 4 toujours actives
        assert engine.emotion_analyzer is not None
        assert engine.context_analyzer is not None
        
        # Phases 1 & 2 désactivées
        assert engine.memory_manager is None
        assert engine.personality_engine is None
    
    def test_chat_basic_mode(self, basic_config, mock_model_manager):
        """Test : Conversation mode basique."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=False
        )
        
        response = engine.chat("Bonjour Kira !")
        
        assert isinstance(response, ChatResponse)
        assert response.response == "Bonjour ! Comment puis-je t'aider ?"
        assert response.emotion in ["neutral", "joy", "casual"]
        assert response.processing_time > 0
    
    def test_emotion_detection_basic_mode(self, basic_config, mock_model_manager):
        """Test : Détection émotions mode basique."""
        mock_model_manager.generate.return_value = "Je suis super content de t'aider ! 😊"
        
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=False
        )
        
        response = engine.chat("Comment ça va ?")
        
        # EmotionAnalyzer détecte émotion de la réponse
        assert response.emotion in ["joy", "neutral", "happy", "excited"]
    
    def test_context_analysis_basic_mode(self, basic_config, mock_model_manager):
        """Test : Analyse contextuelle mode basique."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=False
        )
        
        # ContextAnalyzer devrait analyser le message
        engine.chat("Comment ça marche ?")
        
        # Vérifier historique ContextAnalyzer
        assert len(engine.context_analyzer.analysis_history) == 1
        analysis = engine.context_analyzer.analysis_history[0]
        assert analysis.intent == "question"


class TestChatEngineAdvancedMode:
    """Tests ChatEngine mode avancé (enable_advanced_ai=True)."""
    
    def test_initialization_advanced_mode(self, basic_config, mock_model_manager, temp_storage):
        """Test : Initialisation mode avancé."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        assert engine.enable_advanced_ai is True
        
        # Toutes les phases actives
        assert engine.emotion_analyzer is not None
        assert engine.context_analyzer is not None
        assert engine.memory_manager is not None
        assert engine.personality_engine is not None
    
    def test_memory_manager_integration(self, basic_config, mock_model_manager, temp_storage):
        """Test : Intégration MemoryManager (Phase 1)."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Conversation
        engine.chat("Mon nom est Alice")
        engine.chat("J'aime le Python")
        
        # Vérifier que MemoryManager a enregistré
        assert len(engine.memory_manager.current_conversation) == 4  # 2 user + 2 assistant
        
        # Vérifier extraction faits (peut prendre quelques messages)
        facts = engine.memory_manager.facts
        assert isinstance(facts, dict)
    
    def test_personality_engine_integration(self, basic_config, mock_model_manager, temp_storage):
        """Test : Intégration PersonalityEngine (Phase 2)."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Récupérer traits de base
        initial_personality = engine.personality_engine.personality.copy()
        
        # Conversation avec feedback positif
        mock_model_manager.generate.return_value = "Super, merci beaucoup ! 😊"
        engine.chat("Aide-moi s'il te plaît")
        
        # Les traits peuvent évoluer légèrement
        # (changement minime car 1 seule interaction)
        current_personality = engine.personality_engine.personality
        assert isinstance(current_personality, dict)
        assert "empathy" in current_personality or "kindness" in current_personality
    
    def test_emotion_memory_integration(self, basic_config, mock_model_manager, temp_storage):
        """Test : Intégration EmotionMemory (Phase 3)."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Plusieurs messages avec émotions
        mock_model_manager.generate.return_value = "Je suis content ! 😊"
        engine.chat("Bonjour !")
        
        mock_model_manager.generate.return_value = "Génial, super !"
        engine.chat("Merci !")
        
        # Vérifier EmotionMemory
        stats = engine.emotion_analyzer.get_stats()
        if "emotion_memory_stats" in stats:
            assert stats["emotion_memory_stats"]["total_entries"] >= 2
    
    def test_all_phases_together(self, basic_config, mock_model_manager, temp_storage):
        """Test : Toutes les phases ensemble (intégration complète)."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Conversation réaliste
        messages = [
            ("Bonjour Kira !", "Bonjour ! Comment vas-tu ?"),
            ("Mon nom est Bob", "Enchanté Bob ! Comment puis-je t'aider ?"),
            ("J'aime Python et Unity", "Super ! Python et Unity sont géniaux."),
            ("Comment créer un chatbot ?", "Pour créer un chatbot, tu peux..."),
            ("Merci beaucoup !", "Avec plaisir ! N'hésite pas si tu as d'autres questions."),
        ]
        
        for user_msg, bot_response in messages:
            mock_model_manager.generate.return_value = bot_response
            response = engine.chat(user_msg)
            
            assert isinstance(response, ChatResponse)
            assert response.response == bot_response
            assert response.processing_time > 0
        
        # Vérifications finales
        
        # Phase 1: MemoryManager
        assert len(engine.memory_manager.current_conversation) == 10  # 5 user + 5 assistant
        
        # Phase 2: PersonalityEngine
        assert engine.personality_engine.personality is not None
        assert len(engine.personality_engine.personality) > 0
        
        # Phase 3: EmotionAnalyzer
        assert len(engine.emotion_analyzer.emotion_history) > 0
        
        # Phase 4: ContextAnalyzer
        assert len(engine.context_analyzer.analysis_history) == 5
        summary = engine.context_analyzer.get_conversation_summary(window=5)
        assert summary["total_messages"] == 5


class TestBackwardCompatibility:
    """Tests de compatibilité backward (ancien code doit fonctionner)."""
    
    def test_old_code_still_works(self, basic_config, mock_model_manager):
        """Test : Ancien code fonctionne toujours."""
        # Code qui existait avant Session 14
        engine = ChatEngine(config=basic_config, model_manager=mock_model_manager)
        
        response = engine.chat("Test")
        
        assert isinstance(response, ChatResponse)
        assert response.response is not None
        assert response.emotion is not None
    
    def test_memory_cleared(self, basic_config, mock_model_manager):
        """Test : clear_user_history fonctionne."""
        engine = ChatEngine(config=basic_config, model_manager=mock_model_manager)
        
        engine.chat("Message 1")
        engine.chat("Message 2")
        
        deleted = engine.clear_user_history("desktop_user")
        assert deleted >= 0


class TestErrorHandling:
    """Tests de gestion d'erreurs."""
    
    def test_chat_without_loaded_model(self, basic_config):
        """Test : Erreur si modèle non chargé."""
        mock_model = MagicMock()
        mock_model.is_loaded = False
        
        engine = ChatEngine(config=basic_config, model_manager=mock_model)
        
        with pytest.raises(RuntimeError, match="Modèle LLM non chargé"):
            engine.chat("Test")
    
    def test_generation_error_handling(self, basic_config, mock_model_manager):
        """Test : Gestion erreur génération."""
        mock_model_manager.generate.side_effect = Exception("Erreur LLM")
        
        engine = ChatEngine(config=basic_config, model_manager=mock_model_manager)
        
        with pytest.raises(RuntimeError, match="Échec génération réponse"):
            engine.chat("Test")


class TestContextInjection:
    """Tests d'injection de contexte dans prompts."""
    
    def test_personality_injected_in_prompt(self, basic_config, mock_model_manager, temp_storage):
        """Test : Personnalité injectée dans prompt."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Espionner _build_prompt
        original_build = engine._build_prompt
        prompts_captured = []
        
        def capture_prompt(*args, **kwargs):
            result = original_build(*args, **kwargs)
            prompts_captured.append(result)
            return result
        
        engine._build_prompt = capture_prompt
        
        engine.chat("Test")
        
        assert len(prompts_captured) == 1
        prompt = prompts_captured[0]
        
        # Vérifier injection personnalité
        # (PersonalityEngine génère un prompt système)
        assert "<|system|>" in prompt
    
    def test_context_analyzer_info_in_prompt(self, basic_config, mock_model_manager):
        """Test : Contexte conversationnel injecté."""
        engine = ChatEngine(config=basic_config, model_manager=mock_model_manager)
        
        # Plusieurs messages pour créer contexte
        engine.chat("Comment ça va ?")
        engine.chat("Pourquoi le ciel est bleu ?")
        
        # Capturer prochain prompt
        prompts_captured = []
        original_build = engine._build_prompt
        
        def capture_prompt(*args, **kwargs):
            result = original_build(*args, **kwargs)
            prompts_captured.append(result)
            return result
        
        engine._build_prompt = capture_prompt
        
        engine.chat("Merci !")
        
        assert len(prompts_captured) == 1
        prompt = prompts_captured[0]
        
        # Vérifier que le prompt contient le système
        assert "<|system|>" in prompt


class TestMemoryPersistence:
    """Tests de persistance des données."""
    
    def test_emotion_memory_persists(self, basic_config, mock_model_manager, temp_storage):
        """Test : Mémoire émotionnelle persiste."""
        # Première instance
        engine1 = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        engine1.chat("Test message")
        
        # Vérifier fichier créé (dans data/memory/ par défaut, pas temp_storage)
        # EmotionMemory utilise toujours data/memory/emotion_history.json
        emotion_file = Path("data") / "memory" / "emotion_history.json"
        assert emotion_file.exists()
        
        # Deuxième instance (charge depuis fichier)
        engine2 = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Devrait avoir chargé historique
        stats = engine2.emotion_analyzer.get_stats()
        if "emotion_memory_stats" in stats:
            assert stats["emotion_memory_stats"]["total_entries"] > 0


# ============================================================================
# MARKERS PYTEST
# ============================================================================

pytestmark = pytest.mark.integration
