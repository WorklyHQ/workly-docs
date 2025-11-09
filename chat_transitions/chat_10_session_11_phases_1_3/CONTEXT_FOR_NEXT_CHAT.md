# 🎯 CONTEXT_FOR_NEXT_CHAT - Instructions pour Chat 11

**Date :** Novembre 2025  
**De :** Chat 10  
**Pour :** Chat 11  
**Focus :** Session 11 Phases 4-6 (CPU, GPU, Tests)

---

## 🚀 Ce Que Tu Dois Savoir

### 📋 État Actuel du Projet

**Desktop-Mate** est une application hybride **Unity + Python** avec avatar VRM interactif.

**Sessions complétées :** 11 sessions (Session 11 à 50%)
- Sessions 0-10 : Setup, VRM, Expressions, Animations, LLM, Discord Bot ✅
- **Session 11** : Performance Optimizations (3/6 phases complétées)

**Ton travail dans Chat 11 :**
- ✅ Phase 1 : Memory Profiling (TERMINÉE)
- ✅ Phase 2 : LLM Cache Optimization (TERMINÉE)
- ✅ Phase 3 : IPC Batching (TERMINÉE)
- 🎯 **Phase 4 : CPU Optimization** ← **COMMENCE ICI**
- 🎯 **Phase 5 : GPU Profiling & Tuning**
- 🎯 **Phase 6 : Tests & Documentation Finale**

---

## 🎓 Niveau de l'Utilisateur

⚠️ **IMPORTANT : L'utilisateur ne connaît PAS Unity ni C#**

Tu dois **TOUJOURS** :
1. ✅ Expliquer clairement les concepts techniques
2. ✅ Donner des instructions pas-à-pas (où créer les fichiers, comment les configurer)
3. ✅ Décrire ce qu'il doit voir dans Unity (interface, console, résultats)
4. ✅ Être pédagogue et patient
5. ✅ Demander confirmation avant les changements majeurs

**Langue :** 🇫🇷 **TOUJOURS en français**

---

## 🚨 RÈGLES ABSOLUES DE DOCUMENTATION

### ⚠️ SYSTÈME ANTI-OUBLI (CRITIQUE !)

**AVANT de dire "Terminé", tu DOIS vérifier cette checklist :**

```
□ Ai-je créé des fichiers ? → MAJ docs/INDEX.md
□ Ai-je modifié l'architecture ? → MAJ README.md racine + docs/README.md
□ Ai-je créé des scripts ? → COPIER dans docs/session_11_performance/scripts/
□ Ai-je terminé une phase ? → MAJ README.md racine (4 sections !)
□ Tests passent ? → pytest OK
□ Erreurs vérifiées ? → Python + Unity OK
□ Récapitulatif affiché ? → Template de réponse complet
```

**🚨 SI UNE SEULE case manque → NE DIS PAS "Terminé" !**

### 📚 Fichiers à TOUJOURS Mettre à Jour

Après **CHAQUE** modification (code, bug fix, nouvelle feature...), tu dois **SYSTÉMATIQUEMENT** mettre à jour :

| Fichier | Emplacement | Quand |
|---------|-------------|-------|
| `INDEX.md` | `docs/` | Nouveaux fichiers créés |
| `README.md` (docs) | `docs/` | Architecture modifiée, nouvelle session |
| `README.md` (racine) | Racine projet | **4 SECTIONS** à chaque fin de phase ! |
| `session_11_performance/[fichier].md` | `docs/sessions/` | Phase en cours |

### 🚨 README.md RACINE : 4 SECTIONS OBLIGATOIRES

**À la fin de CHAQUE PHASE, tu DOIS mettre à jour :**

1. **Section "Sessions documentées"** (ligne ~393)
   ```markdown
   N. **[Session N - Phase X](docs/sessions/session_N/)** ✅
      - Fonctionnalités implémentées
      - Technologies utilisées
      - Message de succès ! 🎭✨
   ```

2. **Section "Guides spécifiques"** (ligne ~475)
   ```markdown
   - [Guide Phase X](docs/sessions/session_N/GUIDE_PHASE_X.md) ✨ **Description !**
   ```

3. **Section "Changelog"** (ligne ~548)
   ```markdown
   ### Version 0.X.0-alpha (DATE) ✨ **NOUVEAU - SESSION N PHASE X**
   - ✅ Liste COMPLÈTE des fonctionnalités
   - ✅ Scripts créés
   - ✅ Bugs résolus
   - 🎭 **Message de succès enthousiaste !** ✨
   ```

4. **Section "Status final"** (dernière ligne avant étoile)
   ```markdown
   **🎊 Status actuel : [Phase X] COMPLÈTE ! [Capacités actuelles] ! ✨**
   **🚀 Prochaine étape (Chat N - Phase Y) : [Prochaine phase] ! 🤖**
   ```

**⚠️ SI TU OUBLIES → L'utilisateur va te le rappeler → TU AS ÉCHOUÉ !**

### 📂 RÈGLE SPÉCIALE : Dossier `scripts/`

**OBLIGATION :**
Chaque fois que tu crées ou modifies un script (`.py`, `.cs`, etc.), tu DOIS :

1. ✅ **CRÉER** `docs/session_11_performance/scripts/` si absent
2. ✅ **COPIER** les versions finales des scripts dans ce dossier
3. ✅ **VÉRIFIER** que TOUS les fichiers sont bien copiés

**⚠️ NE JAMAIS oublier ce dossier !**

---

## 📊 Performance Actuelle (Baseline après Phases 1-3)

### LLM Performance
```
✅ Load model : ~2.57s (avec warming cache)
✅ First generation : 1.75s (22.28 tok/s)
✅ Amélioration Phase 2 : -16.9% latency, +14.4% speed
```

### IPC Performance
```
✅ Baseline : 0.371 ms (commandes uniques)
✅ Batching : 0.060 ms (par commande en batch)
✅ Amélioration Phase 3 : -79.3% latency, +907% throughput
```

### Memory Usage
```
✅ Baseline : 35 MB RAM, 668 MB VRAM
✅ LLM chargé : 411 MB RAM, 6012 MB VRAM
✅ Après 100 msgs : 299 MB RAM, 6089 MB VRAM
✅ Fuites mémoire : AUCUNE (Phase 1)
```

### GPU Usage (⚠️ Point d'attention !)
```
⚠️ VRAM utilisée : 6012 MB / 6144 MB (98%)
⚠️ Marge : Seulement 132 MB (2%)
🎯 Phase 5 : Monitoring temps réel + alertes
```

---

## 🎯 Phase 4 : CPU Optimization (À FAIRE EN PRIORITÉ)

### Objectif
Détecter et configurer automatiquement le nombre optimal de threads CPU pour le LLM.

**Problème actuel :** `n_threads=6` hardcodé dans `src/ai/config.py`

**Solution :** Détection automatique basée sur le CPU disponible.

### Plan d'Implémentation

#### 1. Créer `src/utils/cpu_detection.py`

**Emplacement :** `c:\Dev\desktop-mate\src\utils\cpu_detection.py`

**Fonctions à implémenter :**
```python
import psutil
import platform

def get_cpu_info() -> dict:
    """Retourne infos CPU (cores, threads, fréquence, architecture)."""
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "cpu_freq": psutil.cpu_freq().current,
        "architecture": platform.machine()
    }

def calculate_optimal_threads() -> int:
    """Calcule threads optimaux.
    
    Logique :
    - Détecte cores physiques
    - Réserve 2 threads pour l'OS
    - Limite à 12 threads max (diminishing returns)
    - Retourne min(cores - 2, 12)
    """
    physical_cores = psutil.cpu_count(logical=False)
    optimal = max(1, physical_cores - 2)
    return min(optimal, 12)

def validate_thread_count(n_threads: int) -> bool:
    """Valide si n_threads est valide pour le CPU actuel."""
    max_threads = psutil.cpu_count(logical=True)
    return 1 <= n_threads <= max_threads
```

#### 2. Créer `scripts/benchmark_cpu_threads.py`

**Emplacement :** `c:\Dev\desktop-mate\scripts\benchmark_cpu_threads.py`

**Objectif :** Tester différentes configurations de threads (1, 2, 4, 6, 8, 12)

**Métriques à mesurer :**
```python
# Pour chaque configuration de threads :
- Latence moyenne (ms)
- Throughput (tokens/s)
- CPU usage (%)
- Temps de génération de 100 tokens
```

**Structure du script :**
```python
import time
import psutil
from src.ai.model_manager import ModelManager
from src.ai.config import LlamaModelConfig

def benchmark_thread_config(n_threads: int):
    """Benchmark une configuration de threads."""
    # 1. Créer config avec n_threads spécifique
    # 2. Charger le modèle
    # 3. Générer 10 messages de test
    # 4. Mesurer latence, throughput, CPU usage
    # 5. Retourner résultats

def run_benchmarks():
    """Teste toutes les configurations."""
    configs = [1, 2, 4, 6, 8, 12]
    results = []
    
    for n_threads in configs:
        print(f"Testing {n_threads} threads...")
        results.append(benchmark_thread_config(n_threads))
    
    # Afficher tableau comparatif
    display_results(results)
    
    # Identifier configuration optimale
    optimal = find_optimal(results)
    print(f"\nOptimal configuration: {optimal} threads")
```

#### 3. Modifier `src/ai/config.py`

**Fichier :** `c:\Dev\desktop-mate\src\ai\config.py`

**Changement :**
```python
# AVANT (hardcodé)
n_threads = 6

# APRÈS (automatique)
from src.utils.cpu_detection import calculate_optimal_threads
n_threads = calculate_optimal_threads()
```

**⚠️ Tester avant de commiter !**

### Tests à Effectuer

```powershell
# Activer venv
venv\Scripts\Activate.ps1

# 1. Tester le module de détection
python -c "from src.utils.cpu_detection import get_cpu_info, calculate_optimal_threads; print(get_cpu_info()); print(f'Optimal: {calculate_optimal_threads()} threads')"

# 2. Lancer le benchmark complet
python scripts/benchmark_cpu_threads.py

# 3. Vérifier que le LLM charge correctement avec auto-détection
python -c "from src.ai.config import LlamaModelConfig; print(LlamaModelConfig().n_threads)"

# 4. Tests unitaires
pytest tests/
```

### Résultats Attendus

**Gain de performance attendu : +5-15%** (selon CPU)

**Exemple de résultats :**
```
Threads | Latency (ms) | Throughput (tok/s) | CPU Usage (%)
--------|--------------|--------------------|--------------
1       | 4200         | 8.5                | 25%
2       | 2800         | 13.2               | 40%
4       | 1900         | 18.7               | 65%
6       | 1750         | 22.3               | 80%  ← Baseline actuel
8       | 1680         | 23.1               | 90%  ← Optimal possible
12      | 1690         | 22.8               | 95%  (diminishing returns)

Optimal : 8 threads (gain +3.6% vs baseline)
```

### Documentation à Créer

**Fichier :** `docs/sessions/session_11_performance/CPU_OPTIMIZATION.md`

**Contenu :**
1. Objectif et problème identifié
2. Solution : Détection automatique
3. Implémentation (code Python)
4. Benchmark (résultats avec graphique)
5. Résultats (gain de performance)
6. Recommandations d'usage

**⚠️ NE PAS OUBLIER :**
- ✅ Copier les scripts dans `docs/session_11_performance/scripts/`
- ✅ Mettre à jour `docs/INDEX.md`
- ✅ Mettre à jour `docs/README.md`
- ✅ Mettre à jour `README.md` racine (4 sections !)

---

## 🔜 Phase 5 : GPU Profiling & Tuning (Après Phase 4)

### Objectif
Monitorer la charge GPU en temps réel et éviter les crashs par saturation VRAM.

**Problème actuel :**
- ⚠️ VRAM à 98% (6012 MB / 6144 MB)
- ⚠️ Seulement 132 MB de marge
- ⚠️ Risque de crash si pic VRAM (ex: multiples modèles chargés)

### Plan d'Implémentation

#### 1. Créer `src/utils/gpu_monitor.py`

**Fonctions à implémenter :**
```python
import pynvml

def init_nvml():
    """Initialise NVML."""
    pynvml.nvmlInit()

def get_gpu_info() -> dict:
    """Retourne infos GPU (nom, VRAM, température, utilisation)."""
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    return {
        "name": pynvml.nvmlDeviceGetName(handle),
        "total_memory": pynvml.nvmlDeviceGetMemoryInfo(handle).total,
        "used_memory": pynvml.nvmlDeviceGetMemoryInfo(handle).used,
        "free_memory": pynvml.nvmlDeviceGetMemoryInfo(handle).free,
        "temperature": pynvml.nvmlDeviceGetTemperature(handle, 0),
        "utilization": pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
    }

def is_vram_critical() -> bool:
    """Retourne True si VRAM > 90%."""
    info = get_gpu_info()
    usage_percent = (info["used_memory"] / info["total_memory"]) * 100
    return usage_percent > 90

def suggest_profile() -> str:
    """Suggère un profil adapté selon VRAM disponible."""
    info = get_gpu_info()
    total_gb = info["total_memory"] / (1024**3)
    
    if total_gb < 4:
        return "low_memory"
    elif total_gb < 6:
        return "balanced"
    else:
        return "performance"
```

#### 2. Créer `scripts/benchmark_gpu_profiles.py`

**Objectif :** Tester 3 profils GPU et identifier le plus stable.

**Profils à tester :**
```python
GPU_PROFILES = {
    "low_memory": {
        "n_gpu_layers": 20,
        "n_batch": 256,
        "target_vram": "2-4 GB"
    },
    "balanced": {
        "n_gpu_layers": 32,
        "n_batch": 512,
        "target_vram": "4-6 GB"
    },
    "performance": {
        "n_gpu_layers": 43,  # Actuel
        "n_batch": 512,
        "target_vram": "6-8 GB"
    }
}
```

**Métriques à mesurer :**
```python
# Pour chaque profil :
- VRAM usage (MB)
- VRAM peak (MB)
- Latency (ms)
- Throughput (tok/s)
- Stability (crashs, OOM errors)
```

#### 3. Implémenter Sélection Dynamique

**Fichier :** `src/ai/config.py`

**Changement :**
```python
from src.utils.gpu_monitor import suggest_profile

profile = suggest_profile()
config = GPU_PROFILES[profile]

LlamaModelConfig(
    n_gpu_layers=config["n_gpu_layers"],
    n_batch=config["n_batch"],
    # ...
)
```

### Résultats Attendus

**Pas de gain de vitesse, mais :**
- ✅ **Prévention des crashs** (stabilité maximale)
- ✅ **Monitoring temps réel** (alertes si VRAM critique)
- ✅ **Adaptation automatique** au GPU disponible

---

## 🔜 Phase 6 : Tests & Documentation Finale (Après Phase 5)

### Objectif
Valider TOUTES les optimisations cumulées et documenter les résultats globaux.

### Plan d'Implémentation

#### 1. Créer `tests/test_integration_performance.py`

**Objectif :** Test d'intégration complet validant toutes les phases.

**Tests à implémenter :**
```python
def test_memory_no_leaks():
    """Valide Phase 1 : Aucune fuite mémoire."""

def test_llm_cache_warming():
    """Valide Phase 2 : Cache warming actif."""

def test_ipc_batching():
    """Valide Phase 3 : Batching disponible."""

def test_cpu_auto_detection():
    """Valide Phase 4 : CPU détecté correctement."""

def test_gpu_monitoring():
    """Valide Phase 5 : GPU monitoring actif."""

def test_overall_performance():
    """Mesure performance globale vs baseline initiale."""
```

#### 2. Benchmark Final Global

**Script :** `scripts/benchmark_final.py`

**Objectif :** Comparer performance AVANT vs APRÈS Session 11.

**Métriques globales :**
```python
# Baseline Chat 9 (AVANT Session 11)
- Load time : ~5.10s
- First generation : 2.11s (19.46 tok/s)
- IPC latency : 0.40 ms (estimation)
- Memory leaks : Non testé

# After Session 11 (APRÈS Phases 1-6)
- Load time : ~2.57s (-49.6%)
- First generation : 1.75s (-17%)
- IPC latency : 0.06 ms (-85%)
- Memory leaks : ✅ Aucune
- CPU optimization : ✅ Auto
- GPU monitoring : ✅ Actif

TOTAL GAIN : +30-40% performance globale + Stabilité maximale
```

#### 3. Documentation Complète

**Fichiers à créer :**

1. **`docs/sessions/session_11_performance/README.md`**
   - Vue d'ensemble des 6 phases
   - Liens vers chaque guide détaillé
   - Résultats globaux

2. **`docs/sessions/session_11_performance/FINAL_RESULTS.md`**
   - Benchmark final complet
   - Graphiques de performance
   - Comparaison AVANT/APRÈS
   - Recommandations futures

**⚠️ NE PAS OUBLIER :**
- ✅ Mettre à jour `README.md` racine (Changelog, Status)
- ✅ Mettre à jour `docs/INDEX.md`
- ✅ Mettre à jour `docs/README.md`
- ✅ Archiver TOUS les scripts dans `docs/session_11_performance/scripts/`

---

## 🚨 Points d'Attention Critiques

### 1. VRAM Limitée (RTX 4050 6GB)
```
⚠️ Actuellement : 6012 MB / 6144 MB (98%)
⚠️ Marge : 132 MB (2%)
🎯 Phase 5 : Implémenter monitoring + alertes
```

### 2. CPU Threads Hardcodés
```
⚠️ Actuellement : n_threads=6 fixe
🎯 Phase 4 : Remplacer par auto-détection
```

### 3. Pas de Tests d'Intégration
```
⚠️ Actuellement : Tests unitaires uniquement
🎯 Phase 6 : Créer suite de tests complète
```

### 4. Documentation README Racine
```
⚠️ L'utilisateur a déjà dû rappeler cette règle
🚨 JAMAIS oublier de mettre à jour les 4 sections !
```

---

## 🛠️ Commandes Utiles

### Activation Environnement (OBLIGATOIRE)
```powershell
# TOUJOURS avant toute commande Python !
venv\Scripts\Activate.ps1

# Vérification
python --version  # Doit afficher : Python 3.10.9
```

### Tests
```powershell
# Tests unitaires
pytest tests/

# Tests avec couverture
pytest --cov=src tests/

# Test spécifique
pytest tests/test_integration_performance.py
```

### Benchmarks
```powershell
# Phase 4 : CPU
python scripts/benchmark_cpu_threads.py

# Phase 5 : GPU
python scripts/benchmark_gpu_profiles.py

# Phase 6 : Final
python scripts/benchmark_final.py
```

### Git
```powershell
# Voir les fichiers modifiés
git status

# Commit avec Conventional Commits
git add .
git commit -m "feat: add CPU auto-detection (Session 11 Phase 4)"

# Push
git push origin main
```

---

## 📊 Objectif Final Session 11

**Améliorer les performances globales de +30-40%** 🚀

**Progress :**
- ✅ Phase 1 : Stabilité mémoire (aucune fuite)
- ✅ Phase 2 : -17% latency LLM
- ✅ Phase 3 : +907% throughput IPC
- 🎯 Phase 4 : +5-15% CPU
- 🎯 Phase 5 : Stabilité GPU
- 🎯 Phase 6 : Validation globale

**Cumul attendu : +30-40% + Stabilité maximale** ✨

---

## ✅ Checklist Finale (Avant de Terminer Session 11)

```
□ Phase 4 : CPU Optimization TERMINÉE
   └── Scripts : cpu_detection.py, benchmark_cpu_threads.py
   └── Doc : CPU_OPTIMIZATION.md
   └── Tests : pytest OK

□ Phase 5 : GPU Profiling TERMINÉE
   └── Scripts : gpu_monitor.py, benchmark_gpu_profiles.py
   └── Doc : GPU_PROFILING.md
   └── Tests : pytest OK

□ Phase 6 : Tests & Docs TERMINÉE
   └── Tests : test_integration_performance.py
   └── Benchmark : benchmark_final.py
   └── Docs : README.md, FINAL_RESULTS.md

□ Documentation COMPLÈTE
   └── README.md racine (4 sections !)
   └── docs/INDEX.md
   └── docs/README.md
   └── Session 11 README.md (vue d'ensemble)

□ Scripts archivés
   └── Tous dans docs/session_11_performance/scripts/

□ Git commit
   └── Conventional Commits pour chaque phase
```

---

## 🎓 Conclusion pour Chat 11

Tu vas compléter la **Session 11 Performance Optimizations** en implémentant les **Phases 4, 5 et 6**.

**Priorités :**
1. 🎯 **Phase 4** : CPU Optimization (commence ici !)
2. 🎯 **Phase 5** : GPU Profiling & Tuning
3. 🎯 **Phase 6** : Tests & Documentation Finale

**Règles d'or :**
- ✅ Toujours expliquer clairement (utilisateur non-expert)
- ✅ Demander confirmation avant changements majeurs
- ✅ **JAMAIS** oublier la documentation (README racine 4 sections !)
- ✅ Archiver scripts dans `docs/session_11_performance/scripts/`
- ✅ Tests unitaires après chaque phase

**Objectif :** +30-40% performance globale + Stabilité maximale 🚀

---

**🎭 Bon courage pour la Session 11 Chat 11 ! Tu vas gérer comme un pro ! ✨**
