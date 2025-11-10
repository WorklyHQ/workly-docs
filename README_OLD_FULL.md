# Workly

🎭 **Interactive VRM Desktop Companion** - Une application hybride Unity + Python qui donne vie à votre avatar VRM sur votre bureau !

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Unity 2022.3+](https://img.shields.io/badge/unity-2022.3+-black.svg)](https://unity.com/)
[![Status](https://img.shields.io/badge/status-MVP%20Complete-success.svg)](https://github.com/WorklyHQ/workly-desktop)
[![License](https://img.shields.io/badge/license-MIT--NC-orange.svg)](LICENSE)

## 📋 Description

Workly est une application qui permet d'afficher un avatar VRM interactif sur votre bureau Windows. L'avatar peut :
- 🎤 Synchroniser ses lèvres avec sa propre voix (lip-sync)
- 😊 Afficher des expressions et émotions
- 🎮 Réagir à des commandes et interactions

**Objectif final :** 🤖 Connecter l'avatar à une **IA conversationnelle (chatbot)** pour créer un assistant virtuel qui peut **parler, réagir émotionnellement et se déplacer librement** sur le bureau. L'avatar deviendra un véritable compagnon interactif intelligent !

## ⚡ Quick Start

```powershell
# 1. Cloner le repo
git clone https://github.com/WorklyHQ/workly-desktop.git
cd workly-desktop

# 2. Setup Python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Lancer Unity (ouvrir unity/DesktopMateUnity/ et cliquer Play)

# 4. Lancer Python
python main.py
# → Cliquer "Connect to Unity" puis "Load VRM Model"
```

📖 **[Documentation complète](docs/START_HERE.md)**

## 🏗️ Architecture

Le projet utilise une **architecture hybride** pour combiner les forces de Unity et Python :

### Unity (Rendu 3D)
- Chargement et rendu des modèles VRM
- Gestion des animations et blendshapes
- Physique et effets visuels avancés

### Python (Logique & UI)
- Interface de contrôle (PySide6/Qt)
- Capture audio et traitement
- Communication IPC avec Unity
- Gestion de configuration

```
┌─────────────────┐         ┌──────────────────┐
│   Python App    │◄───────►│   Unity Engine   │
│  (PySide6 GUI)  │  Socket │  (VRM Renderer)  │
│  • Audio Input  │   IPC   │  • 3D Display    │
│  • Controls     │         │  • Animations    │
└─────────────────┘         └──────────────────┘
```

## 📁 Structure du Projet

```
workly-desktop/
├── main.py                 # Point d'entrée de l'application Python
├── requirements.txt        # Dépendances Python
├── README.md              # Ce fichier
├── LICENSE                # Licence MIT
│
├── src/                   # Code source Python
│   ├── gui/              # Interface utilisateur Qt
│   │   └── app.py        # Application principale avec MainWindow
│   ├── ipc/              # Communication Unity ↔ Python
│   │   └── unity_bridge.py  # Client socket TCP
│   ├── audio/            # Capture et traitement audio (à venir)
│   ├── avatar/           # Gestion avatar et VRM (à venir)
│   └── utils/            # Utilitaires
│       ├── config.py     # Gestion configuration JSON
│       └── logger.py     # Système de logs
│
├── unity/                 # Projet Unity
│   ├── PythonBridge.cs   # Template script IPC
│   └── DesktopMateUnity/ # Projet Unity 2022.3 LTS (URP)
│       └── Assets/
│           ├── Scripts/
│           │   ├── IPC/PythonBridge.cs  # Serveur socket
│           │   └── VRMLoader.cs         # Chargeur VRM
│           ├── Models/
│           │   └── Mura Mura - Model.vrm
│           ├── VRM/              # Package UniVRM
│           ├── UniGLTF/          # Dépendance UniVRM
│           └── VRMShaders/       # Shaders VRM
│
├── assets/               # Assets partagés
│   └── Mura Mura - Model.vrm
│
├── web/                  # 🌐 Site web officiel Kira
│   ├── index.html        # Page d'accueil
│   ├── pages/            # Pages (about, api, terms, privacy)
│   ├── assets/           # CSS, JS, images
│   └── README.md         # Documentation du site web
│
├── tests/                # Tests unitaires (8 tests)
├── docs/                 # Documentation détaillée
│   ├── START_HERE.md    # 👈 Commence ici !
│   ├── INDEX.md         # Navigation rapide
│   ├── README.md        # Vue d'ensemble
│   ├── sessions/session_0_git_configuration/ # ⚙️ Configuration Git Unity
│   ├── sessions/session_1_setup/ # Setup Python + GUI
│   ├── sessions/session_2_unity_installation/
│   ├── sessions/session_3_univrm_installation/
│   ├── sessions/session_4_python_unity_connection/
│   └── sessions/session_5_vrm_loading/  # ✅ Dernière session complète
│
└── .github/              # CI/CD et workflows
    ├── workflows/
    └── instructions/
        └── copilot-instructions.instructions.md  # Instructions IA (inclut système anti-oubli doc)
```

**📋 Système de Documentation Anti-Oubli :**
- Checklist systématique pour l'IA
- Prompt système pour maintenir la doc à jour
- Template PR avec vérifications doc obligatoires
- `.github/instructions/copilot-instructions.instructions.md` - Instructions Copilot (applyTo: `**`)

**Système 3 niveaux garantissant la synchronisation documentation ↔ code.**

## 🚀 Installation

### Prérequis

- **Python 3.10+** ✅ (Installé : 3.10.9)
- **Unity 2022.3 LTS** ou plus récent
- **Windows 10/11** (support Linux prévu plus tard)

### Étape 1 : Cloner le repository

```powershell
git clone https://github.com/WorklyHQ/workly-desktop.git
cd workly-desktop
```

### Étape 2 : Créer l'environnement virtuel Python

```powershell
# Créer le venv
python -m venv venv

# Activer le venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 3 : Configurer Unity

1. Ouvrir **Unity Hub**
2. Installer **Unity 2022.3 LTS**
3. Ouvrir le projet existant dans `unity/DesktopMateUnity/`
4. **UniVRM est déjà installé** ✅
5. **PythonBridge.cs est déjà configuré** ✅
6. **VRMLoader.cs est déjà créé** ✅

> 💡 **Le projet Unity est déjà prêt !** Pas besoin de configuration supplémentaire.

### Étape 4 : Lancer l'application

**Terminal 1 - Unity :**
1. Ouvrir le projet Unity dans `unity/DesktopMateUnity/`
2. Cliquer sur **Play** ▶️
3. Vérifier que la console affiche : `[PythonBridge] Serveur démarré avec succès`

**Terminal 2 - Python :**
```powershell
# Activer le venv
.\venv\Scripts\Activate.ps1

# Lancer l'application Python
python main.py
```

**Dans l'interface Python :**
1. Cliquer sur **"Connect to Unity"**
2. Attendre le message de succès
3. Cliquer sur **"Load VRM Model"**
4. Sélectionner `assets/Mura Mura - Model.vrm`
5. **Ton avatar apparaît dans Unity !** 🎭✨

## 🎯 Roadmap

### Phase 1 : MVP 
- [x] Structure du projet Python
- [x] Interface Qt de base
- [x] Communication IPC Unity ↔ Python (socket TCP)
- [x] Installation Unity 2022.3 LTS
- [x] Installation UniVRM
- [x] Script PythonBridge.cs (serveur socket Unity)
- [x] Chargement d'un modèle VRM dans Unity
- [x] **Affichage de l'avatar 3D fonctionnel !** 🎭

### Phase 2 : Expressions & Animations 😊 **
- [x] **Session 6** : Expressions faciales (blendshapes) 
  - VRMBlendshapeController.cs v1.6 avec thread-safety
  - Interface GUI avec sliders (joy, angry, sorrow, surprised, fun)
  - Contrôle précis 0-100% pour chaque expression
  - Bouton "Reset All Expressions"
  - Documentation complète
- [x] **Session 7** : Animations fluides 
  - VRMBlendshapeController.cs v2.0 avec Lerp interpolation
  - Transitions smooth entre expressions
  - Slider de vitesse ajustable (1.0-10.0)
  - Interface française complète avec icône
  - Système de modèle VRM par défaut
  - Chargement/déchargement dynamique
  - Documentation complète (900+ lignes de guides techniques)
- [x] **Session 8** : Clignement automatique 
  - VRMAutoBlinkController.cs avec coroutines Unity
  - Animation SmoothStep (courbes de Hermite)
  - Timing naturel (2-5s entre clignements, 160ms par cycle)
  - Checkbox "Auto Blink" dans l'interface
  - Sauvegarde configuration
  - Documentation technique massive (TECHNICAL_GUIDE.md 900+ lignes)
  - Guide résolution problèmes (TROUBLESHOOTING.md avec 5 bugs résolus)
- [x] **Session 9** : Mouvements de Tête + Réorganisation Interface 
  - VRMHeadMovementController.cs avec Coroutines + SmoothStep
  - Mouvements naturels aléatoires (yaw/pitch)
  - Contrôle fréquence (3-10s) et amplitude (2-10°)
  - Interface réorganisée en 3 onglets (Expressions, Animations, Options)
  - 3 boutons reset contextuels
  - Résolution conflit VRMAutoBlinkController
  - Gestion déconnexion Unity (reset état VRM)
  - Documentation complète (4 guides techniques + scripts)

### Phase 3 : Intégration IA Conversationnelle 🤖 
- [x] **Session 10** : IA Conversationnelle Complète ✅ 🎊
  - ✅ Architecture IA modulaire (src/ai/, ChatEngine, ModelManager, EmotionAnalyzer)
  - ✅ Mémoire conversationnelle SQLite (multi-utilisateurs, multi-sources)
  - ✅ Intégration LLM local (Zephyr-7B avec llama-cpp-python)
  - ✅ Détection GPU automatique (CUDA sur RTX 4050, accélération 6-7x)
  - ✅ Bot Discord opérationnel (commandes !chat, !stats, !clear, auto-reply)
  - ✅ GUI Chat Desktop (PySide6, historique, markdown, émotions temps réel)
  - ✅ GUI Discord Control (Start/Stop, statut, menu Options sécurisé)
  - ✅ 171/171 tests unitaires (100%)
  - 🤖💬 **Kira peut discuter sur Discord ET Desktop avec détection d'émotions !**
- [ ] **Session 11** : Audio & Lip-sync
  - Capture audio microphone (speech-to-text)
  - Synthèse vocale IA (text-to-speech)
  - Synchronisation lip-sync avec voix IA (phonèmes)
  - Détection amplitude vocale (VU-meter)
- [ ] **Session 12** : Mouvement libre sur bureau
  - Fenêtre Unity sans bordures (transparent)
  - Déplacement autonome intelligent
  - Animations marche/vol
  - Interactions avec fenêtres
  - Comportements autonomes (l'avatar décide où aller)

### Phase 6 : Polish & Release 🚀
- [ ] Packaging .exe
- [ ] Installeur Windows
- [ ] Documentation complète
- [ ] Tutoriels vidéo
- [ ] Support multi-plateformes (Linux, macOS)

## 🛠️ Technologies Utilisées

### Python Stack
- **PySide6** : Interface graphique Qt
- **sounddevice** : Capture audio
- **numpy** : Traitement numérique
- **opencv-python** : Traitement d'image et webcam (optionnel)
- **pytest** : Tests unitaires

### Unity Stack
- **Unity 2022.3 LTS** : Moteur de rendu
- **UniVRM** : Support modèles VRM
- **URP** : Universal Render Pipeline

### Communication
- **Sockets TCP** : IPC Python ↔ Unity (port 5555)
- **Format JSON** : Messages structurés
- **Threading** : Queue + Update() pour thread-safety Unity
- *(Futur : OSC ou gRPC pour plus de fonctionnalités)*

## 🎭 Fonctionnalités Actuelles

### ✅ Opérationnel
- **Interface Python Qt** : Fenêtre de contrôle avec onglets, 100% en français, icône personnalisée
- **Connexion Unity** : Communication bidirectionnelle stable avec thread-safety
- **Chargement VRM** : Import, affichage et déchargement dynamique de modèles VRM
- **Modèle par défaut** : Système de modèle VRM par défaut (pas besoin de naviguer à chaque fois) 
- **Avatar 3D** : Modèle "Mura Mura" affiché dans Unity avec rendu optimisé
- **Expressions faciales** : Contrôle blendshapes VRM (joy, angry, sorrow, surprised, fun)
- **Mouvements de tête subtils** : Mouvements de tête automatique confogurable (head bobbing)
- **Transitions smooth** : Interpolation Lerp pour animations fluides 
- **Vitesse ajustable** : Slider 1.0-10.0 pour contrôler la rapidité des transitions 
- **Clignement automatique** : Yeux qui clignent naturellement (2-5s) avec animation SmoothStep (160ms) 
- **Checkbox Auto Blink** : Activation/désactivation du clignement dans l'interface 
- **Interface sliders** : Contrôle précis 0-100% pour chaque expression
- **Logs détaillés** : Console + fichiers pour debugging
- **Tests unitaires** : 8 tests Python qui passent (100%)

### 🚧 En développement
- Lip-sync audio (analyse FFT + phonèmes)
- Eye tracking (suivi curseur)

## 🔧 Architecture Technique

### Communication IPC

```
┌─────────────────────────────┐
│      Python (Client)        │
│                             │
│  ┌───────────────────────┐  │
│  │   MainWindow (Qt)     │  │
│  │  - Connect button     │  │
│  │  - Load VRM button    │  │
│  └───────────┬───────────┘  │
│              │              │
│  ┌───────────▼───────────┐  │
│  │   UnityBridge         │  │
│  │  - send_command()     │  │
│  │  - Socket client      │  │
│  └───────────┬───────────┘  │
└──────────────┼──────────────┘
               │
          JSON/TCP
       127.0.0.1:5555
               │
┌──────────────▼──────────────┐
│     Unity (Serveur)         │
│                             │
│  ┌───────────────────────┐  │
│  │   PythonBridge.cs     │  │
│  │  - TcpListener        │  │
│  │  - HandleMessage()    │  │
│  └───────────┬───────────┘  │
│              │              │
│  ┌───────────▼───────────┐  │
│  │   VRMLoader.cs        │  │
│  │  - LoadVRMModel()     │  │
│  │  - Queue<Action>      │  │
│  │  - Update() thread    │  │
│  └───────────┬───────────┘  │
│              │              │
│  ┌───────────▼───────────┐  │
│  │   Scene Unity         │  │
│  │   🎭 Avatar VRM       │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

### Thread Safety

Unity nécessite l'exécution sur le **main thread** pour les opérations GameObject. VRMLoader utilise un pattern **Queue + Update()** :

```csharp
// Appelé depuis le thread réseau
public void LoadVRMFromPath(string path) {
    lock (mainThreadActions) {
        mainThreadActions.Enqueue(() => LoadVRMModel());
    }
}

// Exécuté sur le main thread Unity
void Update() {
    lock (mainThreadActions) {
        while (mainThreadActions.Count > 0) {
            mainThreadActions.Dequeue()?.Invoke();
        }
    }
}
```

## 📖 Documentation

Documentation complète et organisée par sessions de développement :

- 📄 **[START_HERE.md](docs/START_HERE.md)** - Point d'entrée de la documentation
- 📑 **[INDEX.md](docs/INDEX.md)** - Navigation rapide et recherche
- 📚 **[docs/README.md](docs/README.md)** - Vue d'ensemble complète

### Sessions documentées

0. **[Session 0 - Configuration Git Unity](docs/sessions/session_0_git_configuration/)** ⚙️
   - Configuration `.gitignore` pour Unity
   - Exclusion des fichiers générés (Library/, Temp/)
   - Bonnes pratiques Git pour projets Unity

1. **[Session 1 - Setup Python + GUI](docs/sessions/session_1_setup/)** ✅
   - Configuration environnement Python
   - Interface Qt avec PySide6
   - Système de configuration et logs

2. **[Session 2 - Installation Unity](docs/sessions/session_2_unity_installation/)** ✅
   - Installation Unity 2022.3 LTS
   - Création projet URP
   - Configuration de base

3. **[Session 3 - Installation UniVRM](docs/sessions/session_3_univrm_installation/)** ✅
   - Installation du package UniVRM
   - Support des modèles VRM
   - Configuration des shaders

4. **[Session 4 - Connexion Python ↔ Unity](docs/sessions/session_4_python_unity_connection/)** ✅
   - Communication IPC via socket TCP
   - PythonBridge.cs (serveur Unity)
   - unity_bridge.py (client Python)
   - Résolution des problèmes de connexion

5. **[Session 5 - Chargement VRM](docs/sessions/session_5_vrm_loading/)** ✅
   - VRMLoader.cs avec thread-safety
   - Chargement dynamique des modèles VRM
   - Affichage de l'avatar 3D
   - **Application fonctionnelle !** 🎉

6. **[Session 6 - Expressions Faciales](docs/sessions/session_6_expressions/)** ✅
   - VRMBlendshapeController.cs v1.6 pour expressions
   - Interface GUI avec sliders
   - Contrôle émotions en temps réel
   - **L'avatar exprime des émotions !** 😊😠😢😲😄

7. **[Session 7 - Animations Fluides](docs/sessions/session_7_animations/)** ✅
   - VRMBlendshapeController.cs v2.0 avec Lerp interpolation
   - Transitions smooth entre expressions
   - Slider de vitesse (1.0-10.0)
   - Interface française + icône
   - Système modèle VRM par défaut
   - Thread-safety complet (Queue<Action> pattern)
   - **L'avatar anime ses expressions de façon fluide !** ✨🎭

8. **[Session 8 - Clignement Automatique](docs/sessions/session_8_auto_blink/)** ✅
   - VRMAutoBlinkController.cs avec coroutines Unity
   - Animation SmoothStep (courbes de Hermite) pour réalisme
   - Timing paramétrable (2-5s entre clignements, 160ms par cycle)
   - Checkbox "Auto Blink" dans l'interface Python
   - Sauvegarde de configuration
   - Documentation technique complète (TECHNICAL_GUIDE.md 900+ lignes)
   - Résolution de 5 problèmes majeurs documentés (TROUBLESHOOTING.md)
   - **L'avatar cligne naturellement des yeux !** 👁️✨

9. **[Session 9 - Mouvements de Tête + Réorganisation Interface](docs/sessions/session_9_head_movements/)** ✅
   - VRMHeadMovementController.cs avec Coroutines + SmoothStep
   - Mouvements naturels aléatoires (yaw/pitch)
   - Contrôle fréquence (3-10s) et amplitude (2-10°)
   - Interface réorganisée en 3 onglets (Expressions, Animations, Options)
   - 3 boutons reset contextuels pour chaque onglet
   - Résolution conflit VRMAutoBlinkController
   - Gestion propre de la déconnexion Unity (reset état VRM)
   - Documentation complète (4 guides techniques + scripts archivés)
   - **L'avatar bouge naturellement la tête + interface moderne !** 🎭✨

10. **[Session 10 - IA Conversationnelle (Kira)](docs/sessions/session_10_ai_chat/)** ✅
   - **Phase 1** : Architecture de Base (30 min) ✅
     - Dossiers : src/ai/, src/discord_bot/, src/auth/, models/
     - Modèle LLM copié (Zephyr-7B, 6.8 GB)
     - Configuration : .env, requirements.txt, .gitignore
   - **Phase 2** : Base de Données & Mémoire (1h) ✅
     - src/ai/memory.py (430 lignes)
     - SQLite chat_history avec 4 indexes
     - Tests : 11/11 passés
     - Singleton pattern + Context manager thread-safe
   - **Phase 3** : Configuration IA (45 min) ✅
     - src/ai/config.py (420 lignes) avec GPU_PROFILES
     - 3 profils GPU (performance/balanced/cpu_fallback)
     - data/config.json configuration complète
     - Tests : 31/31 passés
   - **Phase 4** : Model Manager (1.5h) ✅
     - src/ai/model_manager.py (470 lignes)
     - Détection GPU NVIDIA (RTX 4050 6GB détecté)
     - Chargement LLM avec auto-fallback CPU
     - Tests : 23/23 passés
   - **Phase 5** : Chat Engine (2h) ✅
     - src/ai/chat_engine.py (480 lignes)
     - EmotionDetector avec 6 émotions (joy/angry/sorrow/surprised/fun/neutral)
     - Format prompt ChatML (Zephyr)
     - Support multi-utilisateurs et multi-sources
     - Tests : 23/23 passés
   - **Phase 6** : Emotion Analyzer (1h) ✅
     - src/ai/emotion_analyzer.py (680 lignes)
     - Analyse émotionnelle avancée avec intensité 0-100 et confiance
     - Historique émotionnel par utilisateur avec lissage transitions
     - Mapping complet vers Blendshapes VRM (6 émotions)
     - Tests : 39/39 passés
   - **Phase 7** : Discord Bot (1.5h) ✅
     - src/discord_bot/bot.py avec commandes !chat, !stats, !clear
     - Intégration ChatEngine + EmotionAnalyzer
     - Tests Discord : 23/23 passés
   - **Phase 8** : GUI Chat Desktop (1h) ✅
     - Interface PySide6 avec onglet Chat
     - Intégration ChatEngine dans GUI
     - Tests GUI Chat : 11/11 passés
   - **Phase 9** : Compilation CUDA (2h) ✅
     - llama-cpp-python avec support CUDA
     - Performance GPU 6-7x plus rapide (25-35 tok/s)
     - 43/43 GPU layers, 5.4GB VRAM
   - **Phase 10** : GUI Discord Control + Menu Options (1.5h) ✅
     - Interface Discord Control dans GUI
     - Menu Options (Token Bot, Salons autorisés)
     - Tests GUI Discord : 11/11 passés
   - **🎊 SESSION 10 TERMINÉE !** 270/270 tests OK ✅

11. **[Session 11 - Optimisations Performance](docs/sessions/session_11_performance/)** 🔥 ✅ (Phases 1-3/6)
   - **Phase 1** : Memory Profiling (1h) ✅
     - Scripts : profile_memory.py (4 modes de profiling)
     - Baseline RAM/VRAM : 35 MB → 687 MB (première génération)
     - Pas de memory leaks détectés sur 100 messages
     - GC efficace : -509 MB de cleanup après 100 messages
     - Documentation : MEMORY_PROFILING.md avec analyse détaillée
   - **Phase 2** : LLM Cache Optimization (1.5h) ✅
     - Scripts : benchmark_llm.py (4 benchmarks), test_warming.py
     - Warming cache implémenté dans ModelManager
     - Amélioration latence : **-17%** (2.11s → 1.75s)
     - Amélioration vitesse : **+14%** (19.46 → 22.28 tok/s)
     - Documentation : LLM_CACHE_OPTIMIZATION.md
   - **Phase 3** : Unity IPC Optimization (2h) ✅
     - Scripts : benchmark_ipc.py (baseline), test_batching.py (comparison)
     - Baseline IPC : 0.371 ms latency (déjà excellent)
     - Message batching implémenté (Python + Unity C#)
     - Amélioration latency : **-79%** (0.291 ms → 0.060 ms)
     - Amélioration throughput : **+907%** (64 → 642 msg/s)
     - Documentation : IPC_OPTIMIZATION.md avec recommandations d'usage
   - **🔥 Chat 10 TERMINÉ ! 3/6 PHASES COMPLÉTÉES !** Performance significativement améliorée ✨

12. **[Session 12 - Site Web Workly](docs/sessions/session_12_website/)** 🌐 ✅
   - **Site web complet** pour présenter le projet
   - **5 pages HTML** : Accueil, À propos, CGU, Confidentialité, (API archivée)
   - **Design** : Thème violet (#903f9e), dark mode futuriste, animations scroll
   - **Responsive** : Mobile-first (768px breakpoint)
   - **Technologies** : HTML5, CSS3 (557 lignes), JavaScript vanilla (260 lignes)
   - **Performance** : Intersection Observer, animations optimisées (threshold 0.05)
   - **Légal** : Licence MIT-NC, RGPD, Conditions d'utilisation complètes
   - **Hébergement** : Elsites (prêt pour déploiement HTTPS/SSL)
   - **Documentation** : Guide technique complet (personnalisation, couleurs, pages)
   - **🎭 SITE WEB TERMINÉ !** Prêt pour production ✨
     - src/discord_bot/bot.py (417 lignes) - Bot Discord Kira
     - Auto-reply configurable + rate limiting
     - Intégration ChatEngine + émotions Unity
     - Tests : 21/21 passés
   - **Phase 8** : GUI Chat Desktop (1.5h + chargement manuel) ✅
     - Onglet 💬 Chat avec QTextEdit, boutons Load/Unload IA
     - Chargement manuel LLM (contrôle utilisateur)
     - Tests : 164/164 passés
   - **Phase 9** : Compilation CUDA Windows (3-4h) ✅
     - llama-cpp-python avec CUDA 11.8.0 + cuBLAS
     - Accélération GPU RTX 4050 : 6-7x plus rapide
     - Documentation complète CUDA_INSTALLATION_GUIDE.md
   - **Phase 10** : GUI Discord Control + Menu Options ✅
     - Onglet 🤖 Discord avec Start/Stop bot, statut temps réel
     - **Menu "Options"** : Définir Token Discord (dialog password) + Gérer Salons Auto-Reply (QListWidget)
     - Configuration sécurisée : Token dans `.env`, salons dans `config.json`
     - Système `load_dotenv(override=True)` pour persistance token
     - 171/171 tests passent
     - 🎭✨ **Interface Discord intuitive avec configuration facile !** 🤖🔧

11. **[Session 11 - Performance Optimizations](docs/sessions/session_11_performance/)** 🔥 **EN COURS (Phase 3/6)** ✨
   - **Phase 1** : Memory Profiling (1h) ✅
     - Scripts : profile_memory.py avec 4 modes de profiling
     - Baseline RAM/VRAM établi (35 MB → 687 MB première génération)
     - Pas de memory leaks détecté sur 100 messages
     - Garbage collection efficace (-509 MB cleanup)
     - Documentation : MEMORY_PROFILING.md avec analyse complète
   - **Phase 2** : LLM Cache Optimization (1.5h) ✅
     - Scripts : benchmark_llm.py (4 benchmarks), test_warming.py
     - Warming cache implémenté dans ModelManager.load_model()
     - **Amélioration latence : -17%** (2.11s → 1.75s première génération)
     - **Amélioration vitesse : +14%** (19.46 → 22.28 tok/s)
     - Documentation : LLM_CACHE_OPTIMIZATION.md avec résultats détaillés
     - 🔥✨ **Génération LLM 17% plus rapide dès le premier message !** ⚡
   - **Phase 3** : Unity IPC Optimization (2h) ✅
     - Scripts : benchmark_ipc.py (baseline), test_batching.py (comparaison)
     - Message batching implémenté (Python send_batch() + Unity C# HandleBatchMessage())
     - Baseline IPC : 0.371 ms latence (déjà excellent !)
     - **Amélioration latence/commande : -79%** (0.29 ms → 0.06 ms)
     - **Amélioration temps total (100 cmd) : -90%** (1.57s → 0.16s)
     - **Amélioration throughput : +907%** (64 → 642 msg/s)
     - Documentation : IPC_OPTIMIZATION.md avec guide d'usage
     - 📡✨ **Communication Python ↔ Unity 10x plus rapide en mode batch !** 🚀
   - 🔜 **Phase 4** : CPU Optimization (auto-détection n_threads optimal)
   - 🔜 **Phase 5** : GPU Profiling & Tuning (profils dynamiques VRAM)
   - 🔜 **Phase 6** : Tests & Documentation finale

### Guides spécifiques

- [Configuration Git Unity](docs/sessions/session_0_git_configuration/GIT_UNITY_FIX.md)
- [Architecture technique](docs/sessions/session_1_setup/architecture.md)
- [Debug connexion Unity](docs/sessions/session_4_python_unity_connection/DEBUG_CONNECTION.md)
- [Fix script Unity](docs/sessions/session_4_python_unity_connection/FIX_SCRIPT_NOT_RUNNING.md)
- [Récapitulatif Session 5](docs/sessions/session_5_vrm_loading/SESSION_VRM_LOADING_SUCCESS.md)
- [Guide expressions Session 6](docs/sessions/session_6_expressions/BLENDSHAPES_GUIDE.md)
- [Guide transitions Session 7](docs/sessions/session_7_animations/TRANSITIONS_GUIDE.md) 
- [Guide technique Session 8](docs/sessions/session_8_auto_blink/TECHNICAL_GUIDE.md) 
- [Installation CUDA Session 10](docs/sessions/session_10_ai_chat/phase_9_cuda_fix/CUDA_INSTALLATION_GUIDE.md) 
- [Guide utilisateur Discord Session 10](docs/sessions/session_10_ai_chat/phase_10_gui_discord/GUI_DISCORD_GUIDE.md) 
- [Résolution problèmes Session 8](docs/sessions/session_8_auto_blink/TROUBLESHOOTING.md) 
- [Réorganisation interface Session 9](docs/sessions/session_9_head_movements/INTERFACE_REORGANIZATION.md) 
- [Guide mouvements tête Session 9](docs/sessions/session_9_head_movements/HEAD_MOVEMENT_GUIDE.md) 
- [Guide Chat Engine Session 10](docs/sessions/session_10_ai_chat/CHAT_ENGINE_GUIDE.md) 
- [Résolution problèmes Session 9](docs/sessions/session_9_head_movements/DEBUG_ISSUES.md) 
- [Plan Session 10](docs/sessions/session_10_ai_chat/PLAN_SESSION_10.md) ✨ **14 phases IA conversationnelle détaillées !**
- [Contexte Chat 7](docs/chat_transitions/chat_6_session_10_phases_1_2/CONTEXT_FOR_NEXT_CHAT.md)
- [Guide installation CUDA Session 10 Phase 9](docs/sessions/session_10_ai_chat/phase_9_cuda_fix/CUDA_INSTALLATION_GUIDE.md) 
- [Guide simplification GUI Discord Session 10 Phase 10](docs/sessions/session_10_ai_chat/phase_10_gui_discord/SIMPLIFICATION.md) 
- [Guide menu Options Session 10 Phase 10](docs/sessions/session_10_ai_chat/phase_10_gui_discord/MENU_OPTIONS.md) 
- [Memory Profiling Session 11 Phase 1](docs/sessions/session_11_performance/MEMORY_PROFILING.md) ✨ **Baseline RAM/VRAM + Pas de memory leaks !**
- [LLM Cache Optimization Session 11 Phase 2](docs/sessions/session_11_performance/LLM_CACHE_OPTIMIZATION.md) ✨ **-17% latency, +14% speed !**
- [IPC Optimization Session 11 Phase 3](docs/sessions/session_11_performance/IPC_OPTIMIZATION.md) ✨ **-79% latency, +907% throughput !**
- [Guide Site Web Session 12](docs/sessions/session_12_website/README.md) ✨ **Site web complet avec documentation !**
- [Guide Technique Site Web Session 12](docs/sessions/session_12_website/TECHNICAL_GUIDE.md) ✨ **Personnalisation et modification du site !**
- [Chat 10 → Chat 11 Transition](docs/chat_transitions/chat_10_session_11_phases_1_3/README.md) 🚀 **Documentation transition complète !**

### 🌐 Site Web Officiel

**[Site Web Kira Workly](web/)** 💜 ✨ **NOUVEAU !**
- Page d'accueil avec présentation complète du projet
- Documentation technique et architecture détaillée
- Endpoints API Discord (Interactions, Linked Roles)
- Conditions d'utilisation (CGU) et Politique de confidentialité
- Design moderne avec animations (couleur violet #903f9e)
- Prêt pour hébergement sur Elsites
- 🎭 **Site web professionnel pour Kira !** 🌐✨

📖 **[Documentation du site web](web/README.md)**

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment participer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'feat: add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 💾 Screenshots

### Interface Python
Interface de contrôle avec connexion Unity et bouton de chargement VRM.

### Console Unity
```
[PythonBridge] Serveur démarré avec succès sur 127.0.0.1:5555
[PythonBridge] 🔗 Client Python connecté !
[PythonBridge] 📨 Reçu : {"command": "load_model", "data": {"path": "..."}}
[VRMLoader] 📋 Demande de chargement reçue
[VRMLoader] 🎭 Exécution du chargement sur le thread principal
[VRMLoader] ✅ Modèle chargé avec succès : Mura Mura - Model(Clone)
[VRMLoader] 📍 Position : (0.0, 0.0, 0.0)
```

### Avatar dans Unity
Avatar VRM "Mura Mura" affiché dans la fenêtre Game de Unity 🎭

## 🎓 Leçons Apprises

### Threading Unity
Unity nécessite que toutes les opérations GameObject soient sur le main thread. Solution : Pattern Queue + Update().

### API UniVRM
L'API UniVRM varie selon les versions. Pour le MVP, approche simplifiée avec prefab pré-importé.

### IPC Robuste
Socket TCP + JSON fonctionne bien pour la communication bidirectionnelle Python ↔ Unity.

### Documentation
Organisation par sessions chronologiques facilite la compréhension et la maintenance du projet.

## 🎯 Vision du Projet

Ce projet a pour **objectif final** de créer un **assistant virtuel IA complet** :
- 🤖 **Conversation intelligente** : L'avatar pourra discuter naturellement grâce à un LLM (chatbot IA)
- 😊 **Émotions réactives** : Analyse du sentiment et expressions faciales adaptées
- 🚶 **Mobilité libre** : Déplacement autonome sur le bureau, interactions avec l'environnement
- 🎤 **Voix naturelle** : Reconnaissance vocale + synthèse vocale synchronisée
- 🧠 **Comportements intelligents** : Décisions autonomes basées sur le contexte

**L'avatar deviendra un véritable compagnon numérique interactif et intelligent !**

## 👤 Auteur

**Xyon15**
- GitHub: [@Xyon15](https://github.com/Xyon15)

## 🙏 Remerciements

- [UniVRM](https://github.com/vrm-c/UniVRM) pour le support VRM
- [AcidicDoll](https://acidicdollz.booth.pm/) pour le modèle VRM "Mura Mura"
- La communauté VRM pour les ressources et tutoriels

## 📞 Support

Si vous rencontrez des problèmes ou avez des questions :
- 📖 Consultez la [documentation complète](docs/START_HERE.md)
- 🐛 Ouvrez une [issue](https://github.com/WorklyHQ/workly-desktop/issues)
- 💬 Regardez les fichiers DEBUG_ et FIX_ dans docs/

## 📝 Changelog

### Version 0.14.1-alpha (9 novembre 2025) 📚 **CHAT 10 TERMINÉ - TRANSITION CHAT 11**
- ✅ **Chat 10 TERMINÉ avec succès !**
- ✅ **Session 11 Phases 1-3 complétées** : Memory, LLM Cache, IPC Batching
- ✅ **Session 12 complétée** : Site web Workly professionnel
- 📚 **Documentation transition Chat 10 → Chat 11 créée** :
  - `docs/chat_transitions/chat_10_session_11_phases_1_3/README.md` - Vue d'ensemble Chat 10
  - `docs/chat_transitions/chat_10_session_11_phases_1_3/CURRENT_STATE.md` - État technique complet
  - `docs/chat_transitions/chat_10_session_11_phases_1_3/CONTEXT_FOR_NEXT_CHAT.md` - Instructions Chat 11
- ✅ **Résumé Chat 10** :
  - 3 phases Session 11 : Memory Profiling, LLM Cache, IPC Batching
  - Performance améliorée : -17% latency LLM, -79% latency IPC, +907% throughput IPC
  - Baseline mémoire établi : Pas de memory leaks
  - Scripts archivés : profile_memory.py, benchmark_llm.py, benchmark_ipc.py, test_batching.py
  - Documentation complète : 3 guides techniques (MEMORY_PROFILING.md, LLM_CACHE_OPTIMIZATION.md, IPC_OPTIMIZATION.md)
- 🔜 **Prochaines étapes Chat 11** :
  - Phase 4 : CPU Optimization (auto-détection threads)
  - Phase 5 : GPU Profiling & Tuning (monitoring VRAM)
  - Phase 6 : Tests & Documentation finale (validation gains +30-40%)
- ✅ **Documentation mise à jour** :
  - `docs/INDEX.md` → Transition Chat 10 ajoutée
  - `docs/README.md` → Session 11 Phases 1-3 détaillées
  - `README.md` (racine) → 4 sections mises à jour (Sessions, Guides, Changelog, Status)
- 🎯 **Chat 10 complété ! Ready for Chat 11 !** 🚀✨

### Version 0.15.0-alpha (6 novembre 2025) 🌐 **NOUVEAU - SITE WEB OFFICIEL KIRA**
- ✅ **Site Web Officiel Kira Workly créé !**
- 🌐 **Structure du site** :
  - Dossier `web/` créé avec architecture complète
  - Page d'accueil (`index.html`) avec hero section et présentation
  - Page "À propos" (`pages/about.html`) - Histoire, vision, architecture technique
  - Page "API Endpoints" (`pages/api.html`) - Configuration Discord (4 URLs)
  - Page "Terms of Service" (`pages/terms.html`) - CGU complètes (MIT License)
  - Page "Privacy Policy" (`pages/privacy.html`) - Politique de confidentialité (RGPD)
- 🎨 **Design moderne** :
  - Couleur principale : **Violet #903f9e** 💜
  - Thème : Dark mode futuriste
  - Animations : Transitions fluides, effets au scroll (Intersection Observer)
  - Responsive : Compatible mobile, tablette, desktop
  - CSS natif (variables CSS, aucune dépendance externe)
- ⚡ **Fonctionnalités JavaScript** :
  - Navigation sticky avec effet au scroll
  - Animations au scroll (fade-in progressif)
  - Menu mobile responsive (hamburger menu)
  - Smooth scroll pour les ancres
  - Boutons "Copier URL" sur la page API
  - Notifications système (toast)
  - Easter egg (5 clics sur le logo) 🎭
- 📄 **Contenu du site** :
  - **Accueil** : Présentation générale + fonctionnalités principales + technologies
  - **À propos** : Vision du projet + architecture technique + phases de développement + inspiration
  - **API** : 4 endpoints Discord (Interactions, Linked Roles, Terms, Privacy) avec documentation
  - **CGU** : Conditions d'utilisation complètes (Licence MIT, restrictions, garanties, RGPD)
  - **Privacy** : Politique de confidentialité (données locales, aucune télémétrie, RGPD)
- 🔧 **Configuration Discord** :
  - Interactions Endpoint URL : `https://nice-example.local/api/interactions`
  - Linked Roles Verification URL : `https://nice-example.local/verify-user`
  - Terms of Service URL : `https://my-cool-app.com/terms-of-service`
  - Privacy Policy URL : `https://my-cool-app.com/privacy-policy`
- 📚 **Documentation** :
  - `web/README.md` (100+ lignes) - Guide complet d'utilisation et déploiement
  - Instructions pour tester localement (Python HTTP server, Live Server)
  - Guide de déploiement sur Elsites (FTP, DNS, SSL/HTTPS)
  - Conseils de personnalisation (couleurs, images, animations)
  - Recommandations SEO (Open Graph, Twitter Card, sitemap)
- ✅ **Prêt pour production** :
  - Aucune dépendance externe (HTML5, CSS3, JS vanilla)
  - Compatible tous navigateurs modernes (Chrome 90+, Firefox 88+, Safari 14+)
  - Site complet et professionnel
  - Prêt pour hébergement sur Elsites avec HTTPS
- 🎭✨ **Site web élégant et professionnel pour présenter Kira !** 🌐💜
- ✅ **Documentation mise à jour** :
  - `docs/INDEX.md` → Section "Site Web" ajoutée (structure complète)
  - `README.md` (racine) → 4 sections mises à jour (Structure, Sessions, Guides, Changelog, Status)

### Version 0.14.0-alpha (4 novembre 2025) 🔥 **CHAT 10 (Session 11 - Performance Optimizations Phase 3)**
- ✅ **Chat 10 - Session 11 Phase 3 (IPC Optimization) terminée !**
- ✅ **Phase 3 : Unity IPC Optimization (2h)** - Message batching implémenté
  - **Scripts créés** :
    * `scripts/benchmark_ipc.py` (400+ lignes) - Benchmark IPC baseline (4 tests)
    * `scripts/test_batching.py` (300+ lignes) - Comparaison batching avant/après
  - **Baseline IPC mesurée** :
    * Latence moyenne : **0.371 ms** ✅ (déjà excellent !)
    * Latence médiane : **0.342 ms**
    * Throughput : **6871 msg/s** 🚀
    * Impact taille message : **Négligeable** (10B → 10KB = 0.3-0.4ms)
  - **Message Batching implémenté** :
    * Fichier Python modifié : `src/ipc/unity_bridge.py`
    * Méthode `send_batch(commands: list)` ajoutée
    * Fichier Unity modifié : `unity/PythonBridge.cs`
    * Méthode `HandleBatchMessage()` ajoutée pour traiter batches
    * Format batch : `{"command": "batch", "data": {"commands": [...], "count": N}}`
  - **Résultats comparaison (100 commandes, batches de 10)** :
    * **SANS batching** : 0.291 ms/cmd, Total 1568 ms, Throughput 64 msg/s
    * **AVEC batching** : 0.060 ms/cmd, Total 156 ms, Throughput 642 msg/s
    * **Amélioration latence/commande : -79%** (0.291 ms → 0.060 ms) ⚡
    * **Amélioration temps total : -90%** (1.57s → 0.16s) �
    * **Amélioration throughput : +907%** (64 → 642 msg/s) 💥
  - **Recommandations d'usage** :
    * ✅ Utiliser `send_batch()` pour : changements multiples, animations complexes, synchro état
    * ✅ Utiliser `send_command()` pour : commande unique, interaction directe, simplicité
    * 💡 Batching disponible mais utilisation optionnelle (baseline déjà excellent)
  - **Documentation** : `docs/sessions/session_11_performance/IPC_OPTIMIZATION.md` (guide complet)
  - **Scripts archivés** : 
    * `docs/sessions/session_11_performance/scripts/benchmark_ipc.py`
    * `docs/sessions/session_11_performance/scripts/test_batching.py`
    * `docs/sessions/session_11_performance/scripts/ipc_benchmark_results.txt`
    * `docs/sessions/session_11_performance/scripts/batching_comparison_results.txt`
- 📡✨ **Communication Python ↔ Unity 10x plus rapide en mode batch !** 🚀
- ✅ **Documentation mise à jour** :
  - `docs/INDEX.md` → Session 11 Phase 3 ajoutée
  - `docs/README.md` → Phase 3 détaillée avec résultats
  - `README.md` (racine) → 4 sections mises à jour (Sessions, Guides, Changelog, Status)

### Version 0.13.0-alpha (28 octobre 2025) 🔥 **CHAT 10 (Session 11 - Performance Optimizations Phase 1-2)**
- ✅ **Chat 10 - Session 11 Phases 1-2 (Memory & LLM Cache) terminées !**
- ✅ **Phase 1 : Memory Profiling (1h)** - Baseline RAM/VRAM établi
  - **Scripts créés** :
    * `scripts/profile_memory.py` (340 lignes) - 4 modes de profiling
    * Profiling modes : basic startup, LLM loading, conversation (100 messages), all profiles
  - **Résultats Memory Profiling** :
    * Baseline startup : **35 MB RAM**, **668 MB VRAM**
    * Après init GUI : **200 MB RAM**
    * Après chargement LLM : **411 MB RAM**, **6012 MB VRAM** (+433 MB RAM 🔴)
    * Après 10 messages : **807 MB RAM**, **6088 MB VRAM**
    * Après 100 messages : **299 MB RAM** (-509 MB 🟢 GC cleanup), **6089 MB VRAM**
  - **Analyse** :
    * ✅ **Pas de memory leaks** détecté
    * ✅ **Garbage collection efficace** (-509 MB après 100 messages)
    * 🔴 **Pic RAM première génération** : +433 MB (opportunité optimisation)
    * 📊 VRAM stable à ~6 GB (RTX 4050 6GB bien utilisé)
  - **Documentation** : `docs/sessions/session_11_performance/MEMORY_PROFILING.md` (analyse complète)
  - **Scripts archivés** : `docs/sessions/session_11_performance/scripts/profile_memory.py`
- ✅ **Phase 2 : LLM Cache Optimization (1.5h)** - Warming cache implémenté
  - **Scripts créés** :
    * `scripts/benchmark_llm.py` (450+ lignes) - 4 benchmarks LLM
    * `scripts/test_warming.py` (250+ lignes) - Comparaison avant/après warming
  - **Benchmarks effectués** :
    1. **Cold start** : Load time 5.60s, First gen 2.13s (19.27 tok/s)
    2. **Warm cache** (10 runs) : Avg 1.754s, Median 1.760s, Stdev 0.014s (18.08 tok/s)
    3. **Context size** : Short 1.731s, Medium 1.795s (+3.7%), Long 1.855s (+7.2%)
    4. **Max tokens** : 25→0.874s, 50→1.736s, 100→3.485s, 150→4.702s (scaling linéaire)
  - **Warming Cache Test** :
    * **SANS warming** : Load 5.10s, First gen 2.11s (19.46 tok/s)
    * **AVEC warming** : Load 2.57s, First gen 1.75s (22.28 tok/s)
    * **Amélioration latence** : **-16.9%** (2.11s → 1.75s)
    * **Amélioration vitesse** : **+14%** (19.46 → 22.28 tok/s)
  - **Implémentation** :
    * Fichier modifié : `src/ai/model_manager.py`
    * Méthode `load_model()` avec paramètre `warm_cache=True` (default)
    * Génère 2 tokens immédiatement après chargement pour pré-allouer KV cache
    * Logging : "🔥 Warming cache (pré-allocation KV)..." + "✅ Cache warmed"
  - **Résultats** :
    * ⚡ **Latence première génération : -17%** (2.11s → 1.75s)
    * 🚀 **Vitesse génération : +14%** (19.46 → 22.28 tok/s)
    * 💡 Double bénéfice : réduction latence + augmentation vitesse
  - **Documentation** : `docs/sessions/session_11_performance/LLM_CACHE_OPTIMIZATION.md`
  - **Scripts archivés** : 
    * `docs/sessions/session_11_performance/scripts/benchmark_llm.py`
    * `docs/sessions/session_11_performance/scripts/test_warming.py`
- ✅ **Documentation complète** :
  - `docs/sessions/session_11_performance/README.md` (vue d'ensemble Session 11)
  - `docs/sessions/session_11_performance/MEMORY_PROFILING.md` (Phase 1 détails)
  - `docs/sessions/session_11_performance/LLM_CACHE_OPTIMIZATION.md` (Phase 2 détails)
- ✅ **Métriques Session 11 Phases 1-2** :
  - 📊 Baseline mémoire établi (RAM/VRAM toutes étapes)
  - 🔍 Aucun memory leak détecté (100 messages testés)
  - ⚡ Latence première génération : **-17%**
  - 🚀 Vitesse génération : **+14%**
  - ♻️ Garbage collection : **-509 MB** cleanup efficace
- 🔜 **Prochaines phases (3-6)** :
  - Phase 3 : Unity IPC Overhead (optimisation communication)
  - Phase 4 : CPU Optimization (auto-détection n_threads)
  - Phase 5 : GPU Profiling & Tuning (profils dynamiques)
  - Phase 6 : Tests & Documentation finale
- 🔥 **Workly génère maintenant 17% plus vite dès le premier message !** ⚡✨

### Version 0.12.0-alpha (27 octobre 2025) ✨ **CHAT 9 (Bugfixes & GPU Optimizations)**
- ✅ **Chat 9 - Bugfixes & Optimisations GPU terminé !**
- ✅ **6 bugs critiques résolus** :
  1. **Chat input bloqué** après premier message
     - Problème : Impossible d'envoyer plusieurs messages consécutifs
     - Solution : Signal Qt `chat_input_ready` + méthode `enable_chat_input()` thread-safe
     - Fichiers : `src/gui/app.py` (lignes 191, 212, 1131, 1135-1146)
  2. **Émotions Discord non synchronisées GUI**
     - Problème : Émotions détectées par Discord bot ne mettaient pas à jour sliders GUI ni labels
     - Solution : Signal `emotion_detected` + shared `UnityBridge` instance
     - Fichiers : `src/gui/app.py` (lignes 60, 649-651, 738-779), `src/discord_bot/bot.py` (lignes 56, 85, 309-318)
  3. **GUI sliders non mis à jour**
     - Problème : Émotions détectées ne bougeaient pas les sliders programmatiquement
     - Solution : Signal `expression_changed` + méthode `update_expression_slider()`
     - Fichiers : `src/gui/app.py` (lignes 179, 473, 1539-1568)
  4. **Modèle LLM chargé sur RAM au lieu de GPU**
     - Problème : Génération très lente (2-5 tok/s), modèle sur RAM CPU
     - Solutions :
       * Réinstallation llama-cpp-python avec CUDA (`CMAKE_ARGS="-DGGML_CUDA=on"`)
       * Profil GPU par défaut changé de "balanced" → "performance"
       * Configuration `data/config.json` mise à jour
     - Résultats : **25-35 tok/s** (5-7x plus rapide), **5.4 GB VRAM**, **43/43 GPU layers** (100%)
     - Fichiers : `src/ai/config.py` (ligne 83), `data/config.json`
  5. **Compteur messages affichait total DB**
     - Problème : Compteur affichait TOUS les messages de l'historique (base de données)
     - Solution : Compteur local `self.current_session_messages` pour session actuelle uniquement
     - Fichiers : `src/gui/app.py` (lignes 209, 1172-1174, 1183, 1199)
  6. **Oubli activation venv (récurrent)**
     - Problème : Erreurs `ModuleNotFoundError` si venv non activé
     - Solution : Section **CRITIQUE** ajoutée dans instructions Copilot
     - Fichiers : `.github/instructions/copilot-instructions.instructions.md` (lignes 35-42)
- ✅ **5 features UX ajoutées** :
  1. **Indicateur "✍️ Kira écrit..."** pendant génération IA
     - Widget visible uniquement pendant génération, masqué après réponse
     - Fichiers : `src/gui/app.py` (lignes 460-462, 1047, 1141)
  2. **Compteur messages session actuelle** (au lieu de total DB)
  3. **Menu Options restructuré** avec sous-menus IA et Discord
     - Structure : Options > 🤖 IA > Profils IA... (désactivé, à venir)
     - Structure : Options > 💬 Discord > Token + Salons
     - Fichiers : `src/gui/app.py` (lignes 1758-1777, 1003-1020)
  4. **Compteur émotions supprimé** (simplification UX)
  5. **Documentation venv critique** ajoutée dans instructions système
- ✅ **Métriques Performance** :
  - ⚡ Vitesse génération : **2-5 → 25-35 tokens/sec** (5-7x plus rapide)
  - 💾 VRAM utilisée : **0 GB (RAM) → 5.4 GB (VRAM GPU)**
  - 🎮 GPU layers : **35/43 (81%) → 43/43 (100%)**
  - 📏 Context size : **2048 → 4096** tokens (doublé)
  - 📦 Batch size : **256 → 512** (doublé)
- ✅ **Tests** : 270/270 tests unitaires passent (100%, aucune régression)
- ✅ **Fichiers modifiés** : 5 fichiers, ~130 lignes modifiées
  - `src/gui/app.py` (~100 lignes)
  - `src/discord_bot/bot.py` (~15 lignes)
  - `src/ai/config.py` (1 ligne)
  - `data/config.json` (1 ligne)
  - `.github/instructions/copilot-instructions.instructions.md` (~10 lignes)
- ✅ **Documentation complète** :
  - `docs/chat_transitions/chat_9_bugfixes_gpu/README.md` (détails complets)
  - `docs/chat_transitions/chat_9_bugfixes_gpu/CURRENT_STATE.md` (état technique)
  - `docs/chat_transitions/chat_9_bugfixes_gpu/CONTEXT_FOR_NEXT_CHAT.md` (plan Session 11)
  - `docs/chat_transitions/chat_9_bugfixes_gpu/prompt_transition.txt` (transition Chat 10)
- 🎊 **Workly est maintenant 5-7x plus rapide, ultra-stable et agréable à utiliser !** ⚡🔧✨

### Version 0.11.0-alpha (24 octobre 2025) ✨ **NOUVEAU - SESSION 10 (Chat 9 - Phase 10) MENU OPTIONS + PERSISTANCE TOKEN**
- ✅ **Chat 9 - Session 10 Phase 10 (GUI Discord + Menu Options) terminée !**
- ✅ **Phase 10 : Interface GUI Discord Control + Menu Options Configuration**
  - **Menu "Options"** ajouté entre "Fichier" et "Aide" dans la barre de menu
  - **2 sous-menus de configuration** :
    * "Définir Token Bot Discord..." : Dialog QInputDialog en mode password pour saisir/modifier token
    * "Gérer Salons Auto-Reply..." : Dialog QDialog avec QListWidget pour ajouter/retirer salons Discord
  - **Sauvegarde sécurisée des configurations** :
    * Token Discord sauvegardé dans `.env` (variable `DISCORD_TOKEN`)
    * Salons auto-reply sauvegardés dans `config.json` (clé `discord.auto_reply_channels`)
    * Mise à jour automatique de `os.environ` pour application immédiate
  - **Système de persistance token** :
    * `load_dotenv()` ajouté au début de `main.py` (ligne 8-9, avant tous les imports)
    * `load_dotenv(override=True)` dans `start_discord_bot()` pour forcer rechargement .env
    * Token persiste correctement entre redémarrages de l'application
  - **Nettoyage configuration** :
    * Suppression clé `"token"` des fichiers `config.json` (template + utilisateur)
    * Configuration dual : Secrets dans `.env`, paramètres dans `config.json`
  - **Tests mis à jour** :
    * tests/test_gui_discord.py : 14/14 tests passent
    * ✅ **Total projet : 171/171 tests passés (100%)**
  - **Documentation complète** :
    * phase_10_gui_discord/MENU_OPTIONS.md : Guide complet menu Options
    * phase_10_gui_discord/SIMPLIFICATION.md : Documentation simplification UI
    * Scripts archivés : versions finales app.py, main.py, bot.py
  - 🎊 **Workly dispose d'une configuration Discord intuitive et sécurisée (menu Options + persistance token) !** 🤖🔧✨

### Version 0.10.0-alpha (24 octobre 2025) ✨ **SESSION 10 (Chat 8 - Phase 10) TERMINÉE + SIMPLIFICATION**
- ✅ **Chat 9 - Session 10 Phase 10 (GUI Discord Control) terminée + Interface simplifiée !**
- ✅ **Phase 10 : Interface GUI Discord Control (2-3h) + Simplification**
  - **Nouvel onglet "🤖 Discord"** avec interface épurée de contrôle/monitoring du bot
  - **Classes thread-safety Qt** :
    * DiscordSignals (QObject) : 4 signaux (status_changed, message_received, stats_updated, error_occurred)
    * DiscordBotThread (QThread) : Event loop asyncio séparé pour discord.py
    * Communication thread-safe bot Discord ↔ GUI Qt
  - **Interface utilisateur simplifiée** (focus contrôle/monitoring) :
    * Boutons Start/Stop bot avec états visuels (vert/rouge)
    * Statut connexion temps réel (🔴 Déconnecté / 🟡 Connexion... / 🟢 Connecté)
    * Affichage derniers messages (QTextEdit, max 50, monospace)
    * Statistiques Discord (messages reçus/traités, serveurs, uptime)
    * ⚠️ **Section Configuration supprimée** (token dans `.env`, salons dans `config.json` pour éviter redondance)
  - **Configuration Discord externalisée** :
    * Token Discord : Variable `DISCORD_TOKEN` dans fichier `.env`
    * Salons auto-reply : Clé `discord.auto_reply_channels` dans `data/config.json`
    * Rate limit : Clé `discord.rate_limit_seconds` dans `data/config.json`
  - **Méthodes GUI** :
    * start_discord_bot() : Récupère token depuis `.env`, lance DiscordBotThread
    * stop_discord_bot() : Arrêt propre du bot
    * Slots Qt : on_discord_status_changed(), on_discord_message_received(), on_discord_stats_updated(), on_discord_error()
  - **Bot Discord amélioré** :
    * get_status() : Retourne infos connexion (connected, bot_name, guilds_count)
    * get_connection_info() : Détails complets (guilds, active_channels)
  - **Tests mis à jour** :
    * tests/test_gui_discord.py : 14 tests actifs (6 tests config supprimés)
    * ✅ **Total projet : 171/171 tests passés (100%)**
  - **Documentation complète** :
    * phase_10_gui_discord/README.md : Vue d'ensemble + note simplification
    * phase_10_gui_discord/SIMPLIFICATION.md : Documentation détaillée des changements
    * phase_10_gui_discord/GUI_DISCORD_GUIDE.md : Guide utilisateur mis à jour
    * Scripts archivés : app.py, test_gui_discord.py (versions simplifiées)
  - 🎊 **Workly dispose d'une interface Discord épurée et sécurisée (token jamais affiché) !** 🤖✨
- 🎊 **Session 10 (IA Conversationnelle Kira) TERMINÉE ! Interface Discord simplifiée et fonctionnelle !** 🤖💬🎭🎮✨

### Version 0.9.0-alpha (23 octobre 2025) ✨ **SESSION 10 (Chat 8 - Phases 6-9) TERMINÉE**
- ✅ **Chat 8 - Session 10 (Phases 6-9) terminée !**
- ✅ **Phase 6 : Emotion Analyzer (1h)**
  - src/ai/emotion_analyzer.py (680 lignes) avec analyse émotionnelle avancée
  - Analyse intensité (0-100) + confiance (0.0-1.0)
  - Historique émotionnel par utilisateur avec lissage transitions
  - Mapping complet vers Blendshapes VRM (6 émotions)
  - Tests : 39/39 passés
- ✅ **Phase 7 : Discord Bot (1.5h)**
  - src/discord_bot/bot.py (417 lignes) - Bot Discord complet pour Kira
  - Classe KiraDiscordBot avec intégration ChatEngine complète
  - **Fonctionnalités Discord** :
    * Auto-reply configurable par salon (whitelist)
    * Réponse aux mentions utilisateur
    * Rate limiting (délai minimum entre messages)
    * Nettoyage prompts (suppression mentions/URLs)
    * Détection émotions + envoi Unity VRM si connecté
  - **Architecture asynchrone** :
    * Support discord.py async/await
    * Handlers on_ready() + on_message()
    * Gestion erreurs robuste
  - **Statistiques détaillées** :
    * Messages reçus/traités/ignorés
    * Réponses générées
    * Émotions envoyées Unity
    * Tracking salons + mentions
  - Singleton pattern : get_discord_bot()
  - tests/test_discord_bot.py - 21 tests unitaires (pytest-asyncio)
  - ✅ **Tous les tests passent (21/21) !**
- ✅ **Phase 8 : GUI Chat Desktop (1.5h + amélioration chargement manuel)**
  - src/gui/app.py - Nouvel onglet "💬 Chat" intégré
  - **Interface chat complète** :
    * QTextEdit pour messages (HTML avec couleurs Material Design)
    * QLineEdit pour saisie utilisateur
    * Bouton envoi + support Enter
    * Indicateur émotion en temps réel (emoji + nom + intensité)
    * Statistiques messages/émotions en footer
    * Historique effaçable avec confirmation
  - **Thread-safety Qt** :
    * Signaux personnalisés (message_received, emotion_updated, stats_updated)
    * Threading pour traitement chat (évite freeze UI)
    * QTimer.singleShot() pour ré-activation boutons
  - **Thème dark harmonisé** :
    * Fond #2b2b2b, texte #e0e0e0
    * Messages : Vous=#64B5F6, Kira=#CE93D8, Système=#EF5350
    * Timestamps gris #888
    * Indicateur émotion : fond #3a3a3a, bordure #555
  - **🚀 Chargement manuel IA (amélioration majeure)** :
    * Suppression chargement automatique (économie 4-6 GB VRAM)
    * Nouvel onglet "🤖 Modèle IA (LLM)" dans Connexion tab
    * Bouton "📥 Charger IA (Zephyr-7B)" pour chargement manuel
    * Bouton "🗑️ Décharger IA" pour libérer mémoire
    * Labels statut dynamiques (Non chargé / ⏳ / ✅ / ❌)
    * Info utilisateur : "Chargement : ~15-30 secondes | Mémoire : ~4-6 GB VRAM"
    * Chat input désactivé par défaut avec placeholder explicite
    * Gestion ImportError avec QMessageBox si llama-cpp-python manquant
    * Messages système dans chat pour confirmer opérations
  - **Méthodes nouvelles** :
    * load_ai_model() - Chargement ChatEngine + EmotionAnalyzer on-demand
    * unload_ai_model() - Libération mémoire complète
    * Mise à jour UI automatique (statuts, boutons, inputs)
  - **Intégration VRM Unity** :
    * Vérification connexion + VRM chargé
    * get_vrm_blendshape() pour mapping optimal
    * set_expression() automatique lors des réponses
  - ✅ **Gestion erreurs robuste** : ImportError, ConnectionError, génération échec
  - ✅ **Bug fixes** : timing signal emotion_updated, ImportError handling, dark theme
- ✅ **Tests globaux : 158/158 passés (100%) en 14.85s** 🎉
  - +21 tests Discord bot
  - Tests précédents intacts (config, model, chat, emotion, memory, etc.)
- ✅ **Documentation complète Phases 7-8**
  - README.md Session 10 mis à jour avec Phases 7-8 détaillées
  - Section chargement manuel IA (80+ lignes)
  - Tableau états système (4 états : Démarrage/Chargement/Chargé/Erreur)
  - Scripts copiés : bot.py, test_discord_bot.py, app.py
  - docs/INDEX.md mis à jour
  - README.md racine mis à jour (4 sections : Sessions, Guides, Changelog, Status)
- ✅ **Phase 9 : Fix Chargement GPU (CUDA) - 45 minutes**
  - ❌ **Problème** : Modèle chargeait sur RAM CPU au lieu de VRAM GPU malgré config correcte
  - 🔍 **Diagnostic** : llama-cpp-python v0.3.16 installé SANS support CUDA (wheel précompilé CPU-only)
  - ✅ **Solution** : Recompilation depuis sources avec CMAKE_ARGS="-DGGML_CUDA=on"
  - **Compilation réussie** :
    * Durée : 18min 40s
    * CUDA Toolkit v12.9.86
    * Visual Studio 2022 (MSVC 19.44.35217.0)
    * 1349 warnings (normaux), 0 erreurs
    * DLL CUDA générées : ggml-cuda.lib/dll ✅
  - **Tests de vérification** :
    * llama_supports_gpu_offload() → True ✅
    * GPU détecté : NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM)
    * Modèle charge 35 layers GPU (balanced profile)
    * VRAM utilisée : ~3-4 GB pendant inférence
  - **Performance** :
    * Avant (CPU) : ~20s pour 100 tokens (~5 tok/s)
    * Après (GPU) : ~3s pour 100 tokens (~33 tok/s)
    * **Amélioration : 6-7x plus rapide !** ⚡
  - **Documentation complète** :
    * docs/sessions/session_10_ai_chat/phase_9_cuda_fix/README.md
    * docs/sessions/session_10_ai_chat/phase_9_cuda_fix/CUDA_INSTALLATION_GUIDE.md
    * Guide installation CUDA complet (Windows, prérequis, dépannage)
    * Scripts diagnostics (test_cuda_support.py, monitor_vram.py)
- 🎮 **Kira utilise maintenant la VRAM GPU (RTX 4050) pour générer les réponses 6-7x plus vite !** ✨🚀
- 🎭 **Kira peut maintenant discuter sur Discord ET dans le Workly GUI avec contrôle utilisateur complet et accélération GPU !** ✨👁️🤖🎮✨

### Version 0.8.0-alpha (23 octobre 2025) ✨ **NOUVEAU - SESSION 10 (Phase 6) - CHAT 8**
- ✅ **Session 10 - IA Conversationnelle (Chat 8 - Phase 6) terminée !**
- ✅ **Phase 6 : Emotion Analyzer (1h)**
  - src/ai/emotion_analyzer.py (680 lignes) - Analyseur émotionnel avancé
  - Classe EmotionAnalyzer avec analyse contextuelle complète
  - Dataclass EmotionResult (emotion, intensity 0-100, confidence 0-100, keywords_found, context_score, timestamp)
  - **Analyse émotionnelle avancée** :
    * Détection 6 émotions avec mots-clés pondérés (poids 1-3)
    * Support emojis français (😊😠😢😲😂)
    * Calcul intensité 0-100 basé sur densité mots-clés
    * Bonus contexte renforcé (+10-20% si ≥2 mots-clés)
  - **Calcul confiance multi-facteurs** :
    * 40% intensité détectée
    * 30% nombre mots-clés trouvés
    * 30% score contextuel historique
  - **Analyse contextuelle avec historique** :
    * Historique émotionnel par utilisateur (deque max size 5)
    * Score contextuel dynamique (50-80/100 selon cohérence)
    * Détection transitions émotionnelles
  - **Lissage des transitions (smoothing)** :
    * Smoothing factor configurable 0-1 (défaut 0.3)
    * Lissage intensité si émotion répétée
    * Réduction 10% lors changement émotion
    * Transitions douces pour expérience VRM fluide
  - **Mapping VRM Blendshapes complet** :
    * 6 Blendshapes Unity : Joy/Angry/Sorrow/Surprised/Fun/Neutral
    * Multiplicateurs d'intensité personnalisés par émotion (0.5-1.2x)
    * Seuils minimaux et ranges optimaux configurables
    * Valeurs VRM 0.0-1.0 (conversion automatique)
    * Flag 'recommended' si dans range optimal
  - Singleton pattern : get_emotion_analyzer()
  - tests/test_emotion_analyzer.py - 39 tests unitaires
  - ✅ **Tous les tests passent (39/39 en 0.11s) !**
- ✅ **Tests globaux : 137/137 passés (100%) en 15.43s** 🎉
  - +39 tests emotion analyzer
  - Tests précédents intacts (config, model, chat engine, memory, etc.)
- ✅ **Documentation complète Phase 6**
  - README.md Session 10 mis à jour avec détails Phase 6
  - Section complète dans README.md (150+ lignes)
  - Tableau comparatif EmotionDetector vs EmotionAnalyzer
  - Scripts copiés : emotion_analyzer.py, test_emotion_analyzer.py
  - docs/INDEX.md mis à jour (arborescence + scripts)
  - README.md racine mis à jour (4 sections : Sessions, Guides, Changelog, Status)
- 🎭 **Kira analyse maintenant les émotions avec précision ! Intensité, confiance, contexte et mapping VRM complet !** ✨

### Version 0.7.0-alpha (23 octobre 2025) ✨ **NOUVEAU - SESSION 10 (Phases 3-5) - CHAT 7**
- ✅ **Session 10 - IA Conversationnelle (Chat 7 - Phases 3-5) terminée !**
- ✅ **Phase 3 : Configuration IA (45 min)**
  - src/ai/config.py (420 lignes) - AIConfig avec dataclass
  - 3 profils GPU prédéfinis : performance/balanced/cpu_fallback
  - GPU_PROFILES avec n_gpu_layers, n_ctx, estimations vitesse/VRAM
  - Chargement depuis JSON avec valeurs par défaut
  - Validation complète paramètres (context_limit, temperature, top_p, max_tokens)
  - Switch profil dynamique avec get_gpu_params()
  - Singleton pattern : get_config()
  - data/config.json étendu avec section "ai" complète
  - System prompt détaillé pour personnalité Kira
  - tests/test_ai_config.py - 31 tests unitaires
  - ✅ **Tous les tests passent (31/31 en 0.21s) !**
- ✅ **Phase 4 : Model Manager (1.5h)**
  - src/ai/model_manager.py (470 lignes) - Gestionnaire LLM + GPU
  - Classe ModelManager avec détection GPU automatique (pynvml)
  - **GPU détecté : NVIDIA GeForce RTX 4050 Laptop GPU (6.0 GB VRAM, Driver 581.57)**
  - Chargement modèle avec profil GPU configuré (llama-cpp-python)
  - Auto-fallback CPU si OOM GPU
  - Génération texte avec paramètres configurables
  - Déchargement propre avec unload_model()
  - Monitoring VRAM temps réel avec get_gpu_status()
  - Singleton pattern : get_model_manager()
  - tests/test_model_manager.py - 23 tests unitaires (avec mocks)
  - ✅ **Tous les tests passent (23/23 en 1.32s) !**
- ✅ **Phase 5 : Chat Engine (2h)**
  - src/ai/chat_engine.py (480 lignes) - Moteur conversationnel unifié
  - Classe ChatEngine orchestrant mémoire + modèle + émotions
  - Classe EmotionDetector avec 6 émotions (joy/angry/sorrow/surprised/fun/neutral)
  - Détection par mots-clés français + emojis
  - Format prompt ChatML (Zephyr) avec historique
  - Construction prompts : <|system|> + <|user|> + <|assistant|>
  - Génération réponses avec contexte historique (10 messages par défaut)
  - Sauvegarde automatique conversations dans SQLite
  - Support multi-utilisateurs (isolation complète)
  - Support multi-sources (desktop, discord)
  - Dataclass ChatResponse (response, emotion, tokens_used, context_messages, processing_time)
  - Singleton pattern : get_chat_engine()
  - tests/test_chat_engine.py - 23 tests unitaires
  - tests/test_integration_phase5.py - Test intégration complet
  - ✅ **Tous les tests passent (23/23 en 0.33s) !**
- ✅ **Tests globaux : 97/97 passés (100%) en 36.64s** 🎉
  - 31 tests config
  - 23 tests model manager
  - 23 tests chat engine
  - 11 tests memory
  - 5 tests unity bridge
  - 4 tests config général
- ✅ **Documentation complète Chat 7**
  - CHAT_ENGINE_GUIDE.md - Guide utilisation complet
  - Transition Chat 7 → Chat 8 complète (5 fichiers)
  - CONTEXT_FOR_NEXT_CHAT.md avec instructions Phases 6-9
  - CURRENT_STATE.md avec architecture complète
  - prompt_transition.txt prêt pour Chat 8
  - Scripts copiés : config.py, model_manager.py, chat_engine.py, tests
  - docs/INDEX.md, README.md, chat_transitions/README.md mis à jour
- 🤖 **Kira peut maintenant parler intelligemment ! Système IA 100% fonctionnel !** 💬✨

### Version 0.6.0-alpha (22 octobre 2025) ✨ **SESSION 10 (Phases 1-2) - CHAT 6**
- ✅ **Session 10 - IA Conversationnelle (Chat 6 - Phases 1-2) démarrée !**
- ✅ **Phase 1 : Architecture de Base (30 min)**
  - Création dossiers : src/ai/, src/discord_bot/, src/auth/, models/
  - Fichiers __init__.py pour tous les modules
  - Modèle LLM copié : models/zephyr-7b-beta.Q5_K_M.gguf (6.8 GB, Mistral 7B)
  - Configuration : .env, .env.example, .gitignore étendu
  - requirements.txt avec 8 nouvelles dépendances (llama-cpp-python, discord.py, pyotp, etc.)
  - Documentation : PLAN_SESSION_10.md (14 phases détaillées), README.md Session 10
- ✅ **Phase 2 : Base de Données & Mémoire (1h)**
  - src/ai/memory.py (430 lignes) - Système conversationnel complet
  - Classe ConversationMemory avec 10 méthodes CRUD
  - Base SQLite : data/chat_history.db (7 colonnes, 4 indexes optimisés)
  - Singleton pattern avec get_memory()
  - Context manager thread-safe
  - Support multi-source (desktop + discord)
  - Support émotions pour chaque interaction
  - tests/test_memory.py - 11 tests unitaires
  - ✅ **Tous les tests passent (11/11 en 0.71s) !**
- ✅ **Documentation complète Chat 6**
  - Transition Chat 6 → Chat 7 complète (5 fichiers)
  - CONTEXT_FOR_NEXT_CHAT.md avec instructions détaillées Phase 3-5
  - CURRENT_STATE.md avec état technique complet
  - prompt_transition.txt prêt à copier
  - docs/INDEX.md, README.md mis à jour
- ✅ **Dépendances installées** : llama-cpp-python, pynvml, discord.py, pyotp, python-dotenv, qrcode, pillow, psutil
- 🤖 **Bases solides pour IA conversationnelle ! Prochaine étape : Config + LLM + Chat Engine !** ✨

### Version 0.5.0-alpha (22 octobre 2025) ✨ **SESSION 9**
- ✅ **Session 9 - Mouvements de tête + Réorganisation interface terminée !**
- ✅ VRMHeadMovementController.cs avec système de Coroutines Unity
- ✅ Animation SmoothStep pour mouvements naturels (yaw/pitch)
- ✅ Mouvements aléatoires : yaw (-5° à +5°), pitch (-2.5° à +2.5°)
- ✅ Contrôle fréquence (3-10s) et amplitude (2-10°) dans l'interface
- ✅ **Interface réorganisée en 3 onglets** : Expressions, Animations, Options
- ✅ **3 boutons reset contextuels** (un par onglet avec valeurs par défaut)
- ✅ Checkbox "Auto Head Movement" dans l'onglet Animations
- ✅ 2 sliders pour paramétrer fréquence et amplitude
- ✅ Commande IPC `set_auto_head_movement` (enabled, min_interval, max_interval, max_angle)
- ✅ **3 bugs critiques résolus** :
  - Conflit VRMAutoBlinkController (double clignement)
  - État bouton VRM après déconnexion Unity
  - Code dupliqué lors du refactoring (~137 lignes nettoyées)
- ✅ Documentation complète (4 guides techniques + scripts archivés)
- ✅ Transition Chat 6 préparée avec CONTEXT_FOR_NEXT_CHAT
- 🎭 **L'avatar bouge maintenant naturellement la tête + interface moderne et organisée !** ✨

### Version 0.4.0-alpha (21 octobre 2025) ✨ **SESSION 8**
- ✅ **Session 8 - Clignement automatique terminée !**
- ✅ VRMAutoBlinkController.cs avec système de coroutines Unity
- ✅ Animation SmoothStep (courbes de Hermite cubiques) pour réalisme maximal
- ✅ Timing naturel paramétrable (2-5s entre clignements, 160ms par cycle)
- ✅ Checkbox "Auto Blink" dans l'onglet Options de l'interface Python
- ✅ Sauvegarde automatique de configuration (config.json)
- ✅ Commande IPC `set_auto_blink` (true/false)
- ✅ **5 problèmes majeurs résolus** :
  - Blendshapes non appliqués (mapping Blink)
  - Animation trop lente (bypass Lerp)
  - Animation robotique (SmoothStep vs Lerp)
  - Configuration non sauvegardée
  - Unity ne reçoit pas commandes (délai 2.5s)
- ✅ Documentation technique massive (TECHNICAL_GUIDE.md 900+ lignes)
- ✅ Guide résolution problèmes (TROUBLESHOOTING.md complet)
- ✅ Transition Chat 4 documentée avec CONTEXT_FOR_NEXT_CHAT
- 👁️ **L'avatar cligne maintenant naturellement des yeux !** ✨

### Version 0.3.0-alpha (20 octobre 2025) ✨ **SESSION 7**
- ✅ **Session 7 - Animations fluides terminée !**
- ✅ VRMBlendshapeController.cs v2.0 avec Lerp interpolation
- ✅ Transitions smooth entre expressions (dictionnaires currentValues/targetValues)
- ✅ Slider de vitesse ajustable (1.0-10.0, défaut 3.0)
- ✅ Interface 100% en français
- ✅ Icône personnalisée (avec fix AppUserModelID Windows)
- ✅ Système de modèle VRM par défaut (menu-based)
- ✅ Chargement/déchargement dynamique (toggle)
- ✅ Thread-safety complet (Queue<Action> pattern)
- ✅ 7 bugs résolus (calibration slider, thread-safety, etc.)
- ✅ Documentation massive (README, TRANSITIONS_GUIDE 900+ lignes, SESSION_SUCCESS)
- ✅ Transition Chat 3 → Chat 4 documentée
- 🎭 **L'avatar anime maintenant ses expressions de façon fluide !** ✨

### Version 0.2.0-alpha (19 octobre 2025)
- ✅ **Session 6 - Expressions faciales terminée !**
- ✅ VRMBlendshapeController.cs v1.6 avec contrôle expressions VRM
- ✅ Interface GUI avec onglet "Expressions"
- ✅ 5 sliders pour émotions (joy, angry, sorrow, surprised, fun)
- ✅ Contrôle précis 0-100% pour chaque expression
- ✅ Bouton "Reset All Expressions"
- ✅ Commandes IPC : set_expression, reset_expressions
- ✅ Documentation Session 6 complète
- 🎭 **L'avatar peut maintenant exprimer des émotions !** 😊😠😢😲😄

### Version 0.1.0-alpha (18 octobre 2025)
- ✅ **MVP terminé !**
- ✅ Interface Python Qt fonctionnelle
- ✅ Communication IPC Python ↔ Unity stable
- ✅ Chargement et affichage de modèles VRM
- ✅ Documentation complète par sessions (0-5)
- ✅ Configuration Git optimisée pour Unity
- ✅ 8 tests unitaires Python

### Version 0.13.0-alpha (9 novembre 2025) ✨ **NOUVEAU - SESSION 12**
- ✅ **Session 12 - Site Web Workly terminée !**
- ✅ **5 pages HTML créées** : Accueil, À propos, CGU, Confidentialité + API (archivée)
- ✅ **Design violet (#903f9e)** : Dark mode futuriste avec animations scroll
- ✅ **Responsive mobile-first** : Breakpoint 768px, menu hamburger
- ✅ **CSS moderne (557 lignes)** : Variables CSS, animations fade-in, transitions hover
- ✅ **JavaScript vanilla (260 lignes)** : IntersectionObserver, smooth scroll, easter egg
- ✅ **Performance optimisée** : threshold 0.05, rootMargin +100px, transition 0.3s
- ✅ **Légal complet** : Licence MIT-NC, RGPD, CGU (14 sections), Confidentialité (13 sections)
- ✅ **6 développement phases documentées** : 4 complétées (MVP, Expressions, IA, Optimisations), 2 planifiées (Audio, Interactions)
- ✅ **Corrections appliquées** :
  - Licence MIT → MIT-NC (commercial usage interdit)
  - Project rename : Kira → Workly (30+ occurrences)
  - Emoji cleanup : Navigation propre, emojis dans feature cards
  - API page archivée : Moved to archive/ avec guide réutilisation
  - Phases synchronisées : docs/README.md → about.html
  - Animations optimisées : Scroll (threshold 0.1→0.05, rootMargin -100px→+100px), Hover (300ms)
- ✅ **Hébergement préparé** : Elsites avec support HTTPS/SSL
- ✅ **Documentation complète** :
  - README.md (200+ lignes) : Structure, usage, déploiement
  - Session 12 README.md (300+ lignes) : Session complète documentée
  - TECHNICAL_GUIDE.md : Guide personnalisation (couleurs, pages, animations)
- ✅ **Testé localement** : Python HTTP server (ports 8000, 8001)
- ✅ **Statistiques** : ~5h développement, ~2200 lignes HTML/CSS/JS
- 🎭 **Site web professionnel pour Workly prêt pour production !** 🌐✨
- 🎭 **Premier avatar affiché avec succès !**

---

**🎊 Status actuel : Chat 10 TERMINÉ ! Session 11 Phases 1-3 COMPLÉTÉES (Memory Profiling, LLM Cache -17%, IPC Batching -79%) + Session 12 COMPLÉTÉE (Site Web Workly 🌐💜) ! Workly dispose maintenant d'un baseline mémoire stable (pas de leaks), warming cache LLM activé (+14% speed), communication Python ↔ Unity 10x plus rapide (batching +907%), et site web professionnel prêt pour production ! Documentation transition Chat 10 → Chat 11 complète dans `docs/chat_transitions/chat_10_session_11_phases_1_3/` ! 🔥📡⚡🌐💜✨🎊**

**🚀 Prochaine étape (Chat 11 - Session 11 Phases 4-6) : CPU Optimization (auto-détection threads), GPU Profiling & Tuning (monitoring VRAM), Tests & Documentation finale (validation gains +30-40%) ! 🧵⚡🎮**

⭐ **N'oubliez pas de mettre une étoile si ce projet vous plaît !** ⭐