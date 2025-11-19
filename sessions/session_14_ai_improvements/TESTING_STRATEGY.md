# 🧪 Stratégie Tests Unitaires - Session 14

**Date** : 16 novembre 2025
**Version** : 0.18.0-alpha (cible)

---

## 🎯 Objectifs Tests

### Couverture

- **Cible** : >80% coverage pour nouveaux modules
- **Critiques** : MemoryManager, PersonalityEngine, ChatEngine (100%)
- **Secondaires** : ConversationSummarizer, FactExtractor, ContextAnalyzer (80%+)

### Qualité

- ✅ Tests unitaires isolés (mocks pour dépendances)
- ✅ Tests intégration (modules ensemble)
- ✅ Tests performance (temps réponse, mémoire)
- ✅ Tests edge cases (erreurs, données corrompues, etc.)

---

## 📁 Structure Tests

```
tests/ai/
├── conftest.py (fixtures partagées)
│
├── test_memory_manager.py (NOUVEAU ~300 lignes)
├── test_conversation_summarizer.py (NOUVEAU ~150 lignes)
├── test_fact_extractor.py (NOUVEAU ~200 lignes)
├── test_personality_engine.py (NOUVEAU ~250 lignes)
├── test_emotion_analyzer.py (MODIFIER existant ~200→350 lignes)
├── test_emotion_memory.py (NOUVEAU ~150 lignes)
├── test_context_analyzer.py (NOUVEAU ~200 lignes)
│
├── test_integration_chatengine.py (NOUVEAU ~400 lignes)
└── test_performance.py (NOUVEAU ~150 lignes)
```

**Total nouvelles lignes tests** : ~1500 lignes

---

## 🔧 Fixtures Pytest (conftest.py)

**Fichier** : `tests/ai/conftest.py`

```python
import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock
from tempfile import TemporaryDirectory

from src.ai.memory_manager import MemoryManager
from src.ai.personality_engine import PersonalityEngine
from src.ai.emotion_memory import EmotionMemory
from src.ai.context_analyzer import ContextAnalyzer
from src.ai.conversation_summarizer import ConversationSummarizer
from src.ai.fact_extractor import FactExtractor
from src.ai.model_manager import ModelManager
from src.ai.chat_engine import ChatEngine


# ============ FIXTURES STOCKAGE TEMPORAIRE ============

@pytest.fixture
def temp_storage(tmp_path):
    """Dossier temporaire pour tests (auto-nettoyé)."""
    storage_path = tmp_path / "test_data"
    storage_path.mkdir()
    return str(storage_path)


@pytest.fixture
def temp_memory_storage(temp_storage):
    """Dossier temporaire pour memory/ (conversations, facts, embeddings)."""
    memory_path = Path(temp_storage) / "memory"
    memory_path.mkdir()
    return str(memory_path)


# ============ FIXTURES DONNÉES TEST ============

@pytest.fixture
def sample_conversation():
    """Conversation type pour tests."""
    return [
        {"role": "user", "content": "Bonjour, je m'appelle Alice"},
        {"role": "assistant", "content": "Bonjour Alice ! Enchantée de te rencontrer !"},
        {"role": "user", "content": "J'aime beaucoup la musique jazz"},
        {"role": "assistant", "content": "Le jazz c'est magnifique ! Tu as des artistes préférés ?"},
        {"role": "user", "content": "Oui, j'adore Miles Davis et John Coltrane"},
        {"role": "assistant", "content": "Excellent choix ! Ce sont des légendes du jazz."},
    ]


@pytest.fixture
def sample_user_message():
    """Message utilisateur type."""
    return "Comment créer un rappel ?"


@pytest.fixture
def sample_assistant_response():
    """Réponse assistant type."""
    return "Pour créer un rappel, tu peux me dire 'rappelle-moi de [tâche] dans [temps]'. Par exemple : 'rappelle-moi de prendre mes médicaments dans 2 heures'."


# ============ FIXTURES MOCKS ============

@pytest.fixture
def model_manager_mock():
    """Mock ModelManager (évite charger LLM en tests)."""
    mock = Mock(spec=ModelManager)

    # Comportement par défaut generate()
    mock.generate.return_value = "Réponse test générée par mock LLM"

    # Simuler modèle chargé
    mock.is_loaded.return_value = True
    mock.model = Mock()

    return mock


@pytest.fixture
def embeddings_model_mock():
    """Mock SentenceTransformer (évite télécharger modèle)."""
    import numpy as np

    mock = Mock()

    # Retourner vecteurs aléatoires (dimension 384 comme all-MiniLM-L6-v2)
    def encode_mock(texts, **kwargs):
        if isinstance(texts, str):
            texts = [texts]
        return np.random.rand(len(texts), 384).astype(np.float32)

    mock.encode.side_effect = encode_mock

    return mock


# ============ FIXTURES MODULES IA ============

@pytest.fixture
def memory_manager(temp_memory_storage, embeddings_model_mock, monkeypatch):
    """MemoryManager avec stockage temporaire et mock embeddings."""
    # Remplacer SentenceTransformer par mock
    monkeypatch.setattr(
        "src.ai.memory_manager.SentenceTransformer",
        lambda model_name: embeddings_model_mock
    )

    return MemoryManager(storage_path=temp_memory_storage)


@pytest.fixture
def personality_engine(temp_storage):
    """PersonalityEngine avec stockage temporaire."""
    storage_file = Path(temp_storage) / "personality.json"
    return PersonalityEngine(storage_path=str(storage_file))


@pytest.fixture
def emotion_memory(temp_storage):
    """EmotionMemory avec stockage temporaire."""
    storage_file = Path(temp_storage) / "emotion_history.json"
    return EmotionMemory(storage_path=str(storage_file))


@pytest.fixture
def context_analyzer():
    """ContextAnalyzer (pas de stockage nécessaire)."""
    return ContextAnalyzer()


@pytest.fixture
def conversation_summarizer(model_manager_mock):
    """ConversationSummarizer avec mock ModelManager."""
    return ConversationSummarizer(model_manager=model_manager_mock)


@pytest.fixture
def fact_extractor():
    """FactExtractor (pas de dépendances)."""
    return FactExtractor()


@pytest.fixture
def chat_engine_advanced(model_manager_mock, temp_storage, monkeypatch):
    """ChatEngine avec modules avancés activés et stockage temporaire."""
    # Rediriger chemins stockage vers temp
    monkeypatch.setattr(
        "src.ai.memory_manager.MemoryManager.__init__",
        lambda self, storage_path=None: MemoryManager.__init__(self, storage_path=temp_storage + "/memory/")
    )

    return ChatEngine(model_manager_mock, enable_advanced_ai=True)


@pytest.fixture
def chat_engine_legacy(model_manager_mock):
    """ChatEngine en mode legacy (sans modules avancés)."""
    return ChatEngine(model_manager_mock, enable_advanced_ai=False)


# ============ FIXTURES UTILITAIRES ============

@pytest.fixture
def assert_json_file_valid():
    """Helper vérifier validité fichier JSON."""
    def _assert(file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # Lève exception si JSON invalide
        assert isinstance(data, dict)
        assert "version" in data
        return data
    return _assert


@pytest.fixture
def create_test_conversation_file():
    """Helper créer fichier conversations.json de test."""
    def _create(storage_path: str, num_conversations: int = 2):
        conversations_file = Path(storage_path) / "conversations.json"
        conversations_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat() + "Z",
            "conversations": [
                {
                    "id": f"conv_20251116_00{i}",
                    "start_timestamp": "2025-11-16T10:00:00Z",
                    "end_timestamp": "2025-11-16T10:30:00Z",
                    "message_count": 10,
                    "summary": f"Test conversation {i} summary",
                    "key_points": ["point1", "point2"],
                    "topics": ["test", "conversation"],
                    "overall_sentiment": "positive",
                    "sentiment_score": 0.7,
                    "dominant_emotion": "joyeux",
                    "message_ids": list(range(1, 11))
                }
                for i in range(1, num_conversations + 1)
            ],
            "total_conversations": num_conversations,
            "total_messages": num_conversations * 10
        }

        with open(conversations_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(conversations_file)

    return _create
```

---

## 🧪 Tests Par Module

### 1️⃣ test_memory_manager.py

```python
import pytest
from src.ai.memory_manager import MemoryManager


class TestMemoryManagerInitialization:
    """Tests initialisation MemoryManager."""

    def test_creates_storage_directory(self, temp_memory_storage):
        """Vérifie création dossier stockage."""
        mm = MemoryManager(storage_path=temp_memory_storage)
        assert Path(temp_memory_storage).exists()

    def test_initializes_empty_memory(self, memory_manager):
        """Vérifie initialisation mémoire vide."""
        assert len(memory_manager.conversations) == 0
        assert len(memory_manager.facts) == 0

    def test_loads_existing_conversations(self, temp_memory_storage, create_test_conversation_file):
        """Vérifie chargement conversations existantes."""
        create_test_conversation_file(temp_memory_storage, num_conversations=3)

        mm = MemoryManager(storage_path=temp_memory_storage)
        assert len(mm.conversations) == 3


class TestStoreMessage:
    """Tests stockage messages."""

    def test_stores_user_message(self, memory_manager):
        """Stocke message utilisateur."""
        memory_manager.store_message(
            message="Bonjour",
            role="user",
            metadata={"intent": "salutation"}
        )

        assert memory_manager.message_count > 0

    def test_stores_assistant_message(self, memory_manager):
        """Stocke réponse assistant."""
        memory_manager.store_message(
            message="Bonjour ! Comment puis-je t'aider ?",
            role="assistant",
            metadata={"emotion": "joyeux", "intensity": 0.7}
        )

        assert memory_manager.message_count > 0

    def test_metadata_attached_to_message(self, memory_manager):
        """Vérifie metadata attachée au message."""
        memory_manager.store_message(
            message="Test",
            role="user",
            metadata={"test_key": "test_value"}
        )

        recent_messages = memory_manager.get_recent_messages(k=1)
        assert recent_messages[0]["metadata"]["test_key"] == "test_value"


class TestRelevantContext:
    """Tests recherche contexte pertinent."""

    def test_returns_relevant_context(self, memory_manager, sample_conversation):
        """Recherche retourne contexte pertinent."""
        # Stocker conversation
        for msg in sample_conversation:
            memory_manager.store_message(msg["content"], msg["role"], {})

        # Rechercher contexte pertinent
        results = memory_manager.get_relevant_context("Qui est Alice ?", k=3)

        assert len(results) <= 3
        assert any("Alice" in result for result in results)

    def test_empty_query_returns_empty(self, memory_manager):
        """Query vide retourne vide."""
        results = memory_manager.get_relevant_context("", k=5)
        assert len(results) == 0


class TestSummarization:
    """Tests résumés conversations."""

    def test_summarize_after_threshold(self, memory_manager, sample_conversation):
        """Génère résumé après seuil messages."""
        # Stocker 25 messages (seuil = 20)
        for _ in range(5):
            for msg in sample_conversation:
                memory_manager.store_message(msg["content"], msg["role"], {})

        summary = memory_manager.summarize_if_needed(force=False)
        assert summary is not None
        assert len(summary) > 10  # Résumé non vide

    def test_force_summarize(self, memory_manager, sample_conversation):
        """Force résumé même si seuil non atteint."""
        for msg in sample_conversation:
            memory_manager.store_message(msg["content"], msg["role"], {})

        summary = memory_manager.summarize_if_needed(force=True)
        assert summary is not None


# ... (30+ tests additionnels)
```

---

### 2️⃣ test_personality_engine.py

```python
class TestPersonalityTraits:
    """Tests traits personnalité."""

    def test_default_traits_in_range(self, personality_engine):
        """Vérifie traits par défaut entre 0.0-1.0."""
        traits = personality_engine.traits

        for trait_name, value in traits.items():
            assert 0.0 <= value <= 1.0, f"{trait_name} hors plage: {value}"

    def test_all_required_traits_present(self, personality_engine):
        """Vérifie tous traits requis présents."""
        required_traits = [
            "extraversion", "empathie", "humour",
            "formalité", "curiosité", "enthousiasme", "patience"
        ]

        for trait in required_traits:
            assert trait in personality_engine.traits


class TestSystemPromptGeneration:
    """Tests génération prompts système adaptatifs."""

    def test_generates_prompt_for_extraverted(self, personality_engine):
        """Prompt adapté pour personnalité extravertie."""
        personality_engine.traits["extraversion"] = 0.9
        personality_engine.traits["empathie"] = 0.8

        prompt = personality_engine.generate_system_prompt()

        assert "bavarde" in prompt.lower() or "extraverti" in prompt.lower()
        assert "empathique" in prompt.lower()

    def test_generates_prompt_for_reserved(self, personality_engine):
        """Prompt adapté pour personnalité réservée."""
        personality_engine.traits["extraversion"] = 0.2
        personality_engine.traits["formalité"] = 0.8

        prompt = personality_engine.generate_system_prompt()

        assert "concis" in prompt.lower() or "réservé" in prompt.lower()
        assert "formel" in prompt.lower()


class TestTraitUpdate:
    """Tests mise à jour traits."""

    def test_updates_trait_gradually(self, personality_engine):
        """Mise à jour trait progressive (max ±0.05)."""
        initial_extraversion = personality_engine.traits["extraversion"]

        # Simuler feedback positif extraversion
        personality_engine.update_traits({
            "user_message": "J'adore discuter avec toi !",
            "intent": "feedback",
            "sentiment": "positive"
        })

        new_extraversion = personality_engine.traits["extraversion"]

        # Changement devrait être limité
        assert abs(new_extraversion - initial_extraversion) <= 0.05

    def test_trait_never_exceeds_bounds(self, personality_engine):
        """Traits ne dépassent jamais 0.0-1.0."""
        # Forcer trait à limite
        personality_engine.traits["humour"] = 0.99

        # Tenter augmenter encore
        for _ in range(10):
            personality_engine.update_traits({
                "user_message": "Tu es drôle !",
                "intent": "feedback",
                "sentiment": "positive"
            })

        assert personality_engine.traits["humour"] <= 1.0


# ... (20+ tests additionnels)
```

---

### 3️⃣ test_emotion_analyzer.py (améliorer existant)

```python
class TestAdvancedEmotionAnalysis:
    """Tests analyse émotions avancée."""

    def test_analyze_with_context_previous_emotion(self, emotion_analyzer):
        """Analyse prend en compte émotion précédente."""
        # Émotion précédente : joyeux (0.8)
        emotion, intensity = emotion_analyzer.analyze_with_context(
            text="Bon, ça suffit maintenant.",
            previous_emotion="joyeux",
            previous_intensity=0.8
        )

        # Transition douce : pas de saut brusque vers "énervé"
        assert emotion in ["neutre", "pensif", "énervé"]
        if emotion == "énervé":
            assert intensity < 0.6  # Atténué par blend

    def test_blend_emotions(self, emotion_analyzer):
        """Mélange émotions pour transition douce."""
        emotion, intensity = emotion_analyzer.blend_emotions(
            emotion1="joyeux",
            intensity1=0.8,
            emotion2="neutre",
            intensity2=0.5,
            blend_factor=0.3
        )

        # Intensité blendée : 0.8 * 0.7 + 0.5 * 0.3 = 0.71
        assert 0.65 <= intensity <= 0.75


# ... (15+ tests additionnels)
```

---

### 4️⃣ test_integration_chatengine.py (CRUCIAL)

```python
class TestChatEngineIntegration:
    """Tests intégration ChatEngine avec modules IA."""

    def test_full_pipeline_with_advanced_ai(self, chat_engine_advanced, model_manager_mock):
        """Pipeline complet : message → réponse avec tous modules."""
        model_manager_mock.generate.return_value = "Bonjour ! Je suis ravie de t'aider !"

        result = chat_engine_advanced.generate_response("Bonjour, je m'appelle Alice")

        # Vérifier structure résultat
        assert "response" in result
        assert "emotion" in result
        assert "intent" in result
        assert "sentiment" in result
        assert result["advanced_ai_enabled"] is True

        # Vérifier modules appelés
        assert result["intent"] is not None
        assert result["sentiment"] is not None

    def test_memory_stores_conversation(self, chat_engine_advanced, model_manager_mock):
        """Vérifie stockage conversation dans mémoire."""
        model_manager_mock.generate.return_value = "Test réponse"

        # Générer plusieurs messages
        for i in range(5):
            chat_engine_advanced.generate_response(f"Message {i}")

        # Vérifier stockage
        assert chat_engine_advanced.memory_manager.message_count == 10  # 5 user + 5 assistant

    def test_personality_evolves_over_time(self, chat_engine_advanced, model_manager_mock):
        """Personnalité évolue après interactions."""
        initial_traits = chat_engine_advanced.personality_engine.traits.copy()

        # Simuler 100 interactions positives
        for i in range(100):
            chat_engine_advanced.generate_response("Tu es géniale !")

        new_traits = chat_engine_advanced.personality_engine.traits

        # Au moins un trait devrait avoir changé
        assert any(abs(new_traits[k] - initial_traits[k]) > 0.01 for k in initial_traits)


# ... (25+ tests additionnels)
```

---

## ⚡ Tests Performance

**Fichier** : `tests/ai/test_performance.py`

```python
import pytest
import time


class TestResponseTime:
    """Tests temps réponse (<3s objectif)."""

    def test_response_time_under_3s(self, chat_engine_advanced, model_manager_mock):
        """Temps réponse total <3s."""
        # Mock génération LLM rapide (simuler CUDA)
        model_manager_mock.generate.return_value = "Réponse test"

        start = time.time()
        result = chat_engine_advanced.generate_response("Test message")
        elapsed = time.time() - start

        assert elapsed < 3.0, f"Temps réponse: {elapsed:.2f}s (objectif <3s)"

    def test_memory_search_under_100ms(self, memory_manager, sample_conversation):
        """Recherche mémoire <100ms."""
        # Stocker conversation
        for msg in sample_conversation:
            memory_manager.store_message(msg["content"], msg["role"], {})

        start = time.time()
        results = memory_manager.get_relevant_context("Alice musique", k=5)
        elapsed = (time.time() - start) * 1000  # ms

        assert elapsed < 100, f"Recherche: {elapsed:.2f}ms (objectif <100ms)"


class TestMemoryUsage:
    """Tests consommation mémoire RAM."""

    def test_memory_manager_size_reasonable(self, memory_manager, sample_conversation):
        """Taille mémoire raisonnable après 1000 messages."""
        import sys

        # Stocker 1000 messages (simuler)
        for _ in range(100):
            for msg in sample_conversation:
                memory_manager.store_message(msg["content"], msg["role"], {})

        # Estimer taille objet
        size_bytes = sys.getsizeof(memory_manager)
        size_mb = size_bytes / (1024 ** 2)

        assert size_mb < 50, f"Taille MemoryManager: {size_mb:.2f} MB (objectif <50 MB)"
```

---

## 📊 Coverage Reports

### Commandes

```powershell
# Activer venv
.\venv\Scripts\Activate.ps1

# Lancer tests avec coverage
pytest tests/ai/ --cov=src/ai --cov-report=html --cov-report=term

# Ouvrir rapport HTML
start htmlcov/index.html
```

### Objectifs Coverage

| Module | Cible | Priorité |
|--------|-------|----------|
| `memory_manager.py` | 100% | HAUTE |
| `personality_engine.py` | 100% | HAUTE |
| `chat_engine.py` | 95%+ | HAUTE |
| `emotion_analyzer.py` | 90%+ | MOYENNE |
| `context_analyzer.py` | 85%+ | MOYENNE |
| `conversation_summarizer.py` | 80%+ | MOYENNE |
| `fact_extractor.py` | 80%+ | MOYENNE |
| `emotion_memory.py` | 85%+ | MOYENNE |

---

## 🚨 Tests Edge Cases

### Données Corrompues

```python
def test_handles_corrupted_json(self, temp_memory_storage):
    """Gère fichier JSON corrompu."""
    # Créer fichier JSON invalide
    conversations_file = Path(temp_memory_storage) / "conversations.json"
    with open(conversations_file, "w") as f:
        f.write("{invalid json content")

    # MemoryManager devrait gérer erreur
    mm = MemoryManager(storage_path=temp_memory_storage)
    assert mm.conversations == []  # Mémoire réinitialisée
```

### Limites Système

```python
def test_handles_extremely_long_message(self, memory_manager):
    """Gère message très long (>10000 caractères)."""
    long_message = "A" * 15000

    memory_manager.store_message(long_message, "user", {})

    # Devrait tronquer ou gérer sans crash
    assert memory_manager.message_count > 0
```

---

## ✅ Checklist Tests Avant Merge

Avant de merger code Phase X :

- ✅ Tous tests passent (`pytest tests/ai/ -v`)
- ✅ Coverage >80% nouveaux modules
- ✅ Temps réponse <3s (test_performance.py)
- ✅ Pas de memory leaks (tests longs)
- ✅ Tests intégration ChatEngine passent
- ✅ Tests manuels UI (app.py)
- ✅ Tests manuels Discord bot

---

**Créé le** : 16 novembre 2025
**Dernière mise à jour** : 16 novembre 2025
