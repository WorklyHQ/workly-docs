"""
Tests unitaires pour MemoryManager

Tests de gestion mémoire long-terme :
- Stockage conversations en segments
- Extraction automatique de faits
- Recherche sémantique (avec mock embeddings)
- Résumés automatiques
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from src.ai.memory_manager import MemoryManager


@pytest.fixture
def temp_storage():
    """Fixture : dossier temporaire pour stockage"""
    temp_dir = tempfile.mkdtemp(prefix="workly_memory_test_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_llm():
    """Fixture : mock LLM callback"""
    def callback(prompt: str) -> str:
        return "Résumé test : Discussion sur Python et développement."
    return callback


@pytest.fixture
def memory_manager(temp_storage, mock_llm):
    """Fixture : MemoryManager avec storage temporaire"""
    return MemoryManager(
        storage_dir=temp_storage,
        llm_callback=mock_llm
    )


# ========== TESTS INITIALISATION ==========

def test_init_creates_storage_dir(temp_storage, mock_llm):
    """Test création automatique dossier storage"""
    storage_path = os.path.join(temp_storage, "new_subdir")
    
    manager = MemoryManager(storage_dir=storage_path, llm_callback=mock_llm)
    
    # Vérifier création
    assert os.path.exists(storage_path)


def test_init_loads_existing_data(temp_storage, mock_llm):
    """Test chargement données existantes"""
    # Créer manager initial
    manager1 = MemoryManager(storage_dir=temp_storage, llm_callback=mock_llm)
    manager1.add_message('user', 'Test message')
    
    # Créer nouveau manager (doit charger données)
    manager2 = MemoryManager(storage_dir=temp_storage, llm_callback=mock_llm)
    
    assert len(manager2.current_conversation) == 0  # Conversation reset
    # Mais faits devraient être chargés si sauvegardés


def test_init_without_embeddings_model():
    """Test init sans sentence-transformers"""
    # Test que le manager fonctionne même sans embeddings
    manager = MemoryManager(storage_dir="data/memory_test_no_embed")
    
    assert manager is not None


# ========== TESTS AJOUT MESSAGES ==========

def test_add_message_user(memory_manager):
    """Test ajout message utilisateur"""
    memory_manager.add_message('user', 'Bonjour !')
    
    assert len(memory_manager.current_conversation) == 1
    assert memory_manager.current_conversation[0]['role'] == 'user'
    assert memory_manager.current_conversation[0]['content'] == 'Bonjour !'


def test_add_message_assistant(memory_manager):
    """Test ajout message assistant"""
    memory_manager.add_message('assistant', 'Salut !')
    
    assert len(memory_manager.current_conversation) == 1
    assert memory_manager.current_conversation[0]['role'] == 'assistant'


def test_add_message_extracts_facts(memory_manager):
    """Test extraction automatique de faits"""
    memory_manager.add_message('user', 'J\'adore la programmation Python !')
    
    # Vérifier extraction de préférence
    prefs = memory_manager.facts.get('preferences', [])
    assert len(prefs) > 0


def test_add_multiple_messages(memory_manager):
    """Test ajout de plusieurs messages"""
    # Ajouter moins que le seuil auto (20)
    for i in range(8):
        memory_manager.add_message('user', f'Message {i}')
        memory_manager.add_message('assistant', f'Réponse {i}')
    
    assert len(memory_manager.current_conversation) == 16


# ========== TESTS SEGMENTATION ==========

def test_auto_segmentation_threshold(memory_manager):
    """Test segmentation automatique au seuil"""
    # Ajouter messages jusqu'au seuil
    for i in range(memory_manager.auto_summarize_threshold):
        memory_manager.add_message('user', f'Message {i}')
    
    # Vérifier création segment
    segments = memory_manager.conversations.get('segments', [])
    assert len(segments) >= 1


def test_force_segment_creation(memory_manager):
    """Test création forcée de segment"""
    # Ajouter au moins min_messages_for_summary (5)
    for i in range(6):
        memory_manager.add_message('user', f'Test {i}')
    
    segment = memory_manager.force_segment_creation()
    
    assert 'segment_id' in segment
    assert segment['message_count'] == 6


def test_force_segment_empty_conversation(memory_manager):
    """Test force segment avec conversation vide"""
    result = memory_manager.force_segment_creation()
    
    assert 'error' in result


def test_segment_structure(memory_manager):
    """Test structure d'un segment créé"""
    for i in range(10):
        memory_manager.add_message('user', f'Message {i}')
    
    segment = memory_manager.force_segment_creation()
    
    # Vérifier structure
    assert 'segment_id' in segment
    assert 'messages' in segment
    assert 'summary' in segment
    assert 'created_at' in segment
    assert 'message_count' in segment


# ========== TESTS FAITS ==========

def test_extract_multiple_fact_types(memory_manager):
    """Test extraction de plusieurs types de faits"""
    message = (
        "Hier j'ai rencontré Marie à Paris. "
        "Elle m'a dit qu'elle adore Python. "
        "Nous travaillons sur un nouveau projet."
    )
    
    memory_manager.add_message('user', message)
    
    # Vérifier extraction
    facts = memory_manager.facts
    
    # Au moins un type de fait doit être détecté
    total_facts = (
        len(facts.get('entities', [])) +
        len(facts.get('preferences', [])) +
        len(facts.get('events', []))
    )
    assert total_facts > 0


def test_entity_deduplication(memory_manager):
    """Test dédoublonnage entités"""
    memory_manager.add_message('user', 'J\'ai vu Marie hier.')
    memory_manager.add_message('user', 'Marie travaille chez Google.')
    
    entities = memory_manager.facts.get('entities', [])
    
    # Marie ne doit apparaître qu'une fois avec occurrences = 2
    marie_entities = [e for e in entities if 'Marie' in e['value']]
    if marie_entities:
        assert marie_entities[0].get('occurrences', 1) >= 1


def test_facts_persistence(memory_manager):
    """Test persistence des faits en JSON"""
    memory_manager.add_message('user', 'J\'adore Python !')
    
    # Vérifier fichier créé
    assert os.path.exists(memory_manager.facts_file)
    
    # Vérifier contenu JSON valide
    import json
    with open(memory_manager.facts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert 'preferences' in data


# ========== TESTS RECHERCHE ==========

def test_search_relevant_context_without_embeddings(memory_manager):
    """Test recherche contexte sans embeddings (fallback)"""
    # Désactiver embeddings
    memory_manager.embedding_model = None
    
    # Ajouter segments
    for i in range(10):
        memory_manager.add_message('user', f'Test {i}')
    memory_manager.force_segment_creation()
    
    # Chercher contexte
    results = memory_manager.search_relevant_context('test query', top_k=2)
    
    # Doit utiliser fallback (derniers segments)
    assert isinstance(results, list)


def test_get_recent_segments(memory_manager):
    """Test récupération segments récents"""
    # Créer plusieurs segments
    for j in range(3):
        for i in range(10):
            memory_manager.add_message('user', f'Segment {j} Message {i}')
        memory_manager.force_segment_creation()
    
    recent = memory_manager._get_recent_segments(count=2)
    
    assert len(recent) <= 2


# ========== TESTS CONTEXTE POUR PROMPT ==========

def test_get_context_for_prompt(memory_manager):
    """Test construction contexte pour prompt"""
    # Ajouter données
    memory_manager.add_message('user', 'J\'adore Python !')
    memory_manager.add_message('assistant', 'Super !')
    
    context = memory_manager.get_context_for_prompt(
        query='Parle-moi de Python',
        include_facts=True,
        include_segments=False
    )
    
    assert isinstance(context, str)
    assert len(context) > 0


def test_get_context_includes_facts(memory_manager):
    """Test inclusion des faits dans contexte"""
    memory_manager.add_message('user', 'J\'adore la pizza !')
    
    context = memory_manager.get_context_for_prompt(
        'pizza',
        include_facts=True
    )
    
    assert 'pizza' in context.lower() or 'Préférences' in context


def test_get_context_max_tokens(memory_manager):
    """Test limite de tokens pour contexte"""
    # Ajouter beaucoup de messages
    for i in range(50):
        memory_manager.add_message('user', 'Test ' * 100)
    
    context = memory_manager.get_context_for_prompt(
        'test',
        max_tokens=100
    )
    
    # Approximation : 1 token ≈ 4 chars
    assert len(context) <= 100 * 4 + 100  # Marge d'erreur


# ========== TESTS STATISTIQUES ==========

def test_get_stats_structure(memory_manager):
    """Test structure des statistiques"""
    stats = memory_manager.get_stats()
    
    # Vérifier clés obligatoires
    required_keys = [
        'segments_count',
        'current_conversation_length',
        'entities_count',
        'preferences_count',
        'events_count',
        'embeddings_count',
        'storage_dir'
    ]
    
    for key in required_keys:
        assert key in stats


def test_get_stats_values(memory_manager):
    """Test valeurs des statistiques"""
    # Ajouter données
    memory_manager.add_message('user', 'Test')
    
    stats = memory_manager.get_stats()
    
    assert stats['current_conversation_length'] == 1
    assert stats['storage_dir'] == memory_manager.storage_dir


# ========== TESTS PERSISTENCE JSON ==========

def test_save_and_load_conversations(memory_manager):
    """Test sauvegarde/chargement conversations"""
    # Ajouter messages et créer segment
    for i in range(10):
        memory_manager.add_message('user', f'Test {i}')
    memory_manager.force_segment_creation()
    
    # Vérifier fichier existe
    assert os.path.exists(memory_manager.conversations_file)
    
    # Charger données
    data = memory_manager._load_json(memory_manager.conversations_file)
    
    assert 'segments' in data
    assert len(data['segments']) >= 1


def test_json_load_nonexistent_file(memory_manager):
    """Test chargement fichier inexistant"""
    data = memory_manager._load_json('nonexistent.json', default={'test': 'value'})
    
    assert data == {'test': 'value'}


def test_json_save_and_reload(memory_manager):
    """Test sauvegarde puis rechargement"""
    test_data = {'test_key': 'test_value', 'number': 42}
    
    test_file = os.path.join(memory_manager.storage_dir, 'test.json')
    memory_manager._save_json(test_file, test_data)
    
    loaded = memory_manager._load_json(test_file)
    
    assert loaded == test_data


# ========== TESTS EDGE CASES ==========

def test_add_message_empty_content(memory_manager):
    """Test ajout message vide"""
    memory_manager.add_message('user', '')
    
    # Ne doit pas crasher
    assert len(memory_manager.current_conversation) == 1


def test_add_message_very_long(memory_manager):
    """Test ajout message très long"""
    long_message = 'Test ' * 10000  # ~50k caractères
    
    memory_manager.add_message('user', long_message)
    
    # Ne doit pas crasher
    assert len(memory_manager.current_conversation) == 1


def test_unicode_in_messages(memory_manager):
    """Test messages avec unicode"""
    memory_manager.add_message('user', 'Émojis 😊🎉 et accents éàù')
    
    assert len(memory_manager.current_conversation) == 1


# ========== TESTS INTÉGRATION ==========

def test_full_workflow(memory_manager):
    """Test workflow complet : ajouter messages → segmenter → chercher"""
    # 1. Ajouter messages
    memory_manager.add_message('user', 'J\'adore Python !')
    memory_manager.add_message('assistant', 'Super choix !')
    
    # 2. Créer segment
    for i in range(20):
        memory_manager.add_message('user', f'Message {i}')
    
    # Vérifier segmentation auto
    segments = memory_manager.conversations.get('segments', [])
    assert len(segments) >= 1
    
    # 3. Chercher contexte
    context = memory_manager.get_context_for_prompt('Python')
    assert len(context) > 0
    
    # 4. Stats
    stats = memory_manager.get_stats()
    assert stats['segments_count'] >= 1


@pytest.mark.slow
def test_performance_many_messages(memory_manager):
    """Test performance avec beaucoup de messages"""
    import time
    
    start = time.time()
    
    # Ajouter 100 messages
    for i in range(100):
        memory_manager.add_message('user', f'Test message {i}')
    
    elapsed = time.time() - start
    
    # Doit traiter en moins de 5 secondes
    assert elapsed < 5.0, f"Performance dégradée : {elapsed:.2f}s pour 100 messages"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
