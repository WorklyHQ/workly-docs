# 🔄 Contexte pour Chat 10 / Session 11

**Date de transition** : 27 octobre 2025  
**Chat source** : Chat 9 (Bugfixes & Optimisations GPU)  
**Chat destination** : Chat 10 (Session 11 - Performance Optimizations)  
**Version actuelle** : v0.12.0-alpha

---

## 📊 État du Projet à la Fin du Chat 9

### ✅ Accomplissements Chat 9

**6 bugs critiques résolus** :
1. ✅ Chat input bloqué après premier message → Signal Qt `chat_input_ready`
2. ✅ Émotions Discord non synchronisées GUI → Signal `emotion_detected` + shared UnityBridge
3. ✅ GUI sliders non mis à jour → Signal `expression_changed`
4. ✅ Modèle LLM sur RAM → Profil "performance" + CUDA recompilé
5. ✅ Compteur messages (total DB) → Compteur session local
6. ✅ Oubli activation venv → Documentation système

**5 features UX ajoutées** :
1. ✅ Indicateur "✍️ Kira écrit..."
2. ✅ Compteur messages session actuelle
3. ✅ Menu Options restructuré (sous-menus IA/Discord)
4. ✅ Compteur émotions supprimé (simplification)
5. ✅ Documentation venv critique

**Résultats mesurés** :
- ⚡ Performance LLM : **2-5 tok/s → 25-35 tok/s** (5-7x plus rapide)
- 💾 VRAM utilisée : **0 GB → 5.4 GB** (GPU activé)
- 🎮 GPU layers : **35/43 → 43/43** (100%)
- 📏 Context : **2048 → 4096** tokens (doublé)
- ✅ Stabilité : **6 bugs critiques → 0 bug**

---

## 🎯 Prochaine Session : Performance Optimizations

### Objectif Général
**Optimiser les performances globales** de Desktop-Mate sur 4 axes :
1. **Mémoire** (RAM/VRAM)
2. **CPU** (threading, batching)
3. **GPU** (profiling, tuning)
4. **IPC** (Unity-Python overhead)

### Contexte Technique

**Forces actuelles** :
- ✅ GPU 100% utilisé (43/43 layers)
- ✅ Vitesse génération excellente (25-35 tok/s)
- ✅ CUDA support activé
- ✅ Architecture thread-safe (Qt signals)

**Points à optimiser** :
- 🔄 **Mémoire** : Profiler utilisation RAM/VRAM détaillée
- 🔄 **CPU** : Optimiser n_threads (actuellement 6)
- 🔄 **GPU** : Tester profils différents selon charge système
- 🔄 **IPC** : Réduire overhead communication Unity-Python

---

## 🔬 Session 11 - Plan Détaillé

### Phase 1 : Memory Profiling (1-2h)
**Objectif** : Comprendre utilisation mémoire actuelle

**Tâches** :
1. ✅ Installer outils profiling : `memory_profiler`, `psutil`
2. ✅ Créer script profiling RAM : `scripts/profile_memory.py`
3. ✅ Mesurer baseline :
   - Application au démarrage (sans LLM)
   - Après chargement LLM
   - Pendant génération
   - Après 10/50/100 messages
4. ✅ Identifier fuites mémoire potentielles
5. ✅ Documenter résultats : `docs/sessions/session_11_performance/MEMORY_PROFILING.md`

**Métriques attendues** :
- RAM Python : ? MB au démarrage → ? MB après 100 messages
- VRAM GPU : 5.4 GB stable ou croissante ?
- Cache LLM : Taille et évolution

---

### Phase 2 : LLM Cache Optimization (1-2h)
**Objectif** : Réduire latence première génération

**Contexte** :
- Première génération souvent plus lente (cold cache)
- Cache KV peut être optimisé

**Tâches** :
1. ✅ Étudier paramètres llama-cpp-python :
   - `n_ctx` : 4096 (optimal ?)
   - `n_batch` : 512 (optimal ?)
   - `use_mlock` : True (impact ?)
2. ✅ Tester préchargement cache :
   - Charger prompt système au démarrage
   - Pré-générer 1-2 tokens pour warming
3. ✅ Benchmarker latences :
   - Cold cache (premier message session)
   - Warm cache (messages suivants)
   - Après clear historique
4. ✅ Implémenter optimisations
5. ✅ Documenter : `docs/sessions/session_11_performance/LLM_CACHE_OPTIMIZATION.md`

**Métriques attendues** :
- Latence première génération : ? ms → ? ms
- Latence génération suivante : ? ms (stable ?)

---

### Phase 3 : Unity IPC Overhead (1-2h)
**Objectif** : Optimiser communication Python-Unity

**Contexte** :
- Communication TCP/JSON actuelle
- Overhead possible : sérialisation, latence réseau localhost

**Tâches** :
1. ✅ Mesurer latence IPC actuelle :
   - `ping` Unity depuis Python
   - Temps `set_expression()` complet
   - Temps `load_model()` complet
2. ✅ Identifier goulots d'étranglement :
   - Sérialisation JSON
   - TCP overhead (vs named pipes ?)
   - Queue processing Unity (Update loop)
3. ✅ Tester optimisations :
   - Batching commandes (envoyer plusieurs à la fois)
   - Compression JSON (si messages volumineux)
   - Protocol Buffers (si overhead JSON significatif)
4. ✅ Implémenter optimisations validées
5. ✅ Documenter : `docs/sessions/session_11_performance/IPC_OPTIMIZATION.md`

**Métriques attendues** :
- Latence `set_expression()` : ? ms → ? ms
- Throughput commandes : ? cmd/s → ? cmd/s

---

### Phase 4 : CPU Optimization (1h)
**Objectif** : Optimiser utilisation CPU

**Contexte** :
- `n_threads` actuellement 6 (fixe)
- Peut être sous-optimal selon CPU

**Tâches** :
1. ✅ Détecter CPU automatiquement :
   - Nombre cœurs physiques
   - Nombre threads logiques
   - Recommandation : `n_threads = physical_cores - 1`
2. ✅ Benchmarker valeurs `n_threads` :
   - 4, 6, 8, 10 threads
   - Mesurer vitesse génération et CPU usage
3. ✅ Implémenter auto-détection
4. ✅ Documenter : `docs/sessions/session_11_performance/CPU_OPTIMIZATION.md`

**Métriques attendues** :
- CPU usage : ? % → optimal ?%
- Vitesse génération : 25-35 tok/s → ? tok/s (amélioration ?)

---

### Phase 5 : GPU Profiling & Tuning (2h)
**Objectif** : Profiler utilisation GPU et tester profils

**Contexte** :
- Profil "performance" actuellement optimal
- Mais peut varier selon charge système

**Tâches** :
1. ✅ Installer NVIDIA profiling tools :
   - `pynvml` (déjà installé)
   - `nvidia-smi` monitoring continu
2. ✅ Créer script monitoring GPU : `scripts/monitor_gpu.py`
3. ✅ Mesurer métriques :
   - GPU usage % pendant génération
   - VRAM usage évolution
   - GPU temperature
   - Power usage
4. ✅ Benchmarker 3 profils :
   - `performance` (baseline actuel)
   - `balanced` (comparaison)
   - `cpu_fallback` (référence)
5. ✅ Créer profil dynamique :
   - Détecte VRAM disponible
   - Ajuste `n_gpu_layers` automatiquement
6. ✅ Documenter : `docs/sessions/session_11_performance/GPU_PROFILING.md`

**Métriques attendues** :
| Profil | Layers | Vitesse | VRAM | GPU % |
|--------|--------|---------|------|-------|
| performance | 43/43 | 25-35 tok/s | 5.4 GB | ? % |
| balanced | 35/43 | ? tok/s | ? GB | ? % |
| dynamic | auto | ? tok/s | ? GB | ? % |

---

### Phase 6 : Tests & Documentation (1h)
**Objectif** : Valider optimisations et documenter

**Tâches** :
1. ✅ Tests unitaires nouvelles features
2. ✅ Tests intégration performance
3. ✅ Benchmarks comparatifs avant/après
4. ✅ Documentation Session 11 complète :
   - `docs/sessions/session_11_performance/README.md`
   - Tous guides techniques (MEMORY, CPU, GPU, IPC, CACHE)
   - `scripts/` avec outils profiling
5. ✅ Mettre à jour documentation globale

**Livrables** :
- ✅ Tests passent (270+ tests)
- ✅ Benchmarks documentés
- ✅ Outils profiling réutilisables
- ✅ Documentation complète

---

## 📋 Baseline Performance (Chat 9)

### Métriques Actuelles à Battre

**LLM Génération** :
- Vitesse : **25-35 tokens/sec**
- Latence première génération : **? ms** (à mesurer)
- Latence génération suivante : **? ms** (à mesurer)

**Mémoire** :
- RAM Python au démarrage : **? MB** (à mesurer)
- RAM après chargement LLM : **? MB** (à mesurer)
- VRAM GPU : **5.4 GB** (stable)

**CPU** :
- Threads utilisés : **6** (fixe)
- CPU usage pendant génération : **? %** (à mesurer)

**GPU** :
- Layers : **43/43** (100%)
- GPU usage : **? %** (à mesurer)
- Temperature : **? °C** (à mesurer)
- Power : **? W** (à mesurer)

**IPC Unity-Python** :
- Latence `set_expression()` : **? ms** (à mesurer)
- Latence `load_model()` : **? ms** (à mesurer)
- Throughput : **? cmd/sec** (à mesurer)

---

## 🛠️ Outils & Technologies

### À installer (Phase 1)
```powershell
# Profiling mémoire
pip install memory-profiler psutil

# Profiling GPU (déjà installé)
# pip install pynvml

# Benchmarking
pip install pytest-benchmark
```

### Scripts à créer
1. `scripts/profile_memory.py` - Profiling RAM/VRAM
2. `scripts/monitor_gpu.py` - Monitoring GPU continu
3. `scripts/benchmark_llm.py` - Benchmarks LLM
4. `scripts/benchmark_ipc.py` - Benchmarks IPC Unity

---

## 📚 Ressources Techniques

### Documentation llama-cpp-python
- [GitHub llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [GGML Backend Options](https://github.com/ggerganov/llama.cpp/blob/master/docs/backend/CUDA.md)
- [Performance Tuning Guide](https://github.com/ggerganov/llama.cpp/discussions)

### Profiling Tools
- [memory_profiler](https://pypi.org/project/memory-profiler/)
- [psutil](https://psutil.readthedocs.io/)
- [pynvml](https://pypi.org/project/pynvml/)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)

### Unity Performance
- [Unity Profiler](https://docs.unity3d.com/Manual/Profiler.html)
- [C# Memory Profiling](https://docs.unity3d.com/Manual/profiler-memory-module.html)

---

## ⚠️ Points d'Attention

### 1. Ne pas casser la stabilité actuelle
- ✅ Tous les 270 tests doivent passer
- ✅ Vitesse génération ne doit PAS régresser
- ✅ Bugs Chat 9 ne doivent PAS réapparaître

### 2. Mesures scientifiques
- ✅ Mesurer AVANT optimisation (baseline)
- ✅ Mesurer APRÈS optimisation (comparaison)
- ✅ Répéter mesures (moyenne de 5-10 runs)

### 3. Documentation systématique
- ✅ Chaque optimisation documentée
- ✅ Benchmarks inclus
- ✅ Scripts profiling archivés

### 4. Compatibilité
- ✅ Windows 11 (environnement de test)
- ✅ GPU NVIDIA (RTX 4050 6GB)
- ✅ Python 3.10+ (venv)

---

## 🎯 Critères de Succès Session 11

### Objectifs Minimaux
- ✅ **Mémoire** : RAM usage documenté, fuites identifiées
- ✅ **CPU** : `n_threads` auto-détecté
- ✅ **GPU** : Profiling complet avec métriques
- ✅ **IPC** : Latences mesurées

### Objectifs Optimaux
- ✅ **Mémoire** : Réduction RAM usage de 10-20%
- ✅ **Cache LLM** : Réduction latence première génération de 20-30%
- ✅ **CPU** : Optimisation `n_threads` → Amélioration 5-10%
- ✅ **IPC** : Réduction latence de 20-30%

### Objectifs Stretch
- ✅ **GPU** : Profil dynamique fonctionnel
- ✅ **Outils** : Suite profiling complète réutilisable
- ✅ **Documentation** : Guide performance utilisateur final

---

## 🚀 Prochaines Étapes Immédiates

### Chat 10 - Préparation
1. ✅ Lire ce document complet
2. ✅ Installer outils profiling
3. ✅ Créer dossier `docs/sessions/session_11_performance/`
4. ✅ Copier scripts baseline depuis `src/`

### Phase 1 - Memory Profiling
1. ✅ Créer `scripts/profile_memory.py`
2. ✅ Mesurer baseline RAM/VRAM
3. ✅ Identifier fuites potentielles
4. ✅ Documenter résultats

**Estimation durée totale Session 11** : **8-10 heures** (1-2 jours)

---

**🎊 Chat 9 terminé avec succès ! Prêt pour Session 11 - Performance Optimizations ! 🚀✨**

---

_Document préparé le : 27 octobre 2025_  
_Version Desktop-Mate : v0.12.0-alpha_  
_Baseline établie : 25-35 tok/s, 5.4GB VRAM, 43/43 GPU layers_
