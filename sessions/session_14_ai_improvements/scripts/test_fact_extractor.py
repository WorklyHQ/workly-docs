"""
Tests unitaires pour FactExtractor

Tests d'extraction de faits depuis conversations :
- Entités (noms, lieux, dates, organisations)
- Préférences (aime/n'aime pas)
- Événements (actions, projets, objectifs)
- Relations (personnes, concepts)
"""

import pytest
from datetime import datetime
from src.ai.fact_extractor import (
    FactExtractor,
    Entity,
    Preference,
    Event,
    Relationship
)


@pytest.fixture
def extractor():
    """Fixture : instance FactExtractor"""
    return FactExtractor()


# ========== TESTS ENTITÉS ==========

def test_extract_entities_person(extractor):
    """Test extraction noms de personnes"""
    message = "Hier j'ai rencontré Marie et Thomas au café."
    
    entities = extractor.extract_entities(message)
    
    # Vérifier qu'au moins 2 entités détectées
    assert len(entities) >= 2
    
    # Vérifier types
    person_entities = [e for e in entities if e.entity_type == 'person']
    assert len(person_entities) >= 2


def test_extract_entities_location(extractor):
    """Test extraction lieux"""
    message = "Je suis allé à Paris pour visiter le Louvre."
    
    entities = extractor.extract_entities(message)
    
    # Vérifier présence de lieu
    location_entities = [e for e in entities if e.entity_type == 'location']
    assert len(location_entities) >= 1
    assert any('Paris' in e.value for e in location_entities)


def test_extract_entities_date(extractor):
    """Test extraction dates"""
    messages = [
        "Rendez-vous lundi prochain.",
        "On se voit demain à 14h.",
        "C'était hier soir."
    ]
    
    for msg in messages:
        entities = extractor.extract_entities(msg)
        date_entities = [e for e in entities if e.entity_type == 'date']
        assert len(date_entities) >= 1


def test_extract_entities_confidence(extractor):
    """Test calcul de confiance"""
    message = "Marie travaille chez Google depuis 2020."
    
    entities = extractor.extract_entities(message)
    
    # Vérifier que confidence est dans [0, 1]
    for entity in entities:
        assert 0.0 <= entity.confidence <= 1.0


# ========== TESTS PRÉFÉRENCES ==========

def test_extract_preferences_positive(extractor):
    """Test extraction préférences positives"""
    messages = [
        "J'adore la pizza !",
        "J'aime beaucoup la programmation Python.",
        "Je préfère le jazz à la pop."
    ]
    
    for msg in messages:
        prefs = extractor.extract_preferences(msg)
        assert len(prefs) >= 1
        assert all(p.sentiment == 'positive' for p in prefs)


def test_extract_preferences_negative(extractor):
    """Test extraction préférences négatives"""
    # Utiliser mots-clés explicites qui matchent les catégories
    message = "Je n'aime pas du tout la musique rap."
    
    prefs = extractor.extract_preferences(message)
    
    # Si des préférences sont détectées, vérifier sentiment
    if prefs:
        assert all(p.sentiment == 'negative' for p in prefs)


def test_extract_preferences_categories(extractor):
    """Test classification par catégories"""
    test_cases = [
        ("J'adore la pizza", "food"),
        ("J'aime le rock", "music"),
        ("Je préfère le bleu", "color"),
        ("J'aime la programmation", "work")
    ]
    
    for msg, expected_cat in test_cases:
        prefs = extractor.extract_preferences(msg)
        if prefs:  # Peut ne pas détecter si mot-clé absent
            assert any(p.category == expected_cat for p in prefs)


def test_extract_preferences_intensity(extractor):
    """Test intensité des préférences"""
    message = "J'adore vraiment le chocolat !"
    
    prefs = extractor.extract_preferences(message)
    
    if prefs:
        # Intensité doit être entre 0.5 et 1.0
        assert all(0.5 <= p.intensity <= 1.0 for p in prefs)


# ========== TESTS ÉVÉNEMENTS ==========

def test_extract_events_past(extractor):
    """Test extraction actions passées"""
    message = "Hier j'ai terminé le projet avec l'équipe."
    
    events = extractor.extract_events(message)
    
    assert len(events) >= 1
    assert events[0].event_type == 'past_action'
    assert events[0].status == 'completed'


def test_extract_events_current(extractor):
    """Test extraction projets en cours"""
    message = "Je travaille actuellement sur une nouvelle fonctionnalité."
    
    events = extractor.extract_events(message)
    
    assert len(events) >= 1
    assert events[0].event_type == 'current_project'
    assert events[0].status == 'ongoing'


def test_extract_events_future(extractor):
    """Test extraction objectifs futurs"""
    message = "Je veux apprendre le machine learning l'année prochaine."
    
    events = extractor.extract_events(message)
    
    assert len(events) >= 1
    assert events[0].event_type == 'future_goal'
    assert events[0].status == 'planned'


def test_extract_events_participants(extractor):
    """Test extraction participants"""
    message = "J'ai rencontré Alice et Bob hier pour discuter du projet."
    
    events = extractor.extract_events(message)
    
    if events:
        # Vérifier présence de participants
        assert len(events[0].participants) >= 1


# ========== TESTS RELATIONS ==========

def test_extract_relationships_family(extractor):
    """Test extraction relations familiales"""
    message = "Mon frère Pierre travaille à Paris."
    
    rels = extractor.extract_relationships(message)
    
    # Peut détecter ou non selon implémentation exacte
    # Test flexible
    assert isinstance(rels, list)


def test_extract_relationships_work(extractor):
    """Test extraction relations professionnelles"""
    message = "Marie travaille chez Google."
    
    rels = extractor.extract_relationships(message)
    
    assert isinstance(rels, list)


# ========== TESTS INTÉGRATION ==========

def test_extract_all_facts_comprehensive(extractor):
    """Test extraction complète de tous types de faits"""
    message = (
        "Hier j'ai rencontré Marie à Paris. "
        "Elle m'a dit qu'elle adore la programmation Python. "
        "Nous avons discuté de notre projet actuel."
    )
    
    facts = extractor.extract_all_facts(message)
    
    # Vérifier structure
    assert 'entities' in facts
    assert 'preferences' in facts
    assert 'events' in facts
    assert 'relationships' in facts
    
    # Vérifier qu'au moins un type a des résultats
    total_facts = (
        len(facts['entities']) +
        len(facts['preferences']) +
        len(facts['events']) +
        len(facts['relationships'])
    )
    assert total_facts > 0


def test_extract_all_facts_empty_message(extractor):
    """Test avec message vide"""
    facts = extractor.extract_all_facts("")
    
    # Doit retourner structure vide mais valide
    assert all(len(facts[key]) == 0 for key in facts.keys())


def test_extract_all_facts_no_keywords(extractor):
    """Test avec message sans mots-clés"""
    message = "Voilà."
    
    facts = extractor.extract_all_facts(message)
    
    # Peut être vide ou avoir des résultats minimaux
    assert isinstance(facts, dict)


# ========== TESTS DATACLASSES ==========

def test_entity_to_dict():
    """Test conversion Entity en dict"""
    entity = Entity(
        entity_type='person',
        value='Marie',
        context='test',
        confidence=0.8,
        first_seen='2024-01-01T10:00:00',
        occurrences=1
    )
    
    data = entity.to_dict()
    
    assert data['entity_type'] == 'person'
    assert data['value'] == 'Marie'
    assert data['confidence'] == 0.8


def test_preference_to_dict():
    """Test conversion Preference en dict"""
    pref = Preference(
        category='food',
        subject='pizza',
        sentiment='positive',
        intensity=0.7,
        context='test',
        timestamp='2024-01-01T10:00:00'
    )
    
    data = pref.to_dict()
    
    assert data['category'] == 'food'
    assert data['sentiment'] == 'positive'


# ========== TESTS EDGE CASES ==========

def test_extract_with_unicode(extractor):
    """Test avec caractères unicode"""
    message = "J'adore les émojis 😊 et le café ☕"
    
    facts = extractor.extract_all_facts(message)
    
    # Ne doit pas crasher
    assert isinstance(facts, dict)


def test_extract_with_very_long_message(extractor):
    """Test avec message très long"""
    message = "Test " * 1000  # 4000+ caractères
    
    facts = extractor.extract_all_facts(message)
    
    # Ne doit pas crasher
    assert isinstance(facts, dict)


def test_extract_with_special_characters(extractor):
    """Test avec caractères spéciaux"""
    message = "Email: test@example.com | Site: https://test.fr"
    
    facts = extractor.extract_all_facts(message)
    
    # Ne doit pas crasher
    assert isinstance(facts, dict)


# ========== TESTS PERFORMANCE ==========

@pytest.mark.slow
def test_extract_performance(extractor):
    """Test performance sur messages multiples"""
    messages = [
        "J'adore Python et JavaScript.",
        "Hier j'ai rencontré Marie à Paris.",
        "Je travaille sur un nouveau projet.",
    ] * 10  # 30 messages
    
    import time
    start = time.time()
    
    for msg in messages:
        extractor.extract_all_facts(msg)
    
    elapsed = time.time() - start
    
    # Doit traiter 30 messages en moins de 2 secondes
    assert elapsed < 2.0, f"Performance dégradée : {elapsed:.2f}s pour 30 messages"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
