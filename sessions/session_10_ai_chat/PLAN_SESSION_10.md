# 📋 Plan Complet - Session 10 : IA Conversationnelle (Kira)

**Date** : Octobre 2025  
**Session** : 10  
**Nom de l'avatar** : **Kira** 

---

## 🎯 Objectif Final

Créer un système d'IA conversationnelle complet pour Desktop-Mate permettant de discuter avec **Kira** via :
- 💬 **Interface GUI** Desktop-Mate (chat local)
- 🤖 **Discord** (messages Discord)
- 🎭 **Expressions émotionnelles automatiques** basées sur les réponses
- 🔒 **Authentification 2FA** pour actions critiques

---

## ✅ Prérequis Validés

- ✅ **Token Discord** : Disponible
- ✅ **Modèle LLM** : `zephyr-7b-beta.Q5_K_M.gguf` (6.8 GB, excellent choix)
- ✅ **Sessions 0-9** : Complétées (VRM, expressions, animations)
- ✅ **IPC Python ↔ Unity** : Fonctionnel

---

## 📦 Architecture Finale

```
desktop-mate/
├── src/
│   ├── ai/                        ← MODULE IA CENTRAL (NOUVEAU)
│   │   ├── __init__.py
│   │   ├── chat_engine.py         ← Moteur de chat unifié
│   │   ├── model_manager.py       ← Gestion LLM + GPU
│   │   ├── memory.py              ← Mémoire conversationnelle SQLite
│   │   ├── emotion_analyzer.py    ← Analyse émotions → Expressions VRM
│   │   └── config.py              ← Configuration IA
│   │
│   ├── discord_bot/               ← INTÉGRATION DISCORD (NOUVEAU)
│   │   ├── __init__.py
│   │   ├── bot.py                 ← Bot Discord (utilise chat_engine)
│   │   ├── events.py              ← Événements Discord (on_message)
│   │   └── voice.py               ← Vocal Discord (préparation future)
│   │
│   ├── auth/                      ← AUTHENTIFICATION 2FA (NOUVEAU)
│   │   ├── __init__.py
│   │   ├── totp_manager.py        ← Gestion TOTP (pyotp)
│   │   └── decorators.py          ← Décorateurs @require_2fa
│   │
│   ├── avatar/                    ← Existant
│   ├── gui/                       ← Existant (à étendre)
│   │   └── app.py                 ← Ajout onglets "Chat" + "Discord"
│   ├── ipc/                       ← Existant
│   └── utils/                     ← Existant
│
├── data/
│   ├── chat_history.db            ← Base SQLite mémoire (NOUVEAU)
│   └── config.json                ← Config étendue
│
├── models/                         ← Modèles LLM (NOUVEAU)
│   └── zephyr-7b-beta.Q5_K_M.gguf ← Copié depuis Kira-Bot
│
├── .env                            ← Variables sensibles (NOUVEAU)
│   ├── DISCORD_TOKEN=...
│   └── AUTH_SECRET=...
│
└── docs/
    └── sessions/
        └── session_10_ai_chat/
            ├── README.md
            ├── PLAN_SESSION_10.md      ← Ce fichier
            ├── ARCHITECTURE_GUIDE.md
            ├── API_REFERENCE.md
            └── scripts/                 ← Scripts finaux
```

---

## 🔄 Flux de Données

### Scénario 1 : Chat via GUI Desktop-Mate

```
Interface Chat (Onglet "💬 Chat")
    ↓ Utilisateur tape un message
ChatEngine.chat(prompt, user_id="desktop_user", source="desktop")
    ↓ Récupère historique (10 derniers messages)
ModelManager.generate(context)
    ↓ Génération LLM (zephyr-7b)
EmotionAnalyzer.analyze(response)
    ↓ Détecte émotion (joy, angry, sorrow, etc.)
Unity IPC → set_expression(emotion)
    ↓ Kira réagit émotionnellement 🎭
GUI → Affiche réponse
```

### Scénario 2 : Chat via Discord

```
Discord Message (@Kira ou mention)
    ↓ Événement on_message
ChatEngine.chat(prompt, user_id=discord_user_id, source="discord")
    ↓ Même moteur que GUI !
ModelManager.generate(context)
    ↓
EmotionAnalyzer.analyze(response)
    ↓
Unity IPC → Kira réagit 🎭
    ↓
Discord → Envoie réponse
```

---

## 📝 Plan d'Implémentation Détaillé

### ✅ Phase 1 : Architecture de Base (1-2h)

**Objectif** : Créer la structure de dossiers et fichiers de base

**Tâches** :
1. ✅ Créer dossier `src/ai/`
2. ✅ Créer dossier `src/discord_bot/`
3. ✅ Créer dossier `src/auth/`
4. ✅ Créer dossier `models/`
5. ✅ Créer fichiers `__init__.py` dans chaque module
6. ✅ Copier `zephyr-7b-beta.Q5_K_M.gguf` dans `models/`
7. ✅ Créer fichier `.env` avec tokens
8. ✅ Mettre à jour `requirements.txt`

**Fichiers à créer** :
```
src/ai/__init__.py
src/discord_bot/__init__.py
src/auth/__init__.py
models/ (dossier)
.env
```

**Commandes** :
```bash
# Copier le modèle
cp C:\Dev\IA-chatbot\models\zephyr-7b-beta.Q5_K_M.gguf C:\Dev\desktop-mate\models\

# Activer venv
venv\Scripts\activate

# Installer nouvelles dépendances
pip install llama-cpp-python pynvml discord.py pyotp python-dotenv
```

**Validation** :
- ✅ Tous les dossiers créés
- ✅ Modèle LLM copié (6.8 GB)
- ✅ Dépendances installées sans erreur

---

### ✅ Phase 2 : Base de Données & Mémoire (1-2h)

**Objectif** : Système de mémoire conversationnelle SQLite

**Tâches** :
1. ✅ Créer `src/ai/memory.py`
2. ✅ Schema SQLite `chat_history`
3. ✅ Fonctions CRUD (save, get_history, clear)
4. ✅ Tests unitaires basiques

**Schema SQLite** :
```sql
-- Table : chat_history
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,           -- Discord ID ou "desktop_user"
    source TEXT NOT NULL,            -- "discord" ou "desktop"
    user_input TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    emotion TEXT,                    -- Émotion détectée (joy, angry, etc.)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_id ON chat_history(user_id);
CREATE INDEX idx_source ON chat_history(source);
CREATE INDEX idx_timestamp ON chat_history(timestamp);
```

**Fonctions `memory.py`** :
```python
class ConversationMemory:
    def __init__(self, db_path: str)
    def save_interaction(user_id, source, prompt, response, emotion)
    def get_history(user_id, limit=10)
    def clear_user_history(user_id)
    def clear_all_history()  # Nécessite 2FA
    def get_stats()  # Stats globales
```

**Tests** :
```python
# tests/test_memory.py
def test_save_interaction()
def test_get_history()
def test_clear_user_history()
```

**Validation** :
- ✅ Base `data/chat_history.db` créée automatiquement
- ✅ Sauvegarde/récupération fonctionnelle
- ✅ Tests passent (pytest)

---

### ✅ Phase 3 : Configuration IA (1h)

**Objectif** : Système de configuration centralisé pour l'IA

**Tâches** :
1. ✅ Créer `src/ai/config.py`
2. ✅ Charger config depuis `data/config.json`
3. ✅ Profils GPU (Performance, Balanced, CPU Fallback)
4. ✅ Paramètres LLM (temperature, top_p, max_tokens)

**Structure `config.json` étendue** :
```json
{
  "avatar": {
    "default_vrm_path": "assets/Mura Mura - Model.vrm",
    "auto_blink": { "enabled": true },
    "auto_head_movement": {
      "enabled": true,
      "max_interval": 7.0,
      "max_angle": 5.0
    },
    "transition_speed": 3.0
  },
  "ai": {
    "model_path": "models/zephyr-7b-beta.Q5_K_M.gguf",
    "context_limit": 10,
    "gpu_profile": "balanced",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 512,
    "system_prompt": "Tu es Kira, un assistant virtuel amical et serviable. Tu réponds en français de manière naturelle et émotionnelle."
  },
  "discord": {
    "auto_reply_enabled": false,
    "auto_reply_channels": []
  }
}
```

**Profils GPU** :
```python
GPU_PROFILES = {
    'performance': {
        'n_gpu_layers': -1,      # Toutes les couches sur GPU
        'n_ctx': 4096,
        'n_batch': 512,
        'n_threads': 6
    },
    'balanced': {
        'n_gpu_layers': 35,      # Équilibré
        'n_ctx': 2048,
        'n_batch': 256,
        'n_threads': 6
    },
    'cpu_fallback': {
        'n_gpu_layers': 0,       # CPU uniquement
        'n_ctx': 2048,
        'n_batch': 128,
        'n_threads': 8
    }
}
```

**Validation** :
- ✅ Config chargée correctement
- ✅ Profils GPU disponibles
- ✅ Paramètres par défaut valides

---

### ✅ Phase 4 : Gestion du Modèle LLM (2-3h)

**Objectif** : Chargement et gestion du modèle LLM avec optimisation GPU

**Tâches** :
1. ✅ Créer `src/ai/model_manager.py`
2. ✅ Détection GPU automatique (pynvml)
3. ✅ Chargement modèle avec profil GPU
4. ✅ Fonction `generate(prompt, context)`
5. ✅ Gestion erreurs (GPU indisponible, VRAM insuffisante)
6. ✅ Tests avec prompts simples

**Classe `ModelManager`** :
```python
class ModelManager:
    def __init__(self, model_path, gpu_profile='balanced')
    def load_model()
    def unload_model()
    def generate(prompt, context=None, temperature=0.7, max_tokens=512)
    def get_gpu_info()
    def switch_profile(new_profile)
```

**Détection GPU** :
```python
def detect_gpu():
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(handle)
        vram = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return {
            'available': True,
            'name': name,
            'vram_total': vram.total,
            'vram_free': vram.free
        }
    except:
        return {'available': False}
```

**Références Kira-Bot** :
- Copier `LLM_PROFILES` depuis `C:\Dev\IA-chatbot\model.py`
- Adapter détection GPU depuis `C:\Dev\IA-chatbot\gpu_utils.py`

**Validation** :
- ✅ Modèle charge sans erreur
- ✅ GPU détecté (si NVIDIA disponible)
- ✅ Génération simple fonctionne : `generate("Bonjour !")`
- ✅ Profils GPU switchables

---

### ✅ Phase 5 : Moteur de Chat Central (2-3h)

**Objectif** : Moteur de chat unifié pour GUI + Discord

**Tâches** :
1. ✅ Créer `src/ai/chat_engine.py`
2. ✅ API `chat(prompt, user_id, source)`
3. ✅ Intégration mémoire + contexte
4. ✅ Construction prompt système
5. ✅ Limitation tokens réponse
6. ✅ Tests conversation multi-tours

**Classe `ChatEngine`** :
```python
class ChatEngine:
    def __init__(self, model_manager, memory, config)
    
    def chat(self, prompt: str, user_id: str = "desktop_user", 
             source: str = "desktop") -> dict:
        """
        Génère une réponse conversationnelle
        
        Returns:
            {
                'response': str,      # Réponse générée
                'emotion': str,       # Émotion détectée
                'tokens_used': int    # Tokens consommés
            }
        """
        # 1. Récupère historique
        history = self.memory.get_history(user_id, limit=self.context_limit)
        
        # 2. Construit contexte
        context = self._build_context(history, prompt)
        
        # 3. Génère réponse
        response = self.model_manager.generate(
            context, 
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # 4. Analyse émotion
        emotion = self._analyze_emotion(response)
        
        # 5. Sauvegarde interaction
        self.memory.save_interaction(user_id, source, prompt, response, emotion)
        
        # 6. Envoie émotion à Unity (si connecté)
        self._send_to_unity(emotion)
        
        return {
            'response': response,
            'emotion': emotion,
            'tokens_used': len(response.split())  # Approximation
        }
```

**Construction du contexte** :
```python
def _build_context(self, history, current_prompt):
    messages = [
        {"role": "system", "content": self.system_prompt}
    ]
    
    # Ajoute historique
    for interaction in history:
        messages.append({"role": "user", "content": interaction['user_input']})
        messages.append({"role": "assistant", "content": interaction['bot_response']})
    
    # Ajoute prompt actuel
    messages.append({"role": "user", "content": current_prompt})
    
    return messages
```

**Validation** :
- ✅ Conversation simple fonctionne
- ✅ Contexte maintenu sur plusieurs tours
- ✅ Émotions détectées
- ✅ Sauvegarde en base

---

### ✅ Phase 6 : Analyse Émotionnelle (1-2h)

**Objectif** : Détecter émotions dans les réponses → Expressions VRM

**Tâches** :
1. ✅ Créer `src/ai/emotion_analyzer.py`
2. ✅ Analyse par mots-clés (simple et efficace)
3. ✅ Mappage émotion → expression VRM
4. ✅ Tests avec phrases types

**Classe `EmotionAnalyzer`** :
```python
class EmotionAnalyzer:
    EMOTION_KEYWORDS = {
        'joy': [
            'heureux', 'content', 'super', 'génial', 'excellent', 'parfait',
            'cool', 'top', '😊', '😄', '😁', '🎉', '✨', 'joie'
        ],
        'angry': [
            'énervé', 'colère', 'furieux', 'agacé', 'irrité', 
            '😠', '😡', 'grrr', 'rage'
        ],
        'sorrow': [
            'triste', 'désolé', 'dommage', 'malheureusement', 'hélas',
            '😢', '😭', '😔', 'peine', 'chagrin'
        ],
        'surprised': [
            'wow', 'incroyable', 'surprenant', 'étonnant', 'ooh',
            '😲', '😮', '🤯', 'waouh', 'oh'
        ],
        'fun': [
            'drôle', 'lol', 'mdr', 'hilarant', 'rigolo', 
            '😆', '😂', '🤣', 'haha', 'hehe'
        ]
    }
    
    def analyze(self, text: str) -> str:
        """
        Analyse le texte et retourne l'émotion dominante
        
        Returns:
            'joy', 'angry', 'sorrow', 'surprised', 'fun', ou 'neutral'
        """
        text_lower = text.lower()
        
        # Compte les occurrences par émotion
        scores = {}
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[emotion] = score
        
        # Retourne émotion dominante ou neutral
        if not scores:
            return 'neutral'
        
        return max(scores, key=scores.get)
```

**Tests** :
```python
def test_emotion_joy():
    analyzer = EmotionAnalyzer()
    assert analyzer.analyze("Je suis super content ! 😊") == 'joy'

def test_emotion_sorrow():
    assert analyzer.analyze("C'est vraiment triste 😢") == 'sorrow'
```

**Validation** :
- ✅ Émotions détectées correctement
- ✅ Tests passent
- ✅ Intégration avec `ChatEngine`

---

### ✅ Phase 7 : Bot Discord (2h)

**Objectif** : Intégration Discord utilisant `ChatEngine`

**Tâches** :
1. ✅ Créer `src/discord_bot/bot.py`
2. ✅ Créer `src/discord_bot/events.py`
3. ✅ Événement `on_message` avec ChatEngine
4. ✅ Auto-reply dans canaux configurés
5. ✅ Commande `!ping` (test)
6. ✅ Tests Discord (bot connecté)

**Classe `KiraBot`** :
```python
# src/discord_bot/bot.py
from discord.ext import commands
from src.ai.chat_engine import ChatEngine

class KiraBot(commands.Bot):
    def __init__(self, chat_engine: ChatEngine, auto_reply_channels: list):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)
        
        self.chat_engine = chat_engine
        self.auto_reply_channels = auto_reply_channels
    
    async def on_ready(self):
        print(f"✅ Kira connectée : {self.user}")
    
    async def on_message(self, message):
        # Ignore les bots
        if message.author.bot:
            return
        
        # Auto-reply dans certains canaux
        should_reply = (
            self.user.mentioned_in(message) or 
            message.channel.id in self.auto_reply_channels
        )
        
        if should_reply:
            # Nettoie le prompt (enlève la mention)
            prompt = message.content.replace(f"<@{self.user.id}>", "").strip()
            
            # Génère réponse via ChatEngine
            result = self.chat_engine.chat(
                prompt=prompt,
                user_id=str(message.author.id),
                source="discord"
            )
            
            # Envoie réponse
            await message.channel.send(result['response'])
        
        # Traite les commandes
        await self.process_commands(message)

# Commandes basiques
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong !")
```

**Fichier `.env`** :
```env
DISCORD_TOKEN=your_discord_token_here
AUTH_SECRET=your_2fa_secret_here
```

**Validation** :
- ✅ Bot se connecte à Discord
- ✅ Répond aux mentions
- ✅ Auto-reply dans canaux configurés
- ✅ Commande `!ping` fonctionne
- ✅ Kira réagit émotionnellement (Unity)

---

### ✅ Phase 8 : Interface Chat GUI (2-3h)

**Objectif** : Onglet "💬 Chat" dans Desktop-Mate

**Tâches** :
1. ✅ Ajouter onglet "Chat" dans `src/gui/app.py`
2. ✅ Zone historique (QTextEdit scrollable)
3. ✅ Input utilisateur (QLineEdit)
4. ✅ Bouton "Envoyer" (ou Enter)
5. ✅ Indicateur "Kira est en train d'écrire..."
6. ✅ Affichage émotions détectées
7. ✅ Formatage bulles de chat (utilisateur vs Kira)

**Interface Chat** :
```python
class ChatTab(QWidget):
    def __init__(self, chat_engine):
        super().__init__()
        self.chat_engine = chat_engine
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Historique
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)
        
        # Input
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Message à Kira...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)
        
        self.send_button = QPushButton("📤 Envoyer")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
    
    def send_message(self):
        prompt = self.chat_input.text().strip()
        if not prompt:
            return
        
        # Affiche message utilisateur
        self.append_message("Vous", prompt, is_user=True)
        self.chat_input.clear()
        
        # Indicateur "typing"
        self.show_typing_indicator()
        
        # Génère réponse (dans thread pour ne pas bloquer UI)
        QTimer.singleShot(100, lambda: self._generate_response(prompt))
    
    def _generate_response(self, prompt):
        result = self.chat_engine.chat(prompt, user_id="desktop_user", source="desktop")
        
        # Cache indicateur
        self.hide_typing_indicator()
        
        # Affiche réponse Kira
        emotion_emoji = self.get_emotion_emoji(result['emotion'])
        self.append_message(
            f"Kira {emotion_emoji}", 
            result['response'], 
            is_user=False
        )
    
    def append_message(self, sender, text, is_user=False):
        color = "#0078d4" if is_user else "#28a745"
        self.chat_history.append(
            f"<p><b style='color:{color}'>{sender}:</b> {text}</p>"
        )
```

**Formatage Bulles** :
```
┌──────────────────────────────────────────┐
│ Vous: Bonjour Kira !                     │
│                                          │
│ Kira 😊: Salut ! Comment puis-je t'aider│
│          aujourd'hui ?                   │
│                                          │
│ Vous: Raconte-moi une blague             │
│                                          │
│ Kira 😆: Pourquoi les plongeurs plongent │
│          toujours en arrière ? Parce que │
│          sinon ils tombent dans le       │
│          bateau ! 😄                     │
└──────────────────────────────────────────┘
```

**Validation** :
- ✅ Interface s'affiche correctement
- ✅ Messages envoyés et reçus
- ✅ Historique scrollable
- ✅ Émotions affichées
- ✅ Kira réagit dans Unity

---

### ✅ Phase 9 : Onglet Discord GUI (1-2h)

**Objectif** : Contrôle du bot Discord depuis GUI

**Tâches** :
1. ✅ Ajouter onglet "🤖 Discord" dans `src/gui/app.py`
2. ✅ Status bot (Connecté / Déconnecté)
3. ✅ Boutons Start/Stop Discord bot
4. ✅ Toggle auto-reply
5. ✅ Liste canaux auto-reply

**Interface Discord** :
```python
class DiscordTab(QWidget):
    def __init__(self, bot_manager):
        super().__init__()
        self.bot_manager = bot_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Status
        self.status_label = QLabel("Status: Déconnecté")
        layout.addWidget(self.status_label)
        
        # Boutons
        self.start_button = QPushButton("▶️ Démarrer Discord Bot")
        self.start_button.clicked.connect(self.start_bot)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹️ Arrêter Discord Bot")
        self.stop_button.clicked.connect(self.stop_bot)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        # Auto-reply
        self.auto_reply_checkbox = QCheckBox("Auto-reply activé")
        layout.addWidget(self.auto_reply_checkbox)
    
    def start_bot(self):
        self.bot_manager.start()
        self.status_label.setText("Status: ✅ Connecté")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
    
    def stop_bot(self):
        self.bot_manager.stop()
        self.status_label.setText("Status: ❌ Déconnecté")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
```

**Validation** :
- ✅ Bot démarre/s'arrête depuis GUI
- ✅ Status affiché correctement
- ✅ Auto-reply configurable

---

### ✅ Phase 10 : Système 2FA (1-2h)

**Objectif** : Authentification 2FA pour actions critiques

**Tâches** :
1. ✅ Créer `src/auth/totp_manager.py`
2. ✅ Génération/validation codes TOTP
3. ✅ Créer `src/auth/decorators.py` (@require_2fa)
4. ✅ Popup GUI pour code 2FA
5. ✅ Protéger "Effacer historique complet"
6. ✅ Configuration Google Authenticator

**Classe `TOTPManager`** :
```python
import pyotp
import os
from dotenv import load_dotenv

class TOTPManager:
    def __init__(self):
        load_dotenv()
        self.secret = os.getenv("AUTH_SECRET")
        if not self.secret:
            # Génère nouveau secret
            self.secret = pyotp.random_base32()
            print(f"⚠️ Nouveau secret 2FA généré : {self.secret}")
            print("⚠️ Ajoutez-le à votre fichier .env : AUTH_SECRET={self.secret}")
        
        self.totp = pyotp.TOTP(self.secret)
    
    def generate_code(self) -> str:
        """Génère un code 2FA (pour debug/test)"""
        return self.totp.now()
    
    def verify_code(self, code: str) -> bool:
        """Vérifie un code 2FA"""
        return self.totp.verify(code, valid_window=1)
    
    def get_provisioning_uri(self, name: str = "Desktop-Mate") -> str:
        """URI pour Google Authenticator"""
        return self.totp.provisioning_uri(
            name=name,
            issuer_name="Desktop-Mate (Kira)"
        )
```

**Popup 2FA GUI** :
```python
def show_2fa_dialog(parent) -> str:
    """Affiche popup pour entrer code 2FA"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("🔒 Authentification 2FA")
    
    layout = QVBoxLayout(dialog)
    
    label = QLabel("Entrez votre code 2FA (Google Authenticator) :")
    layout.addWidget(label)
    
    code_input = QLineEdit()
    code_input.setPlaceholderText("123456")
    code_input.setMaxLength(6)
    layout.addWidget(code_input)
    
    buttons = QHBoxLayout()
    ok_button = QPushButton("✅ Valider")
    ok_button.clicked.connect(dialog.accept)
    cancel_button = QPushButton("❌ Annuler")
    cancel_button.clicked.connect(dialog.reject)
    buttons.addWidget(ok_button)
    buttons.addWidget(cancel_button)
    layout.addLayout(buttons)
    
    if dialog.exec() == QDialog.Accepted:
        return code_input.text()
    return None
```

**Protection actions critiques** :
```python
def clear_all_history_with_2fa(self):
    """Efface TOUT l'historique (nécessite 2FA)"""
    code = show_2fa_dialog(self)
    
    if code is None:
        return  # Annulé
    
    if self.totp_manager.verify_code(code):
        self.memory.clear_all_history()
        show_success("Historique complet effacé !")
    else:
        show_error("Code 2FA invalide !")
```

**Configuration Google Authenticator** :
```python
# Script one-time pour configurer 2FA
totp_manager = TOTPManager()
uri = totp_manager.get_provisioning_uri()

import qrcode
qr = qrcode.make(uri)
qr.save("qr_code_2fa.png")
print("Scannez qr_code_2fa.png avec Google Authenticator")
```

**Validation** :
- ✅ Code 2FA généré/vérifié
- ✅ Google Authenticator configuré
- ✅ Actions protégées fonctionnent
- ✅ Codes invalides rejetés

---

### ✅ Phase 11 : Intégration Unity (1h)

**Objectif** : Connexion émotions → Expressions VRM

**Tâches** :
1. ✅ Dans `ChatEngine`, appeler `unity_bridge.set_expression()`
2. ✅ Mapping émotion → expression VRM
3. ✅ Gérer cas Unity non connecté
4. ✅ Tests avec Unity en cours d'exécution

**Mapping Émotions** :
```python
EMOTION_TO_VRM = {
    'joy': ('joy', 80),
    'angry': ('angry', 75),
    'sorrow': ('sorrow', 70),
    'surprised': ('surprised', 85),
    'fun': ('fun', 90),
    'neutral': ('neutral', 0)
}

def _send_to_unity(self, emotion: str):
    """Envoie expression à Unity"""
    if not unity_bridge.is_connected():
        return
    
    expression, intensity = EMOTION_TO_VRM.get(emotion, ('neutral', 0))
    unity_bridge.set_expression(expression, intensity)
```

**Validation** :
- ✅ Kira réagit émotionnellement pendant conversation
- ✅ Pas d'erreur si Unity déconnecté
- ✅ Expressions correctement mappées

---

### ✅ Phase 12 : Configuration & Optimisation (1-2h)

**Objectif** : Interface de configuration complète

**Tâches** :
1. ✅ Étendre onglet "Options"
2. ✅ Sélecteur modèle LLM
3. ✅ Slider contexte (5-30 messages)
4. ✅ Sélecteur profil GPU
5. ✅ Slider temperature (0.1-1.5)
6. ✅ Bouton "Générer QR Code 2FA"

**Interface Options Étendue** :
```
┌──────────────────────────────────────────┐
│ ⚙️ Options                                │
├──────────────────────────────────────────┤
│                                          │
│ 🤖 Configuration IA                      │
│ ├─ Modèle LLM: [zephyr-7b ▼]            │
│ ├─ Profil GPU: [Balanced  ▼]            │
│ ├─ Contexte: [10] messages              │
│ └─ Temperature: [0.7]                    │
│                                          │
│ 🎭 Avatar                                │
│ └─ Vitesse transition: [3.0]             │
│                                          │
│ 🔒 Sécurité                              │
│ ├─ Secret 2FA: [••••••••••]             │
│ └─ [📱 Générer QR Code]                  │
│                                          │
│ [💾 Sauvegarder] [🔄 Réinitialiser]      │
└──────────────────────────────────────────┘
```

**Validation** :
- ✅ Tous les paramètres modifiables
- ✅ Sauvegarde dans config.json
- ✅ Changements appliqués en temps réel

---

### ✅ Phase 13 : Tests & Validation (2-3h)

**Objectif** : Tests complets du système

**Tests Unitaires** :
```python
# tests/test_memory.py
def test_save_and_retrieve()
def test_clear_user_history()

# tests/test_chat_engine.py
def test_simple_chat()
def test_context_maintained()
def test_emotion_detection()

# tests/test_model_manager.py
def test_load_model()
def test_gpu_detection()

# tests/test_2fa.py
def test_generate_code()
def test_verify_valid_code()
def test_verify_invalid_code()
```

**Tests d'Intégration** :
1. ✅ Conversation GUI → Unity réagit
2. ✅ Conversation Discord → Unity réagit
3. ✅ Mémoire partagée GUI + Discord
4. ✅ 2FA bloque actions non autorisées
5. ✅ Changement profil GPU fonctionne

**Validation** :
- ✅ Tous les tests passent (pytest)
- ✅ Pas d'erreurs console
- ✅ Performance acceptable (< 3s par réponse)

---

### ✅ Phase 14 : Documentation (2h)

**Objectif** : Documentation complète Session 10

**Fichiers à créer** :
```
docs/sessions/session_10_ai_chat/
├── README.md                    ← Vue d'ensemble
├── PLAN_SESSION_10.md          ← Ce fichier
├── ARCHITECTURE_GUIDE.md       ← Architecture technique
├── API_REFERENCE.md            ← Documentation API
├── USER_GUIDE.md               ← Guide utilisateur
├── TROUBLESHOOTING.md          ← Dépannage
└── scripts/                     ← Scripts finaux
    ├── chat_engine.py
    ├── model_manager.py
    ├── memory.py
    ├── emotion_analyzer.py
    ├── bot.py
    ├── totp_manager.py
    └── app.py (extrait onglets Chat/Discord)
```

**Mise à jour fichiers globaux** :
- ✅ `docs/INDEX.md` → Ajouter Session 10
- ✅ `docs/README.md` → Ajouter fonctionnalités IA
- ✅ `README.md` (racine) → Sections (Sessions, Changelog, Status)
- ✅ `docs/chat_transitions/chat_6_session_10/CURRENT_STATE.md`

**Validation** :
- ✅ Toute la documentation créée
- ✅ INDEX.md à jour
- ✅ README.md racine mis à jour (4 sections)
- ✅ Scripts copiés dans `scripts/`

---

## 📦 Dépendances Complètes

**Fichier `requirements.txt`** :
```txt
# Interface graphique
PySide6>=6.5.0

# Monitoring système
psutil>=5.9.0

# IA & LLM (NOUVEAU)
llama-cpp-python>=0.2.0
pynvml>=11.5.0

# Discord (NOUVEAU)
discord.py>=2.3.0

# Authentification (NOUVEAU)
pyotp>=2.8.0
python-dotenv>=1.0.0
qrcode>=7.4.2

# Tests
pytest>=7.0.0
```

**Installation** :
```bash
# Activer venv
venv\Scripts\activate

# Installer toutes les dépendances
pip install -r requirements.txt
```

---

## ⏱️ Estimation Temps Total

| Phase | Temps | Status |
|-------|-------|--------|
| Phase 1 : Architecture | 30min | ✅ |
| Phase 2 : Mémoire | 1h | ✅ |
| Phase 3 : Config IA | 45min | ✅ |
| Phase 4 : Model Manager | 1.5h | ✅ |
| Phase 5 : Chat Engine | 2h | ✅ |
| Phase 6 : Emotion Analyzer | 1h | ✅ |
| Phase 7 : Bot Discord | 1.5h | ✅ |
| Phase 8 : GUI Chat | 1.5h | ✅ |
| Phase 9 : CUDA Fix | 3-4h | ✅ |
| Phase 10 : GUI Discord + Menu Options | 2-3h | ✅ |
| **TOTAL** | **~15-17h** | **100%** 🎊 |

**Session 10 TERMINÉE !** ✅

---

## 🎯 Résultat Final Session 10

**Fonctionnalités complètes** :
- ✅ Kira discute via **GUI Desktop-Mate**
- ✅ Kira discute via **Discord**
- ✅ **Mémoire conversationnelle unifiée** (GUI + Discord)
- ✅ **Expressions émotionnelles automatiques** (VRM réagit)
- ✅ **Optimisation GPU automatique** (profils adaptatifs)
- ✅ **Authentification 2FA** (actions critiques protégées)
- ✅ **Configuration complète** (modèle, GPU, temperature, etc.)
- ✅ **Architecture propre et maintenable**
- ✅ **Documentation exhaustive**

**Interface complète** :
- Onglet "💬 Chat" → Chat local avec Kira
- Onglet "🤖 Discord" → Contrôle bot Discord
- Onglet "⚙️ Options" → Configuration IA complète
- Onglets existants (Connexion, Expressions, Animations)

**Préparation future** :
- Structure prête pour vocal Discord (Phase 7 - `voice.py`)
- Extensibilité recherche web (Session future)
- Système de plugins IA (Session future)

---

## 📚 Références Kira-Bot

**Fichiers à consulter** :
- `C:\Dev\IA-chatbot\model.py` → Gestion LLM + profils GPU
- `C:\Dev\IA-chatbot\memory.py` → Mémoire conversationnelle
- `C:\Dev\IA-chatbot\bot.py` → Bot Discord
- `C:\Dev\IA-chatbot\config.py` → Configuration
- `C:\Dev\IA-chatbot\tools\gpu_optimizer.py` → Optimisation GPU
- `C:\Dev\IA-chatbot\auth_decorators.py` → Système 2FA

**Code à copier/adapter** :
- ✅ Profils LLM (`LLM_PROFILES`)
- ✅ Détection GPU (pynvml)
- ✅ Fonctions mémoire SQLite
- ✅ Système TOTP

**Code à NE PAS copier** :
- ❌ Commandes Discord (`commands/`)
- ❌ Recherche web (pas prioritaire)
- ❌ GUI multiple (on a notre interface)
- ❌ Configuration fragmentée (JSON multiples)

---

## 💡 Notes Importantes

### Modèle LLM Choisi

**`zephyr-7b-beta.Q5_K_M.gguf`** :
- ✅ **Taille** : 6.8 GB (parfait pour RTX 4050 6GB VRAM)
- ✅ **Qualité** : Excellent modèle 7B (Mistral fine-tuné)
- ✅ **Quantification** : Q5_K_M (bon équilibre qualité/taille)
- ✅ **Performance** : ~20-30 tokens/sec sur RTX 4050

**Recommandation** : Garde Zephyr-7B, excellent choix !

### GPU NVIDIA

**Détection automatique** :
- Si GPU NVIDIA détecté → Profil "balanced" par défaut
- Sinon → Profil "cpu_fallback"

**Profils GPU** :
- **Performance** : Toutes couches GPU (-1), 4096 ctx → Max vitesse
- **Balanced** : 35 couches GPU, 2048 ctx → Équilibré (défaut)
- **CPU Fallback** : 0 couches GPU → Secours si VRAM insuffisante

### 2FA Configuration

**Première utilisation** :
1. Lance Desktop-Mate
2. Va dans Options → Sécurité
3. Clique "Générer QR Code 2FA"
4. Scanne avec Google Authenticator
5. Teste avec une action protégée

**Secret 2FA** :
- Stocké dans `.env` (pas versionné)
- Format Base32 (pyotp.random_base32())
- À conserver précieusement !

---

## 🚀 Prochaines Étapes (Chat 6)

**Session 10 préparation** :
1. ✅ Lire ce plan complet
2. ✅ Comprendre l'architecture
3. ✅ Préparer environnement (venv activé)
4. ✅ Créer dossier `models/`
5. ✅ Copier modèle LLM

**Puis on démarre Phase 1** : Architecture de Base !

---

**Prêt à transformer Desktop-Mate en véritable assistante IA ? 🎭🤖✨**
