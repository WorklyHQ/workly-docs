"""
Tests unitaires pour ConversationSummarizer

Tests de génération de résumés de conversations :
- Résumés via LLM (avec mock)
- Détection de points clés
- Seuils automatiques
- Formatage contexte
"""

import pytest
from datetime import datetime
from src.ai.conversation_summarizer import ConversationSummarizer


@pytest.fixture
def mock_llm():
    """Fixture : mock LLM callback"""
    def callback(prompt: str) -> str:
        if "résumer" in prompt.lower():
            return "Résumé : Discussion sur Python et développement."
        elif "points clés" in prompt.lower():
            return "- Point 1\n- Point 2\n- Point 3"
        return "Réponse test"
    
    return callback


@pytest.fixture
def summarizer(mock_llm):
    """Fixture : ConversationSummarizer avec mock LLM"""
    return ConversationSummarizer(llm_callback=mock_llm, max_tokens=200)


@pytest.fixture
def sample_messages():
    """Fixture : messages de test"""
    return [
        {'role': 'user', 'content': 'Bonjour !', 'timestamp': '2024-01-01T10:00:00'},
        {'role': 'assistant', 'content': 'Salut !', 'timestamp': '2024-01-01T10:00:05'},
        {'role': 'user', 'content': 'Comment programmer en Python ?', 'timestamp': '2024-01-01T10:01:00'},
        {'role': 'assistant', 'content': 'Je vais t\'expliquer les bases.', 'timestamp': '2024-01-01T10:01:15'},
        {'role': 'user', 'content': 'Merci beaucoup !', 'timestamp': '2024-01-01T10:02:00'},
    ]


# ========== TESTS RÉSUMÉS ==========

def test_summarize_basic(summarizer, sample_messages):
    """Test résumé basique"""
    result = summarizer.summarize(sample_messages)
    
    # Vérifier structure
    assert 'summary' in result
    assert 'message_count' in result
    assert 'timestamp' in result
    
    # Vérifier contenu
    assert result['message_count'] == 5
    assert len(result['summary']) > 0


def test_summarize_empty_messages(summarizer):
    """Test résumé avec liste vide"""
    result = summarizer.summarize([])
    
    assert 'error' in result
    assert result['message_count'] == 0


def test_summarize_too_few_messages(summarizer):
    """Test résumé avec trop peu de messages (< 5)"""
    messages = [
        {'role': 'user', 'content': 'Bonjour'},
        {'role': 'assistant', 'content': 'Salut'},
    ]
    
    result = summarizer.summarize(messages)
    
    # Doit signaler erreur
    assert 'error' in result


def test_summarize_with_keypoints(summarizer, sample_messages):
    """Test résumé avec extraction de points clés"""
    result = summarizer.summarize(sample_messages, include_keypoints=True)
    
    assert 'keypoints' in result
    assert isinstance(result['keypoints'], list)


def test_summarize_no_llm():
    """Test résumé sans LLM (fallback)"""
    summarizer_no_llm = ConversationSummarizer(llm_callback=None)
    
    messages = [
        {'role': 'user', 'content': 'Test ' * 50},
        {'role': 'assistant', 'content': 'Réponse ' * 50},
    ] * 3  # 6 messages
    
    result = summarizer_no_llm.summarize(messages)
    
    # Doit générer résumé basique
    assert 'summary' in result
    assert len(result['summary']) > 0


# ========== TESTS FORMATAGE ==========

def test_format_conversation(summarizer, sample_messages):
    """Test formatage conversation pour LLM"""
    formatted = summarizer._format_conversation(sample_messages)
    
    # Vérifier présence des rôles
    assert 'Utilisateur:' in formatted
    assert 'Assistant:' in formatted
    
    # Vérifier contenu
    assert 'Bonjour' in formatted
    assert 'Python' in formatted


def test_format_conversation_empty(summarizer):
    """Test formatage conversation vide"""
    formatted = summarizer._format_conversation([])
    
    assert formatted == ""


def test_clean_summary(summarizer):
    """Test nettoyage résumé"""
    raw_summary = "  <|system|>  Test   résumé  avec extra spaces  <|end|>  "
    
    cleaned = summarizer._clean_summary(raw_summary)
    
    # Vérifier nettoyage
    assert '<|system|>' not in cleaned
    assert '<|end|>' not in cleaned
    assert '  ' not in cleaned  # Pas de double espaces
    assert cleaned == cleaned.strip()


def test_clean_summary_long(summarizer):
    """Test nettoyage résumé trop long"""
    long_summary = "Test " * 200  # ~1000 caractères
    
    cleaned = summarizer._clean_summary(long_summary)
    
    # Doit être tronqué à max_chars
    assert len(cleaned) <= 500


# ========== TESTS POINTS CLÉS ==========

def test_detect_key_points_decision(summarizer):
    """Test détection décision"""
    message = "J'ai décidé d'utiliser Python pour ce projet."
    
    keypoints = summarizer.detect_key_points(message)
    
    assert 'decision' in keypoints


def test_detect_key_points_question(summarizer):
    """Test détection question"""
    message = "Comment faire pour installer Python ?"
    
    keypoints = summarizer.detect_key_points(message)
    
    assert 'question' in keypoints


def test_detect_key_points_action(summarizer):
    """Test détection action"""
    message = "Je vais faire un script Python demain."
    
    keypoints = summarizer.detect_key_points(message)
    
    assert 'action' in keypoints


def test_detect_key_points_problem(summarizer):
    """Test détection problème"""
    message = "J'ai un problème avec mon code Python."
    
    keypoints = summarizer.detect_key_points(message)
    
    assert 'problem' in keypoints


def test_detect_key_points_goal(summarizer):
    """Test détection objectif"""
    message = "Mon objectif est d'apprendre l'IA cette année."
    
    keypoints = summarizer.detect_key_points(message)
    
    assert 'goal' in keypoints


def test_detect_key_points_none(summarizer):
    """Test détection sans points clés"""
    message = "Voilà."
    
    keypoints = summarizer.detect_key_points(message)
    
    assert len(keypoints) == 0


# ========== TESTS SEUILS ==========

def test_should_summarize_true(summarizer):
    """Test seuil auto-résumé atteint"""
    assert summarizer.should_summarize(25) == True


def test_should_summarize_false(summarizer):
    """Test seuil auto-résumé non atteint"""
    assert summarizer.should_summarize(10) == False


def test_should_summarize_exact_threshold(summarizer):
    """Test seuil exact"""
    threshold = summarizer.auto_summarize_threshold
    assert summarizer.should_summarize(threshold) == True


# ========== TESTS BATCH ==========

def test_summarize_batch(summarizer, sample_messages):
    """Test résumé batch de conversations"""
    conversations = [
        sample_messages,
        sample_messages[:3],  # Conversation plus courte
        sample_messages * 2,  # Conversation plus longue
    ]
    
    summaries = summarizer.summarize_batch(conversations)
    
    # Vérifier nombre de résumés
    assert len(summaries) == 3
    
    # Vérifier qu'au moins un résumé existe
    assert any(s.get('summary') for s in summaries)


def test_summarize_batch_skip_short(summarizer):
    """Test batch skip conversations trop courtes"""
    conversations = [
        [{'role': 'user', 'content': 'Test'}],  # Trop court
        [{'role': 'user', 'content': 'Test'}] * 6,  # Assez long
    ]
    
    summaries = summarizer.summarize_batch(conversations)
    
    # Vérifier skip
    assert summaries[0].get('skipped') == True
    assert summaries[1].get('summary')


# ========== TESTS FORMATAGE CONTEXTE ==========

def test_format_summary_for_context(summarizer):
    """Test formatage résumé pour contexte prompt"""
    summary_data = {
        'summary': 'Test résumé.',
        'message_count': 10,
        'keypoints': ['Point 1', 'Point 2']
    }
    
    formatted = summarizer.format_summary_for_context(summary_data)
    
    # Vérifier structure
    assert '[Résumé conversation précédente' in formatted
    assert 'Test résumé' in formatted
    assert 'Points clés' in formatted
    assert 'Point 1' in formatted


def test_format_summary_for_context_empty(summarizer):
    """Test formatage résumé vide"""
    summary_data = {'summary': ''}
    
    formatted = summarizer.format_summary_for_context(summary_data)
    
    assert formatted == ""


def test_format_summary_for_context_no_keypoints(summarizer):
    """Test formatage résumé sans points clés"""
    summary_data = {
        'summary': 'Test résumé.',
        'message_count': 5
    }
    
    formatted = summarizer.format_summary_for_context(summary_data)
    
    # Ne doit pas contenir section points clés
    assert 'Points clés' not in formatted


# ========== TESTS INTÉGRATION ==========

def test_full_workflow(summarizer, sample_messages):
    """Test workflow complet : résumer + formater + détecter points"""
    # 1. Résumer
    summary = summarizer.summarize(sample_messages, include_keypoints=True)
    
    assert summary['summary']
    assert summary['keypoints']
    
    # 2. Formater pour contexte
    formatted = summarizer.format_summary_for_context(summary)
    
    assert len(formatted) > 0
    
    # 3. Détecter points clés dans un message
    keypoints = summarizer.detect_key_points(sample_messages[2]['content'])
    
    assert isinstance(keypoints, list)


# ========== TESTS EDGE CASES ==========

def test_messages_with_missing_fields(summarizer):
    """Test messages avec champs manquants"""
    messages = [
        {'content': 'Test'},  # Pas de role
        {'role': 'user'},     # Pas de content
    ]
    
    # Ne doit pas crasher
    result = summarizer.summarize(messages)
    
    assert isinstance(result, dict)


def test_messages_with_very_long_content(summarizer):
    """Test messages avec contenu très long"""
    messages = [
        {'role': 'user', 'content': 'Test ' * 5000},  # ~25k caractères
    ] * 6
    
    result = summarizer.summarize(messages)
    
    # Résumé doit être tronqué
    assert len(result['summary']) <= 500


def test_unicode_handling(summarizer):
    """Test gestion unicode"""
    messages = [
        {'role': 'user', 'content': 'Émojis 😊🎉 et accents éàù'},
    ] * 6
    
    result = summarizer.summarize(messages)
    
    assert isinstance(result['summary'], str)


# ========== TESTS CONFIGURATION ==========

def test_custom_max_tokens():
    """Test configuration max_tokens custom"""
    summarizer_custom = ConversationSummarizer(max_tokens=100)
    
    assert summarizer_custom.max_tokens == 100


def test_custom_thresholds():
    """Test configuration seuils custom"""
    summarizer_custom = ConversationSummarizer()
    summarizer_custom.auto_summarize_threshold = 15
    summarizer_custom.min_messages_for_summary = 3
    
    assert summarizer_custom.should_summarize(16) == True
    assert summarizer_custom.should_summarize(10) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
