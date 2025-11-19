"""
Tests unitaires pour ContextAnalyzer

Session 14 Phase 4 : Analyse Contextuelle
"""

import pytest
from datetime import datetime
from src.ai.context_analyzer import ContextAnalyzer, ContextAnalysis


@pytest.fixture
def analyzer():
    """Fixture : Analyseur contextuel."""
    return ContextAnalyzer()


class TestContextAnalyzerInit:
    """Tests d'initialisation."""
    
    def test_creates_analyzer(self, analyzer):
        """Test : Crée analyseur."""
        assert analyzer is not None
        assert isinstance(analyzer, ContextAnalyzer)
        assert analyzer.analysis_history == []
    
    def test_has_intent_definitions(self, analyzer):
        """Test : Définit intentions."""
        assert "question" in analyzer.INTENTS
        assert "command" in analyzer.INTENTS
        assert "casual" in analyzer.INTENTS
        assert "gratitude" in analyzer.INTENTS
        assert len(analyzer.INTENTS) >= 8
    
    def test_has_sentiment_keywords(self, analyzer):
        """Test : Définit keywords sentiment."""
        assert len(analyzer.POSITIVE_KEYWORDS) > 0
        assert len(analyzer.NEGATIVE_KEYWORDS) > 0
        assert "bien" in analyzer.POSITIVE_KEYWORDS
        assert "mal" in analyzer.NEGATIVE_KEYWORDS


class TestIntentDetection:
    """Tests détection d'intentions."""
    
    def test_detects_question(self, analyzer):
        """Test : Détecte question."""
        analysis = analyzer.analyze("Comment ça marche ?")
        assert analysis.intent == "question"
        assert analysis.intent_confidence > 0.5
    
    def test_detects_command(self, analyzer):
        """Test : Détecte commande."""
        analysis = analyzer.analyze("Lance l'application maintenant !")
        assert analysis.intent == "command"
        assert analysis.intent_confidence > 0.5
    
    def test_detects_casual(self, analyzer):
        """Test : Détecte casual."""
        analysis = analyzer.analyze("Bonjour Kira !")
        assert analysis.intent == "casual"
        assert analysis.intent_confidence > 0.5
    
    def test_detects_gratitude(self, analyzer):
        """Test : Détecte gratitude."""
        analysis = analyzer.analyze("Merci beaucoup pour ton aide !")
        assert analysis.intent == "gratitude"
        assert analysis.intent_confidence > 0.5
    
    def test_detects_complaint(self, analyzer):
        """Test : Détecte plainte."""
        analysis = analyzer.analyze("J'ai un problème, ça marche pas !")
        assert analysis.intent == "complaint"
        assert analysis.intent_confidence > 0.0
    
    def test_detects_request_help(self, analyzer):
        """Test : Détecte demande d'aide."""
        analysis = analyzer.analyze("Peux-tu m'aider s'il te plaît ?")
        assert analysis.intent == "request_help"
        assert analysis.intent_confidence > 0.5
    
    def test_defaults_to_statement(self, analyzer):
        """Test : Défaut statement."""
        analysis = analyzer.analyze("Je pense que c'est intéressant.")
        assert analysis.intent == "statement"


class TestSentimentAnalysis:
    """Tests analyse sentiment."""
    
    def test_detects_positive_sentiment(self, analyzer):
        """Test : Détecte sentiment positif."""
        analysis = analyzer.analyze("Super génial merci ! 😊")
        assert analysis.sentiment == "positive"
        assert analysis.sentiment_score > 0.2
    
    def test_detects_negative_sentiment(self, analyzer):
        """Test : Détecte sentiment négatif."""
        analysis = analyzer.analyze("Nul problème bug crash 😡")
        assert analysis.sentiment == "negative"
        assert analysis.sentiment_score < -0.2
    
    def test_detects_neutral_sentiment(self, analyzer):
        """Test : Détecte sentiment neutre."""
        analysis = analyzer.analyze("Le code est dans le fichier.")
        assert analysis.sentiment == "neutral"
        assert -0.2 <= analysis.sentiment_score <= 0.2
    
    def test_sentiment_score_range(self, analyzer):
        """Test : Score sentiment dans [-1, 1]."""
        analysis = analyzer.analyze("Texte quelconque")
        assert -1.0 <= analysis.sentiment_score <= 1.0


class TestTopicExtraction:
    """Tests extraction de topics."""
    
    def test_extracts_technique_topic(self, analyzer):
        """Test : Extrait topic technique."""
        analysis = analyzer.analyze("J'ai un bug dans mon code Python")
        assert "technique" in analysis.topics
        assert "python" in analysis.topics
    
    def test_extracts_ia_topic(self, analyzer):
        """Test : Extrait topic IA."""
        analysis = analyzer.analyze("Comment fonctionne le chatbot AI ?")
        assert "ia" in analysis.topics
    
    def test_extracts_unity_topic(self, analyzer):
        """Test : Extrait topic Unity."""
        analysis = analyzer.analyze("Problème avec Unity GameObject")
        assert "unity" in analysis.topics
    
    def test_extracts_multiple_topics(self, analyzer):
        """Test : Extrait plusieurs topics."""
        analysis = analyzer.analyze("Bug Unity Python dans le code IA")
        assert len(analysis.topics) >= 3
        assert "technique" in analysis.topics
    
    def test_no_topics_generic_message(self, analyzer):
        """Test : Peu de topics si message générique."""
        analysis = analyzer.analyze("Salut ça va bien ?")
        # Peut avoir 0 ou 1 topic max (pas de sujets techniques)
        assert len(analysis.topics) <= 1


class TestEntityExtraction:
    """Tests extraction d'entités."""
    
    def test_extracts_capitalized_words(self, analyzer):
        """Test : Extrait mots avec majuscules."""
        analysis = analyzer.analyze("Bonjour Kira comment va Unity ?")
        # Kira et Unity détectés (pas Bonjour car début phrase)
        assert "Kira" in analysis.entities or "Unity" in analysis.entities
    
    def test_ignores_sentence_start(self, analyzer):
        """Test : Ignore début de phrase."""
        analysis = analyzer.analyze("Bonjour tout le monde")
        # "Bonjour" ne doit pas être détecté (début phrase)
        assert "Bonjour" not in analysis.entities
    
    def test_empty_entities_lowercase(self, analyzer):
        """Test : Vide si tout minuscule."""
        analysis = analyzer.analyze("bonjour comment ça va ?")
        assert len(analysis.entities) == 0


class TestComplexityAnalysis:
    """Tests analyse complexité."""
    
    def test_simple_message(self, analyzer):
        """Test : Message simple."""
        analysis = analyzer.analyze("Bonjour !")
        assert analysis.complexity == "simple"
    
    def test_medium_message(self, analyzer):
        """Test : Message moyen."""
        analysis = analyzer.analyze("Comment puis-je installer Python et configurer le projet ?")
        assert analysis.complexity == "medium"
    
    def test_complex_message(self, analyzer):
        """Test : Message complexe."""
        text = ("Je voudrais savoir comment configurer l'environnement de développement "
                "Python avec Unity pour créer un chatbot IA intégré avec des modèles VRM "
                "et une interface graphique PySide6.")
        analysis = analyzer.analyze(text)
        assert analysis.complexity == "complex"


class TestProactiveActions:
    """Tests suggestions d'actions proactives."""
    
    def test_question_suggests_detailed_answer(self, analyzer):
        """Test : Question suggère réponse détaillée."""
        analysis = analyzer.analyze("Comment ça marche ?")
        assert analysis.requires_action is True
        assert "provide_detailed_answer" in analysis.suggested_actions
    
    def test_command_suggests_execute(self, analyzer):
        """Test : Commande suggère exécution."""
        analysis = analyzer.analyze("Lance l'application !")
        assert analysis.requires_action is True
        assert "execute_command" in analysis.suggested_actions
    
    def test_complaint_suggests_empathy(self, analyzer):
        """Test : Plainte suggère empathie."""
        analysis = analyzer.analyze("J'ai un bug, ça marche pas !")
        assert analysis.requires_action is True
        assert "show_empathy" in analysis.suggested_actions
    
    def test_gratitude_suggests_acknowledge(self, analyzer):
        """Test : Gratitude suggère remerciement."""
        analysis = analyzer.analyze("Merci beaucoup !")
        assert analysis.requires_action is True
        assert "acknowledge_thanks" in analysis.suggested_actions
    
    def test_negative_sentiment_suggests_empathy(self, analyzer):
        """Test : Sentiment négatif suggère empathie."""
        analysis = analyzer.analyze("Je suis vraiment déçu et frustré 😔")
        assert "adjust_tone_empathetic" in analysis.suggested_actions


class TestContextAnalysisDataclass:
    """Tests dataclass ContextAnalysis."""
    
    def test_creates_analysis_result(self, analyzer):
        """Test : Crée résultat d'analyse."""
        analysis = analyzer.analyze("Test message")
        assert isinstance(analysis, ContextAnalysis)
        assert hasattr(analysis, 'intent')
        assert hasattr(analysis, 'sentiment')
        assert hasattr(analysis, 'topics')
        assert hasattr(analysis, 'timestamp')
        assert isinstance(analysis.timestamp, datetime)


class TestConversationHistory:
    """Tests historique de conversation."""
    
    def test_stores_analysis_in_history(self, analyzer):
        """Test : Stocke analyses dans historique."""
        analyzer.analyze("Message 1")
        analyzer.analyze("Message 2")
        assert len(analyzer.analysis_history) == 2
    
    def test_limits_history_to_100(self, analyzer):
        """Test : Limite historique à 100."""
        for i in range(150):
            analyzer.analyze(f"Message {i}")
        assert len(analyzer.analysis_history) == 100
    
    def test_clear_history(self, analyzer):
        """Test : Vide historique."""
        analyzer.analyze("Message 1")
        analyzer.analyze("Message 2")
        analyzer.clear_history()
        assert len(analyzer.analysis_history) == 0


class TestConversationSummary:
    """Tests résumé de conversation."""
    
    def test_summary_empty_history(self, analyzer):
        """Test : Résumé avec historique vide."""
        summary = analyzer.get_conversation_summary()
        assert summary["total_messages"] == 0
        assert summary["dominant_intent"] is None
        assert summary["dominant_sentiment"] is None
    
    def test_summary_with_messages(self, analyzer):
        """Test : Résumé avec messages."""
        analyzer.analyze("Comment ça va ?")
        analyzer.analyze("Pourquoi ça ?")
        analyzer.analyze("Quoi faire ?")
        
        summary = analyzer.get_conversation_summary(window=3)
        assert summary["total_messages"] == 3
        assert summary["dominant_intent"] == "question"
    
    def test_summary_dominant_sentiment(self, analyzer):
        """Test : Sentiment dominant dans résumé."""
        analyzer.analyze("Super génial ! 😊")
        analyzer.analyze("Merci beaucoup cool !")
        analyzer.analyze("Parfait top !")
        
        summary = analyzer.get_conversation_summary(window=3)
        assert summary["dominant_sentiment"] == "positive"
    
    def test_summary_common_topics(self, analyzer):
        """Test : Topics communs dans résumé."""
        analyzer.analyze("Bug Python dans le code")
        analyzer.analyze("Erreur Python")
        analyzer.analyze("Aide Python s'il te plaît")
        
        summary = analyzer.get_conversation_summary(window=3)
        assert "python" in summary["common_topics"]
    
    def test_summary_with_window(self, analyzer):
        """Test : Résumé avec fenêtre limitée."""
        for i in range(20):
            analyzer.analyze(f"Message {i}")
        
        summary = analyzer.get_conversation_summary(window=5)
        assert summary["total_messages"] == 5


class TestContextForPrompt:
    """Tests génération contexte pour prompt."""
    
    def test_context_empty_history(self, analyzer):
        """Test : Contexte vide si pas d'historique."""
        context = analyzer.get_context_for_prompt()
        assert context == ""
    
    def test_context_with_questions(self, analyzer):
        """Test : Contexte avec questions."""
        analyzer.analyze("Comment ça marche ?")
        analyzer.analyze("Pourquoi ça ?")
        
        context = analyzer.get_context_for_prompt(window=2)
        assert "question" in context.lower()
    
    def test_context_with_sentiment(self, analyzer):
        """Test : Contexte avec sentiment."""
        analyzer.analyze("Super génial merci ! 😊")
        analyzer.analyze("Cool parfait !")
        
        context = analyzer.get_context_for_prompt(window=2)
        assert "bonne humeur" in context.lower() or "positive" in context.lower()
    
    def test_context_with_topics(self, analyzer):
        """Test : Contexte avec topics."""
        analyzer.analyze("Bug Python dans Unity")
        analyzer.analyze("Erreur code Python")
        
        context = analyzer.get_context_for_prompt(window=2)
        assert "python" in context.lower() or "technique" in context.lower()
    
    def test_context_is_french(self, analyzer):
        """Test : Contexte en français."""
        analyzer.analyze("Comment ça va ?")
        context = analyzer.get_context_for_prompt(window=1)
        # Vérifier qu'il y a du français (accents, mots français)
        assert any(char in context for char in "éèàù") or \
               any(word in context.lower() for word in ["utilisateur", "souvent", "semble"])


class TestRepr:
    """Tests représentation string."""
    
    def test_repr(self, analyzer):
        """Test : Représentation string."""
        analyzer.analyze("Message 1")
        analyzer.analyze("Message 2")
        repr_str = repr(analyzer)
        assert "ContextAnalyzer" in repr_str
        assert "2 analyses" in repr_str


# ============================================================================
# MARKERS PYTEST
# ============================================================================

pytestmark = pytest.mark.unit
