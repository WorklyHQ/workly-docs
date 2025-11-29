# 📑 INDEX - Documentation Workly

**Vue d'ensemble rapide de toute la documentation**

---

## 🗂️ Organisation par sessions

```
docs/
│
├── 📄 README.md                                    ← Commence ici !
├── 📄 START_HERE.md                                ← Point d'entrée
├── 📄 SESSIONS.md                                  ← ✨ Liste détaillée des 12 sessions
├── 📄 CHANGELOG.md                                 ← 📋 Historique complet des versions
├── 📄 README_OLD_FULL.md                           ← 🗂️ Ancien README complet (archive)
├── 📄 DOCUMENTATION_CHECKLIST.md                   ← ⚠️ Checklist docs (IMPORTANT!)
├── 📄 AI_DOCUMENTATION_PROMPT.md                   ← 🤖 Instructions IA (système)
│
├── ⚠️ État actuel → chat_transitions/chat_12_gpu_ui_discord/CURRENT_STATE.md
│   Chat 12 (Interface GPU Profiles + Logs + Discord + Fixes) ✅ TERMINÉ
│   Phase 1-2 : UI GPU Profiles + Logs | Phase 3 : Fixes critiques CUDA + Discord auto-reply
│
├── 📁 .github/                                    ← Templates GitHub
│   └── PULL_REQUEST_TEMPLATE.md                    Template PR avec checklist doc
│
├── 🌐 Site Web (../web/)                          ← Site officiel Workly 💜 ✨ **SESSION 12 COMPLÉTÉE !**
│   ├── index.html                                  Page d'accueil (hero, 6 features, 3 tech cards, CTA)
│   ├── pages/                                      Pages du site
│   │   ├── about.html                              À propos (6 phases développement, architecture)
│   │   ├── terms.html                              CGU (MIT-NC, 14 sections)
│   │   └── privacy.html                            Confidentialité (RGPD, 13 sections, 100% local)
│   ├── archive/                                    Pages archivées
│   │   ├── api.html                                Endpoints Discord (archivé, non utilisé)
│   │   └── README.md                               Guide réutilisation
│   ├── assets/                                     Ressources statiques
│   │   ├── css/style.css                           557 lignes (violet #903f9e, animations)
│   │   ├── js/main.js                              260 lignes (IntersectionObserver, interactions)
│   │   └── images/                                 Images et icônes (à venir)
│   └── README.md                                   Documentation complète (200+ lignes)
│
├── 📁 sessions/                                   ← 🗂️ Toutes les sessions de développement
│   ├── session_0_git_configuration/                ← Session 0 : Configuration Git ⚙️
│   │   ├── README.md                               Vue d'ensemble
│   │   └── GIT_UNITY_FIX.md                        Fix .gitignore Unity
│   │
│   ├── session_1_setup/                            ← Session 1 : Setup Python
│   │   ├── SUCCESS_SESSION_1.md                    Récapitulatif succès
│   │   └── architecture.md                         Architecture globale
│   │
│   ├── session_2_unity_installation/               ← Session 2 : Unity 2022.3 LTS
│   │
│   ├── session_2_unity_installation/               ← Session 2 : Unity 2022.3 LTS
│   │   ├── UNITY_INSTALL_GUIDE.md                  Guide installation Unity
│   │   ├── UNITY_CREATE_PROJECT.md                 Création du projet
│   │   └── UNITY_PROJECT_SETUP.md                  Configuration du projet
│   │
│   ├── session_3_univrm_installation/              ← Session 3 : UniVRM
│   │   ├── UNIVRM_INSTALL.md                       Installation UniVRM (Git)
│   │   └── UNIVRM_INSTALL_MANUAL.md                Installation manuelle (.unitypackage) ✅
│   │
│   ├── session_4_python_unity_connection/          ← Session 4 : IPC Python ↔ Unity
│   │   ├── UNITY_PYTHONBRIDGE_SETUP.md             Setup du PythonBridge
│   │   ├── TEST_CONNECTION.md                      Test de connexion
│   │   ├── DEBUG_CONNECTION.md                     Debug connexion
│   │   └── FIX_SCRIPT_NOT_RUNNING.md               Fix checkbox Unity ✅
│   │
│   ├── session_5_vrm_loading/                      ← Session 5 : Chargement VRM ✅
│   │   ├── SESSION_VRM_LOADING_SUCCESS.md          Récapitulatif complet
│   │   ├── LOAD_VRM_MODEL.md                       Guide chargement VRM
│   │   ├── README.md                               Vue d'ensemble session 5
│   │   └── scripts/
│   │       └── VRMLoader.cs                        Script de référence
│   │
│   ├── session_6_expressions/                      ← Session 6 : Expressions faciales 😊 ✅
│   │   ├── README.md                               Vue d'ensemble session 6
│   │   ├── BLENDSHAPES_GUIDE.md                    Guide technique blendshapes
│   │   ├── UNITY_SETUP_GUIDE.md                    Configuration Unity pas-à-pas
│   │   ├── SESSION_SUCCESS.md                      Récapitulatif succès
│   │   └── scripts/
│   │       ├── VRMBlendshapeController.cs          Script de référence
│   │       └── VRMBlendshapeController_V1.6_BACKUP.cs  Backup version 1.6
│   │
│   ├── session_7_animations/                       ← Session 7 : Animations & Transitions 🎬 ✅
│   │   ├── README.md                               Vue d'ensemble session 7
│   │   ├── TRANSITIONS_GUIDE.md                    Guide technique Lerp & transitions
│   │   ├── SESSION_SUCCESS.md                      Récapitulatif succès complet
│   │   └── scripts/
│   │       ├── VRMBlendshapeController.cs          Script de référence (avec Lerp)
│   │       └── app.py                              GUI Python avec slider vitesse
│   │
│   ├── session_8_auto_blink/                       ← Session 8 : Clignement Automatique 👁️ ✅
│   │   ├── README.md                               Vue d'ensemble session 8
│   │   ├── BLINK_GUIDE.md                          Guide rapide d'implémentation
│   │   ├── TECHNICAL_GUIDE.md                      Architecture détaillée SmoothStep
│   │   ├── TROUBLESHOOTING.md                      Résolution de problèmes
│   │   └── scripts/
│   │       ├── VRMAutoBlinkController.cs           Contrôleur clignement (SmoothStep)
│   │       ├── VRMBlendshapeController.cs          Script avec mapping Blink
│   │       ├── PythonBridge.cs                     Serveur IPC (commande set_auto_blink)
│   │       ├── unity_bridge.py                     Client IPC Python
│   │       ├── config.py                           Config auto_blink
│   │       └── app.py                              GUI avec checkbox clignement
│   │
│   ├── session_9_head_movements/                   ← Session 9 : Mouvements Tête + Réorg UI 🎭 ✅
│   │   ├── README.md                               Vue d'ensemble session 9
│   │   ├── INTERFACE_REORGANIZATION.md             Guide réorganisation 3 onglets
│   │   ├── HEAD_MOVEMENT_GUIDE.md                  Guide technique (SmoothStep, Coroutine)
│   │   ├── DEBUG_ISSUES.md                         Problèmes résolus (VRMAutoBlinkController, déconnexion)
│   │   └── scripts/
│   │       ├── VRMHeadMovementController.cs        Contrôleur mouvements de tête
│   │       ├── PythonBridge.cs                     IPC (commande set_auto_head_movement)
│   │       ├── app.py                              Interface 3 onglets (Expressions, Animations, Options)
│   │       ├── unity_bridge.py                     Client IPC Python
│   │       └── config.py                           Config head_movement
│   │
   └── session_10_ai_chat/                         ← Session 10 : IA Conversationnelle (Kira) 🤖 ✅ TERMINÉE
       ├── README.md                               Vue d'ensemble session 10
       ├── PLAN_SESSION_10.md                      Plan complet détaillé (14 phases)
       ├── CHAT_ENGINE_GUIDE.md                    Guide utilisation Chat Engine ✅ (Phase 5)
       ├── phase_9_cuda_fix/                       ← Phase 9 : Fix chargement GPU (CUDA) 🎮 ✅
       │   ├── README.md                           Résolution problème VRAM
       │   └── CUDA_INSTALLATION_GUIDE.md          Guide installation CUDA complet
       ├── phase_10_gui_discord/                   ← Phase 10 : Interface GUI Discord Control 🤖 ✅ (Simplifiée + Menu Options)
       │   ├── README.md                           Vue d'ensemble Phase 10 + note simplification
       │   ├── SIMPLIFICATION.md                   Documentation détaillée simplification UI
       │   ├── MENU_OPTIONS.md                     Menu Options : Configurer Token & Salons 🔧 ✨
       │   └── GUI_DISCORD_GUIDE.md                Guide utilisateur Discord bot (mis à jour)
       └── scripts/                                Scripts de référence (Phases 1-10)
           ├── config.py                           Configuration IA ✅ (Phase 3)
           ├── model_manager.py                    Gestionnaire LLM + GPU ✅ (Phase 4)
           ├── chat_engine.py                      Chat Engine + Émotions ✅ (Phase 5)
           ├── emotion_analyzer.py                 Analyseur émotionnel avancé ✅ (Phase 6)
           ├── bot.py                              Bot Discord Kira ✅ (Phase 7 + 10)
           ├── test_discord_bot.py                 Tests Discord bot ✅ (Phase 7)
           ├── app.py                              GUI avec Chat + Discord Control ✅ (Phase 8 + 10)
           └── test_gui_discord.py                 Tests GUI Discord ✅ (Phase 10)
│
   ├── session_11_performance/                     ← Session 11 : Optimisations Performance 🔥 ✅ COMPLÈTE (7/7 phases)
   │   ├── README.md                               Vue d'ensemble session 11 (12h, 7 phases)
   │   ├── MEMORY_PROFILING.md                     Phase 1 : Profiling Mémoire ✅
   │   ├── LLM_CACHE_OPTIMIZATION.md               Phase 2 : Optimisation Cache LLM ✅
   │   ├── IPC_OPTIMIZATION.md                     Phase 3 : Optimisation IPC (Batching) ✅
   │   ├── CPU_OPTIMIZATION.md                     Phase 4 : Auto-détection CPU threads ✅
   │   ├── GPU_PROFILING.md                        Phase 5 : GPU Profiling data-driven ✅
   │   ├── PERFORMANCE_SUMMARY.md                  Phase 6 : Tests & Documentation ✅
   │   ├── GPU_AUTO_SWITCHING.md                   Phase 7 : GPU Auto-Switching Universel ✅ ⭐⭐
   │   └── scripts/                                Scripts de profiling et benchmarks
   │       ├── profile_memory.py                   Script profiling RAM/VRAM ✅
   │       ├── benchmark_llm.py                    Benchmarks LLM (4 scénarios) ✅
   │       ├── test_warming.py                     Test warming cache (avant/après) ✅
   │       ├── benchmark_ipc.py                    Benchmark IPC baseline ✅
   │       ├── test_batching.py                    Test comparaison batching ✅
   │       ├── ipc_benchmark_results.txt           Résultats baseline IPC ✅
   │       ├── batching_comparison_results.txt     Résultats comparaison batching ✅
   │       ├── benchmark_cpu_threads.py            Benchmark threads CPU (Phase 4) ✅
   │       └── benchmark_gpu_profiling.py          Benchmark GPU layers (Phase 5) ✅
   │
   ├── session_12_website/                         ← Session 12 : Site Web Workly 🌐 ✅ **TERMINÉE !**
   │   ├── README.md                               Vue d'ensemble session 12 (300+ lignes)
   │   ├── TECHNICAL_GUIDE.md                      Guide technique personnalisation
   │   └── scripts/                                ← (Aucun script, HTML/CSS/JS dans web/)
   │
   ├── session_13_refactoring_workly/              ← Session 13 : Refactoring Desktop-Mate → Workly 🔄 ✅ **TERMINÉE !**
   │   ├── README.md                               Documentation complète refactoring (280+ lignes)
   │   └── scripts/                                Scripts finaux après renommage
   │       ├── main.py                             main.py avec WorklyApp ✅
   │       ├── app.py                              app.py avec classe WorklyApp ✅
   │       ├── config.py                           config.py avec chemins .workly ✅
   │       ├── logger.py                           logger.py avec workly.log ✅
   │       └── config.json                         config.json avec prompt Kira mis à jour ✅
   │
   ├── session_15_sqlite_migration/                ← Session 15 : Migration SQLite (Phase 6) 🗄️ ✅ **TERMINÉE !**
   │   ├── README.md                               Vue d'ensemble session 15 (migration complète)
   │   ├── TECHNICAL_GUIDE.md                      Guide technique architecture SQLite
   │   └── scripts/                                Scripts finaux après migration
   │       ├── database.py                         Wrapper SQLite (792 lignes, 7 tables) ✅
   │       ├── migrate_json_to_sqlite.py           Script migration JSON → SQLite (400 lignes) ✅
   │       ├── memory_manager.py                   MemoryManager migré (689 lignes) ✅
   │       ├── emotion_memory.py                   EmotionMemory migré (566 lignes) ✅
   │       └── personality_engine.py               PersonalityEngine migré (510 lignes) ✅
   │
   └── session_16_bugfixes/                        ← Session 16 : Corrections de Bugs 🐛 ✅ **TERMINÉE !**
       ├── README.md                               Documentation complète bugfixes (420+ lignes)
       └── scripts/                                Scripts finaux après corrections
           ├── logger.py                           Logger UTF-8 (emojis supportés) ✅
           ├── chat_engine.py                      Chat Engine (enable_advanced_ai=True) ✅
           ├── app.py                              GUI (Reset DB + Windows taskbar icon) ✅
           ├── personality_engine.py               PersonalityEngine 100% SQLite ✅
           └── database.py                         Database (add_personality_evolution) ✅
│
├── 📁 chat_transitions/                           ← Transitions entre chats 🔄
│   ├── README.md                                   Historique des chats
│   ├── chat_1_python_unity_start_session_0_to_5/
│   │   ├── CURRENT_STATE.md                        État fin Chat 1
│   │   ├── prompt_chat1_vers_chat_2.txt           Prompt Chat 2
│   │   └── CHAT_SUMMARY.md                         Résumé Chat 1
│   ├── chat_2_expressions_session_6/
│   │   └── ...                                     Transition Session 6
│   ├── chat_3_animations_session_7/
│   │   └── ...                                     Transition Session 7
│   ├── chat_4_session_8_blink/
│   │   ├── README.md                               Vue d'ensemble transition
│   │   ├── CONTEXT_FOR_NEXT_CHAT.md                Contexte complet pour Chat 5
│   │   ├── CURRENT_STATE.md                        État technique actuel
│   │   └── prompt_transition.txt                   Prompt Chat 5
│   ├── chat_5_session_9/
│   │   ├── README.md                               Vue d'ensemble transition
│   │   ├── CONTEXT_FOR_NEXT_CHAT.md                Contexte complet pour Chat 6
│   │   ├── CURRENT_STATE.md                        État technique actuel
│   │   └── prompt_transition.txt                   Prompt Chat 6
│   ├── chat_6_session_10_phases_1_2/               ← Chat 6 : Phases 1-2 ✅
│   │   ├── README.md                               Vue d'ensemble transition
│   │   ├── CONTEXT_FOR_NEXT_CHAT.md                Contexte complet pour Chat 7
│   │   ├── CURRENT_STATE.md                        État technique après Phases 1-2
│   │   ├── CHAT_SUMMARY.md                         Résumé Chat 6 (Phases 1-2)
│   │   └── prompt_transition.txt                   Prompt Chat 7
   ├── chat_7_session_10_phases_3_5/               ← Chat 7 : Phases 3-5 ✅
   │   ├── README.md                               Vue d'ensemble transition
   │   ├── CONTEXT_FOR_NEXT_CHAT.md                Contexte complet pour Chat 8
   │   ├── CURRENT_STATE.md                        État technique après Phases 3-5
   │   ├── CHAT_SUMMARY.md                         Résumé Chat 7 (Phases 3-5)
   │   └── prompt_transition.txt                   Prompt Chat 8
   ├── chat_8_session_10_phase_9/                  ← Chat 8 : Phases 6-9 ✅
   │   ├── README.md                               Vue d'ensemble transition
   │   ├── CONTEXT_FOR_NEXT_CHAT.md                Contexte complet pour Chat 9
   │   ├── CURRENT_STATE.md                        État technique après Phases 6-9
   │   └── prompt_transition.txt                   Prompt Chat 9
   ├── chat_9_session_10_phase_10/                 ← Chat 9 : Phase 10 ✅
   │   ├── CURRENT_STATE.md                        État technique après Phase 10
   │   └── (pas de prompt next si Session 10 terminée)
   ├── chat_9_bugfixes_gpu/                        ← Chat 9 : Bugfixes & GPU Optimizations ✅ **NOUVEAU**
   │   ├── README.md                               Documentation complète (6 bugs, 5 features)
   │   ├── CURRENT_STATE.md                        État technique v0.12.0-alpha
   │   ├── CONTEXT_FOR_NEXT_CHAT.md                Contexte Session 11 (Performance)
   │   └── prompt_transition.txt                   Prompt Chat 10
   └── chat_10_session_11_phases_1_3/              ← Chat 10 : Session 11 Phases 1-3 ✅ **NOUVEAU**
       ├── README.md                               Documentation complète (3 phases terminées)
       ├── CURRENT_STATE.md                        État technique après Phases 1-3
       └── CONTEXT_FOR_NEXT_CHAT.md                Contexte Chat 11 (Phases 4-6)
│
└── 📁 1st/                                        ← Archives premières notes
    ├── START_HERE.md
    ├── QUICKSTART.md
    ├── PROJECT_SUMMARY.md
    ├── NOTES.md
    └── SUCCESS.md

```

---

## 🚀 Démarrage rapide

### Pour commencer le projet de zéro :

0. 📍 `chat_transitions/chat_9_session_10_phase_10/CURRENT_STATE.md` - État actuel complet du projet
1. ⚙️ `sessions/session_0_git_configuration/` - Configurer Git pour Unity
2. 📖 `README.md` - Vue d'ensemble
3. 📁 `sessions/session_1_setup/` - Setup Python
4. 📁 `sessions/session_2_unity_installation/` - Installer Unity
5. 📁 `sessions/session_3_univrm_installation/` - Installer UniVRM
6. 📁 `sessions/session_4_python_unity_connection/` - Connecter Python et Unity
7. 📁 `sessions/session_5_vrm_loading/` - Charger les modèles VRM
8. 📁 `sessions/session_6_expressions/` - Implémenter expressions faciales (blendshapes)

### Pour reprendre après une pause :

- **État du projet** → `chat_transitions/chat_10_session_11_phases_1_3/CURRENT_STATE.md`
- **Contexte Chat 11** → `chat_transitions/chat_10_session_11_phases_1_3/CONTEXT_FOR_NEXT_CHAT.md`
- **Prompt Chat 11** → `chat_transitions/chat_10_session_11_phases_1_3/README.md`

### Pour résoudre un problème spécifique :

- **Problèmes Git avec Unity ?** → `sessions/session_0_git_configuration/GIT_UNITY_FIX.md`
- **Unity ne démarre pas ?** → `sessions/session_2_unity_installation/UNITY_INSTALL_GUIDE.md`
- **UniVRM erreur ?** → `sessions/session_3_univrm_installation/UNIVRM_INSTALL_MANUAL.md`
- **Python ne se connecte pas ?** → `sessions/session_4_python_unity_connection/DEBUG_CONNECTION.md`
- **Script Unity inactif ?** → `sessions/session_4_python_unity_connection/FIX_SCRIPT_NOT_RUNNING.md`
- **Erreur de chargement VRM ?** → `sessions/session_5_vrm_loading/SESSION_VRM_LOADING_SUCCESS.md`

---

## 📊 Progression du projet

### 🎊 Chat 1 - Terminé (Sessions 0-5)

| Session | Objectif                 | Statut     | Fichiers clés                                                     |
| ------- | ------------------------ | ---------- | ----------------------------------------------------------------- |
| **0**   | Configuration Git Unity  | ✅ Complet | `sessions/session_0_git_configuration/GIT_UNITY_FIX.md`           |
| **1**   | Setup Python + GUI       | ✅ Complet | `sessions/session_1_setup/SUCCESS_SESSION_1.md`                   |
| **2**   | Installation Unity       | ✅ Complet | `sessions/session_2_unity_installation/`                          |
| **3**   | Installation UniVRM      | ✅ Complet | `sessions/session_3_univrm_installation/UNIVRM_INSTALL_MANUAL.md` |
| **4**   | Connexion Python ↔ Unity | ✅ Complet | `sessions/session_4_python_unity_connection/`                     |
| **5**   | Chargement VRM           | ✅ Complet | `sessions/session_5_vrm_loading/SESSION_VRM_LOADING_SUCCESS.md`   |

**Résumé Chat 1 :** `chat_transitions/chat_1.../CHAT_SUMMARY.md`

### 🎊 Chat 2 - Terminé (Session 6)

| Session | Objectif                           | Statut     | Fichiers clés                                                      |
| ------- | ---------------------------------- | ---------- | ------------------------------------------------------------------ |
| **6**   | Expressions faciales (blendshapes) | ✅ Complet | `sessions/session_6_expressions/README.md`, `BLENDSHAPES_GUIDE.md` |

### 🎊 Chat 3 - Terminé (Session 7)

| Session | Objectif                         | Statut     | Fichiers clés                                                     |
| ------- | -------------------------------- | ---------- | ----------------------------------------------------------------- |
| **7**   | Animations & Transitions fluides | ✅ Complet | `sessions/session_7_animations/README.md`, `TRANSITIONS_GUIDE.md` |

### 🎊 Chat 4 - Terminé (Session 8)

| Session | Objectif                        | Statut     | Fichiers clés                                                            |
| ------- | ------------------------------- | ---------- | ------------------------------------------------------------------------ |
| **8**   | Clignement automatique des yeux | ✅ Complet | `sessions/session_8_auto_blink/TECHNICAL_GUIDE.md`, `TROUBLESHOOTING.md` |

### 🎊 Chat 5 - Terminé (Session 9)

| Session | Objectif                                   | Statut     | Fichiers clés                                                           |
| ------- | ------------------------------------------ | ---------- | ----------------------------------------------------------------------- |
| **9**   | Mouvements Tête + Réorganisation Interface | ✅ Complet | `sessions/session_9_head_movements/README.md`, `HEAD_MOVEMENT_GUIDE.md` |

### 🚀 Chat 9 - TERMINÉ (Bugfixes & GPU Optimizations)

| Chat  | Objectif                     | Statut         | Fichiers clés                           |
| ----- | ---------------------------- | -------------- | --------------------------------------- |
| **9** | Bugfixes & Optimisations GPU | ✅ **COMPLET** | `chat_transitions/chat_9_bugfixes_gpu/` |

**6 bugs critiques résolus** : Input bloqué, sync Discord, sliders GUI, GPU/RAM, compteur messages, venv
**5 features ajoutées** : Typing indicator, compteur session, menu restructuré, doc venv
**Performance** : 25-35 tok/s (5-7x plus rapide), 5.4GB VRAM, 43/43 GPU layers

### 🔥 Chat 10 - EN COURS (Session 11 - Performance Optimizations + Session 12 - Site Web)

| Session | Objectif                             | Statut                | Fichiers clés                      |
| ------- | ------------------------------------ | --------------------- | ---------------------------------- |
| **11**  | Optimisations Performance (6 phases) | 🚧 **EN COURS (3/6)** | `sessions/session_11_performance/` |
| **12**  | Site Web Workly                      | ✅ **COMPLÈTE**       | `sessions/session_12_website/`     |

**Session 11 - Phases complétées** :

- ✅ **Phase 1** : Memory Profiling - Baseline RAM/VRAM établi (pas de memory leaks)
- ✅ **Phase 2** : LLM Cache Optimization - Warming cache (-17% latency, +14% speed)
- ✅ **Phase 3** : Unity IPC Batching - (-79% latency, +907% throughput)

**Session 11 - Phases en cours** :

- 🔜 **Phase 4** : CPU Optimization (n_threads auto-detection)
- 🔜 **Phase 5** : GPU Profiling & Tuning (profils dynamiques)
- 🔜 **Phase 6** : Tests & Documentation finale

**Session 12 - COMPLÈTE** :

- ✅ Site web professionnel avec 5 pages HTML
- ✅ Design violet (#903f9e) dark mode futuriste
- ✅ Responsive mobile-first (768px)
- ✅ Animations scroll optimisées (IntersectionObserver)
- ✅ Licence MIT-NC + RGPD complet
- ✅ Documentation technique complète

**Plan détaillé :** `sessions/session_10_ai_chat/PLAN_SESSION_10.md`

**Phases Session 10** :

- Phase 1 : Architecture de base ✅ TERMINÉE (Chat 6)
- Phase 2 : Base de données & Mémoire ✅ TERMINÉE (Chat 6)
- Phase 3 : Configuration IA ✅ TERMINÉE (Chat 7)
- Phase 4 : Model Manager ✅ TERMINÉE (Chat 7)
- Phase 5 : Chat Engine ✅ TERMINÉE (Chat 7)
- Phase 6 : Emotion Analyzer ✅ TERMINÉE (Chat 8)
- Phase 7 : Discord Bot ✅ TERMINÉE (Chat 8)
- Phase 8 : GUI Chat Desktop ✅ TERMINÉE (Chat 8)
- Phase 9 : Compilation CUDA ✅ TERMINÉE (Chat 8)
- Phase 10 : GUI Discord + Menu Options ✅ TERMINÉE (Chat 9)
- Phases 11-14 : Voir PLAN_SESSION_10.md (si nécessaire)

### 🔮 Chats Futurs (Sessions 11+)

| Session   | Objectif                              | Statut      | Fichiers clés |
| --------- | ------------------------------------- | ----------- | ------------- |
| **11-12** | Vocal Discord + TTS                   | 🚧 Planifié | -             |
| **13-14** | Interactions souris + Idle animations | 🚧 Planifié | -             |

---

## 🔍 Recherche rapide

### Par fonctionnalité

- **État actuel du projet** → `chat_transitions/chat_9_bugfixes_gpu/CURRENT_STATE.md`
- **Résumé Chat 1** → `chat_transitions/chat_1.../CHAT_SUMMARY.md`
- **Configuration Git Unity** → `sessions/session_0_git_configuration/GIT_UNITY_FIX.md`
- **Architecture du projet** → `sessions/session_1_setup/architecture.md`
- **Communication IPC** → `sessions/session_4_python_unity_connection/UNITY_PYTHONBRIDGE_SETUP.md`
- **Chargement VRM** → `sessions/session_5_vrm_loading/LOAD_VRM_MODEL.md`
- **Threading Unity** → `sessions/session_5_vrm_loading/SESSION_VRM_LOADING_SUCCESS.md` (section "Leçons apprises")
- **Expressions faciales (blendshapes)** → `sessions/session_6_expressions/BLENDSHAPES_GUIDE.md`
- **Contrôle blendshapes VRM** → `sessions/session_6_expressions/README.md`
- **Transitions fluides (Lerp)** → `sessions/session_7_animations/TRANSITIONS_GUIDE.md`
- **Modèle VRM par défaut** → `sessions/session_7_animations/README.md`
- **Chargement/Déchargement VRM** → `sessions/session_7_animations/README.md`
- **Clignement automatique des yeux** → `sessions/session_8_auto_blink/TECHNICAL_GUIDE.md`
- **Animation SmoothStep (courbes Hermite)** → `sessions/session_8_auto_blink/TECHNICAL_GUIDE.md`
- **Coroutines Unity (timing)** → `sessions/session_8_auto_blink/TECHNICAL_GUIDE.md`
- **Configuration IA (profils GPU)** → `sessions/session_10_ai_chat/` + `src/ai/config.py`
- **Mémoire conversationnelle (SQLite)** → `src/ai/memory.py`
- **Gestionnaire LLM (chargement modèle)** → `src/ai/model_manager.py`
- **Détection GPU NVIDIA** → `src/ai/model_manager.py` (pynvml)

### Par problème

- **Library/ et Temp/ versionnés par erreur** → `sessions/session_0_git_configuration/GIT_UNITY_FIX.md`
- **Port 5555 déjà utilisé** → `sessions/session_4_python_unity_connection/DEBUG_CONNECTION.md`
- **EnsureRunningOnMainThread error** → `sessions/session_5_vrm_loading/SESSION_VRM_LOADING_SUCCESS.md`
- **Script Unity ne démarre pas** → `sessions/session_4_python_unity_connection/FIX_SCRIPT_NOT_RUNNING.md`

### Scripts de référence

- **VRMLoader.cs** → `sessions/session_5_vrm_loading/scripts/VRMLoader.cs`
- **VRMBlendshapeController.cs v1.6** → `sessions/session_6_expressions/scripts/VRMBlendshapeController_V1.6_BACKUP.cs`
- **VRMBlendshapeController.cs v2.0** → `sessions/session_7_animations/scripts/VRMBlendshapeController.cs` (avec Lerp)
- **VRMAutoBlinkController.cs** → `sessions/session_8_auto_blink/scripts/VRMAutoBlinkController.cs` (SmoothStep)
- **PythonBridge.cs** → `unity/DesktopMateUnity/Assets/Scripts/IPC/PythonBridge.cs` (avec Queue thread-safe)
- **app.py (Session 8)** → `sessions/session_8_auto_blink/scripts/app.py` (avec checkbox clignement)
- **config.py (Session 8)** → `sessions/session_8_auto_blink/scripts/config.py` (avec auto_blink)

---

## 💡 Notes importantes

- ✅ Toujours lire les **récapitulatifs de session** (fichiers `SUCCESS_*.md`) pour comprendre ce qui a été fait
- 🐛 Les fichiers `DEBUG_*.md` et `FIX_*.md` contiennent les solutions aux problèmes rencontrés
- 📝 Les fichiers dans `scripts/` sont des versions propres et commentées du code
- 🗂️ Les sessions sont **indépendantes** mais suivent une progression logique

---

## 📞 Besoin d'aide ?

1. Consulte le `README.md` de la session concernée
2. Regarde les fichiers `DEBUG_` et `FIX_` pour les problèmes connus
3. Vérifie les récapitulatifs `SUCCESS_` pour voir comment c'était censé fonctionner

---

**Dernière mise à jour :** 16 novembre 2025
**Organisation par :** Sessions chronologiques + catégories fonctionnelles
**Sessions complètes :** 0-12 ✅ (Session 12 Site Web Workly COMPLÉTÉE !) 🌐💜
**Chat actuel :** Chat 12 ✅ TERMINÉ (Interface GPU + Logs + CUDA Fix + Discord Fix) → Chat 13 🚀 EN PRÉPARATION (Améliorations IA)
**État Chat 12 :** [chat_transitions/chat_12_gpu_ui_discord/CURRENT_STATE.md](chat_transitions/chat_12_gpu_ui_discord/CURRENT_STATE.md)
**Transition Chat 13 :** [chat_transitions/chat_13_ai_improvements/CURRENT_STATE.md](chat_transitions/chat_13
2_gpu_ui_discord/CURRENT_STATE.md)
