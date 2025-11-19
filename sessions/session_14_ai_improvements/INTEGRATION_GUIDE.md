# 🔌 Guide Intégration ChatEngine - Session 14

**Date** : 16 novembre 2025
**Version** : 0.18.0-alpha (cible)

---

## 🎯 Objectif

Ce guide détaille **comment intégrer** les 6 nouveaux modules IA avec le `ChatEngine` existant, en minimisant les modifications du code actuel et en garantissant la rétrocompatibilité.

---

## 📊 État Actuel ChatEngine

**Fichier** : `src/ai/chat_engine.py` (~400 lignes)

### Structure Actuelle

```python
class ChatEngine:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.emotion_analyzer = EmotionAnalyzer()
        self.conversation_history = []  # Limite 10 messages
        self.system_prompt = "Tu es Kira, une assistante virtuelle amicale et empathique..."

    def generate_response(self, user_message: str) -> dict:
        # 1. Ajouter message à historique
        self.conversation_history.append({"role": "user", "content": user_message})

        # 2. Construire contexte (10 derniers messages)
        context = self._build_context()

        # 3. Générer réponse via LLM
        response = self.model_manager.generate(context, system_prompt=self.system_prompt)

        # 4. Détecter émotion (keywords)
        emotion, intensity = self.emotion_analyzer.analyze_emotion(response)

        # 5. Ajouter réponse à historique
        self.conversation_history.append({"role": "assistant", "content": response})

        # 6. Limiter historique à 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

        return {
            "response": response,
            "emotion": emotion,
            "intensity": intensity
        }
```

---

## 🔧 Modifications Nécessaires

### Étape 1 : Ajouter Imports

**Fichier** : `src/ai/chat_engine.py` (début fichier)

```python
# Imports existants
from typing import List, Dict, Any, Optional, Tuple
import logging

# NOUVEAUX imports
from src.ai.memory_manager import MemoryManager
from src.ai.personality_engine import PersonalityEngine
from src.ai.emotion_memory import EmotionMemory
from src.ai.context_analyzer import ContextAnalyzer

logger = logging.getLogger(__name__)
```

---

### Étape 2 : Modifier __init__()

**Avant** :

```python
def __init__(self, model_manager):
    self.model_manager = model_manager
    self.emotion_analyzer = EmotionAnalyzer()
    self.conversation_history = []
    self.system_prompt = "Tu es Kira, une assistante virtuelle amicale et empathique..."
```

**Après** :

```python
def __init__(self, model_manager, enable_advanced_ai: bool = True):
    """
    Initialise le ChatEngine.

    Args:
        model_manager: Gestionnaire modèle LLM
        enable_advanced_ai: Activer modules IA avancés (défaut: True)
    """
    self.model_manager = model_manager
    self.enable_advanced_ai = enable_advanced_ai

    # Module émotions (AMÉLIORER existant)
    self.emotion_analyzer = EmotionAnalyzer()

    # État émotionnel actuel
    self.current_emotion = "neutre"
    self.current_intensity = 0.5

    # Historique court-terme (garder pour compatibilité)
    self.conversation_history = []

    # NOUVEAUX modules IA (si activés)
    if self.enable_advanced_ai:
        logger.info("🧠 Initialisation modules IA avancés...")

        self.memory_manager = MemoryManager(storage_path="data/memory/")
        self.personality_engine = PersonalityEngine(storage_path="data/personality.json")
        self.context_analyzer = ContextAnalyzer()

        # EmotionMemory utilisé par EmotionAnalyzer amélioré
        self.emotion_analyzer.emotion_memory = EmotionMemory(storage_path="data/emotion_history.json")

        logger.info("✅ Modules IA avancés prêts !")
    else:
        logger.info("⚠️ Modules IA avancés désactivés (mode legacy)")
        self.memory_manager = None
        self.personality_engine = None
        self.context_analyzer = None

    # Prompt système (sera remplacé dynamiquement si PersonalityEngine activé)
    self.base_system_prompt = "Tu es Kira, une assistante virtuelle amicale et empathique."
```

**Raisons** :
- ✅ Rétrocompatibilité : `enable_advanced_ai=False` désactive nouveaux modules
- ✅ Logs clairs : Utilisateur sait si modules actifs
- ✅ État émotionnel : Suivi émotion courante pour transitions douces

---

### Étape 3 : Modifier generate_response() (CRITIQUE)

**Structure Nouvelle** :

```python
def generate_response(self, user_message: str) -> dict:
    """
    Génère réponse avec tous modules IA activés.

    Args:
        user_message: Message utilisateur

    Returns:
        dict avec response, emotion, intensity, metadata
    """
    logger.debug(f"📩 Message utilisateur: {user_message[:50]}...")

    # === PHASE 1: ANALYSE CONTEXTUELLE ===
    intent, intent_conf = None, 0.0
    sentiment, sent_score = None, 0.0

    if self.enable_advanced_ai and self.context_analyzer:
        intent, intent_conf = self.context_analyzer.detect_intent(user_message)
        sentiment, sent_score = self.context_analyzer.analyze_sentiment(user_message)
        logger.debug(f"🔍 Intent: {intent} ({intent_conf:.2f}), Sentiment: {sentiment} ({sent_score:.2f})")

    # === PHASE 2: RÉCUPÉRATION MÉMOIRE LONG-TERME ===
    relevant_context = []

    if self.enable_advanced_ai and self.memory_manager:
        relevant_context = self.memory_manager.get_relevant_context(user_message, k=3)
        logger.debug(f"🧠 Contexte pertinent: {len(relevant_context)} entrées")

    # === PHASE 3: GÉNÉRATION PROMPT SYSTÈME ADAPTATIF ===
    system_prompt = self.base_system_prompt

    if self.enable_advanced_ai and self.personality_engine:
        system_prompt = self.personality_engine.generate_system_prompt()
        logger.debug(f"🎭 Prompt système adaptatif généré")

    # === PHASE 4: CONSTRUCTION CONTEXTE COMPLET ===
    full_context = self._build_full_context(
        user_message=user_message,
        relevant_memory=relevant_context,
        short_term_history=self.conversation_history[-10:],  # Garder 10 derniers
    )

    # === PHASE 5: GÉNÉRATION RÉPONSE LLM ===
    logger.debug("💬 Génération réponse LLM...")
    response = self.model_manager.generate(
        prompt=full_context,
        system_prompt=system_prompt,
    )
    logger.debug(f"✅ Réponse générée: {response[:50]}...")

    # === PHASE 6: ANALYSE ÉMOTION AVEC CONTEXTE ===
    if self.enable_advanced_ai:
        # Analyse avancée (avec mémoire émotionnelle)
        emotion, intensity = self.emotion_analyzer.analyze_with_context(
            text=response,
            previous_emotion=self.current_emotion,
            previous_intensity=self.current_intensity,
        )
    else:
        # Analyse basique (keywords uniquement)
        emotion, intensity = self.emotion_analyzer.analyze_emotion(response)

    logger.debug(f"🎨 Émotion: {emotion} (intensité: {intensity:.2f})")

    # === PHASE 7: STOCKAGE MÉMOIRE ===
    if self.enable_advanced_ai and self.memory_manager:
        # Stocker message utilisateur
        self.memory_manager.store_message(
            message=user_message,
            role="user",
            metadata={
                "intent": intent,
                "intent_confidence": intent_conf,
                "sentiment": sentiment,
                "sentiment_score": sent_score,
            }
        )

        # Stocker réponse assistant
        self.memory_manager.store_message(
            message=response,
            role="assistant",
            metadata={
                "emotion": emotion,
                "intensity": intensity,
            }
        )

    # === PHASE 8: RÉSUMÉ SI NÉCESSAIRE ===
    summary_generated = False

    if self.enable_advanced_ai and self.memory_manager:
        summary = self.memory_manager.summarize_if_needed()
        if summary:
            logger.info(f"📝 Résumé conversation généré: {len(summary)} caractères")
            summary_generated = True

    # === PHASE 9: MISE À JOUR PERSONNALITÉ ===
    if self.enable_advanced_ai and self.personality_engine:
        self.personality_engine.update_traits({
            "user_message": user_message,
            "intent": intent,
            "sentiment": sentiment,
            "response": response,
        })

    # === PHASE 10: MISE À JOUR ÉTAT ACTUEL ===
    self.current_emotion = emotion
    self.current_intensity = intensity

    # Ajouter à historique court-terme (compatibilité)
    self.conversation_history.append({"role": "user", "content": user_message})
    self.conversation_history.append({"role": "assistant", "content": response})

    # Limiter historique court-terme
    if len(self.conversation_history) > 20:  # Augmenté de 10 à 20
        self.conversation_history = self.conversation_history[-20:]

    # === RETOUR RÉSULTAT ===
    return {
        "response": response,
        "emotion": emotion,
        "intensity": intensity,
        # Metadata additionnelles
        "intent": intent,
        "intent_confidence": intent_conf,
        "sentiment": sentiment,
        "sentiment_score": sent_score,
        "summary_generated": summary_generated,
        "advanced_ai_enabled": self.enable_advanced_ai,
    }
```

---

### Étape 4 : Nouvelle Méthode _build_full_context()

**Ajouter méthode** :

```python
def _build_full_context(
    self,
    user_message: str,
    relevant_memory: List[str],
    short_term_history: List[dict],
) -> str:
    """
    Construit contexte complet pour LLM.

    Combine :
    - Mémoire long-terme pertinente
    - Historique court-terme (10-20 derniers messages)
    - Message utilisateur actuel

    Args:
        user_message: Message actuel utilisateur
        relevant_memory: Contexte pertinent mémoire long-terme
        short_term_history: 10-20 derniers messages

    Returns:
        Contexte formaté pour LLM
    """
    context_parts = []

    # 1. Mémoire long-terme (si disponible)
    if relevant_memory:
        context_parts.append("=== Contexte pertinent ===")
        for i, memory in enumerate(relevant_memory, 1):
            context_parts.append(f"{i}. {memory}")
        context_parts.append("")  # Ligne vide

    # 2. Historique court-terme
    if short_term_history:
        context_parts.append("=== Conversation récente ===")
        for msg in short_term_history:
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        context_parts.append("")

    # 3. Message actuel
    context_parts.append("=== Message actuel ===")
    context_parts.append(f"Utilisateur: {user_message}")
    context_parts.append("")
    context_parts.append("Assistant:")

    return "\n".join(context_parts)
```

---

### Étape 5 : Garder Méthodes Existantes (Rétrocompatibilité)

**Méthodes à GARDER** (utilisées ailleurs) :

```python
def update_context(self, user_message: str, assistant_response: str):
    """
    Mise à jour contexte (LEGACY - pour compatibilité).
    Utilisé par certains anciens tests.
    """
    self.conversation_history.append({"role": "user", "content": user_message})
    self.conversation_history.append({"role": "assistant", "content": assistant_response})

    if len(self.conversation_history) > 20:
        self.conversation_history = self.conversation_history[-20:]

def get_conversation_history(self) -> List[dict]:
    """Retourne historique conversation (LEGACY)."""
    return self.conversation_history.copy()

def clear_history(self):
    """Efface historique conversation."""
    self.conversation_history.clear()
    logger.info("🗑️ Historique conversation effacé")
```

---

## 🧪 Tests Unitaires à Modifier

**Fichier** : `tests/ai/test_chat_engine.py`

### Ajouter Tests Nouveaux Modules

```python
import pytest
from src.ai.chat_engine import ChatEngine
from src.ai.model_manager import ModelManager

@pytest.fixture
def chat_engine_advanced(model_manager_mock):
    """ChatEngine avec modules IA avancés activés."""
    return ChatEngine(model_manager_mock, enable_advanced_ai=True)

@pytest.fixture
def chat_engine_legacy(model_manager_mock):
    """ChatEngine en mode legacy (sans modules avancés)."""
    return ChatEngine(model_manager_mock, enable_advanced_ai=False)

def test_advanced_modules_initialization(chat_engine_advanced):
    """Vérifie que modules avancés sont initialisés."""
    assert chat_engine_advanced.memory_manager is not None
    assert chat_engine_advanced.personality_engine is not None
    assert chat_engine_advanced.context_analyzer is not None

def test_legacy_mode_no_advanced_modules(chat_engine_legacy):
    """Vérifie que mode legacy ne charge pas modules avancés."""
    assert chat_engine_legacy.memory_manager is None
    assert chat_engine_legacy.personality_engine is None
    assert chat_engine_legacy.context_analyzer is None

def test_generate_response_with_advanced_ai(chat_engine_advanced, model_manager_mock):
    """Test génération réponse avec modules avancés."""
    model_manager_mock.generate.return_value = "Bonjour ! Comment puis-je t'aider ?"

    result = chat_engine_advanced.generate_response("Bonjour")

    assert "response" in result
    assert "emotion" in result
    assert "intent" in result
    assert "sentiment" in result
    assert result["advanced_ai_enabled"] is True

def test_context_analyzer_detects_intent(chat_engine_advanced):
    """Vérifie détection intention par ContextAnalyzer."""
    result = chat_engine_advanced.generate_response("Comment créer un rappel ?")

    assert result["intent"] == "question"
    assert result["intent_confidence"] > 0.8

def test_memory_stores_messages(chat_engine_advanced, tmp_path):
    """Vérifie stockage messages dans mémoire."""
    chat_engine_advanced.memory_manager.storage_path = str(tmp_path)

    chat_engine_advanced.generate_response("Je m'appelle Alice")

    # Vérifier message stocké
    assert len(chat_engine_advanced.memory_manager.get_recent_messages()) > 0
```

---

## 🔄 Migration Code Existant

### Modules Utilisant ChatEngine

**Fichiers à vérifier** :

1. `src/gui/app.py` : Interface Qt utilise ChatEngine
2. `src/discord_bot/bot.py` : Bot Discord utilise ChatEngine
3. `tests/ai/test_chat_engine.py` : Tests unitaires

### Changements Nécessaires

#### 1. src/gui/app.py

**Avant** :

```python
self.chat_engine = ChatEngine(self.model_manager)
```

**Après** :

```python
# Activer modules IA avancés (défaut: True)
enable_advanced = self.config.get("ai.enable_advanced_features", default=True)
self.chat_engine = ChatEngine(self.model_manager, enable_advanced_ai=enable_advanced)
```

**Ajout dans config.json** :

```json
{
  "ai": {
    "enable_advanced_features": true
  }
}
```

#### 2. Affichage Metadata Interface

**Ajouter dans app.py** (optionnel, pour debug) :

```python
def _display_response_metadata(self, result: dict):
    """Affiche metadata réponse IA (debug)."""
    if result.get("advanced_ai_enabled"):
        metadata = []

        if result.get("intent"):
            metadata.append(f"Intent: {result['intent']} ({result['intent_confidence']:.2f})")

        if result.get("sentiment"):
            metadata.append(f"Sentiment: {result['sentiment']} ({result['sentiment_score']:.2f})")

        if result.get("summary_generated"):
            metadata.append("📝 Résumé conversation généré")

        if metadata:
            logger.debug("📊 Metadata: " + ", ".join(metadata))
```

---

## ⚠️ Points d'Attention

### 1. Performances

**Objectif** : Temps réponse <3s

**Mesures** :
- ✅ Recherche embeddings : ~50ms (OK)
- ✅ Génération LLM : ~2000ms (OK avec CUDA)
- ✅ Analyse contextuelle : ~10ms (OK)
- ✅ **TOTAL** : ~2100ms ✅

**Optimisations** :
- Recherche embeddings peut être async (parallèle génération LLM)
- Cache résultats ContextAnalyzer si messages similaires

### 2. Gestion Erreurs

**Stratégies** :

```python
def generate_response(self, user_message: str) -> dict:
    try:
        # ... code génération ...

    except Exception as e:
        logger.error(f"❌ Erreur génération réponse: {e}", exc_info=True)

        # Fallback : Réponse basique sans modules avancés
        response = "Désolée, j'ai rencontré un problème. Peux-tu reformuler ?"

        return {
            "response": response,
            "emotion": "neutre",
            "intensity": 0.5,
            "error": str(e),
            "advanced_ai_enabled": self.enable_advanced_ai,
        }
```

### 3. Migrations Données

**Si structures JSON changent** :

```python
# memory_manager.py
def _load_memory(self):
    """Charge mémoire avec migration auto si nécessaire."""
    try:
        with open(self.conversations_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Vérifier version schéma
        if data.get("version") == "1.0":
            # OK, version actuelle
            return data
        elif data.get("version") == "0.9":
            # Migrer 0.9 → 1.0
            logger.info("🔄 Migration données 0.9 → 1.0...")
            data = self._migrate_v09_to_v10(data)
            self._save_conversations(data)  # Sauvegarder version migrée
            return data
        else:
            logger.warning(f"⚠️ Version schéma inconnue: {data.get('version')}")
            return data

    except FileNotFoundError:
        logger.info("📁 Fichier mémoire non trouvé, création...")
        return self._create_empty_memory()
```

---

## 📋 Checklist Intégration

### Avant Codage

- ✅ Lire ARCHITECTURE.md
- ✅ Lire DATA_SCHEMAS.md
- ✅ Comprendre flux données
- ✅ Identifier modifications ChatEngine nécessaires

### Pendant Codage

- ✅ Créer nouveaux modules un par un
- ✅ Tests unitaires chaque module (>80% coverage)
- ✅ Modifier ChatEngine progressivement
- ✅ Garder rétrocompatibilité (mode legacy)
- ✅ Logs debug abondants

### Après Codage

- ✅ Tests intégration ChatEngine complet
- ✅ Benchmark temps réponse (<3s)
- ✅ Vérifier VRAM (<6 GB)
- ✅ Tests avec UI (app.py)
- ✅ Tests avec Discord bot
- ✅ Documentation mise à jour

---

## 🎯 Ordre Implémentation Recommandé

### Phase 1 : Mémoire Long-Terme (Priorité HAUTE)

1. Créer `MemoryManager` (squelette)
2. Créer `ConversationSummarizer`
3. Créer `FactExtractor`
4. Compléter `MemoryManager`
5. Tests unitaires (3 modules)
6. **Intégrer dans ChatEngine** (phases 2, 7, 8)

### Phase 2 : Personnalité Évolutive

1. Créer `PersonalityEngine`
2. Tests unitaires
3. **Intégrer dans ChatEngine** (phases 3, 9)

### Phase 3 : Émotions Avancées

1. Améliorer `EmotionAnalyzer`
2. Créer `EmotionMemory`
3. Tests unitaires
4. **Intégrer dans ChatEngine** (phase 6)

### Phase 4 : Analyse Contextuelle

1. Créer `ContextAnalyzer`
2. Tests unitaires
3. **Intégrer dans ChatEngine** (phase 1)

### Phase 5 : Tests Intégration Finaux

1. Tests ChatEngine complet
2. Tests app.py + Discord
3. Benchmarks performance
4. Corrections bugs
5. Documentation finale

---

**Créé le** : 16 novembre 2025
**Dernière mise à jour** : 16 novembre 2025
