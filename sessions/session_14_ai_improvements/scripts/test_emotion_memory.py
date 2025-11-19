"""
Tests unitaires pour EmotionMemory

Tests de mémoire émotionnelle :
- Stockage/récupération émotions
- Distribution et statistiques
- Détection patterns
- Tendances émotionnelles
- Génération contexte pour prompts
"""

import pytest
import os
import tempfile
import shutil
from src.ai.emotion_memory import EmotionMemory, EmotionEntry


@pytest.fixture
def temp_storage():
    """Fixture : fichier temporaire pour stockage"""
    temp_dir = tempfile.mkdtemp(prefix="workly_emotion_memory_test_")
    temp_file = os.path.join(temp_dir, "emotion_history.json")
    yield temp_file
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def memory(temp_storage):
    """Fixture : EmotionMemory avec storage temporaire"""
    return EmotionMemory(storage_file=temp_storage, max_entries=10)


# ========== TESTS INITIALISATION ==========

def test_init_creates_memory(memory):
    """Test création mémoire"""
    assert len(memory.history) == 0
    assert memory.max_entries == 10


def test_init_creates_storage_file(temp_storage):
    """Test création fichier storage"""
    memory = EmotionMemory(storage_file=temp_storage)
    # Ajouter une émotion pour forcer sauvegarde
    memory.add_emotion('joy', 80, 90, 'user', 'Test message')
    
    assert os.path.exists(temp_storage)


# ========== TESTS ADD EMOTION ==========

def test_add_emotion_basic(memory):
    """Test ajout émotion basique"""
    memory.add_emotion('joy', 80, 90, 'user', 'Je suis content !')
    
    assert len(memory.history) == 1
    assert memory.history[0].emotion == 'joy'


def test_add_emotion_creates_preview(memory):
    """Test génération preview message"""
    long_message = "A" * 150
    memory.add_emotion('joy', 80, 90, 'user', long_message)
    
    entry = memory.history[0]
    assert len(entry.message_preview) <= 103  # 100 + "..."


def test_add_emotion_respects_max_entries(memory):
    """Test limite max_entries"""
    # Ajouter 15 émotions (max = 10)
    for i in range(15):
        memory.add_emotion('joy', 80, 90, 'user', f'Message {i}')
    
    assert len(memory.history) == 10


# ========== TESTS GET RECENT ==========

def test_get_recent_emotions(memory):
    """Test récupération émotions récentes"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('sorrow', 60, 80, 'user', 'Test 2')
    memory.add_emotion('angry', 70, 85, 'user', 'Test 3')
    
    recent = memory.get_recent_emotions(2)
    
    assert len(recent) == 2
    assert recent[0].emotion == 'angry'  # Plus récent d'abord
    assert recent[1].emotion == 'sorrow'


def test_get_recent_filter_by_source(memory):
    """Test filtre par source"""
    memory.add_emotion('joy', 80, 90, 'user', 'User message')
    memory.add_emotion('neutral', 30, 95, 'assistant', 'Assistant response')
    memory.add_emotion('fun', 85, 90, 'user', 'User message 2')
    
    user_only = memory.get_recent_emotions(10, source='user')
    
    assert len(user_only) == 2
    assert all(e.source == 'user' for e in user_only)


# ========== TESTS DISTRIBUTION ==========

def test_get_emotion_distribution(memory):
    """Test distribution émotions"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('joy', 75, 85, 'user', 'Test 2')
    memory.add_emotion('sorrow', 60, 80, 'user', 'Test 3')
    
    dist = memory.get_emotion_distribution()
    
    assert dist['joy'] == 2
    assert dist['sorrow'] == 1


def test_get_dominant_emotion(memory):
    """Test émotion dominante"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('joy', 75, 85, 'user', 'Test 2')
    memory.add_emotion('sorrow', 60, 80, 'user', 'Test 3')
    
    dominant = memory.get_dominant_emotion()
    
    assert dominant == 'joy'


def test_get_dominant_emotion_empty(memory):
    """Test émotion dominante vide"""
    dominant = memory.get_dominant_emotion()
    
    assert dominant is None


# ========== TESTS AVERAGE INTENSITY ==========

def test_get_average_intensity(memory):
    """Test intensité moyenne"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('joy', 60, 85, 'user', 'Test 2')
    
    avg = memory.get_average_intensity()
    
    assert avg == 70.0


def test_get_average_intensity_by_emotion(memory):
    """Test intensité moyenne par émotion"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('sorrow', 60, 85, 'user', 'Test 2')
    
    avg_joy = memory.get_average_intensity(emotion='joy')
    
    assert avg_joy == 80.0


# ========== TESTS PATTERN DETECTION ==========

def test_detect_consecutive_pattern(memory):
    """Test détection pattern consécutif"""
    memory.add_emotion('sorrow', 60, 80, 'user', 'Test 1')
    memory.add_emotion('sorrow', 55, 75, 'user', 'Test 2')
    memory.add_emotion('sorrow', 65, 85, 'user', 'Test 3')
    
    has_pattern = memory.detect_emotional_pattern('consecutive', 'sorrow', 3)
    
    assert has_pattern is True


def test_detect_consecutive_pattern_false(memory):
    """Test pattern consécutif absent"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('sorrow', 60, 80, 'user', 'Test 2')
    memory.add_emotion('joy', 75, 85, 'user', 'Test 3')
    
    has_pattern = memory.detect_emotional_pattern('consecutive', 'joy', 3)
    
    assert has_pattern is False


# ========== TESTS EMOTIONAL TREND ==========

def test_get_emotional_trend_improving(memory):
    """Test tendance améliorante"""
    # Anciennes émotions négatives
    memory.add_emotion('sorrow', 60, 80, 'user', 'Test 1')
    memory.add_emotion('sorrow', 55, 75, 'user', 'Test 2')
    memory.add_emotion('angry', 50, 70, 'user', 'Test 3')
    memory.add_emotion('neutral', 30, 95, 'user', 'Test 4')
    memory.add_emotion('neutral', 25, 90, 'user', 'Test 5')
    
    # Récentes émotions positives
    memory.add_emotion('joy', 70, 85, 'user', 'Test 6')
    memory.add_emotion('joy', 80, 90, 'user', 'Test 7')
    memory.add_emotion('fun', 85, 90, 'user', 'Test 8')
    memory.add_emotion('joy', 75, 88, 'user', 'Test 9')
    memory.add_emotion('fun', 90, 92, 'user', 'Test 10')
    
    trend = memory.get_emotional_trend(window_size=5)
    
    assert trend == 'improving'


def test_get_emotional_trend_unknown(memory):
    """Test tendance inconnue (pas assez données)"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    
    trend = memory.get_emotional_trend()
    
    assert trend == 'unknown'


# ========== TESTS CONTEXT GENERATION ==========

def test_get_context_for_prompt(memory):
    """Test génération contexte prompt"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('joy', 75, 85, 'user', 'Test 2')
    memory.add_emotion('joy', 85, 92, 'user', 'Test 3')
    
    context = memory.get_context_for_prompt()
    
    assert 'joyeux' in context.lower()


def test_get_context_for_prompt_empty(memory):
    """Test contexte vide"""
    context = memory.get_context_for_prompt()
    
    assert context == ""


# ========== TESTS STATISTICS ==========

def test_get_statistics(memory):
    """Test statistiques complètes"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('neutral', 30, 95, 'assistant', 'Test 2')
    
    stats = memory.get_statistics()
    
    assert stats['total_entries'] == 2
    assert stats['user_entries'] == 1
    assert stats['assistant_entries'] == 1


def test_get_statistics_empty(memory):
    """Test statistiques vides"""
    stats = memory.get_statistics()
    
    assert stats['total_entries'] == 0


# ========== TESTS PERSISTENCE ==========

def test_persistence_across_instances(temp_storage):
    """Test persistance entre instances"""
    # Instance 1
    memory1 = EmotionMemory(storage_file=temp_storage)
    memory1.add_emotion('joy', 80, 90, 'user', 'Test persistence')
    
    # Instance 2
    memory2 = EmotionMemory(storage_file=temp_storage)
    
    assert len(memory2.history) == 1
    assert memory2.history[0].emotion == 'joy'


# ========== TESTS CLEAR ==========

def test_clear_history(memory):
    """Test effacement historique"""
    memory.add_emotion('joy', 80, 90, 'user', 'Test 1')
    memory.add_emotion('sorrow', 60, 80, 'user', 'Test 2')
    
    memory.clear_history()
    
    assert len(memory.history) == 0


# ========== TESTS REPR ==========

def test_repr(memory):
    """Test représentation string"""
    repr_str = repr(memory)
    
    assert 'EmotionMemory' in repr_str
    assert 'max=10' in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
