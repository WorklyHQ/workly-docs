# 🚀 Guide Développement Phases - Session 14

**Date** : 16 novembre 2025
**Version** : 0.18.0-alpha (cible)
**Durée estimée totale** : 30-39 heures

---

## 📋 Vue d'Ensemble Phases

```
Phase Planning → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
   (2h)         (8-10h)    (6-8h)     (6-8h)     (5-7h)    (2-3h)    (1-2h)
```

**Total** : 30-40 heures développement + tests + documentation

---

## 📚 Phase Planning (ACTUELLE - ✅ TERMINÉE)

**Durée** : ~2 heures
**Statut** : ✅ **COMPLÉTÉE**

### Objectifs

- ✅ Créer structure documentation session_14
- ✅ Documenter architecture globale (ARCHITECTURE.md)
- ✅ Définir structures JSON (DATA_SCHEMAS.md)
- ✅ Créer schémas JSON validation (schemas/)
- ✅ Plan intégration ChatEngine (INTEGRATION_GUIDE.md)
- ✅ Stratégie tests (TESTING_STRATEGY.md)
- ✅ Ce guide phases (DEVELOPMENT_PHASES.md)

### Livrables

- ✅ `docs/sessions/session_14_ai_improvements/README.md`
- ✅ `docs/sessions/session_14_ai_improvements/ARCHITECTURE.md`
- ✅ `docs/sessions/session_14_ai_improvements/DATA_SCHEMAS.md`
- ✅ `docs/sessions/session_14_ai_improvements/INTEGRATION_GUIDE.md`
- ✅ `docs/sessions/session_14_ai_improvements/TESTING_STRATEGY.md`
- ✅ `docs/sessions/session_14_ai_improvements/DEVELOPMENT_PHASES.md`
- ✅ `docs/sessions/session_14_ai_improvements/schemas/*.json` (4 fichiers)

### Prochaine Étape

→ **Phase 1 : Mémoire Long-Terme**

---

## 🧠 Phase 1 : Mémoire Long-Terme

**Durée estimée** : 8-10 heures
**Priorité** : 🔴 HAUTE
**Modules** : MemoryManager, ConversationSummarizer, FactExtractor

### Objectifs

- ✅ Créer système mémoire persistante
- ✅ Résumés conversations automatiques
- ✅ Extraction faits importants (nom, préférences, événements)
- ✅ Recherche sémantique dans historique

### 📝 Étapes Détaillées

#### Étape 1.1 : Installer Dépendances (15 min)

**Commandes** :

```powershell
cd c:\Dev\workly_project\workly-desktop
.\venv\Scripts\Activate.ps1

# Installer sentence-transformers (embeddings)
pip install sentence-transformers

# Vérifier installation
python -c "from sentence_transformers import SentenceTransformer; print('✅ OK')"
```

**Packages installés** :
- `sentence-transformers` (~300 MB avec dépendances)
- `torch` (déjà installé via llama-cpp-python)
- `numpy` (déjà installé)

#### Étape 1.2 : Créer FactExtractor (2h)

**Fichier** : `src/ai/fact_extractor.py`

**Ordre implémentation** :

1. **Classe squelette** (15 min)
```python
class FactExtractor:
    def __init__(self):
        self.name_patterns = [...]
        self.preference_keywords = [...]

    def extract_all_facts(self, messages: List[dict]) -> Dict[str, Any]:
        pass
```

2. **Extraction nom** (30 min)
```python
def _extract_name(self, text: str) -> Optional[str]:
    # Patterns regex : "je m'appelle X", "mon nom est X", etc.
    pass

def extract_entities(self, text: str) -> Dict[str, List[str]]:
    # Nom, lieux, dates
    pass
```

3. **Extraction préférences** (45 min)
```python
@dataclass
class Preference:
    category: str
    item: str
    sentiment: str  # "positive" ou "negative"
    confidence: float

def extract_preferences(self, text: str) -> List[Preference]:
    # Patterns : "j'aime X", "je préfère X", "j'adore X", etc.
    pass
```

4. **Extraction événements** (30 min)
```python
@dataclass
class Event:
    description: str
    timestamp: Optional[datetime]
    importance: float

def extract_events(self, text: str) -> List[Event]:
    # Événements marquants
    pass
```

5. **Tests unitaires** (15 min)
```python
# tests/ai/test_fact_extractor.py
def test_extracts_name():
    extractor = FactExtractor()
    name = extractor._extract_name("Bonjour, je m'appelle Alice")
    assert name == "Alice"
```

#### Étape 1.3 : Créer ConversationSummarizer (2h)

**Fichier** : `src/ai/conversation_summarizer.py`

**Ordre implémentation** :

1. **Classe squelette** (15 min)
```python
class ConversationSummarizer:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.summary_prompt_template = "..."

    def summarize(self, messages: List[dict], max_tokens: int = 150) -> str:
        pass
```

2. **Formatage conversation** (30 min)
```python
def _format_conversation(self, messages: List[dict]) -> str:
    # Formater messages pour prompt LLM
    formatted = []
    for msg in messages:
        role = "Utilisateur" if msg["role"] == "user" else "Assistant"
        formatted.append(f"{role}: {msg['content']}")
    return "\n".join(formatted)
```

3. **Génération résumé via LLM** (45 min)
```python
def summarize(self, messages: List[dict], max_tokens: int = 150) -> str:
    conv_text = self._format_conversation(messages)

    prompt = self.summary_prompt_template.format(conversation=conv_text)

    summary = self.model_manager.generate(
        prompt=prompt,
        system_prompt="Tu es un assistant qui résume des conversations.",
        max_tokens=max_tokens,
    )

    return summary.strip()
```

4. **Détection points clés** (30 min)
```python
def detect_key_points(self, messages: List[dict]) -> List[str]:
    # Extraire phrases importantes
    pass
```

5. **Tests unitaires** (30 min)

#### Étape 1.4 : Créer MemoryManager (3-4h)

**Fichier** : `src/ai/memory_manager.py`

**Ordre implémentation** :

1. **Classe squelette + init** (30 min)
```python
from sentence_transformers import SentenceTransformer
import numpy as np

class MemoryManager:
    def __init__(self, storage_path: str = "data/memory/"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.summarizer = ConversationSummarizer(...)
        self.fact_extractor = FactExtractor()

        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.conversations = []
        self.facts = {}
        self.embeddings = []

        self._load_memory()
```

2. **Chargement/sauvegarde JSON** (1h)
```python
def _load_memory(self):
    # Charger conversations.json, facts.json, embeddings.json
    pass

def _save_conversations(self):
    # Sauvegarder conversations.json
    pass

def _save_facts(self):
    # Sauvegarder facts.json
    pass

def _save_embeddings(self):
    # Sauvegarder embeddings.json
    pass
```

3. **Stockage messages** (45 min)
```python
def store_message(self, message: str, role: str, metadata: dict):
    # Ajouter message à buffer interne
    # Stocker metadata (intent, sentiment, emotion, etc.)
    pass
```

4. **Résumé automatique** (45 min)
```python
def summarize_if_needed(self, force: bool = False) -> Optional[str]:
    # Vérifier si seuil atteint (20-30 messages)
    # Générer résumé via ConversationSummarizer
    # Extraire faits via FactExtractor
    # Sauvegarder résumé + faits
    # Calculer embeddings résumé
    pass
```

5. **Recherche sémantique** (1h)
```python
def _compute_embedding(self, text: str) -> np.ndarray:
    return self.embeddings_model.encode(text)

def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_relevant_context(self, query: str, k: int = 5) -> List[str]:
    # 1. Encoder query
    query_emb = self._compute_embedding(query)

    # 2. Calculer similarités avec tous embeddings
    similarities = []
    for emb_entry in self.embeddings:
        sim = self._cosine_similarity(query_emb, emb_entry["embedding"])
        similarities.append((emb_entry["id"], sim))

    # 3. Trier et retourner top-k
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_ids = [id for id, sim in similarities[:k]]

    # 4. Récupérer textes correspondants
    results = []
    for id in top_ids:
        # Trouver conversation/fact correspondant
        for conv in self.conversations:
            if conv["id"] == id:
                results.append(conv["summary"])
                break

    return results
```

6. **Tests unitaires** (1h)

#### Étape 1.5 : Intégration ChatEngine (1-2h)

**Fichier** : `src/ai/chat_engine.py`

**Modifications** :

1. Ajouter imports (5 min)
2. Modifier `__init__()` (15 min)
3. Ajouter `self.memory_manager = MemoryManager()` (5 min)
4. Modifier `generate_response()` phases 2, 7, 8 (45 min)
5. Tests intégration (30 min)

#### Étape 1.6 : Tests Intégration Complets (1h)

```python
# tests/ai/test_integration_memory.py
def test_memory_stores_and_retrieves():
    # Test complet : stocker 30 messages, résumé auto, recherche
    pass
```

### ✅ Checklist Phase 1

**Avant de passer Phase 2** :

- ✅ `src/ai/fact_extractor.py` créé et testé
- ✅ `src/ai/conversation_summarizer.py` créé et testé
- ✅ `src/ai/memory_manager.py` créé et testé
- ✅ `tests/ai/test_fact_extractor.py` (>80% coverage)
- ✅ `tests/ai/test_conversation_summarizer.py` (>80% coverage)
- ✅ `tests/ai/test_memory_manager.py` (100% coverage)
- ✅ `tests/ai/test_integration_memory.py` passant
- ✅ ChatEngine intégré (phases 2, 7, 8)
- ✅ `data/memory/` créé avec fichiers JSON valides
- ✅ Copie scripts dans `docs/session_14/scripts/`
- ✅ Documentation session mise à jour
- ✅ pytest passe (tous tests)
- ✅ Temps réponse <3s vérifié

### 📊 Métriques Succès Phase 1

- ✅ Résumé généré après 20-30 messages
- ✅ Au moins 5 faits extraits par conversation longue
- ✅ Recherche sémantique retourne résultats pertinents (top-3 accuracy >70%)
- ✅ Temps recherche <100ms
- ✅ Fichiers JSON valides et lisibles

---

## 🎭 Phase 2 : Personnalité Évolutive

**Durée réelle** : ~7 heures
**Statut** : ✅ **TERMINÉE** (17 novembre 2025)
**Priorité** : 🔴 HAUTE
**Modules** : PersonalityEngine

### Objectifs

- ✅ 7 traits personnalité quantifiables
- ✅ Génération prompts système adaptatifs
- ✅ Évolution traits selon interactions
- ✅ Cohérence personnalité long-terme

### 📝 Étapes Détaillées

#### Étape 2.1 : Créer PersonalityEngine (4-5h)

**Fichier** : `src/ai/personality_engine.py`

**Ordre implémentation** :

1. **Classe squelette + traits par défaut** (30 min)
```python
class PersonalityEngine:
    def __init__(self, storage_path: str = "data/personality.json"):
        self.storage_path = Path(storage_path)
        self.traits = {
            "extraversion": 0.6,
            "empathie": 0.8,
            "humour": 0.5,
            "formalité": 0.3,
            "curiosité": 0.7,
            "enthousiasme": 0.6,
            "patience": 0.7,
        }
        self.history = []
        self._load_personality()
```

2. **Chargement/sauvegarde** (45 min)

3. **Génération prompts adaptatifs** (2h)
```python
def generate_system_prompt(self) -> str:
    base = "Tu es Kira, une assistante virtuelle"

    # Adapter selon traits
    if self.traits["extraversion"] > 0.7:
        base += " très bavarde et engageante"
    # ... etc pour tous traits

    return base
```

4. **Mise à jour traits** (1-1.5h)
```python
def update_traits(self, interaction_data: dict) -> Dict[str, float]:
    # Analyser interaction
    # Ajuster traits (max ±0.05)
    # Vérifier cohérence
    # Sauvegarder historique
    pass
```

5. **Tests unitaires** (1h)

#### Étape 2.2 : Intégration ChatEngine (1h)

**Modifications** :

1. Ajouter `self.personality_engine = PersonalityEngine()` (5 min)
2. Modifier phase 3 `generate_response()` (30 min)
3. Modifier phase 9 `generate_response()` (30 min)
4. Tests intégration (30 min)

#### Étape 2.3 : Tests Évolution Personnalité (1h)

```python
def test_personality_evolves_after_100_interactions():
    # Simuler 100 interactions
    # Vérifier au moins 1 trait a changé >0.05
    pass
```

### ✅ Checklist Phase 2 (✅ COMPLÉTÉE)

- ✅ `src/ai/personality_engine.py` créé (~490 lignes) et testé
- ✅ `tests/ai/test_personality_engine.py` créé (43 tests, 100% passants)
- ✅ 6 traits personnalité : kindness, humor, formality, enthusiasm, empathy, creativity
- ✅ Génération prompts adaptatifs via `generate_personality_prompt()`
- ✅ Adaptation contextuelle : time_of_day, conversation_length, user_preferences
- ✅ Analyse feedback utilisateur via `analyze_user_feedback()`
- ✅ Modifieurs contextuels temporaires (-0.5 à +0.5)
- ✅ Historique d'évolution par trait (max 100 entrées)
- ✅ ChatEngine intégré (phases 3, 9) : inject personality prompt + analyze feedback
- ✅ `data/memory/personality.json` créé et persisté
- ✅ Bug fix : initialisation ordre appels save (self.personality avant _save_personality)
- ✅ pytest passe (43/43 tests)
- ✅ Scripts copiés : `docs/sessions/session_14_ai_improvements/scripts/personality_engine.py`
- ✅ Scripts copiés : `docs/sessions/session_14_ai_improvements/scripts/test_personality_engine.py`

### 🎉 Résultats Phase 2

**Fonctionnalités implémentées** :
- Système de traits personnalité évolutif et persistant
- 6 traits avec scores 0.0-1.0 : kindness (0.8), humor (0.6), formality (0.3), enthusiasm (0.7), empathy (0.8), creativity (0.6)
- Prompts système dynamiques générés selon personnalité actuelle
- Adaptation contextuelle automatique (heure, longueur conversation, préférences utilisateur)
- Analyse feedback utilisateur → ajustement traits permanents
- Modifieurs temporaires pour adaptation contextuelle immédiate
- Historique complet évolution traits avec timestamps et raisons
- Persistance JSON complète avec métadonnées

**Tests** :
- 43 tests unitaires couvrant tous les aspects
- 100% tests passants après bug fix initialisation
- Coverage : initialisation, get/update traits, modifieurs contextuels, feedback analysis, adaptation, prompt generation, persistence, edge cases

**Intégration ChatEngine** :
- Phase 3 : injection personality prompt dans system prompt
- Phase 9 : analyse feedback après détection émotion utilisateur
- Adaptation automatique avant génération réponse (time_of_day, conversation_length)

**Performance** :
- Temps initialisation : <50ms
- Temps génération prompt : <10ms
- Taille fichier personality.json : ~5-10 KB
- Overhead mémoire : <5 MB

---

## 🎨 Phase 3 : Émotions Avancées

**Durée estimée** : 6-8 heures
**Priorité** : 🟠 MOYENNE
**Modules** : EmotionAnalyzer (amélioration), EmotionMemory

### Objectifs

- ✅ Analyse contextuelle (au-delà keywords)
- ✅ Transitions émotionnelles douces
- ✅ Mémoire émotionnelle
- ✅ Émotions composées (excité, frustré, etc.)

### 📝 Étapes Détaillées

#### Étape 3.1 : Créer EmotionMemory (2-3h)

**Fichier** : `src/ai/emotion_memory.py`

#### Étape 3.2 : Améliorer EmotionAnalyzer (3-4h)

**Fichier** : `src/ai/emotion_analyzer.py`

**Modifications** :

1. Ajouter méthodes :
   - `analyze_with_context()`
   - `blend_emotions()`
   - `should_transition()`

2. Intégrer `EmotionMemory`

3. Ajouter émotions composées

#### Étape 3.3 : Intégration ChatEngine (1h)

**Modification phase 6 `generate_response()`**

### ✅ Checklist Phase 3

- ✅ `src/ai/emotion_memory.py` créé
- ✅ `src/ai/emotion_analyzer.py` amélioré
- ✅ Tests unitaires (>85% coverage)
- ✅ ChatEngine intégré (phase 6)
- ✅ `data/emotion_history.json` créé
- ✅ Transitions douces vérifiées
- ✅ pytest passe

---

## 🔍 Phase 4 : Analyse Contextuelle

**Durée estimée** : 5-7 heures
**Priorité** : 🟠 MOYENNE
**Modules** : ContextAnalyzer

### Objectifs

- ✅ Détection intentions (8+ types)
- ✅ Analyse sentiment global
- ✅ Suggestions proactives
- ✅ Extraction sujet conversation

### 📝 Étapes Détaillées

#### Étape 4.1 : Créer ContextAnalyzer (4-5h)

**Fichier** : `src/ai/context_analyzer.py`

**Ordre implémentation** :

1. Classe squelette (30 min)
2. Détection intentions (2h)
3. Analyse sentiment (1h)
4. Extraction sujets (1h)
5. Tests unitaires (1h)

#### Étape 4.2 : Intégration ChatEngine (1h)

**Modification phase 1 `generate_response()`**

### ✅ Checklist Phase 4

- ✅ `src/ai/context_analyzer.py` créé
- ✅ Tests (>85% coverage)
- ✅ ChatEngine intégré (phase 1)
- ✅ Détection intentions >85% précision
- ✅ pytest passe

---

## 🧪 Phase 5 : Tests & Optimisations

**Durée estimée** : 2-3 heures
**Priorité** : 🟡 MOYENNE

### Objectifs

- ✅ Tests intégration complets
- ✅ Benchmarks performance
- ✅ Optimisations si nécessaire
- ✅ Corrections bugs

### 📝 Étapes

1. **Tests intégration ChatEngine complet** (1h)
2. **Benchmarks performance** (30 min)
   - Temps réponse <3s
   - VRAM <6 GB
   - RAM <500 MB additionnelle
3. **Optimisations** (si nécessaire, 1h)
4. **Corrections bugs** (30 min)

---

## 📚 Phase 6 : Documentation Finale

**Durée estimée** : 1-2 heures
**Priorité** : 🟡 BASSE

### Objectifs

- ✅ Documentation utilisateur features IA
- ✅ CHANGELOG mis à jour
- ✅ README.md racine mis à jour (4 sections)
- ✅ INDEX.md mis à jour
- ✅ Scripts copiés dans docs/session_14/scripts/

### 📝 Étapes

1. Créer `docs/session_14/USER_GUIDE.md` (30 min)
2. Mettre à jour `CHANGELOG.md` (15 min)
3. Mettre à jour `README.md` racine (30 min)
4. Mettre à jour `INDEX.md` (15 min)
5. Copier scripts finaux (15 min)

---

## 📊 Tableau Récapitulatif

| Phase | Durée | Priorité | Modules | Tests | Intégration ChatEngine |
|-------|-------|----------|---------|-------|------------------------|
| Planning | 2h | ✅ Fait | Docs | N/A | N/A |
| Phase 1 | 8-10h | 🔴 HAUTE | MemoryManager, ConversationSummarizer, FactExtractor | >80% | Phases 2, 7, 8 |
| Phase 2 | 6-8h | 🔴 HAUTE | PersonalityEngine | 100% | Phases 3, 9 |
| Phase 3 | 6-8h | 🟠 MOYENNE | EmotionAnalyzer, EmotionMemory | >85% | Phase 6 |
| Phase 4 | 5-7h | 🟠 MOYENNE | ContextAnalyzer | >85% | Phase 1 |
| Phase 5 | 2-3h | 🟡 MOYENNE | Tests, Benchmarks | 100% | Validation |
| Phase 6 | 1-2h | 🟡 BASSE | Documentation | N/A | N/A |

**TOTAL** : 30-40 heures

---

## 🎯 Prochaine Action Immédiate

→ **Commencer Phase 1 : Mémoire Long-Terme**

**Première étape** :

```powershell
# Installer sentence-transformers
cd c:\Dev\workly_project\workly-desktop
.\venv\Scripts\Activate.ps1
pip install sentence-transformers
```

---

**Créé le** : 16 novembre 2025
**Dernière mise à jour** : 16 novembre 2025
