# 📖 Contexte pour Chat 7 - Desktop-Mate (Session 10 - Phase 3+)

**Date** : Octobre 2025  
**Session** : Session 10 - IA Conversationnelle (Kira)  
**Phase suivante** : Phase 3 - Configuration IA  
**Progression** : 2/14 phases (14%)

---

## 🎯 Objectif Chat 7

**Compléter les phases suivantes** :
- ✅ **Phase 3** : Configuration IA (1h)
- ✅ **Phase 4** : Model Manager (2-3h)
- ✅ **Phase 5** : Chat Engine (2-3h)
- ⚠️ *Optionnel si temps* : Phase 6 - Emotion Analyzer (1-2h)

**Durée estimée** : 5-8h (ou jusqu'à 10h avec Phase 6)

---

## 📚 Documents à Lire AVANT de Commencer

### 1️⃣ Transition Chat 6 → Chat 7

**OBLIGATOIRES** :
- ✅ `docs/chat_transitions/chat_6_session_10_phases_1_2/CURRENT_STATE.md`  
  → État technique complet après Phases 1-2
  
- ✅ `docs/chat_transitions/chat_6_session_10_phases_1_2/CHAT_SUMMARY.md`  
  → Résumé des réalisations Chat 6

- ✅ Ce fichier : `CONTEXT_FOR_NEXT_CHAT.md`  
  → Contexte et instructions pour Chat 7

### 2️⃣ Documentation Session 10

**OBLIGATOIRES** :
- ✅ `docs/sessions/session_10_ai_chat/PLAN_SESSION_10.md`  
  → **CRITIQUE** : Plan complet 14 phases avec détails Phase 3-5
  
- ✅ `docs/sessions/session_10_ai_chat/README.md`  
  → Vue d'ensemble Session 10 et progression

### 3️⃣ Instructions Copilot

**OBLIGATOIRES** :
- ✅ `.github/instructions/copilot-instructions.instructions.md`  
  → Règles de documentation, workflow, communication

---

## 🧠 Ce que tu Dois Savoir du Chat 6

### ✅ Ce qui a été fait (Phases 1-2)

#### Phase 1 : Architecture de Base
- ✅ Dossiers créés : `src/ai/`, `src/discord_bot/`, `src/auth/`, `models/`
- ✅ Fichiers `__init__.py` pour tous les modules
- ✅ Modèle LLM copié : `models/zephyr-7b-beta.Q5_K_M.gguf` (6.8 GB)
- ✅ Configuration : `.env`, `.env.example`, `.gitignore`, `requirements.txt`
- ✅ Documentation : `README.md`, `PLAN_SESSION_10.md`, `INDEX.md` mis à jour

#### Phase 2 : Base de Données & Mémoire
- ✅ `src/ai/memory.py` (430 lignes) - Système conversationnel complet
- ✅ SQLite `data/chat_history.db` avec 4 indexes optimisés
- ✅ Tests `tests/test_memory.py` - 11/11 tests passent ✅
- ✅ Singleton pattern avec `get_memory()`
- ✅ Context manager thread-safe

### 🔑 Informations Critiques

**Modèle LLM** :
- Fichier : `models/zephyr-7b-beta.Q5_K_M.gguf`
- Taille : 6.8 GB
- Quantization : Q5_K_M (excellent pour RTX 4050)
- Performance : ~20-30 tokens/sec

**Base de données** :
- SQLite : `data/chat_history.db`
- Table : `chat_history` (7 colonnes)
- Indexes : 4 (user_id, source, timestamp, user_timestamp)

**GPU Utilisateur** :
- NVIDIA RTX 4050 (6 GB VRAM)
- Profils prévus : Performance, Balanced, CPU Fallback

**Variables d'environnement** :
- `.env` configuré avec `DISCORD_TOKEN`
- `.env.example` comme template

### 📦 Modules Opérationnels

```python
# Système de mémoire (FONCTIONNEL)
from src.ai.memory import ConversationMemory, get_memory

memory = get_memory()  # Singleton
memory.save_interaction(user_id, source, user_input, bot_response, emotion)
history = memory.get_history(user_id, limit=10)
stats = memory.get_stats()
```

**Tests** :
```powershell
pytest tests/test_memory.py -v
# 11 passed in 0.70s ✅
```

### ⚠️ Ce qui N'est PAS fait

- ⏳ Configuration IA centralisée
- ⏳ Gestion LLM (chargement, génération)
- ⏳ Moteur conversationnel
- ⏳ Analyse émotionnelle
- ⏳ Bot Discord
- ⏳ Interface GUI chat
- ⏳ Système 2FA
- ⏳ Intégration Unity IPC

---

## 🎯 Phase 3 : Configuration IA (PROCHAINE)

### Objectif Phase 3

Créer un système de configuration centralisé pour l'IA avec :
- ✅ Profils GPU adaptatifs
- ✅ Paramètres LLM configurables
- ✅ System prompt personnalisable
- ✅ Validation des paramètres

### Fichiers à Créer

#### 1️⃣ `src/ai/config.py`

**Contenu attendu** :
```python
"""
Configuration IA pour Desktop-Mate
Gestion profils GPU, paramètres LLM, system prompt
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Profils GPU prédéfinis
GPU_PROFILES = {
    "performance": {
        "n_gpu_layers": -1,      # Toutes layers sur GPU
        "n_ctx": 4096,           # Contexte max
        "n_batch": 512,          # Batch size max
        "description": "Max GPU, idéal conversations courtes"
    },
    "balanced": {
        "n_gpu_layers": 35,      # 35 layers GPU (Zephyr-7B)
        "n_ctx": 2048,           # Contexte modéré
        "n_batch": 256,          # Batch modéré
        "description": "Équilibre GPU/CPU (DÉFAUT)"
    },
    "cpu_fallback": {
        "n_gpu_layers": 0,       # CPU uniquement
        "n_ctx": 2048,
        "n_batch": 128,
        "description": "Fallback sans GPU"
    }
}

@dataclass
class AIConfig:
    """Configuration IA"""
    model_path: str
    context_limit: int
    gpu_profile: str
    temperature: float
    top_p: float
    max_tokens: int
    system_prompt: str
    
    @classmethod
    def from_json(cls, config_path: str = "data/config.json") -> "AIConfig":
        """Charge config depuis JSON"""
        # Charger config.json
        # Extraire section "ai"
        # Valider paramètres
        # Retourner AIConfig
        pass
    
    def get_gpu_params(self) -> Dict[str, Any]:
        """Retourne paramètres GPU du profil"""
        return GPU_PROFILES.get(self.gpu_profile, GPU_PROFILES["balanced"])
    
    def validate(self) -> bool:
        """Valide les paramètres"""
        # Vérifier model_path existe
        # Vérifier gpu_profile valide
        # Vérifier temperature/top_p dans [0, 1]
        # Vérifier max_tokens > 0
        pass
```

**Voir détails complets** : `PLAN_SESSION_10.md` Phase 3

#### 2️⃣ Étendre `data/config.json`

**Ajouter section IA** :
```json
{
  "existing_config": "...",
  
  "ai": {
    "model_path": "models/zephyr-7b-beta.Q5_K_M.gguf",
    "context_limit": 2048,
    "gpu_profile": "balanced",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 512,
    "system_prompt": "Tu es Kira, l'assistante IA de Desktop-Mate. Tu es amicale, serviable et expressive. Tu peux ressentir et exprimer des émotions à travers tes expressions faciales. Réponds de manière naturelle et engageante."
  }
}
```

#### 3️⃣ Tests : `tests/test_config.py`

**Tests à créer** :
- ✅ `test_load_config()` - Chargement config.json
- ✅ `test_gpu_profiles()` - Profils GPU valides
- ✅ `test_validation()` - Validation paramètres
- ✅ `test_default_values()` - Valeurs par défaut
- ✅ `test_invalid_profile()` - Gestion erreurs

### Durée Phase 3

**Estimée** : 1h

**Décomposition** :
- 30 min : `src/ai/config.py` + `GPU_PROFILES`
- 15 min : Étendre `data/config.json`
- 15 min : Tests `test_config.py`

---

## 🚀 Phase 4 : Model Manager (APRÈS Phase 3)

### Objectif Phase 4

Créer le gestionnaire LLM qui :
- ✅ Charge le modèle avec llama-cpp-python
- ✅ Détecte GPU avec pynvml
- ✅ Applique profil GPU approprié
- ✅ Génère texte avec contexte
- ✅ Gère erreurs (OOM, model not found)

### Fichier à Créer

#### `src/ai/model_manager.py`

**Contenu attendu** :
```python
"""
Model Manager pour Desktop-Mate
Gestion LLM (llama-cpp-python), GPU, génération texte
"""

from llama_cpp import Llama
import pynvml
from typing import Optional, Dict, List
from .config import AIConfig
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """Gestionnaire du modèle LLM"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.model: Optional[Llama] = None
        self.gpu_available = self._check_gpu()
        
    def _check_gpu(self) -> bool:
        """Détecte GPU NVIDIA"""
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle)
                logger.info(f"GPU détecté : {name}")
                return True
        except Exception as e:
            logger.warning(f"GPU non détecté : {e}")
        return False
    
    def load_model(self) -> bool:
        """Charge le modèle LLM"""
        # Récupérer paramètres GPU du profil
        # Créer Llama avec llama-cpp-python
        # Gérer erreurs (OOM, fichier absent)
        pass
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Génère texte depuis prompt"""
        # Utiliser self.model(prompt, ...)
        # Extraire texte généré
        # Gérer erreurs
        pass
    
    def get_gpu_info(self) -> Dict:
        """Retourne info GPU (VRAM, température)"""
        pass
```

**Voir détails complets** : `PLAN_SESSION_10.md` Phase 4

### Tests : `tests/test_model_manager.py`

**Tests à créer** :
- ✅ `test_gpu_detection()` - Détection GPU
- ✅ `test_load_model()` - Chargement modèle
- ✅ `test_generate()` - Génération texte
- ✅ `test_gpu_info()` - Info GPU
- ✅ `test_error_handling()` - Gestion erreurs

### Durée Phase 4

**Estimée** : 2-3h

---

## 🎤 Phase 5 : Chat Engine (APRÈS Phase 4)

### Objectif Phase 5

Créer le moteur conversationnel unifié qui :
- ✅ Orchestre mémoire + model manager
- ✅ Gère contexte conversations (historique)
- ✅ Construit prompts avec system prompt
- ✅ Génère réponses cohérentes
- ✅ Détecte émotions (basique)

### Fichier à Créer

#### `src/ai/chat_engine.py`

**Contenu attendu** :
```python
"""
Chat Engine pour Desktop-Mate
Moteur conversationnel unifié (GUI + Discord)
"""

from typing import Optional, Dict
from .model_manager import ModelManager
from .memory import ConversationMemory, get_memory
from .config import AIConfig
import logging

logger = logging.getLogger(__name__)

class ChatEngine:
    """Moteur conversationnel unifié"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.model_manager = ModelManager(config)
        self.memory = get_memory()
        
    def start(self) -> bool:
        """Démarre le moteur (charge modèle)"""
        return self.model_manager.load_model()
    
    def chat(self, user_id: str, user_input: str, source: str = "desktop") -> Dict:
        """
        Génère réponse pour user_input
        
        Returns:
            {
                "response": str,
                "emotion": str,
                "error": Optional[str]
            }
        """
        # 1. Récupérer historique
        # 2. Construire prompt avec system_prompt + historique + user_input
        # 3. Générer réponse
        # 4. Détecter émotion (basique)
        # 5. Sauvegarder interaction
        # 6. Retourner dict
        pass
    
    def _build_prompt(self, history: List[Dict], user_input: str) -> str:
        """Construit prompt complet"""
        pass
    
    def _detect_emotion(self, text: str) -> str:
        """Détection émotionnelle basique (keywords)"""
        # Détection simple par mots-clés
        # Version améliorée en Phase 6
        pass
```

**Voir détails complets** : `PLAN_SESSION_10.md` Phase 5

### Tests : `tests/test_chat_engine.py`

**Tests à créer** :
- ✅ `test_chat_basic()` - Conversation basique
- ✅ `test_chat_with_history()` - Avec contexte
- ✅ `test_emotion_detection()` - Détection émotion
- ✅ `test_memory_integration()` - Intégration mémoire
- ✅ `test_error_handling()` - Gestion erreurs

### Durée Phase 5

**Estimée** : 2-3h

---

## 📊 Ordre d'Implémentation Chat 7

### Séquence Recommandée

```
1. Phase 3 : Configuration IA (1h)
   ├── src/ai/config.py
   ├── data/config.json (étendre)
   └── tests/test_config.py

2. Phase 4 : Model Manager (2-3h)
   ├── src/ai/model_manager.py
   └── tests/test_model_manager.py

3. Phase 5 : Chat Engine (2-3h)
   ├── src/ai/chat_engine.py
   └── tests/test_chat_engine.py

4. [OPTIONNEL] Phase 6 : Emotion Analyzer (1-2h)
   ├── src/ai/emotion_analyzer.py
   └── tests/test_emotion_analyzer.py
```

**Temps total estimé** :
- Phases 3-5 : 5-7h
- Avec Phase 6 : 6-9h

---

## 🧪 Stratégie de Tests

### Commandes Importantes

**Tester module spécifique** :
```powershell
pytest tests/test_config.py -v
pytest tests/test_model_manager.py -v
pytest tests/test_chat_engine.py -v
```

**Tester tous les tests IA** :
```powershell
pytest tests/test_memory.py tests/test_config.py tests/test_model_manager.py tests/test_chat_engine.py -v
```

**Tests avec couverture** :
```powershell
pytest --cov=src.ai tests/ --cov-report=html
```

### Validation Après Chaque Phase

**Après Phase 3** :
```powershell
pytest tests/test_config.py -v
# Vérifier chargement config.json OK
```

**Après Phase 4** :
```powershell
pytest tests/test_model_manager.py -v
# Vérifier détection GPU OK
# Vérifier chargement modèle OK (peut être long ~30s)
```

**Après Phase 5** :
```powershell
pytest tests/test_chat_engine.py -v
# Vérifier conversation basique OK
# Vérifier sauvegarde mémoire OK
```

---

## 📚 Références Utiles

### Documentation Externe

**llama-cpp-python** :
- Docs : https://llama-cpp-python.readthedocs.io/
- Paramètres Llama : `n_gpu_layers`, `n_ctx`, `n_batch`, `temperature`, `top_p`

**pynvml** :
- Docs : https://pypi.org/project/pynvml/
- Fonctions : `nvmlInit()`, `nvmlDeviceGetCount()`, `nvmlDeviceGetHandleByIndex()`

**SQLite Python** :
- Docs : https://docs.python.org/3/library/sqlite3.html

### Code de Référence (Kira-Bot)

**⚠️ IMPORTANT** : Kira-Bot existe mais est désorganisé (score 5.7/10)

**Utilise comme référence UNIQUEMENT** :
- `C:\Dev\IA-chatbot\model.py` - Exemple ModelManager
- `C:\Dev\IA-chatbot\config.py` - Exemple configuration
- `C:\Dev\IA-chatbot\memory.py` - Notre version est meilleure !

**NE PAS copier-coller** : Adapter les concepts, réécrire proprement

---

## 🔧 Configuration Utilisateur

### Variables d'Environnement

**Fichier** : `.env` (configuré)
```
DISCORD_TOKEN=<configuré_par_utilisateur>
TOTP_SECRET=<sera_généré_en_phase_10>
```

### Matériel

**GPU** : NVIDIA RTX 4050 (6 GB VRAM)  
**Profil recommandé** : `balanced` (défaut)  
**Performance attendue** : 20-30 tokens/sec

---

## 🚨 Points d'Attention

### 1. Chargement Modèle (Phase 4)

**⚠️ Peut être lent** : Chargement initial ~20-30s pour 6.8 GB

**Solutions** :
- Afficher message "Chargement modèle..."
- Logger progression
- Gérer timeout

### 2. Gestion Mémoire GPU (Phase 4)

**⚠️ Risque OOM** : Si profil trop élevé pour GPU

**Solutions** :
- Commencer avec profil `balanced`
- Détecter erreur OOM
- Fallback automatique vers `cpu_fallback`
- Logger événement

### 3. Contexte Conversations (Phase 5)

**⚠️ Limite contexte** : 2048 tokens (profil balanced)

**Solutions** :
- Limiter historique à 10 derniers messages
- Résumer vieux messages (Phase future)
- Afficher warning si contexte plein

### 4. Tests Longs (Phase 4-5)

**⚠️ Tests avec LLM** : Génération texte peut prendre 5-10s

**Solutions** :
- Utiliser `@pytest.mark.slow` pour tests LLM
- Permettre `pytest -m "not slow"` pour tests rapides
- Mock pour tests unitaires, intégration pour tests lents

---

## 📖 Documentation à Mettre à Jour

### Après CHAQUE Phase

**OBLIGATOIRE** :
- ✅ `docs/INDEX.md` - Ajouter nouveaux fichiers
- ✅ `docs/README.md` - Si architecture modifiée
- ✅ `README.md` (racine) - Si fonctionnalité majeure
- ✅ `docs/sessions/session_10_ai_chat/README.md` - Progression phases

**SYSTÈME CRITIQUE** :
Suivre `.github/instructions/copilot-instructions.instructions.md`

**Règle d'or** :
> "L'utilisateur ne devrait JAMAIS avoir à demander si la documentation est à jour"

---

## 🎯 Objectif Final Chat 7

À la fin du Chat 7, Desktop-Mate devrait avoir :

✅ Configuration IA centralisée et testée  
✅ Modèle LLM chargeable avec profils GPU  
✅ Moteur conversationnel fonctionnel  
✅ Génération de réponses avec contexte  
✅ Sauvegarde automatique des conversations  
✅ Détection émotionnelle basique  
✅ Tests complets (15-20 tests)  
✅ Documentation à jour  

**Prêt pour** :
- Phase 7 : Bot Discord (Chat 8)
- Phase 8 : GUI Chat (Chat 8)

---

## 💡 Conseils pour l'IA (Toi)

### Workflow Recommandé

**Pour chaque phase** :
1. ✅ Lire détails dans `PLAN_SESSION_10.md`
2. ✅ Expliquer ce que tu vas faire
3. ✅ Créer les fichiers Python
4. ✅ Créer les tests
5. ✅ Exécuter les tests
6. ✅ Corriger les erreurs
7. ✅ **METTRE À JOUR DOCUMENTATION**
8. ✅ Afficher récapitulatif phase

**JAMAIS dire "Terminé" sans** :
- ✅ Tests passants
- ✅ Documentation mise à jour
- ✅ Récapitulatif affiché

### Communication avec Utilisateur

**Rappels** :
- 🇫🇷 Toujours en français
- 📖 Expliquer clairement les concepts techniques
- ⚠️ Demander confirmation avant changements majeurs
- 🎓 L'utilisateur n'est pas expert → Être pédagogue

### Gestion du Temps

**Phases longues (4-5)** :
- Découper en sous-tâches
- Afficher progression régulièrement
- Permettre pauses si demandées

**Tests** :
- Ne pas attendre la fin pour tester
- Tester après chaque méthode critique
- Corriger au fur et à mesure

---

## 🔗 Liens Rapides

**Documentation Session 10** :
- `docs/sessions/session_10_ai_chat/PLAN_SESSION_10.md` ← **CRITIQUE**
- `docs/sessions/session_10_ai_chat/README.md`

**Transition Chat 6** :
- `docs/chat_transitions/chat_6_session_10_phases_1_2/CURRENT_STATE.md`
- `docs/chat_transitions/chat_6_session_10_phases_1_2/CHAT_SUMMARY.md`

**Instructions Projet** :
- `.github/instructions/copilot-instructions.instructions.md`

**Code Existant** :
- `src/ai/memory.py` ← Exemple qualité attendue
- `tests/test_memory.py` ← Exemple tests complets

---

## 🎊 Message de Motivation

Chat 6 a posé des **bases solides** ! 🎉

L'architecture est propre, la mémoire fonctionne parfaitement (11/11 tests ✅), et le modèle LLM est prêt.

**Chat 7 va donner vie à Kira** en lui permettant de :
- 🧠 Penser (Model Manager)
- 💬 Converser (Chat Engine)
- 🎭 Ressentir (Emotion basique)

**Tu es prêt à créer la partie la plus excitante du projet ! 🚀**

---

**Bon développement Chat 7 ! Tu as toutes les infos nécessaires ! 🎭✨**
