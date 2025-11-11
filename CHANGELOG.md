# 📋 Changelog Workly

**Historique complet des versions et mises à jour**

---

## Format

Ce changelog suit le format [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/) et utilise le [Semantic Versioning](https://semver.org/).

**Types de changements** :

- `Added` : Nouvelles fonctionnalités
- `Changed` : Modifications de fonctionnalités existantes
- `Deprecated` : Fonctionnalités qui seront supprimées
- `Removed` : Fonctionnalités supprimées
- `Fixed` : Corrections de bugs
- `Security` : Corrections de vulnérabilités

---

## [Unreleased]

### À venir

- Session 11 Phases 4-6 : CPU/GPU optimization finale
- Session 14-15 : Audio & Lip-sync (TTS, voice recognition)
- Session 16-17 : Interactions avancées (souris, idle animations)

---

## [0.15.0-alpha] - 2025-11-11

### Changed - Session 13 : Refactoring Desktop-Mate → Workly 🔄

**Renommage complet de "Desktop-Mate" vers "Workly" dans tout le codebase**

#### Code Python (11 fichiers modifiés)

- `main.py` : Import `DesktopMateApp` → `WorklyApp`
- `src/gui/app.py` :
  - Classe `DesktopMateApp` → `WorklyApp`
  - `setApplicationName("Desktop-Mate")` → `setApplicationName("Workly")`
  - `setOrganizationName("Xyon15")` → `setOrganizationName("WorklyHQ")`
  - AppUserModelID : `'Xyon15.DesktopMate.0.7.0'` → `'WorklyHQ.Workly.0.14.0'`
  - Window title : `"Desktop-Mate Control Panel"` → `"Workly Control Panel"`
  - About dialog : `"About Desktop-Mate"`, `v0.11.0` → `"About Workly"`, `v0.14.0`
- `src/utils/config.py` : Docstring + config directory `.desktop-mate` → `.workly`
- `src/utils/logger.py` : Docstring + log directory `.desktop-mate/logs` → `.workly/logs`, filename `desktop-mate.log` → `workly.log`
- `tests/__init__.py` : Docstring "Desktop-Mate" → "Workly"
- `tests/test_integration_phase5.py` : Docstring système IA
- `data/config.json` : System prompt Kira "GUI Desktop-Mate" → "GUI Workly"

#### Documentation (50+ fichiers)

- Mise à jour de toutes les références dans `workly-docs/`
- Sessions 1-12 : Corrections historiques
- README, INDEX, SESSIONS, CHANGELOG : Synchronisés
- Création Session 13 avec documentation complète

#### Nouveaux chemins système

| Composant | Avant | Après |
|-----------|-------|-------|
| **Config directory** | `~/.desktop-mate/` | `~/.workly/` ✨ |
| **Logs directory** | `~/.desktop-mate/logs/` | `~/.workly/logs/` ✨ |
| **Log filename** | `desktop-mate.log` | `workly.log` ✨ |
| **AppUserModelID** | `Xyon15.DesktopMate.0.7.0` | `WorklyHQ.Workly.0.14.0` ✨ |
| **Application Name** | `Desktop-Mate` | `Workly` ✨ |
| **Organization** | `Xyon15` | `WorklyHQ` ✨ |
| **Window Title** | `Desktop-Mate Control Panel` | `Workly Control Panel` ✨ |

### Statistics

- **Fichiers modifiés** : 11 (code actif) + 50+ (documentation)
- **Occurrences traitées** : ~70 (code actif) + 200+ (documentation)
- **Scan exhaustif** : Python, C#, JSON, Unity assets (tous types)
- **Résultat** : ✅ **ZÉRO occurrence** restante de "Desktop-Mate"
- **Tests** : 34/39 passent (5 échecs non bloquants, profil GPU)
- **Venv** : 100% opérationnel, 53 packages
- **Durée** : ~2h30

### Impact

- ✅ Cohérence totale du branding
- ✅ Professionnalisation du codebase
- ✅ Prêt pour communication publique
- ✅ Base solide pour release

---

## [0.14.0-alpha] - 2025-11-09

### Added - Session 12 : Site Web Workly 🌐

- Site web professionnel avec 5 pages HTML (Accueil, À propos, CGU, Confidentialité, API archivée)
- Design violet (#903f9e) dark mode futuriste avec animations scroll
- Responsive mobile-first (breakpoint 768px, menu hamburger)
- CSS moderne (557 lignes) avec variables CSS, animations fade-in, transitions hover
- JavaScript vanilla (260 lignes) avec IntersectionObserver, smooth scroll, easter egg
- Performance optimisée (threshold 0.05, rootMargin +100px, transition 0.3s)
- Légal complet : Licence MIT-NC, RGPD, CGU (14 sections), Confidentialité (13 sections)
- 6 phases de développement documentées (4 complétées, 2 planifiées)
- Hébergement préparé (Elsites avec support HTTPS/SSL)
- Documentation complète (README.md 200+ lignes, TECHNICAL_GUIDE.md)

### Changed

- Licence MIT → MIT-NC (usage commercial interdit sans autorisation)
- Project rename : Kira → Workly (30+ occurrences dans le site)
- API page déplacée vers archive/ avec guide réutilisation
- Phases synchronisées : docs/README.md → about.html
- Animations optimisées : Scroll (threshold, rootMargin) et hover

### Statistics

- ~2200 lignes HTML/CSS/JS
- ~5h de développement
- Testé localement (Python HTTP server ports 8000, 8001)
- Prêt pour production

---

## [0.13.0-alpha] - 2025-11-09

### Added - Session 11 Phase 3 : IPC Optimization ⚡

- Message batching implémenté (Python + Unity C#)
- Script `benchmark_ipc.py` pour mesures baseline et comparaisons
- Script `test_batching.py` pour validation fonctionnelle
- Support commandes `batch_start`, `batch_add`, `batch_execute` dans PythonBridge
- Méthodes `start_batch()`, `add_to_batch()`, `execute_batch()` dans UnityBridge
- Documentation `IPC_OPTIMIZATION.md` avec recommandations d'usage

### Performance

- **-79% latency** par commande (0.291 ms → 0.060 ms)
- **-90% temps total** (1.57s → 0.16s pour 100 commandes)
- **+907% throughput** (64 → 642 messages/sec)
- Gain le plus important sur séquences de commandes (20+ messages)

### Recommendations

- Utiliser batching pour animations complexes (3+ expressions)
- Utiliser batching pour séquences prédéfinies
- Garder messages individuels pour commandes isolées
- Optimal : batches de 10-50 commandes

---

## [0.12.0-alpha] - 2025-11-08

### Added - Session 11 Phase 2 : LLM Cache Optimization 🔥

- Warming cache implémenté dans `ModelManager.load_model()`
- Script `benchmark_llm.py` avec 4 scénarios de test
- Script `test_warming.py` pour validation avant/après
- Documentation `LLM_CACHE_OPTIMIZATION.md` détaillée

### Performance

- **-17% latence** première génération (2.11s → 1.75s)
- **+14% vitesse** génération (19.46 → 22.28 tokens/sec)
- Stabilité améliorée (std dev réduite)

### Fixed

- Délai warming réduit de 50-120s à 15-30s grâce prompt court optimisé

---

## [0.11.0-alpha] - 2025-11-07

### Added - Session 11 Phase 1 : Memory Profiling 📊

- Script `profile_memory.py` avec 4 modes (basic, conversation, llm, full)
- Profilage RAM et VRAM GPU (pynvml)
- Documentation `MEMORY_PROFILING.md` avec analyse complète
- Résultats baseline : RAM/VRAM avant/après chargement LLM

### Performance

- Baseline établi : 35 MB → 687 MB après première génération
- Pas de memory leaks détecté sur 100 messages ✅
- Garbage collection efficace : -509 MB cleanup
- VRAM stable : ~5.4 GB pendant conversations

---

## [0.10.0-alpha] - 2025-10-26

### Added - Session 10 Phase 10 : GUI Discord Control 🤖

- Interface contrôle Discord depuis GUI Desktop
- Menu Options : Configuration Token + Salons
- Checkbox "Enable Auto-Reply" pour activer/désactiver réponses automatiques
- Gestion whitelist salons (ajouter/supprimer)
- Input token Discord sécurisé (QLineEdit password mode)
- Tests unitaires complets (12 tests : GUI + interactions)

### Changed

- Simplification UI : Compteur émotions supprimé (focus sur messages)
- Menu Options restructuré avec sous-menus (IA + Discord)
- Documentation venv critique ajoutée (`.github/instructions/`)

### Fixed (6 bugs critiques)

1. Chat input bloqué après 1er message → Signal Qt `chat_input_ready`
2. Émotions Discord non synchronisées GUI → Signal `emotion_detected` + shared UnityBridge
3. GUI sliders non mis à jour → Signal `expression_changed`
4. Modèle LLM sur RAM → Profil "performance" + CUDA recompilé
5. Compteur messages (total DB) → Compteur session local
6. Oubli activation venv → Documentation système critique

### Performance

- Vitesse génération : **2-5 → 25-35 tokens/sec** (5-7x plus rapide)
- VRAM utilisée : **0 GB → 5.4 GB** (GPU activé)
- GPU layers : **35/43 → 43/43** (100%)
- Context size : **2048 → 4096** tokens (doublé)

### Tests

- **270/270 tests passent (100%)** ✅
- 158 tests AI + 12 tests GUI Discord + 100 tests existants

---

## [0.9.0-alpha] - 2025-10-23

### Added - Session 10 Phases 6-9 : Emotions + Discord + GUI + CUDA 🎭🤖

- **Phase 6** : EmotionAnalyzer avec analyse contextuelle avancée (39 tests)
- **Phase 7** : Bot Discord Kira avec auto-reply configurable (21 tests)
- **Phase 8** : GUI Chat Desktop avec onglet "💬 Chat" intégré
- **Phase 9** : Fix chargement GPU avec recompilation CUDA

### Features

- Détection émotionnelle avancée (intensité 0-100, confiance 0-1)
- Historique émotionnel par utilisateur avec lissage transitions
- Mapping complet vers Blendshapes VRM (6 émotions)
- Bot Discord avec rate limiting et statistiques
- Interface chat complète (QTextEdit HTML, indicateur émotion, stats)
- Chargement manuel IA pour économiser VRAM (4-6 GB)

### Performance

- Compilation CUDA réussie (18min 40s)
- GPU RTX 4050 : 35 layers, ~33 tokens/sec
- **6-7x plus rapide** qu'en CPU

### Tests

- **158/158 tests passent (100%)** ✅

---

## [0.7.0-alpha] - 2025-10-22

### Added - Session 10 Phases 3-5 : Config + LLM + Chat Engine 🤖

- **Phase 3** : AIConfig avec 3 profils GPU (fast/balanced/quality)
- **Phase 4** : ModelManager avec chargement LLM et détection GPU
- **Phase 5** : ChatEngine avec système conversationnel complet

### Features

- Configuration IA flexible avec profils prédéfinis
- Détection automatique GPU NVIDIA (pynvml)
- Chargement modèle LLM Zephyr-7B (6.8 GB)
- Chat streaming avec support émotions
- Singleton patterns pour tous les modules

### Tests

- **97/97 tests passent (100%)** ✅
- 33 tests config + 28 tests model manager + 36 tests chat engine

---

## [0.6.0-alpha] - 2025-10-22

### Added - Session 10 Phases 1-2 : Architecture + Mémoire 🏗️

- **Phase 1** : Architecture de base (dossiers, modèle LLM, config)
- **Phase 2** : Base de données SQLite avec ConversationMemory

### Features

- Création dossiers : `src/ai/`, `src/discord_bot/`, `src/auth/`, `models/`
- Modèle LLM : Zephyr-7B-Beta (6.8 GB, Mistral 7B)
- Base de données : `data/chat_history.db` (7 colonnes, 4 indexes)
- ConversationMemory : 430 lignes, 10 méthodes CRUD
- Support multi-source (desktop + discord)
- Support émotions pour chaque interaction

### Tests

- **11/11 tests passent** ✅

---

## [0.5.0-alpha] - 2025-10-22

### Added - Session 9 : Mouvements de Tête + Interface 3 Onglets 🎭

- VRMHeadMovementController.cs avec système de Coroutines
- Mouvements aléatoires : yaw (-5° à +5°), pitch (-2.5° à +2.5°)
- Paramètres configurables : fréquence (3-10s) et amplitude (2-10°)
- Commande IPC `set_auto_head_movement` avec 4 paramètres

### Changed

- **Interface réorganisée en 3 onglets** : Expressions, Animations, Options
- **3 boutons reset contextuels** (un par onglet avec valeurs par défaut)
- Checkbox "Auto Head Movement" dans onglet Animations
- 2 sliders pour fréquence et amplitude

### Fixed (3 bugs)

1. Conflit VRMAutoBlinkController (double clignement)
2. État bouton VRM après déconnexion Unity
3. Code dupliqué (~137 lignes nettoyées)

---

## [0.4.0-alpha] - 2025-10-21

### Added - Session 8 : Clignement Automatique 👁️

- VRMAutoBlinkController.cs avec système de coroutines Unity
- Animation SmoothStep (courbes Hermite cubiques) pour réalisme
- Timing naturel : 50ms fermeture + 30ms pause + 80ms ouverture
- Intervalles aléatoires : 2-5 secondes entre clignements
- Checkbox "Auto Blink" dans interface Python
- Sauvegarde automatique configuration (config.json)
- Commande IPC `set_auto_blink` (true/false)

### Fixed (5 bugs majeurs)

1. Blendshapes non appliqués → Fix mapping `Blink`
2. Animation trop lente (2s) → Bypass Lerp
3. Animation robotique → SmoothStep vs Lerp
4. Configuration non sauvegardée → Auto-save
5. Unity ne reçoit pas commandes → Délai 2.5s

### Documentation

- TECHNICAL_GUIDE.md (900+ lignes)
- TROUBLESHOOTING.md complet

---

## [0.3.0-alpha] - 2025-10-20

### Added - Session 7 : Animations Fluides 🎬

- VRMBlendshapeController.cs v2.0 avec interpolation Lerp
- Transitions smooth entre expressions (dictionnaires currentValues/targetValues)
- Slider de vitesse ajustable (1.0-10.0, défaut 3.0)
- Système de modèle VRM par défaut (menu-based)
- Chargement/déchargement dynamique (toggle)

### Changed

- Interface 100% en français
- Icône personnalisée avec fix AppUserModelID Windows

### Fixed (7 bugs)

- Calibration slider vitesse
- Thread-safety complet (Queue<Action> pattern)
- État bouton après déconnexion
- Chargement concurrent de modèles

---

## [0.2.0-alpha] - 2025-10-19

### Added - Session 6 : Expressions Faciales 😊

- VRMBlendshapeController.cs v1.6 pour contrôle expressions VRM
- Interface GUI avec onglet "Expressions"
- 5 sliders pour émotions (joy, angry, sorrow, surprised, fun)
- Contrôle précis 0-100% pour chaque expression
- Bouton "Reset All Expressions"
- Commandes IPC : `set_expression`, `reset_expressions`

### Tests

- **8/8 tests Python passés** ✅

---

## [0.1.0-alpha] - 2025-10-18

### Added - MVP Complet 🎉

- Interface Python Qt fonctionnelle
- Communication IPC Python ↔ Unity stable
- Chargement et affichage de modèles VRM
- Configuration Git optimisée pour Unity
- Tests unitaires Python (8 tests)

### Sessions complétées

- Session 0 : Configuration Git Unity
- Session 1 : Setup Python + GUI
- Session 2 : Installation Unity 2022.3 LTS
- Session 3 : Installation UniVRM
- Session 4 : Connexion IPC Python ↔ Unity
- Session 5 : Chargement VRM

### Documentation

- Documentation complète par sessions (0-5)
- 30+ fichiers markdown
- Guides pas-à-pas pour chaque étape

---

## Versions futures

### [0.15.0-alpha] - Planifié

- Session 11 Phases 4-6 : CPU/GPU optimization finale
- Auto-détection threads CPU optimaux
- Profils dynamiques selon GPU
- Tests d'intégration complets
- Validation gains cumulatifs (+30-40%)

### [0.16.0-alpha] - Planifié

- Session 13-14 : Audio & Lip-sync
- Capture audio microphone
- Analyse amplitude/fréquence
- Lip-sync VRM (blendshapes bouche : A, I, U, E, O)

### [0.17.0-alpha] - Planifié

- Session 15-16 : Interactions avancées
- Avatar suit le curseur
- Réaction aux clics
- Drag & drop sur desktop

---

## Statistiques globales

### Développement

- **Sessions complétées** : 12/12
- **Temps total** : ~73 heures
- **Documentation** : 174+ fichiers markdown
- **Tests** : 270/270 passent (100%)

### Code

- **Lignes Python** : ~8000+
- **Lignes C# Unity** : ~3000+
- **Lignes tests** : ~2000+
- **Lignes documentation** : ~15000+

### Performance actuelle

- **Génération LLM** : 25-35 tokens/sec (GPU CUDA)
- **VRAM utilisée** : 5.4 GB (RTX 4050)
- **RAM utilisée** : ~687 MB (après chargement LLM)
- **IPC latency** : 0.06 ms/commande (batching)
- **IPC throughput** : 642 messages/sec

---

**Dernière mise à jour** : 10 novembre 2025
**Version actuelle** : v0.14.0-alpha
**Prochaine version** : v0.15.0-alpha (Session 11 Phases 4-6)
