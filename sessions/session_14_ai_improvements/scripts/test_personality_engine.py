"""
Tests unitaires pour PersonalityEngine

Tests de personnalité évolutive :
- Initialisation et chargement
- Lecture/écriture traits
- Évolution basée sur feedback
- Adaptation contextuelle
- Génération prompts personnalisés
"""

import pytest
import os
import tempfile
import shutil
from src.ai.personality_engine import PersonalityEngine, PersonalityTrait


@pytest.fixture
def temp_storage():
    """Fixture : fichier temporaire pour stockage"""
    temp_dir = tempfile.mkdtemp(prefix="workly_personality_test_")
    temp_file = os.path.join(temp_dir, "personality.json")
    yield temp_file
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def engine(temp_storage):
    """Fixture : PersonalityEngine avec storage temporaire"""
    return PersonalityEngine(storage_file=temp_storage)


# ========== TESTS INITIALISATION ==========

def test_init_creates_default_personality(engine):
    """Test création personnalité par défaut"""
    assert len(engine.personality) == 6  # 6 traits par défaut

    # Vérifier présence des traits principaux
    required_traits = ['kindness', 'humor', 'formality', 'enthusiasm', 'empathy', 'creativity']
    for trait in required_traits:
        assert trait in engine.personality


def test_init_creates_storage_file(temp_storage):
    """Test création automatique fichier storage"""
    engine = PersonalityEngine(storage_file=temp_storage)

    # Vérifier fichier créé
    assert os.path.exists(temp_storage)


def test_init_loads_existing_personality(temp_storage):
    """Test chargement personnalité existante"""
    # Créer engine initial
    engine1 = PersonalityEngine(storage_file=temp_storage)
    engine1.update_trait('humor', 0.2, "Test modification")

    # Créer nouveau engine (doit charger données)
    engine2 = PersonalityEngine(storage_file=temp_storage)

    # Vérifier humor modifié chargé
    assert engine2.personality['humor'].score > 0.6  # Score initial + 0.2


def test_default_trait_scores(engine):
    """Test scores par défaut des traits"""
    # Vérifier que scores sont dans [0, 1]
    for trait_name, trait in engine.personality.items():
        assert 0.0 <= trait.score <= 1.0


# ========== TESTS GET TRAIT ==========

def test_get_trait_existing(engine):
    """Test récupération trait existant"""
    kindness = engine.get_trait('kindness')

    assert isinstance(kindness, float)
    assert 0.0 <= kindness <= 1.0


def test_get_trait_nonexistent(engine):
    """Test récupération trait inexistant"""
    score = engine.get_trait('nonexistent_trait')

    # Doit retourner valeur neutre
    assert score == 0.5


def test_get_trait_with_modifier(engine):
    """Test trait avec modifieur contextuel"""
    base_score = engine.personality['enthusiasm'].score

    # Ajouter modifieur
    engine.set_context_modifier('enthusiasm', 0.1)

    modified_score = engine.get_trait('enthusiasm')

    assert modified_score == pytest.approx(base_score + 0.1, abs=0.01)


# ========== TESTS UPDATE TRAIT ==========

def test_update_trait_increase(engine):
    """Test augmentation d'un trait"""
    initial_score = engine.personality['humor'].score

    engine.update_trait('humor', 0.1, "Test increase")

    new_score = engine.personality['humor'].score
    assert new_score > initial_score


def test_update_trait_decrease(engine):
    """Test diminution d'un trait"""
    initial_score = engine.personality['formality'].score

    engine.update_trait('formality', -0.1, "Test decrease")

    new_score = engine.personality['formality'].score
    assert new_score < initial_score


def test_update_trait_clipping_max(engine):
    """Test clipping à 1.0"""
    engine.update_trait('kindness', 10.0, "Test max")  # Énorme delta

    score = engine.personality['kindness'].score
    assert score == 1.0


def test_update_trait_clipping_min(engine):
    """Test clipping à 0.0"""
    engine.update_trait('humor', -10.0, "Test min")  # Énorme delta négatif

    score = engine.personality['humor'].score
    assert score == 0.0


def test_update_trait_creates_history(engine):
    """Test création historique d'évolution"""
    initial_history_len = len(engine.personality['enthusiasm'].evolution_history)

    engine.update_trait('enthusiasm', 0.05, "Test history")

    new_history_len = len(engine.personality['enthusiasm'].evolution_history)
    assert new_history_len > initial_history_len


def test_update_trait_ignores_small_delta(engine):
    """Test que petits deltas (<0.01) sont ignorés"""
    initial_score = engine.personality['empathy'].score
    initial_history = len(engine.personality['empathy'].evolution_history)

    engine.update_trait('empathy', 0.005, "Tiny change")  # < 0.01

    # Score et historique ne devraient pas changer
    assert engine.personality['empathy'].score == initial_score
    assert len(engine.personality['empathy'].evolution_history) == initial_history


def test_update_trait_unknown(engine):
    """Test update trait inexistant (ne doit pas crasher)"""
    engine.update_trait('unknown_trait', 0.1, "Test")

    # Ne doit pas crasher ni créer le trait
    assert 'unknown_trait' not in engine.personality


# ========== TESTS CONTEXT MODIFIERS ==========

def test_set_context_modifier(engine):
    """Test application modifieur contextuel"""
    engine.set_context_modifier('humor', 0.2)

    assert 'humor' in engine.context_modifiers
    assert engine.context_modifiers['humor'] == 0.2


def test_set_context_modifier_clipping(engine):
    """Test clipping modifieurs (-0.5 à +0.5)"""
    engine.set_context_modifier('enthusiasm', 10.0)

    # Doit être clippé à 0.5
    assert engine.context_modifiers['enthusiasm'] == 0.5

    engine.set_context_modifier('formality', -10.0)

    # Doit être clippé à -0.5
    assert engine.context_modifiers['formality'] == -0.5


def test_clear_context_modifiers(engine):
    """Test effacement modifieurs"""
    engine.set_context_modifier('humor', 0.1)
    engine.set_context_modifier('kindness', -0.1)

    engine.clear_context_modifiers()

    assert len(engine.context_modifiers) == 0


# ========== TESTS FEEDBACK ANALYSIS ==========

def test_analyze_feedback_positive_humor(engine):
    """Test feedback positif sur humour"""
    initial_humor = engine.personality['humor'].score

    engine.analyze_user_feedback("Haha c'est vraiment drôle ! Merci !")

    new_humor = engine.personality['humor'].score
    assert new_humor > initial_humor


def test_analyze_feedback_negative_enthusiasm(engine):
    """Test demande de réduction enthousiasme"""
    initial_enthusiasm = engine.personality['enthusiasm'].score

    engine.analyze_user_feedback("Calme-toi un peu, tu es trop excité.")

    new_enthusiasm = engine.personality['enthusiasm'].score
    assert new_enthusiasm < initial_enthusiasm


def test_analyze_feedback_general_positive(engine):
    """Test feedback général positif"""
    initial_kindness = engine.personality['kindness'].score

    engine.analyze_user_feedback("Merci beaucoup, c'est parfait !")

    new_kindness = engine.personality['kindness'].score
    assert new_kindness >= initial_kindness  # Au moins égal ou augmenté


def test_analyze_feedback_with_emotion(engine):
    """Test feedback avec émotion utilisateur"""
    initial_empathy = engine.personality['empathy'].score

    engine.analyze_user_feedback("Je suis triste...", user_emotion='sorrow')

    new_empathy = engine.personality['empathy'].score
    assert new_empathy > initial_empathy


# ========== TESTS CONTEXT ADAPTATION ==========

def test_adapt_to_time_morning(engine):
    """Test adaptation heure du matin"""
    engine.adapt_to_context(time_of_day='morning')

    # Enthousiasme doit augmenter le matin
    assert 'enthusiasm' in engine.context_modifiers
    assert engine.context_modifiers['enthusiasm'] > 0


def test_adapt_to_time_night(engine):
    """Test adaptation heure de nuit"""
    engine.adapt_to_context(time_of_day='night')

    # Enthousiasme et formalité doivent baisser la nuit
    assert engine.context_modifiers['enthusiasm'] < 0
    assert engine.context_modifiers['formality'] < 0


def test_adapt_to_long_conversation(engine):
    """Test adaptation conversation longue"""
    engine.adapt_to_context(conversation_length=25)

    # Formalité baisse, empathie augmente
    assert engine.context_modifiers.get('formality', 0) < 0
    assert engine.context_modifiers.get('empathy', 0) > 0


def test_adapt_to_user_preferences(engine):
    """Test adaptation préférences utilisateur"""
    user_prefs = {
        'prefers_formal': True,
        'likes_humor': True
    }

    engine.adapt_to_context(user_preferences=user_prefs)

    # Formalité et humour augmentent
    assert engine.context_modifiers.get('formality', 0) > 0
    assert engine.context_modifiers.get('humor', 0) > 0


def test_adapt_clears_previous_modifiers(engine):
    """Test que adapt_to_context réinitialise modifieurs"""
    engine.set_context_modifier('humor', 0.3)

    engine.adapt_to_context(time_of_day='morning')

    # 'humor' ne devrait plus être dans modifieurs (sauf si ajouté par adapt)
    # Vérifier que les modifieurs sont réinitialisés
    assert engine.context_modifiers != {'humor': 0.3}


# ========== TESTS PROMPT GENERATION ==========

def test_generate_personality_prompt(engine):
    """Test génération fragment prompt"""
    prompt = engine.generate_personality_prompt()

    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_generate_personality_prompt_high_kindness(engine):
    """Test prompt avec kindness élevé"""
    engine.personality['kindness'].score = 0.9

    prompt = engine.generate_personality_prompt()

    assert 'chaleureux' in prompt.lower() or 'bienveillant' in prompt.lower()


def test_generate_personality_prompt_high_humor(engine):
    """Test prompt avec humor élevé"""
    engine.personality['humor'].score = 0.9

    prompt = engine.generate_personality_prompt()

    assert 'humour' in prompt.lower() or 'amusant' in prompt.lower()


def test_generate_personality_prompt_formal(engine):
    """Test prompt avec formalité élevée"""
    engine.personality['formality'].score = 0.9

    prompt = engine.generate_personality_prompt()

    assert 'formel' in prompt.lower()


def test_generate_personality_prompt_casual(engine):
    """Test prompt avec formalité basse"""
    engine.personality['formality'].score = 0.1

    prompt = engine.generate_personality_prompt()

    assert 'décontracté' in prompt.lower() or 'casual' in prompt.lower()


# ========== TESTS SUMMARY ==========

def test_get_personality_summary(engine):
    """Test résumé personnalité"""
    summary = engine.get_personality_summary()

    # Vérifier structure
    assert isinstance(summary, dict)
    assert len(summary) == 6  # 6 traits

    # Vérifier clés pour chaque trait
    for trait_name, trait_info in summary.items():
        assert 'base_score' in trait_info
        assert 'current_score' in trait_info
        assert 'modifier' in trait_info
        assert 'description' in trait_info


def test_get_personality_summary_includes_modifiers(engine):
    """Test résumé inclut modifieurs"""
    engine.set_context_modifier('humor', 0.15)

    summary = engine.get_personality_summary()

    assert summary['humor']['modifier'] == 0.15
    assert summary['humor']['current_score'] != summary['humor']['base_score']


# ========== TESTS EVOLUTION HISTORY ==========

def test_get_evolution_history(engine):
    """Test récupération historique"""
    engine.update_trait('creativity', 0.1, "Test 1")
    engine.update_trait('creativity', 0.05, "Test 2")

    history = engine.get_evolution_history('creativity', limit=10)

    assert isinstance(history, list)
    assert len(history) >= 2  # Au moins 2 événements


def test_get_evolution_history_limit(engine):
    """Test limite historique"""
    # Créer beaucoup d'événements
    for i in range(20):
        engine.update_trait('humor', 0.01, f"Test {i}")

    history = engine.get_evolution_history('humor', limit=5)

    assert len(history) <= 5


def test_get_evolution_history_unknown_trait(engine):
    """Test historique trait inexistant"""
    history = engine.get_evolution_history('unknown_trait')

    assert history == []


# ========== TESTS PERSISTENCE ==========

def test_persistence_across_instances(temp_storage):
    """Test persistence entre instances"""
    # Instance 1 : modifier traits
    engine1 = PersonalityEngine(storage_file=temp_storage)
    engine1.update_trait('enthusiasm', 0.15, "Test persistence")
    initial_score = engine1.personality['enthusiasm'].score

    # Instance 2 : charger
    engine2 = PersonalityEngine(storage_file=temp_storage)

    # Vérifier même score
    assert engine2.personality['enthusiasm'].score == pytest.approx(initial_score, abs=0.01)


def test_persistence_preserves_history(temp_storage):
    """Test que historique est persisté"""
    # Instance 1
    engine1 = PersonalityEngine(storage_file=temp_storage)
    engine1.update_trait('creativity', 0.1, "Important change")

    # Instance 2
    engine2 = PersonalityEngine(storage_file=temp_storage)

    history = engine2.get_evolution_history('creativity')

    # Vérifier événement présent
    assert any('Important change' in entry.get('reason', '') for entry in history)


# ========== TESTS RESET ==========

def test_reset_to_defaults(engine):
    """Test reset à valeurs par défaut"""
    # Modifier traits
    engine.update_trait('humor', 0.3, "Test")
    engine.set_context_modifier('kindness', 0.2)

    # Reset
    engine.reset_to_defaults()

    # Vérifier reset (proche des valeurs par défaut)
    assert 0.5 <= engine.personality['humor'].score <= 0.7
    assert len(engine.context_modifiers) == 0


# ========== TESTS REPR ==========

def test_repr(engine):
    """Test représentation string"""
    repr_str = repr(engine)

    assert 'PersonalityEngine' in repr_str
    assert 'kindness' in repr_str
    assert 'humor' in repr_str


# ========== TESTS EDGE CASES ==========

def test_empty_feedback(engine):
    """Test feedback vide"""
    initial_scores = {
        name: trait.score
        for name, trait in engine.personality.items()
    }

    engine.analyze_user_feedback("")

    # Scores ne doivent pas changer significativement
    for name, trait in engine.personality.items():
        assert abs(trait.score - initial_scores[name]) < 0.1


def test_unicode_in_feedback(engine):
    """Test feedback avec unicode"""
    engine.analyze_user_feedback("Émojis 😊🎉 super drôle !")

    # Ne doit pas crasher
    assert True


def test_very_long_prompt_generation(engine):
    """Test génération prompt ne devient pas trop long"""
    # Forcer tous les traits à valeurs extrêmes
    for trait in engine.personality.values():
        trait.score = 0.9

    prompt = engine.generate_personality_prompt()

    # Prompt ne doit pas être excessivement long
    assert len(prompt) < 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
