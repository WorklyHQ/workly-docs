# 🏗️ Architecture Modules IA - Session 14

**Date** : 16 novembre 2025
**Version** : 0.18.0-alpha (cible)

---

## 📊 Vue d'Ensemble

Cette architecture décrit comment les 6 nouveaux modules IA s'intègrent avec le système existant.

### Diagramme Général

```
┌─────────────────────────────────────────────────────────────────┐
│                      Application Qt (app.py)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ChatEngine (Orchestrateur)                    │
│  - Gère conversation principale                                 │
│  - Coordonne tous les modules IA                                │
│  - Génère réponses utilisateur                                  │
└─┬───────────┬───────────┬───────────┬───────────┬──────────────┘
  │           │           │           │           │
  ▼           ▼           ▼           ▼           ▼
┌───────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
│Memory │ │Persona │ │Emotion   │ │Context │ │Model     │
│Manager│ │lity    │ │Analyzer  │ │Analyzer│ │Manager   │
│       │ │Engine  │ │          │ │        │ │          │
└───┬───┘ └───┬────┘ └────┬─────┘ └───┬────┘ └──────────┘
    │         │           │            │
    ▼         ▼           ▼            ▼
┌───────┐ ┌──────┐  ┌──────────┐  (Pas de sous-module)
│Conv.  │ │Traits│  │Emotion   │
│Summ.  │ │Dict  │  │Memory    │
└───┬───┘ └──────┘  └──────────┘
    │
    ▼
┌───────┐
│Fact   │
│Extract│
└───────┘
```

---

## 🧩 Modules Détaillés

### 1️⃣ MemoryManager (Nouveau)

**Fichier** : `src/ai/memory_manager.py`
**Lignes estimées** : ~400

**Responsabilités** :
- Stockage/récupération mémoire long-terme
- Recherche sémantique dans historique
- Coordination résumés et extraction faits
- Gestion persistance fichiers JSON

**Classe Principale** :

```python
class MemoryManager:
    """Gestionnaire mémoire long-terme de l'assistant."""

    def __init__(self, storage_path: str = "data/memory/"):
        self.storage_path = storage_path
        self.summarizer = ConversationSummarizer()
        self.fact_extractor = FactExtractor()
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.conversations: List[ConversationSummary] = []
        self.facts: Dict[str, Any] = {}
        self._load_memory()

    # Méthodes publiques
    def store_message(self, message: str, role: str, metadata: dict) -> None
    def get_relevant_context(self, query: str, k: int = 5) -> List[str]
    def summarize_if_needed(self, force: bool = False) -> Optional[str]
    def extract_facts(self, messages: List[dict]) -> Dict[str, Any]
    def search_by_topic(self, topic: str, k: int = 3) -> List[str]

    # Méthodes privées
    def _load_memory(self) -> None
    def _save_conversations(self) -> None
    def _save_facts(self) -> None
    def _save_embeddings(self) -> None
    def _compute_embedding(self, text: str) -> np.ndarray
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float
```

**Dépendances** :
- `ConversationSummarizer` (résumés)
- `FactExtractor` (extraction faits)
- `sentence-transformers` (embeddings)
- `numpy` (cosine similarity)

**Stockage** :
- `data/memory/conversations.json` : Résumés conversations
- `data/memory/facts.json` : Faits extraits
- `data/memory/embeddings.json` : Vecteurs embeddings

---

### 2️⃣ ConversationSummarizer (Nouveau)

**Fichier** : `src/ai/conversation_summarizer.py`
**Lignes estimées** : ~200

**Responsabilités** :
- Générer résumés conversations via LLM
- Détecter points clés importants
- Compression intelligente contexte

**Classe Principale** :

```python
class ConversationSummarizer:
    """Génère résumés de conversations."""

    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.summary_prompt_template = """Résume la conversation suivante en 2-3 phrases.
Garde les informations importantes (nom, préférences, sujets principaux).

Conversation:
{conversation}

Résumé:"""

    # Méthodes publiques
    def summarize(self, messages: List[dict], max_tokens: int = 150) -> str
    def detect_key_points(self, messages: List[dict]) -> List[str]
    def should_summarize(self, message_count: int, threshold: int = 20) -> bool

    # Méthodes privées
    def _format_conversation(self, messages: List[dict]) -> str
    def _extract_key_sentences(self, text: str, top_k: int = 3) -> List[str]
```

**Dépendances** :
- `ModelManager` (accès Zephyr-7B)
- Prompts spécialisés résumé

**Logique Résumé** :
1. Trigger : Après 20-30 messages
2. Format : 2-3 phrases concises
3. Stocke : Résumé + timestamp + IDs messages originaux

---

### 3️⃣ FactExtractor (Nouveau)

**Fichier** : `src/ai/fact_extractor.py`
**Lignes estimées** : ~250

**Responsabilités** :
- Extraire entités (nom, lieux, dates)
- Détecter préférences utilisateur
- Identifier événements marquants
- Extraire relations entre entités

**Classe Principale** :

```python
class FactExtractor:
    """Extrait faits importants des conversations."""

    def __init__(self):
        # Patterns regex pour extraction basique
        self.name_patterns = [
            r"je m'appelle (\w+)",
            r"mon nom est (\w+)",
            r"appelle[-\s]moi (\w+)",
        ]
        self.preference_keywords = [
            "j'aime", "je préfère", "je déteste", "je n'aime pas",
            "mon favori", "ma passion", "j'adore"
        ]

    # Méthodes publiques
    def extract_entities(self, text: str) -> Dict[str, List[str]]
    def extract_preferences(self, text: str) -> List[Preference]
    def extract_events(self, text: str) -> List[Event]
    def extract_relationships(self, entities: List[str]) -> List[Relationship]
    def extract_all_facts(self, messages: List[dict]) -> Dict[str, Any]

    # Méthodes privées
    def _extract_name(self, text: str) -> Optional[str]
    def _extract_dates(self, text: str) -> List[str]
    def _extract_locations(self, text: str) -> List[str]
    def _detect_preference_context(self, text: str) -> Optional[dict]
```

**Types Faits Extraits** :

```python
@dataclass
class Preference:
    category: str  # ex: "musique", "nourriture", "activité"
    item: str      # ex: "jazz", "pizza", "course"
    sentiment: str # "positive" ou "negative"
    confidence: float

@dataclass
class Event:
    description: str
    timestamp: Optional[datetime]
    importance: float  # 0.0-1.0

@dataclass
class Relationship:
    entity_1: str
    relation_type: str
    entity_2: str
```

**Méthodes Extraction** :
1. **Regex** : Patterns simples (nom, dates)
2. **Keywords** : Préférences explicites
3. **LLM** : Faits complexes (optionnel si temps calcul OK)

---

### 4️⃣ PersonalityEngine (Nouveau)

**Fichier** : `src/ai/personality_engine.py`
**Lignes estimées** : ~350

**Responsabilités** :
- Gérer traits personnalité (5-7 traits)
- Générer prompts système adaptatifs
- Faire évoluer personnalité selon interactions
- Garantir cohérence long-terme

**Classe Principale** :

```python
class PersonalityEngine:
    """Moteur personnalité évolutive."""

    def __init__(self, storage_path: str = "data/personality.json"):
        self.storage_path = storage_path
        self.traits: Dict[str, float] = {
            "extraversion": 0.6,   # 0.0=introverti, 1.0=extraverti
            "empathie": 0.8,       # 0.0=rationnel, 1.0=empathique
            "humour": 0.5,         # 0.0=sérieux, 1.0=blagueur
            "formalité": 0.3,      # 0.0=casual, 1.0=formel
            "curiosité": 0.7,      # 0.0=passif, 1.0=curieux
            "enthousiasme": 0.6,   # 0.0=calme, 1.0=énergique
            "patience": 0.7,       # 0.0=impatient, 1.0=patient
        }
        self.history: List[TraitUpdate] = []
        self._load_personality()

    # Méthodes publiques
    def generate_system_prompt(self) -> str
    def update_traits(self, interaction_data: dict) -> Dict[str, float]
    def get_response_style(self) -> dict
    def should_ask_followup(self) -> bool
    def get_trait_description(self) -> str

    # Méthodes privées
    def _load_personality(self) -> None
    def _save_personality(self) -> None
    def _compute_trait_change(self, feedback: str, trait: str) -> float
    def _ensure_coherence(self) -> None
    def _generate_trait_modifiers(self) -> dict
```

**Génération Prompts Exemples** :

```python
# Extraversion=0.8, Empathie=0.9, Humour=0.6
"Tu es Kira, une assistante virtuelle très bavarde et profondément empathique.
Tu adores engager la conversation, poser des questions, et montrer une grande
sensibilité aux émotions. Tu utilises occasionnellement l'humour pour détendre."

# Extraversion=0.3, Empathie=0.5, Formalité=0.8
"Tu es Kira, une assistante virtuelle concise et professionnelle.
Tu privilégies les réponses courtes et factuelles, avec un ton formel.
Tu restes neutre émotionnellement et vas droit au but."
```

**Évolution Traits** :
- Feedback positif → Renforce trait utilisé
- Feedback négatif → Atténue trait
- Changement graduel (max ±0.05 par interaction)
- Vérification cohérence (pas de contradictions extrêmes)

---

### 5️⃣ EmotionAnalyzer (Amélioration Existant)

**Fichier** : `src/ai/emotion_analyzer.py`
**Lignes actuelles** : ~300 → **Cible : ~500**

**Responsabilités** :
- Analyser émotions avec contexte (pas seulement keywords)
- Gérer transitions émotionnelles douces
- Intégrer mémoire émotionnelle
- Détecter émotions composées

**Classe Modifiée** :

```python
class EmotionAnalyzer:
    """Analyseur émotions avancé avec contexte."""

    def __init__(self):
        # Émotions existantes
        self.emotions = ["neutre", "joyeux", "triste", "surpris",
                        "énervé", "pensif", "timide"]
        # Nouvelles émotions composées
        self.compound_emotions = {
            "excité": ("joyeux", "surpris", 0.6, 0.4),
            "frustré": ("énervé", "triste", 0.7, 0.3),
            "mélancolique": ("triste", "pensif", 0.5, 0.5),
            "confiant": ("neutre", "joyeux", 0.6, 0.4),
            "anxieux": ("timide", "énervé", 0.6, 0.4),
        }
        self.emotion_memory = EmotionMemory()
        self.keywords = {...}  # Existant

    # Méthodes publiques (nouvelles/modifiées)
    def analyze_emotion(self, text: str, context: List[str] = None) -> Tuple[str, float]
    def analyze_with_context(self, text: str, previous_emotion: str,
                            previous_intensity: float) -> Tuple[str, float]
    def detect_emotion_llm(self, text: str) -> Tuple[str, float]
    def blend_emotions(self, emotion1: str, intensity1: float,
                      emotion2: str, intensity2: float,
                      blend_factor: float = 0.3) -> Tuple[str, float]
    def should_transition(self, new_emotion: str, new_intensity: float) -> bool

    # Méthodes existantes (garder)
    def _analyze_keywords(self, text: str) -> Tuple[str, float]
    def _get_emotion_from_intensity(self, scores: dict) -> Tuple[str, float]
```

**Améliorations** :
1. **Analyse contextuelle** : Prend en compte messages précédents
2. **LLM-based** (optionnel) : Détection émotions complexes via Zephyr
3. **Transitions douces** : Blend entre émotion actuelle et nouvelle
4. **Mémoire émotionnelle** : Se souvient états précédents

**Formule Transition** :

```python
# Éviter changements brusques
if abs(new_intensity - previous_intensity) > 0.4:
    # Transition douce sur 2-3 réponses
    blended_intensity = previous_intensity * 0.7 + new_intensity * 0.3
```

---

### 6️⃣ EmotionMemory (Nouveau)

**Fichier** : `src/ai/emotion_memory.py`
**Lignes estimées** : ~200

**Responsabilités** :
- Stocker historique émotions (100 dernières)
- Analyser tendances émotionnelles
- Valider transitions réalistes
- Détecter patterns émotionnels

**Classe Principale** :

```python
class EmotionMemory:
    """Mémoire émotionnelle pour transitions réalistes."""

    def __init__(self, storage_path: str = "data/emotion_history.json"):
        self.storage_path = storage_path
        self.history: Deque[EmotionEntry] = deque(maxlen=100)
        self._load_history()

    # Méthodes publiques
    def add_emotion(self, emotion: str, intensity: float, context: str) -> None
    def get_recent_emotions(self, window: int = 10) -> List[EmotionEntry]
    def get_dominant_emotion(self, window: int = 10) -> Tuple[str, float]
    def get_emotional_trend(self) -> str  # "stable", "ascending", "descending"
    def should_allow_transition(self, current: str, new: str) -> bool
    def get_transition_probability(self, from_emotion: str,
                                   to_emotion: str) -> float

    # Méthodes privées
    def _load_history(self) -> None
    def _save_history(self) -> None
    def _compute_trend(self, intensities: List[float]) -> str
    def _get_transition_matrix(self) -> Dict[str, Dict[str, float]]
```

**EmotionEntry** :

```python
@dataclass
class EmotionEntry:
    emotion: str
    intensity: float
    timestamp: datetime
    context: str  # Court résumé pourquoi cette émotion
```

**Matrice Transitions** (exemple) :

```python
# Probabilités transitions émotionnelles réalistes
{
    "joyeux": {"joyeux": 0.6, "neutre": 0.2, "surpris": 0.15, "triste": 0.05},
    "triste": {"triste": 0.5, "neutre": 0.3, "joyeux": 0.1, "énervé": 0.1},
    "énervé": {"énervé": 0.4, "neutre": 0.3, "triste": 0.2, "joyeux": 0.1},
    # ... etc pour toutes émotions
}
```

---

### 7️⃣ ContextAnalyzer (Nouveau)

**Fichier** : `src/ai/context_analyzer.py`
**Lignes estimées** : ~300

**Responsabilités** :
- Détecter intentions utilisateur
- Analyser sentiment global message
- Suggérer actions proactives
- Identifier sujets de conversation

**Classe Principale** :

```python
class ContextAnalyzer:
    """Analyseur contextuel avancé."""

    def __init__(self):
        self.intents = [
            "question",
            "demande_action",
            "conversation_casual",
            "plainte",
            "remerciement",
            "salutation",
            "au_revoir",
            "feedback",
        ]
        self.intent_keywords = {...}  # Patterns par intent

    # Méthodes publiques
    def detect_intent(self, message: str) -> Tuple[str, float]
    def analyze_sentiment(self, message: str) -> Tuple[str, float]  # positif/négatif/neutre
    def extract_topic(self, message: str) -> Optional[str]
    def should_ask_followup(self, conversation_history: List[dict]) -> bool
    def generate_proactive_suggestion(self, context: dict) -> Optional[str]
    def detect_question_type(self, message: str) -> str  # "comment", "pourquoi", "quoi", etc.

    # Méthodes privées
    def _match_intent_keywords(self, message: str) -> Dict[str, float]
    def _analyze_sentence_structure(self, message: str) -> dict
    def _compute_sentiment_score(self, message: str) -> float
    def _extract_action_verbs(self, message: str) -> List[str]
```

**Exemples Détections** :

```python
# Input: "Comment créer un rappel ?"
→ Intent: "question" (0.95)
→ Topic: "features_app"
→ Question type: "comment"
→ Suggestion: Afficher exemple commande rappel

# Input: "J'en ai marre de ce projet"
→ Intent: "plainte" (0.90)
→ Sentiment: négatif (-0.7)
→ Topic: "projet"
→ Suggestion: Proposer pause ou aide

# Input: "Merci pour ton aide !"
→ Intent: "remerciement" (1.0)
→ Sentiment: positif (0.9)
→ Suggestion: Offrir aide future
```

---

## 🔄 Intégration avec ChatEngine

**Fichier** : `src/ai/chat_engine.py` (à modifier)

### Modifications Principales

```python
class ChatEngine:
    def __init__(self, model_manager):
        self.model_manager = model_manager

        # Modules existants
        self.emotion_analyzer = EmotionAnalyzer()
        self.conversation_history = []

        # NOUVEAUX modules
        self.memory_manager = MemoryManager()
        self.personality_engine = PersonalityEngine()
        self.context_analyzer = ContextAnalyzer()

        # État actuel
        self.current_emotion = "neutre"
        self.current_intensity = 0.5

    def generate_response(self, user_message: str) -> dict:
        """Génère réponse avec tous modules IA activés."""

        # 1. Analyse contextuelle
        intent, intent_conf = self.context_analyzer.detect_intent(user_message)
        sentiment, sent_conf = self.context_analyzer.analyze_sentiment(user_message)

        # 2. Récupération contexte mémoire long-terme
        relevant_context = self.memory_manager.get_relevant_context(user_message, k=3)

        # 3. Génération prompt système adaptatif (personnalité)
        system_prompt = self.personality_engine.generate_system_prompt()

        # 4. Construction prompt avec contexte
        full_context = self._build_context(
            user_message,
            relevant_context,
            self.conversation_history[-10:],  # Court-terme
        )

        # 5. Génération réponse LLM
        response = self.model_manager.generate(
            prompt=full_context,
            system_prompt=system_prompt,
        )

        # 6. Analyse émotion réponse (avec contexte précédent)
        emotion, intensity = self.emotion_analyzer.analyze_with_context(
            response,
            self.current_emotion,
            self.current_intensity,
        )

        # 7. Stockage mémoire
        self.memory_manager.store_message(
            user_message,
            role="user",
            metadata={"intent": intent, "sentiment": sentiment}
        )
        self.memory_manager.store_message(
            response,
            role="assistant",
            metadata={"emotion": emotion, "intensity": intensity}
        )

        # 8. Résumé si nécessaire
        summary = self.memory_manager.summarize_if_needed()

        # 9. Mise à jour personnalité
        self.personality_engine.update_traits({
            "user_message": user_message,
            "intent": intent,
            "sentiment": sentiment,
        })

        # 10. Mise à jour état émotionnel
        self.current_emotion = emotion
        self.current_intensity = intensity

        return {
            "response": response,
            "emotion": emotion,
            "intensity": intensity,
            "intent": intent,
            "summary_generated": summary is not None,
        }
```

---

## 📊 Flux de Données

### Scénario : Utilisateur envoie message

```
1. USER → "Comment vas-tu ?"
         │
         ▼
2. ContextAnalyzer.detect_intent()
   → intent = "question", confidence = 0.95
   → sentiment = "neutre", confidence = 0.8
         │
         ▼
3. MemoryManager.get_relevant_context("Comment vas-tu ?", k=3)
   → Recherche sémantique dans conversations passées
   → Retourne : ["User a demandé comment je vais hier", ...]
         │
         ▼
4. PersonalityEngine.generate_system_prompt()
   → Génère prompt selon traits actuels (extraversion=0.7, empathie=0.8)
   → "Tu es Kira, bavarde et empathique..."
         │
         ▼
5. ChatEngine._build_context()
   → Combine : system_prompt + contexte long-terme + historique court-terme
         │
         ▼
6. ModelManager.generate()
   → Zephyr-7B génère : "Je vais très bien merci ! Et toi ?"
         │
         ▼
7. EmotionAnalyzer.analyze_with_context()
   → Détecte : emotion="joyeux", intensity=0.7
   → Vérifie transition OK (précédent: neutre → joyeux = OK)
         │
         ▼
8. MemoryManager.store_message() × 2
   → Stocke message user + metadata (intent, sentiment)
   → Stocke réponse assistant + metadata (emotion, intensity)
         │
         ▼
9. MemoryManager.summarize_if_needed()
   → Compte messages : 25 → Trigger résumé
   → ConversationSummarizer.summarize() via LLM
   → Stocke résumé dans data/memory/conversations.json
         │
         ▼
10. PersonalityEngine.update_traits()
    → Analyse interaction : intent=question, sentiment=neutre
    → Ajuste légèrement : curiosité +0.02, empathie +0.01
         │
         ▼
11. RETURN → {"response": "...", "emotion": "joyeux", ...}
    → Envoyé à Unity pour affichage blendshape
    → Affiché dans GUI Qt
```

---

## 🧪 Tests Unitaires

### Structure Tests

```
tests/ai/
├── test_memory_manager.py
├── test_conversation_summarizer.py
├── test_fact_extractor.py
├── test_personality_engine.py
├── test_emotion_analyzer.py (existant, à étendre)
├── test_emotion_memory.py
├── test_context_analyzer.py
└── test_integration_chatengine.py (nouveau)
```

### Fixtures Pytest

```python
# tests/ai/conftest.py
import pytest
from src.ai.memory_manager import MemoryManager
from src.ai.personality_engine import PersonalityEngine

@pytest.fixture
def temp_storage(tmp_path):
    """Dossier temporaire pour tests."""
    return str(tmp_path)

@pytest.fixture
def memory_manager(temp_storage):
    """MemoryManager avec stockage temporaire."""
    return MemoryManager(storage_path=temp_storage)

@pytest.fixture
def personality_engine(temp_storage):
    """PersonalityEngine avec stockage temporaire."""
    storage = f"{temp_storage}/personality.json"
    return PersonalityEngine(storage_path=storage)

@pytest.fixture
def sample_conversation():
    """Conversation type pour tests."""
    return [
        {"role": "user", "content": "Bonjour, je m'appelle Alice"},
        {"role": "assistant", "content": "Bonjour Alice ! Enchantée !"},
        {"role": "user", "content": "J'aime beaucoup la musique jazz"},
        {"role": "assistant", "content": "Le jazz c'est magnifique !"},
    ]
```

---

## ⚠️ Considérations Performance

### VRAM (GPU)

**Budget strict** : RTX 4050 6GB VRAM

```
Zephyr-7B (profil performance) : 5.0-5.5 GB
Embeddings all-MiniLM-L6-v2    : ~80 MB (RAM, pas VRAM)
Marge disponible               : ~500 MB
```

**Pas de risque saturation VRAM** : Les embeddings sentence-transformers tournent sur CPU par défaut.

### RAM

**Budget** : 16 GB total (Windows + Unity + Python)

```
Windows 11                  : ~4 GB
Unity (avatar VRM)          : ~1.5 GB
Python app + PySide6        : ~500 MB
Zephyr-7B (hors VRAM)       : ~500 MB
Embeddings model            : ~150 MB
Memory data (conversations) : ~50-100 MB
Marge                       : ~9 GB disponibles
```

**OK** : Largement suffisant.

### Temps Réponse

**Objectif** : <3s par réponse (avec tous modules)

**Décomposition estimée** :

```
ContextAnalyzer.detect_intent()       : ~10 ms
MemoryManager.get_relevant_context()  : ~50 ms (recherche embeddings)
PersonalityEngine.generate_prompt()   : ~5 ms
ModelManager.generate() (Zephyr)      : ~2000 ms (CUDA)
EmotionAnalyzer.analyze_with_context(): ~20 ms
MemoryManager.store_message()         : ~10 ms
PersonalityEngine.update_traits()     : ~5 ms
────────────────────────────────────────────────
TOTAL                                 : ~2100 ms = 2.1s
```

**✅ Objectif atteint** : <3s

**Optimisations possibles** :
- Recherche embeddings async (parallèle génération LLM)
- Cache résultats ContextAnalyzer si message similaire
- Batch updates PersonalityEngine (tous les 5-10 messages)

---

## 🔒 Gestion Erreurs

### Stratégies Robustesse

**MemoryManager** :
- Fichier JSON corrompu → Backup + recréer
- Embeddings manquants → Recalculer à la demande
- Disk full → Purge anciennes conversations (>6 mois)

**ConversationSummarizer** :
- LLM timeout → Utiliser résumé basique (premiers/derniers messages)
- Résumé incohérent → Retry avec prompt modifié

**PersonalityEngine** :
- Traits incohérents → Reset valeurs par défaut
- Évolution trop rapide → Limiter changements (max ±0.05/interaction)

**EmotionAnalyzer** :
- Émotion inconnue → Fallback "neutre"
- Transition invalide → Forcer blend progressif

**ContextAnalyzer** :
- Intent incertain → Utiliser "conversation_casual" par défaut
- Sentiment ambigu → "neutre" avec confidence faible

---

## 📝 Prochaines Étapes

✅ Architecture documentée
🚧 Structures JSON à définir → **DATA_SCHEMAS.md**
🚧 Guide intégration ChatEngine → **INTEGRATION_GUIDE.md**
🚧 Stratégie tests détaillée → **TESTING_STRATEGY.md**
🚧 Plan phases développement → **DEVELOPMENT_PHASES.md**

---

**Créé le** : 16 novembre 2025
**Dernière mise à jour** : 16 novembre 2025
