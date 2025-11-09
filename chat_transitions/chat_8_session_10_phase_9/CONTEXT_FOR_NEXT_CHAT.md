# 🚀 Context pour le prochain chat (Chat 9)

**IMPORTANT** : Copie ce prompt au début du Chat 9 pour avoir tout le contexte nécessaire.

---

## 📋 Résumé Rapide

**Chat 8 terminé** : Phase 9 (Fix Chargement GPU CUDA) ✅  
**Chat 9 à faire** : Phase 10 (GUI Discord Control)  
**Version actuelle** : Desktop-Mate v0.9.0-alpha  
**Tests** : 158/158 passent (100%)  
**Status** : GPU CUDA actif et optimisé (6-7x plus rapide)

---

## ✅ Ce qui fonctionne actuellement

### Avatar VRM (Unity)
- ✅ Chargement modèles VRM dynamique
- ✅ Expressions faciales (6 émotions + blendshapes)
- ✅ Transitions fluides (Lerp + SmoothStep)
- ✅ Clignement automatique naturel
- ✅ Mouvements de tête aléatoires

### IA Conversationnelle (Python)
- ✅ ChatEngine avec Zephyr-7B Q5_K_M
- ✅ **GPU CUDA actif** : RTX 4050 (6GB), 35 layers, 33 tok/s
- ✅ EmotionAnalyzer avancé (intensité, confiance, contexte)
- ✅ ConversationMemory (SQLite)
- ✅ Chargement manuel IA (contrôle utilisateur)

### Interfaces Chat
- ✅ GUI Desktop : Onglet "💬 Chat" fonctionnel
- ✅ Discord Bot Kira : Auto-reply + rate limiting + émotions

### IPC & Configuration
- ✅ Communication Python ↔ Unity stable (TCP JSON)
- ✅ Thread-safety complet
- ✅ 3 profils GPU (performance/balanced/low_end)

---

## 🎯 Tâche pour Chat 9

### Phase 10 : GUI Discord Control (2-3 heures)

**Objectif** : Créer une interface dans la GUI Desktop-Mate pour contrôler le bot Discord.

#### Fonctionnalités requises

1. **Nouvel onglet "🤖 Discord"**
   - Position : Après l'onglet "💬 Chat"
   - Design harmonisé avec les autres onglets

2. **Contrôles Bot**
   - Bouton "▶️ Démarrer Bot Discord"
   - Bouton "⏹️ Arrêter Bot Discord"
   - États visuels (enabled/disabled selon statut)

3. **Statut Connexion**
   - Label temps réel : "🔴 Déconnecté" / "🟢 Connecté"
   - Nom du bot (ex: "Kira#1234")
   - Uptime bot (si connecté)

4. **Configuration Discord**
   - QLineEdit pour token Discord (password mode)
   - Liste éditable des salons auto-reply (QListWidget)
   - QSpinBox pour délai rate limiting (secondes)
   - Bouton "💾 Sauvegarder Configuration"

5. **Affichage Messages**
   - QTextEdit read-only pour derniers messages
   - Format : "[HH:MM:SS] [Salon] Utilisateur: message → Émotion"
   - Limiter à 50 derniers messages

6. **Statistiques Discord**
   - Messages reçus (total)
   - Messages traités (auto-reply envoyés)
   - Salons actifs
   - Émotions envoyées Unity

#### Architecture Technique

**Thread-Safety Qt** :
```python
class DiscordSignals(QObject):
    status_changed = Signal(bool, str)  # (connected, bot_name)
    message_received = Signal(str)      # formatted_message
    stats_updated = Signal(dict)        # stats_dict
```

**Intégration Bot Discord** :
```python
# Dans src/discord_bot/bot.py
def get_status():
    """Retourne (is_connected, bot_name, uptime)"""
    pass

def get_stats():
    """Retourne dict avec messages_received, etc."""
    pass
```

**Thread Asyncio séparé** :
```python
class DiscordBotThread(QThread):
    def run(self):
        asyncio.run(bot.start(token))
```

#### Fichiers à modifier

1. **src/gui/app.py** (principal)
   - Ajouter onglet Discord après Chat tab
   - Créer classe DiscordSignals
   - Implémenter UI Discord
   - Méthodes start_discord_bot() / stop_discord_bot()
   - Thread management pour asyncio

2. **src/discord_bot/bot.py** (si nécessaire)
   - Ajouter méthodes get_status() / get_stats()
   - Ajouter callback pour messages (update GUI)
   - Queue thread-safe pour communication

3. **data/config.json**
   - Section discord : token, auto_reply_channels, rate_limit

#### Contraintes

⚠️ **Sécurité** :
- Token Discord **JAMAIS** commit dans Git
- Stocker dans config.json (user home : `~/.desktop-mate/config.json`)
- QLineEdit en mode password (echoMode)

⚠️ **Thread-Safety** :
- Bot Discord tourne dans QThread séparé (asyncio)
- Communication via Signals Qt uniquement
- Pas de manipulation UI depuis thread Discord

⚠️ **Performance** :
- Limiter updates GUI (throttling)
- Max 50 messages affichés
- Stats updates toutes les 5 secondes

---

## 📂 Structure Fichiers

```
C:\Dev\desktop-mate\
├── src/
│   ├── ai/              ✅ Complet (config, model, chat, emotion, memory)
│   ├── discord_bot/     ✅ Bot fonctionnel (bot.py)
│   ├── gui/             🔄 À modifier (app.py → ajouter onglet Discord)
│   └── ipc/             ✅ unity_bridge.py
├── unity/               ✅ Tous scripts Unity fonctionnels
├── data/
│   └── config.json      🔄 À mettre à jour (section discord)
├── models/
│   └── zephyr-7b-beta.Q5_K_M.gguf  ✅ Modèle LLM
└── docs/
    ├── sessions/session_10_ai_chat/  ✅ Phases 1-9 documentées
    └── chat_transitions/chat_8_*/    ✅ Transition Chat 8→9
```

---

## 🧪 Tests à créer

**Fichier** : `tests/test_gui_discord.py` (nouveau)

Tests requis :
1. Création onglet Discord
2. Start/Stop bot (mock)
3. Status updates (signals)
4. Configuration save/load
5. Message display (max 50)
6. Stats updates

**Commande** :
```powershell
.\venv\Scripts\Activate.ps1
pytest tests/test_gui_discord.py -v
```

---

## 📚 Documentation à créer

### Obligatoire

1. **docs/sessions/session_10_ai_chat/phase_10_gui_discord/README.md**
   - Vue d'ensemble Phase 10
   - Architecture technique
   - Guide utilisateur
   - Screenshots (si possible)

2. **docs/sessions/session_10_ai_chat/phase_10_gui_discord/GUI_DISCORD_GUIDE.md**
   - Configuration step-by-step
   - Obtenir token Discord
   - Ajouter salons auto-reply
   - Troubleshooting

3. **Mise à jour docs/INDEX.md**
   - Ajouter Phase 10 dans arborescence Session 10

4. **Mise à jour README.md (4 sections)**
   - Sessions documentées (Session 10 Phase 10)
   - Guides spécifiques (GUI_DISCORD_GUIDE)
   - Changelog (Version 0.10.0-alpha Phase 10)
   - Status final (Phase 10 COMPLÈTE)

5. **Scripts copiés**
   - `docs/sessions/session_10_ai_chat/scripts/app.py` (version finale)
   - `docs/sessions/session_10_ai_chat/scripts/bot.py` (si modifié)

---

## 🚨 Points d'Attention

### 1. Ne PAS oublier le venv

**Toujours activer le venv** dans les commandes :
```powershell
.\venv\Scripts\Activate.ps1 ; python ...
```

### 2. GPU CUDA est actif

Le modèle charge maintenant sur GPU RTX 4050 :
- 35 GPU layers
- 3-4 GB VRAM
- 33 tokens/seconde
- Génération en 2.63s

Pas besoin de recompiler llama-cpp-python !

### 3. Token Discord sécurisé

**CRITICAL** :
```python
# ❌ NE JAMAIS FAIRE
token = "MTIzNDU2Nzg5..."  # Hard-coded

# ✅ FAIRE
token = config.get("discord", {}).get("token", "")
if not token:
    QMessageBox.warning(self, "Token manquant", "...")
```

### 4. Asyncio + Qt

**Pattern recommandé** :
```python
# Thread séparé pour bot Discord
class DiscordBotThread(QThread):
    signals = DiscordSignals()
    
    def run(self):
        try:
            asyncio.run(self.bot.start(self.token))
        except Exception as e:
            self.signals.status_changed.emit(False, f"Erreur: {e}")

# Dans GUI
self.discord_thread = DiscordBotThread(token)
self.discord_thread.signals.status_changed.connect(self.on_discord_status)
self.discord_thread.start()
```

### 5. Documentation complète obligatoire

Avant de dire "Terminé" :
- [ ] Phase 10 README créé
- [ ] GUI_DISCORD_GUIDE créé
- [ ] docs/INDEX.md mis à jour
- [ ] README.md mis à jour (4 sections)
- [ ] Scripts copiés dans docs/.../scripts/
- [ ] Tests passent (160+/160+)

---

## 🎯 Critères de Succès Phase 10

✅ Interface Discord fonctionnelle dans GUI  
✅ Start/Stop bot Discord depuis l'interface  
✅ Statut connexion affiché en temps réel  
✅ Configuration Discord sauvegardée  
✅ Derniers messages affichés (max 50)  
✅ Statistiques Discord mises à jour  
✅ Token sécurisé (pas de commit Git)  
✅ Thread-safety Qt respectée  
✅ Tests créés et passent  
✅ Documentation complète créée  
✅ README.md et INDEX.md mis à jour  

---

## 📝 Commandes Utiles

### Activer venv
```powershell
cd C:\Dev\desktop-mate
.\venv\Scripts\Activate.ps1
```

### Lancer application
```powershell
python main.py
```

### Lancer tests
```powershell
pytest tests/ -v
```

### Vérifier GPU CUDA
```python
import llama_cpp.llama_cpp as lc
print('GPU offload:', lc.llama_supports_gpu_offload())  # True
```

---

## 🔗 Ressources

### Documentation Discord.py
- https://discordpy.readthedocs.io/
- Bot events: on_ready, on_message
- Asyncio integration

### Documentation Qt
- QThread: https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html
- Signals/Slots: https://doc.qt.io/qtforpython-6/PySide6/QtCore/Signal.html

### Documentation Projet
- `docs/sessions/session_10_ai_chat/PLAN_SESSION_10.md` - Plan complet
- `docs/sessions/session_10_ai_chat/CHAT_ENGINE_GUIDE.md` - Guide ChatEngine
- `docs/sessions/session_10_ai_chat/phase_9_cuda_fix/CUDA_INSTALLATION_GUIDE.md` - Guide CUDA

---

## 💡 Tips

1. **Commencer simple** : D'abord statut connexion, puis ajouter fonctionnalités
2. **Tester au fur et à mesure** : Ne pas tout coder d'un coup
3. **Signals Qt** : Toujours pour communication entre threads
4. **Logs** : Ajouter logging.info() pour debug
5. **Documentation** : Écrire au fur et à mesure, pas à la fin

---

## ✅ Checklist Avant de Commencer

- [ ] Lire ce fichier en entier
- [ ] Activer venv : `.\venv\Scripts\Activate.ps1`
- [ ] Vérifier tests passent : `pytest tests/ -v` (158/158)
- [ ] Ouvrir `src/gui/app.py` dans éditeur
- [ ] Consulter `src/discord_bot/bot.py` pour comprendre API
- [ ] Avoir Discord Developer Portal ouvert (token bot)
- [ ] Créer dossier `docs/sessions/session_10_ai_chat/phase_10_gui_discord/`

---

**🚀 Prêt pour la Phase 10 : GUI Discord Control ! 🤖✨**

**Objectif** : Interface complète de contrôle Discord dans Desktop-Mate  
**Durée estimée** : 2-3 heures  
**Difficulté** : Moyenne (Qt + asyncio + thread-safety)  
**Reward** : Interface unifiée Desktop-Mate + Discord Bot 🎊

---

**Bonne chance ! Tu as tout ce qu'il faut pour réussir ! 💪✨**
