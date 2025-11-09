# 📋 Contexte pour Chat 8 - Session 10 Phases 6-9

**Pour** : Démarrage Chat 8  
**Depuis** : Chat 7 complété (Phases 3-5)  
**Objectif Chat 8** : Phases 6-9 (Émotions avancées + Discord + GUI)

---

## 🎯 Objectif Chat 8

Créer les interfaces et intégrations pour que Kira puisse :
- 🎭 Analyser émotions avancées avec intensité
- 🤖 Discuter sur Discord avec commandes
- 💬 Discuter via GUI Desktop
- 🎮 Contrôler Discord depuis GUI
- 🔄 Synchroniser émotions → Avatar VRM

---

## ✅ Ce Qui Est Déjà Fait (Chat 6-7)

### Architecture IA Complète

Le système IA de base est **100% fonctionnel** :

```python
# Exemple d'utilisation actuelle
from src.ai.chat_engine import get_chat_engine

# Initialiser
engine = get_chat_engine()
engine.model_manager.load_model()

# Discuter
response = engine.chat("Bonjour Kira !", "user123", "desktop")

# Résultat
print(response.response)  # "Salut ! Content de te voir ! 😊"
print(response.emotion)   # "joy"
```

### 5 Phases Opérationnelles

1. ✅ **Phase 1** : Architecture (dossiers src/ai/, src/discord_bot/, src/auth/)
2. ✅ **Phase 2** : ConversationMemory (SQLite, 11 tests)
3. ✅ **Phase 3** : AIConfig (GPU profiles, 31 tests)
4. ✅ **Phase 4** : ModelManager (GPU detection, 23 tests)
5. ✅ **Phase 5** : ChatEngine + EmotionDetector (23 tests)

**Total** : 97/97 tests passent (100%)

---

## 🔄 Phases à Faire (Chat 8)

### Phase 6 : Emotion Analyzer (~1-2h)

**Pourquoi ?**
- EmotionDetector actuel est basique (mots-clés uniquement)
- Besoin d'analyse contextuelle et intensité

**Quoi créer ?**

**`src/ai/emotion_analyzer.py`** (~300 lignes) :
```python
class EmotionAnalyzer:
    """
    Analyseur émotionnel avancé
    
    Features :
    - Analyse contextuelle (pas juste mots-clés)
    - Intensité émotionnelle (0-100)
    - Historique émotionnel par utilisateur
    - Transitions douces
    - Mapping VRM complet
    """
    
    def analyze(self, text: str, context: List[str]) -> EmotionResult:
        """Analyse texte avec contexte"""
        pass
    
    def get_emotion_history(self, user_id: str) -> List[EmotionResult]:
        """Historique émotionnel utilisateur"""
        pass
    
    def get_vrm_blendshape(self, emotion: str, intensity: float) -> Dict:
        """Mapping émotion → Blendshape VRM"""
        pass
```

**Mapping VRM** :
```python
EMOTION_TO_VRM = {
    'joy': {'blendshape': 'Joy', 'intensity_multiplier': 1.0},
    'angry': {'blendshape': 'Angry', 'intensity_multiplier': 0.8},
    'sorrow': {'blendshape': 'Sorrow', 'intensity_multiplier': 0.9},
    'surprised': {'blendshape': 'Surprised', 'intensity_multiplier': 1.2},
    'fun': {'blendshape': 'Fun', 'intensity_multiplier': 1.1},
    'neutral': {'blendshape': 'Neutral', 'intensity_multiplier': 0.5}
}
```

**Tests** : `tests/test_emotion_analyzer.py` (~20 tests)

---

### Phase 7 : Bot Discord (~2h)

**Pourquoi ?**
- Kira doit pouvoir discuter sur Discord
- Support commandes administrateur

**Quoi créer ?**

**`src/discord_bot/bot.py`** (~400 lignes) :
```python
import discord
from discord.ext import commands
from src.ai.chat_engine import get_chat_engine

bot = commands.Bot(command_prefix='!')
engine = get_chat_engine()

@bot.event
async def on_ready():
    """Bot prêt"""
    print(f'✅ {bot.user} connecté !')

@bot.event
async def on_message(message):
    """Gestion messages"""
    if message.author == bot.user:
        return
    
    # Mentions @Kira
    if bot.user.mentioned_in(message):
        response = engine.chat(
            user_input=message.content,
            user_id=str(message.author.id),
            source="discord"
        )
        await message.channel.send(response.response)
    
    await bot.process_commands(message)

@bot.command(name='chat')
async def chat_command(ctx, *, text):
    """!chat <message> - Discuter avec Kira"""
    response = engine.chat(text, str(ctx.author.id), "discord")
    await ctx.send(response.response)

@bot.command(name='stats')
async def stats_command(ctx):
    """!stats - Statistiques utilisateur"""
    stats = engine.memory.get_user_stats(str(ctx.author.id))
    await ctx.send(f"📊 Messages : {stats['total_interactions']}")

@bot.command(name='clear')
async def clear_command(ctx):
    """!clear - Effacer historique"""
    deleted = engine.clear_user_history(str(ctx.author.id))
    await ctx.send(f"🗑️ {deleted} messages effacés")

# Lancer bot
bot.run(os.getenv('DISCORD_TOKEN'))
```

**Configuration** :
- `.env` : Ajouter `DISCORD_TOKEN`
- `data/config.json` : Compléter section `discord`

**Tests** : `tests/test_discord_bot.py` (~15 tests avec mocks)

---

### Phase 8 : GUI Chat Desktop (~2-3h)

**Pourquoi ?**
- Interface utilisateur pour discuter avec Kira
- Affichage émotions et historique

**Quoi créer ?**

**`src/gui/chat_window.py`** (~500 lignes) :
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from src.ai.chat_engine import get_chat_engine
from src.ipc.unity_bridge import UnityBridge

class ChatWindow(QWidget):
    """Fenêtre chat Desktop-Mate"""
    
    def __init__(self):
        super().__init__()
        self.engine = get_chat_engine()
        self.unity_bridge = UnityBridge()
        self.setup_ui()
    
    def setup_ui(self):
        """Interface"""
        layout = QVBoxLayout()
        
        # Historique
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
        # Input
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        
        # Boutons
        send_btn = QPushButton("Envoyer")
        send_btn.clicked.connect(self.send_message)
        layout.addWidget(send_btn)
        
        self.setLayout(layout)
    
    def send_message(self):
        """Envoyer message"""
        text = self.input_field.text()
        if not text:
            return
        
        # Afficher message utilisateur
        self.append_message("Vous", text, "user")
        
        # Générer réponse
        response = self.engine.chat(text, "desktop_user", "desktop")
        
        # Afficher réponse Kira
        self.append_message("Kira", response.response, response.emotion)
        
        # Mettre à jour avatar VRM
        self.unity_bridge.send_command({
            'action': 'set_expression',
            'expression': response.emotion
        })
        
        self.input_field.clear()
    
    def append_message(self, sender, text, emotion):
        """Ajouter message à l'historique"""
        emotion_icon = self.get_emotion_icon(emotion)
        self.history_text.append(f"{emotion_icon} {sender} : {text}\n")
    
    def get_emotion_icon(self, emotion):
        """Icône émotion"""
        icons = {
            'joy': '😊', 'angry': '😠', 'sorrow': '😢',
            'surprised': '😲', 'fun': '😂', 'neutral': '😐',
            'user': '👤'
        }
        return icons.get(emotion, '💬')
```

**Intégration** :
- Connecter à ChatEngine (déjà fait)
- Envoyer émotions à Unity via IPC (déjà existant)
- Sauvegarder préférences GUI

**Tests** : `tests/test_chat_window.py` (~10 tests)

---

### Phase 9 : GUI Discord Control (~1-2h)

**Pourquoi ?**
- Contrôler bot Discord depuis GUI Desktop-Mate
- Voir stats Discord en temps réel

**Quoi créer ?**

**`src/gui/discord_panel.py`** (~400 lignes) :
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit
import asyncio
from src.discord_bot.bot import bot

class DiscordPanel(QWidget):
    """Panel contrôle Discord"""
    
    def __init__(self):
        super().__init__()
        self.bot_running = False
        self.setup_ui()
    
    def setup_ui(self):
        """Interface"""
        layout = QVBoxLayout()
        
        # Boutons contrôle
        self.start_btn = QPushButton("▶️ Démarrer Bot")
        self.start_btn.clicked.connect(self.start_bot)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏸️ Arrêter Bot")
        self.stop_btn.clicked.connect(self.stop_bot)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # Logs Discord
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)
        
        self.setLayout(layout)
    
    def start_bot(self):
        """Démarrer bot Discord"""
        # Lancer en thread séparé
        asyncio.run(bot.start(os.getenv('DISCORD_TOKEN')))
        self.bot_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.append_log("✅ Bot Discord démarré")
    
    def stop_bot(self):
        """Arrêter bot"""
        asyncio.run(bot.close())
        self.bot_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.append_log("⏸️ Bot Discord arrêté")
    
    def append_log(self, message):
        """Ajouter log"""
        self.logs_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
```

**Tests** : `tests/test_discord_panel.py` (~8 tests)

---

## 📚 Ressources Code Référence

### Kira-Bot (C:\Dev\IA-chatbot\)

Utilise ces fichiers comme **référence** pour les patterns :

**Bot Discord** :
- `bot.py` - Initialisation bot, commandes
- `events/on_message.py` - Gestion messages Discord
- `commands/memory.py` - Commandes gestion mémoire
- `commands/stats.py` - Commandes statistiques

**GUI** :
- `gui/kira_gui.py` - Interface principale
- `gui/enhanced_main_gui.py` - GUI avancée
- `gui/notification_system.py` - Notifications

**Patterns** :
- Threading pour bot Discord en background
- Intégration ChatEngine dans GUI
- Gestion erreurs et fallbacks

---

## 🧪 Tests à Créer

### Phase 6 : Emotion Analyzer

```python
# tests/test_emotion_analyzer.py

def test_analyze_with_context():
    """Test analyse avec contexte"""
    pass

def test_emotion_intensity():
    """Test intensité 0-100"""
    pass

def test_emotion_history():
    """Test historique émotionnel"""
    pass

def test_vrm_mapping():
    """Test mapping vers Blendshapes"""
    pass
```

### Phase 7 : Discord Bot

```python
# tests/test_discord_bot.py

@pytest.mark.asyncio
async def test_on_message():
    """Test gestion message"""
    pass

@pytest.mark.asyncio
async def test_chat_command():
    """Test commande !chat"""
    pass

def test_mentions():
    """Test mentions @Kira"""
    pass
```

### Phase 8-9 : GUI

```python
# tests/test_chat_window.py

def test_send_message():
    """Test envoi message"""
    pass

def test_display_emotion():
    """Test affichage émotion"""
    pass

# tests/test_discord_panel.py

def test_start_bot():
    """Test démarrage bot"""
    pass

def test_stop_bot():
    """Test arrêt bot"""
    pass
```

---

## ⚙️ Configuration Nécessaire

### .env (à compléter)

```env
# Discord
DISCORD_TOKEN=your_token_here
DISCORD_GUILD_ID=your_guild_id
DISCORD_CHANNEL_ID=your_channel_id

# 2FA (Phase 10)
TOTP_SECRET=
```

### data/config.json (à compléter)

```json
{
  "discord": {
    "enabled": false,
    "command_prefix": "!",
    "auto_reply_channels": [],
    "rate_limit_seconds": 3,
    "admin_roles": []
  }
}
```

---

## 🔧 Commandes Utiles

### Activer Venv

```powershell
c:\Dev\desktop-mate\venv\Scripts\activate
```

### Lancer Tests

```powershell
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_emotion_analyzer.py -v
pytest tests/test_discord_bot.py -v

# Avec couverture
pytest tests/ --cov=src/ai --cov-report=html
```

### Lancer Application

```powershell
# GUI Chat (Phase 8)
python -m src.gui.chat_window

# Bot Discord (Phase 7)
python -m src.discord_bot.bot

# Test intégration
python tests/test_integration_phase5.py
```

---

## 🎯 Workflow Recommandé

### Pour Chaque Phase

1. **Comprendre** : Lire plan phase dans PLAN_SESSION_10.md
2. **Référence** : Checker code Kira-Bot correspondant
3. **Coder** : Créer fichiers src/ avec implémentation
4. **Tester** : Créer tests/ avec ~20 tests
5. **Valider** : `pytest tests/test_*.py -v` doit passer
6. **Documenter** : Mettre à jour README session
7. **Copier** : Scripts dans docs/sessions/session_10_ai_chat/scripts/

### Pattern de Développement

```python
# 1. Import depuis modules existants
from src.ai.chat_engine import get_chat_engine
from src.ai.emotion_analyzer import EmotionAnalyzer  # NOUVEAU

# 2. Utiliser singletons
engine = get_chat_engine()
analyzer = EmotionAnalyzer()

# 3. Intégrer progressivement
response = engine.chat("Bonjour", "user123")
emotion_result = analyzer.analyze(response.response, context=[])

# 4. Tester unitairement
assert emotion_result.emotion == 'joy'
assert 0 <= emotion_result.intensity <= 100
```

---

## ✅ Checklist Avant de Commencer

- [ ] Chat 7 complété (tu viens de le faire !)
- [ ] Lire `CURRENT_STATE.md` pour état technique
- [ ] Lire `PLAN_SESSION_10.md` pour plan détaillé
- [ ] Venv activé : `c:\Dev\desktop-mate\venv\Scripts\activate`
- [ ] Tests passent : `pytest tests/ -v` (97/97)
- [ ] GPU détecté : RTX 4050 6GB OK
- [ ] Modèle LLM présent : `models/zephyr-7b-beta.Q5_K_M.gguf`

---

## 🚀 Démarrer Chat 8

1. Copier contenu de `prompt_transition.txt`
2. Ouvrir nouveau chat GitHub Copilot
3. Coller le prompt
4. Commencer **Phase 6 : Emotion Analyzer** !

---

**Prochaine phase** : Phase 6 (Emotion Analyzer) ! 🎭✨

**Durée Chat 8 estimée** : 6-9h (4 phases)

**Let's go ! 🚀**
