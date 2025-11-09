"""
Tests pour le Chat Engine (src/ai/chat_engine.py)

Tests :
- EmotionDetector
- ChatEngine (avec mocks)
- Intégration complète
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from src.ai.chat_engine import (
    ChatEngine,
    ChatResponse,
    EmotionDetector,
    get_chat_engine
)
from src.ai.config import AIConfig
from src.ai.memory import ConversationMemory
from src.ai.model_manager import ModelManager


# ============================================================================
# Tests EmotionDetector
# ============================================================================

class TestEmotionDetector:
    """Tests du détecteur d'émotions par mots-clés"""
    
    def test_detector_initialization(self):
        """Test initialisation du détecteur"""
        detector = EmotionDetector()
        
        assert hasattr(detector, 'EMOTION_KEYWORDS')
        assert 'joy' in detector.EMOTION_KEYWORDS
        assert 'angry' in detector.EMOTION_KEYWORDS
        assert 'sorrow' in detector.EMOTION_KEYWORDS
        assert 'surprised' in detector.EMOTION_KEYWORDS
        assert 'fun' in detector.EMOTION_KEYWORDS
        assert 'neutral' in detector.EMOTION_KEYWORDS
    
    def test_detect_joy(self):
        """Test détection de joie"""
        detector = EmotionDetector()
        
        texts = [
            "Je suis super content ! 😊",
            "C'est génial, vraiment top !",
            "Wow, parfait, excellent !",
            "Je suis trop heureux !"
        ]
        
        for text in texts:
            emotion = detector.analyze(text)
            assert emotion == 'joy', f"Failed for: {text}"
    
    def test_detect_angry(self):
        """Test détection de colère"""
        detector = EmotionDetector()
        
        texts = [
            "Je suis vraiment énervé ! 😠",
            "C'est de la rage pure !",
            "Trop agacé par ça...",
            "Je suis furieux !"
        ]
        
        for text in texts:
            emotion = detector.analyze(text)
            assert emotion == 'angry', f"Failed for: {text}"
    
    def test_detect_sorrow(self):
        """Test détection de tristesse"""
        detector = EmotionDetector()
        
        texts = [
            "C'est vraiment triste... 😢",
            "Malheureusement, c'est dommage",
            "Je suis désolé pour ça",
            "Quel chagrin !"
        ]
        
        for text in texts:
            emotion = detector.analyze(text)
            assert emotion == 'sorrow', f"Failed for: {text}"
    
    def test_detect_surprised(self):
        """Test détection de surprise"""
        detector = EmotionDetector()
        
        texts = [
            "Wow, c'est incroyable ! 😲",
            "Oh, vraiment surprenant !",
            "Waouh, étonnant !",
            "C'est stupéfiant !"
        ]
        
        for text in texts:
            emotion = detector.analyze(text)
            assert emotion == 'surprised', f"Failed for: {text}"
    
    def test_detect_fun(self):
        """Test détection d'amusement"""
        detector = EmotionDetector()
        
        texts = [
            "Haha, trop drôle ! 😂",
            "MDR c'est hilarant",
            "LOL, vraiment marrant",
            "Quelle blague amusante !"
        ]
        
        for text in texts:
            emotion = detector.analyze(text)
            assert emotion == 'fun', f"Failed for: {text}"
    
    def test_detect_neutral(self):
        """Test détection de neutre"""
        detector = EmotionDetector()
        
        texts = [
            "Voilà, c'est fait.",
            "Ok, bien reçu.",
            "Donc effectivement oui.",
            "Aucun mot-clé émotionnel ici."
        ]
        
        for text in texts:
            emotion = detector.analyze(text)
            assert emotion == 'neutral', f"Failed for: {text}"
    
    def test_empty_text(self):
        """Test avec texte vide"""
        detector = EmotionDetector()
        
        assert detector.analyze("") == 'neutral'
        assert detector.analyze("   ") == 'neutral'
    
    def test_mixed_emotions(self):
        """Test avec émotions mixtes (le plus fort l'emporte)"""
        detector = EmotionDetector()
        
        # Plus de joie que de tristesse
        text = "Je suis content, heureux, joyeux, mais un peu triste"
        emotion = detector.analyze(text)
        assert emotion == 'joy'
        
        # Plus de tristesse
        text = "C'est triste, dommage, malheureux, hélas, mais un peu content"
        emotion = detector.analyze(text)
        assert emotion == 'sorrow'


# ============================================================================
# Tests ChatEngine (mocked)
# ============================================================================

class TestChatEngine:
    """Tests du moteur conversationnel avec mocks"""
    
    @pytest.fixture
    def mock_config(self):
        """Config de test"""
        return AIConfig(
            model_path="fake_model.gguf",
            context_limit=10,
            gpu_profile="cpu_fallback",
            temperature=0.7,
            top_p=0.9,
            max_tokens=100,
            system_prompt="Tu es Kira, un assistant virtuel."
        )
    
    @pytest.fixture
    def mock_memory(self):
        """Memory mockée"""
        memory = Mock(spec=ConversationMemory)
        memory.get_history.return_value = []
        memory.save_interaction.return_value = None
        memory.clear_user_history.return_value = 5
        memory.get_stats.return_value = {'total_interactions': 100}
        return memory
    
    @pytest.fixture
    def mock_model_manager(self):
        """ModelManager mocké"""
        manager = Mock(spec=ModelManager)
        manager.is_loaded = True
        manager.generate.return_value = "Bonjour ! Je suis Kira ! 😊"
        manager.get_model_info.return_value = {
            'loaded': True,
            'model_path': 'fake_model.gguf'
        }
        return manager
    
    @pytest.fixture
    def chat_engine(self, mock_config, mock_memory, mock_model_manager):
        """ChatEngine avec toutes les dépendances mockées"""
        return ChatEngine(mock_config, mock_memory, mock_model_manager)
    
    def test_initialization(self, chat_engine):
        """Test initialisation du ChatEngine"""
        assert chat_engine.config is not None
        assert chat_engine.memory is not None
        assert chat_engine.model_manager is not None
        assert chat_engine.emotion_detector is not None
        assert isinstance(chat_engine.emotion_detector, EmotionDetector)
    
    def test_build_prompt_empty_history(self, chat_engine):
        """Test construction prompt sans historique"""
        prompt = chat_engine._build_prompt("Bonjour", [])
        
        assert "<|system|>" in prompt
        assert "Tu es Kira" in prompt
        assert "<|user|>" in prompt
        assert "Bonjour" in prompt
        assert "<|assistant|>" in prompt
    
    def test_build_prompt_with_history(self, chat_engine):
        """Test construction prompt avec historique"""
        history = [
            {'user_input': 'Salut', 'bot_response': 'Bonjour !'},
            {'user_input': 'Ça va ?', 'bot_response': 'Très bien merci !'}
        ]
        
        prompt = chat_engine._build_prompt("Comment tu t'appelles ?", history)
        
        assert "Salut" in prompt
        assert "Bonjour !" in prompt
        assert "Ça va ?" in prompt
        assert "Très bien merci !" in prompt
        assert "Comment tu t'appelles ?" in prompt
        assert prompt.count("<|user|>") == 3  # 2 historique + 1 actuel
        assert prompt.count("<|assistant|>") == 3  # 2 historique + 1 vide
    
    def test_chat_model_not_loaded(self, mock_config, mock_memory):
        """Test chat avec modèle non chargé (doit raise)"""
        mock_manager = Mock(spec=ModelManager)
        mock_manager.is_loaded = False
        
        engine = ChatEngine(mock_config, mock_memory, mock_manager)
        
        with pytest.raises(RuntimeError, match="Modèle LLM non chargé"):
            engine.chat("Bonjour", "test_user", "desktop")
    
    def test_chat_success(self, chat_engine, mock_memory, mock_model_manager):
        """Test conversation réussie"""
        response = chat_engine.chat(
            user_input="Bonjour Kira !",
            user_id="test_user",
            source="desktop"
        )
        
        # Vérifier la réponse
        assert isinstance(response, ChatResponse)
        assert response.response == "Bonjour ! Je suis Kira ! 😊"
        assert response.emotion == 'joy'  # À cause du 😊
        assert response.tokens_used > 0
        assert response.processing_time >= 0  # >= 0 car mock peut être instantané
        
        # Vérifier que memory a été appelée
        mock_memory.get_history.assert_called_once_with(
            user_id="test_user",
            limit=10,
            source="desktop"
        )
        
        mock_memory.save_interaction.assert_called_once()
        
        # Vérifier que generate a été appelé
        mock_model_manager.generate.assert_called_once()
    
    def test_chat_with_history(
        self,
        chat_engine,
        mock_memory,
        mock_model_manager
    ):
        """Test conversation avec historique"""
        # Simuler historique
        mock_memory.get_history.return_value = [
            {'user_input': 'Salut', 'bot_response': 'Bonjour !'}
        ]
        
        response = chat_engine.chat(
            user_input="Comment ça va ?",
            user_id="test_user",
            source="desktop"
        )
        
        assert isinstance(response, ChatResponse)
        assert response.context_messages == 1  # 1 message d'historique
    
    def test_chat_generation_error(
        self,
        chat_engine,
        mock_model_manager
    ):
        """Test erreur lors de la génération"""
        mock_model_manager.generate.side_effect = Exception("CUDA OOM")
        
        with pytest.raises(RuntimeError, match="Échec génération réponse"):
            chat_engine.chat("Bonjour", "test_user", "desktop")
    
    def test_clear_user_history(self, chat_engine, mock_memory):
        """Test effacement historique utilisateur"""
        deleted = chat_engine.clear_user_history("test_user", "desktop")
        
        assert deleted == 5
        mock_memory.clear_user_history.assert_called_once_with(
            "test_user",
            "desktop"
        )
    
    def test_get_stats(self, chat_engine, mock_memory, mock_model_manager):
        """Test récupération statistiques"""
        stats = chat_engine.get_stats()
        
        assert 'memory' in stats
        assert 'model' in stats
        assert 'config' in stats
        
        assert stats['memory']['total_interactions'] == 100
        assert stats['model']['loaded'] is True
        assert stats['config']['context_limit'] == 10
        assert stats['config']['gpu_profile'] == "cpu_fallback"
    
    def test_repr(self, chat_engine):
        """Test représentation string"""
        repr_str = repr(chat_engine)
        
        assert "ChatEngine" in repr_str
        assert "prêt" in repr_str
        assert "context=10" in repr_str
        assert "profile=cpu_fallback" in repr_str


# ============================================================================
# Tests Singleton
# ============================================================================

class TestGetChatEngine:
    """Tests de la fonction singleton get_chat_engine()"""
    
    def test_get_chat_engine_creates_instance(self):
        """Test que get_chat_engine crée une instance"""
        # Reset singleton
        import src.ai.chat_engine as module
        module._chat_engine_instance = None
        
        with patch('src.ai.chat_engine.get_config'), \
             patch('src.ai.chat_engine.get_memory'), \
             patch('src.ai.chat_engine.get_model_manager'):
            
            engine = get_chat_engine()
            
            assert engine is not None
            assert isinstance(engine, ChatEngine)
    
    def test_get_chat_engine_returns_same_instance(self):
        """Test que get_chat_engine retourne toujours la même instance"""
        # Reset singleton
        import src.ai.chat_engine as module
        module._chat_engine_instance = None
        
        with patch('src.ai.chat_engine.get_config'), \
             patch('src.ai.chat_engine.get_memory'), \
             patch('src.ai.chat_engine.get_model_manager'):
            
            engine1 = get_chat_engine()
            engine2 = get_chat_engine()
            
            assert engine1 is engine2


# ============================================================================
# Tests d'intégration (optionnels, lents)
# ============================================================================

@pytest.mark.slow
class TestChatEngineIntegration:
    """Tests d'intégration avec vraies dépendances (sauf modèle)"""
    
    def test_integration_with_real_memory(self, tmp_path):
        """Test intégration avec vraie mémoire SQLite"""
        # Créer DB temporaire
        db_path = tmp_path / "test_chat.db"
        
        # Config de test
        config = AIConfig(
            model_path="fake_model.gguf",
            context_limit=5,
            gpu_profile="cpu_fallback",
            temperature=0.7,
            top_p=0.9,
            max_tokens=50,
            system_prompt="Tu es Kira."
        )
        
        # Vraie mémoire
        memory = ConversationMemory(str(db_path))
        
        # Model manager mocké
        mock_manager = Mock(spec=ModelManager)
        mock_manager.is_loaded = True
        mock_manager.generate.return_value = "Salut ! Content de te voir ! 😊"
        mock_manager.get_model_info.return_value = {'loaded': True}
        
        # ChatEngine avec vraie mémoire
        engine = ChatEngine(config, memory, mock_manager)
        
        # Conversation 1
        response1 = engine.chat("Bonjour", "user123", "desktop")
        assert response1.response == "Salut ! Content de te voir ! 😊"
        assert response1.emotion == 'joy'
        
        # Conversation 2 (doit avoir historique)
        response2 = engine.chat("Comment ça va ?", "user123", "desktop")
        assert response2.context_messages == 1
        
        # Vérifier sauvegarde
        history = memory.get_history("user123", limit=10, source="desktop")
        assert len(history) == 2
        # Note: get_history retourne du plus récent au plus ancien
        assert history[-1]['user_input'] == "Bonjour"
        assert history[-2]['user_input'] == "Comment ça va ?"
    
    def test_emotion_detection_in_real_scenario(self):
        """Test détection émotions dans scénario réaliste"""
        detector = EmotionDetector()
        
        # Scénarios réalistes
        scenarios = [
            ("Génial ! Je suis super content d'apprendre ça !", "joy"),
            ("Pfff, c'est vraiment agaçant cette erreur...", "angry"),
            ("Oh non, c'est vraiment dommage pour toi... 😢", "sorrow"),
            ("Wow ! Je ne m'attendais pas du tout à ça !", "surprised"),
            ("Haha, excellent ! Vraiment trop drôle ! 😂", "fun"),
            ("D'accord, j'ai bien compris. Merci.", "neutral")
        ]
        
        for text, expected in scenarios:
            emotion = detector.analyze(text)
            assert emotion == expected, (
                f"Failed for: {text}\n"
                f"Expected: {expected}, Got: {emotion}"
            )


# ============================================================================
# Exécution
# ============================================================================

if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v", "--tb=short"])
