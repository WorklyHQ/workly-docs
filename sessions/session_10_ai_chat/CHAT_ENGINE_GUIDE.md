# 💬 Guide Rapide : Chat Engine (Phase 5)

**Utilisation du moteur conversationnel de Kira**

---

## 🚀 Démarrage Rapide

### 1. Initialisation Simple

```python
from src.ai.chat_engine import ChatEngine

# Initialisation (charge config par défaut)
engine = ChatEngine()

# Charger le modèle LLM
engine.model_manager.load_model()

# Prêt à discuter !
```

### 2. Première Conversation

```python
# Envoyer un message
response = engine.chat(
    user_input="Bonjour Kira, présente-toi !",
    user_id="desktop_user",
    source="desktop"
)

# Afficher la réponse
print(f"🤖 Kira : {response.response}")
print(f"🎭 Émotion : {response.emotion}")
print(f"⏱️ Temps : {response.processing_time:.2f}s")
print(f"📝 Tokens : {response.tokens_used}")
```

---

## 🎯 Utilisation Avancée

### Pattern Singleton

```python
from src.ai.chat_engine import get_chat_engine

# Récupère l'instance globale (singleton)
engine = get_chat_engine()

# Même instance partout dans l'application
engine2 = get_chat_engine()
assert engine is engine2  # True
```

### Conversation Multi-Utilisateurs

```python
# Utilisateur 1
response1 = engine.chat(
    user_input="Salut Kira !",
    user_id="user_alice",
    source="desktop"
)

# Utilisateur 2
response2 = engine.chat(
    user_input="Hello Kira !",
    user_id="user_bob",
    source="discord"
)

# Historiques séparés automatiquement !
```

### Gestion Contexte

```python
# Conversation avec contexte
for message in ["Bonjour", "Comment ça va ?", "Parle-moi de toi"]:
    response = engine.chat(message, "user123", "desktop")
    print(f"User: {message}")
    print(f"Kira: {response.response}\n")
    # Historique géré automatiquement !
```

---

## 🎭 Détection Émotions

### Émotions Détectables

Le ChatEngine détecte automatiquement 6 émotions :

| Émotion | Mots-clés Exemples | Blendshape VRM |
|---------|-------------------|----------------|
| `joy` | content, heureux, génial, 😊 | Joy |
| `angry` | énervé, colère, agacé, 😠 | Angry |
| `sorrow` | triste, dommage, désolé, 😢 | Sorrow |
| `surprised` | wow, incroyable, 😲 | Surprised |
| `fun` | drôle, lol, haha, 😂 | Fun |
| `neutral` | ok, bien, alors | Neutral |

### Test Manuel Détecteur

```python
from src.ai.chat_engine import EmotionDetector

detector = EmotionDetector()

# Test
phrases = [
    "Je suis super content ! 😊",
    "C'est énervant...",
    "Tristement..."
]

for phrase in phrases:
    emotion = detector.analyze(phrase)
    print(f"{phrase} → {emotion}")
```

---

## ⚙️ Configuration

### Profils GPU

Le ChatEngine utilise les profils GPU de la config :

```python
from src.ai.config import get_config

config = get_config()

# Voir profil actuel
print(config.gpu_profile)  # "balanced" par défaut

# Changer profil
config.switch_profile("performance")

# Recharger modèle avec nouveau profil
engine.model_manager.unload_model()
engine.model_manager.load_model()
```

### Paramètres Génération

```python
# Modifier config avant génération
config = get_config()
config.temperature = 0.8  # Plus créatif
config.max_tokens = 256   # Réponses plus courtes
config.top_p = 0.95       # Sampling plus large

# La prochaine génération utilisera ces valeurs
response = engine.chat("Raconte-moi une blague !", "user123")
```

---

## 📊 Statistiques

### Stats Globales

```python
stats = engine.get_stats()

# Stats mémoire
print(stats['memory']['total_interactions'])
print(stats['memory']['unique_users'])

# Stats modèle
print(stats['model']['is_loaded'])
print(stats['model']['gpu_info'])

# Config active
print(stats['config']['gpu_profile'])
```

### Stats Utilisateur

```python
# Via la mémoire directement
user_stats = engine.memory.get_user_stats("user123")

print(f"Messages : {user_stats['total_interactions']}")
print(f"Émotions : {user_stats['emotions']}")
```

---

## 🗑️ Gestion Historique

### Effacer Historique Utilisateur

```python
# Effacer tout l'historique d'un utilisateur
deleted = engine.clear_user_history("user123")
print(f"{deleted} interactions supprimées")

# Effacer seulement une source
deleted = engine.clear_user_history("user123", source="discord")
```

### Effacer Tout

```python
# Via la mémoire
engine.memory.clear_all_history()
```

---

## 🔧 Debugging

### Vérifier État

```python
# État du modèle
print(f"Modèle chargé : {engine.model_manager.is_loaded}")

# Info GPU
gpu_info = engine.model_manager.detect_gpu()
if gpu_info and gpu_info.available:
    print(f"GPU : {gpu_info.name}")
    vram_gb = gpu_info.vram_total / (1024**3)
    print(f"VRAM : {vram_gb:.1f} GB")

# Historique
history = engine.memory.get_history("user123", limit=5)
print(f"{len(history)} messages en historique")
```

### Logs

```python
import logging

# Activer logs debug
logging.basicConfig(level=logging.DEBUG)

# Maintenant tous les logs sont visibles
response = engine.chat("Test", "user123")
```

---

## 🚨 Gestion Erreurs

### Modèle Non Chargé

```python
try:
    response = engine.chat("Hello", "user123")
except RuntimeError as e:
    print(f"Erreur : {e}")
    # Charger le modèle
    engine.model_manager.load_model()
    # Réessayer
    response = engine.chat("Hello", "user123")
```

### Génération Échouée

```python
try:
    response = engine.chat("Test très long..." * 1000, "user123")
except RuntimeError as e:
    print(f"Génération échouée : {e}")
    # Réduire taille input ou max_tokens
```

---

## 📝 Format Prompt ChatML

Le ChatEngine utilise le format **ChatML** (Zephyr) :

```
<|system|>
[System prompt personnalisé Kira]
</|system|>

<|user|>
Message historique 1
</|user|>
<|assistant|>
Réponse historique 1
</|assistant|>

<|user|>
Message historique 2
</|user|>
<|assistant|>
Réponse historique 2
</|assistant|>

<|user|>
Message actuel
</|user|>
<|assistant|>
```

Les balises `<|user|>` et `<|system|>` sont utilisées comme **stop sequences** pour arrêter la génération.

---

## 🎯 Cas d'Usage

### 1. Interface Desktop (GUI)

```python
# main.py ou gui.py
from src.ai.chat_engine import get_chat_engine

class ChatWindow:
    def __init__(self):
        self.engine = get_chat_engine()
        self.engine.model_manager.load_model()
    
    def send_message(self, text):
        response = self.engine.chat(
            user_input=text,
            user_id="desktop_user",
            source="desktop"
        )
        
        # Afficher réponse dans GUI
        self.display_message(response.response)
        
        # Mettre à jour expression faciale
        self.update_avatar_emotion(response.emotion)
```

### 2. Bot Discord

```python
# discord_bot/bot.py
from src.ai.chat_engine import get_chat_engine

engine = get_chat_engine()
engine.model_manager.load_model()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    response = engine.chat(
        user_input=message.content,
        user_id=str(message.author.id),
        source="discord"
    )
    
    await message.channel.send(response.response)
```

### 3. Tests Unitaires

```python
# tests/test_my_feature.py
from unittest.mock import Mock
from src.ai.chat_engine import ChatEngine

def test_my_feature():
    # Mock le ModelManager
    mock_manager = Mock()
    mock_manager.is_loaded = True
    mock_manager.generate.return_value = "Bonjour !"
    
    engine = ChatEngine(model_manager=mock_manager)
    
    response = engine.chat("Test", "user123")
    assert response.response == "Bonjour !"
```

---

## ✅ Checklist Déploiement

Avant d'utiliser le ChatEngine en production :

- [ ] **Modèle LLM** : `models/zephyr-7b-beta.Q5_K_M.gguf` présent
- [ ] **Config** : `data/config.json` avec section `"ai"` configurée
- [ ] **Base de données** : `data/chat_history.db` accessible (créée auto)
- [ ] **GPU** : Drivers NVIDIA à jour (si GPU utilisé)
- [ ] **Profil GPU** : Adapté à VRAM disponible (balanced = 3-4GB)
- [ ] **Tests** : `pytest tests/test_chat_engine.py` passe (23/23)

---

## 🔗 Liens Utiles

- **README Session 10** : `docs/sessions/session_10_ai_chat/README.md`
- **Config IA** : `src/ai/config.py`
- **Model Manager** : `src/ai/model_manager.py`
- **Mémoire** : `src/ai/memory.py`
- **Tests** : `tests/test_chat_engine.py`
- **Test Intégration** : `tests/test_integration_phase5.py`

---

**🎉 Kira est prête à discuter ! 💬**
