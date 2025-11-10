# 📋 Détail des Phases 3 à 6 - Session 11 Performance

> **⚠️ Note** : Ce document est une référence personnelle détaillant les phases restantes de la Session 11.

---

## 🔌 Phase 3 : Unity IPC Overhead (Communication Python ↔ Unity)

### 🤔 C'est quoi le problème ?

Workly a **2 parties** qui communiquent ensemble :

- 🐍 **Python** : L'interface graphique (boutons, chat) + l'IA
- 🎮 **Unity** : L'avatar 3D VRM (qui bouge, fait des expressions)

Ils parlent entre eux via un **"socket TCP"** (port 5555) en s'envoyant des **messages JSON**.

**Exemple de communication :**

```json
Python → Unity : {"command": "expression", "name": "happy", "weight": 1.0}
Unity → Python : {"status": "ok", "message": "Expression applied"}
```

**Le problème potentiel :**

- Chaque message prend du temps à voyager (latence)
- JSON doit être converti en texte puis re-parsé (serialization)
- Unity doit mettre les messages dans une file d'attente (Queue) pour les traiter dans son "main thread"

**Si cette communication est lente → l'avatar réagit avec retard !** 😴

### 🎯 Ce qu'on va faire

#### 1️⃣ **Créer un script de benchmark IPC** (`benchmark_ipc.py`)

On va mesurer :

- **Round-trip time** : Temps total Python → Unity → Python
- **Latence moyenne** : Sur 100 messages envoyés
- **Impact de la taille** : Petit message vs gros message
- **Fréquence maximale** : Combien de messages/seconde avant que ça ralentisse ?

**Code simplifié :**

```python
# On envoie 100 messages et on chronomètre
for i in range(100):
    start = time.time()
    bridge.send_message({"command": "test", "id": i})
    response = bridge.wait_response()
    latency = time.time() - start
    latencies.append(latency)

# Calcul statistiques
moyenne = statistics.mean(latencies)
median = statistics.median(latencies)
print(f"Latence moyenne : {moyenne*1000:.2f}ms")
```

#### 2️⃣ **Identifier les goulots d'étranglement**

On va regarder où ça ralentit :

- 🐌 Sérialisation JSON trop lourde ?
- 🐌 Socket TCP lent ?
- 🐌 Queue Unity qui s'accumule ?
- 🐌 Parsing JSON côté Unity ?

#### 3️⃣ **Optimiser selon les résultats**

**Optimisations possibles :**

**A) Message batching (regroupement)**

```python
# Au lieu d'envoyer 10 messages séparés :
send("expression happy")
send("expression sad")
send("move left")
# ...

# On les regroupe :
send({
    "batch": [
        {"command": "expression", "name": "happy"},
        {"command": "expression", "name": "sad"},
        {"command": "move", "direction": "left"}
    ]
})
```

→ **1 seul voyage réseau** au lieu de 10 !

**B) Protocole binaire (si JSON est trop lent)**

- JSON en texte : `{"command":"test"}` = 18 bytes
- Binaire (MessagePack) : `\x81\xa7command\xa4test` = 13 bytes
  → Plus compact = plus rapide

**C) Asynchrone (fire and forget)**

- Actuellement : Python attend la réponse Unity
- Optimisé : Python envoie et continue sans attendre (sauf pour les commandes critiques)

#### 4️⃣ **Documenter les gains**

On va créer `IPC_OPTIMIZATION.md` avec :

- Baseline (avant) : X ms de latence
- Après optimisation : Y ms de latence
- Amélioration : -Z% ! 🚀

### 📊 Résultats attendus

| Métrique           | Baseline (avant) | Optimisé (après)   | Gain estimé    |
| ------------------ | ---------------- | ------------------ | -------------- |
| Latence round-trip | ~15-20ms         | ~5-8ms             | **-50 à -70%** |
| Messages/seconde   | ~50-60 msg/s     | ~150-200 msg/s     | **+200%**      |
| Taille message     | 100 bytes (JSON) | 60 bytes (binaire) | **-40%**       |

---

## 🧵 Phase 4 : CPU Optimization (Threads du processeur)

### 🤔 C'est quoi le problème ?

L'IA (llama.cpp) utilise le **CPU** pour certains calculs, même si le gros du travail est sur le GPU.

**Paramètre actuel :** `n_threads = 6`

**Problème :**

- Si ton PC a 4 cœurs → 6 threads = trop, ça ralentit (overhead)
- Si ton PC a 16 cœurs → 6 threads = sous-utilisé, on peut aller plus vite !

**Actuellement, c'est configuré "à la main" dans le code. Pas optimal !** 🤷

### 🎯 Ce qu'on va faire

#### 1️⃣ **Détecter automatiquement le CPU**

On va créer un module de détection :

```python
import psutil
import platform

def detect_optimal_threads():
    # Nombre de cœurs physiques
    physical_cores = psutil.cpu_count(logical=False)
    # Nombre de threads logiques (hyperthreading)
    logical_cores = psutil.cpu_count(logical=True)

    # Architecture CPU
    cpu_info = platform.processor()

    return {
        "physical": physical_cores,  # Ex: 8
        "logical": logical_cores,    # Ex: 16
        "architecture": cpu_info     # Ex: "Intel Core i7-9700K"
    }
```

#### 2️⃣ **Benchmarker différentes valeurs de threads**

On va tester avec **1, 2, 4, 6, 8, 12, 16 threads** et mesurer :

- Temps de génération
- Utilisation CPU
- Tokens/seconde

**Script de benchmark :**

```python
for n_threads in [1, 2, 4, 6, 8, 12, 16]:
    # Charger le modèle avec ce nombre de threads
    model = Llama(n_threads=n_threads, ...)

    # Générer 10 fois et mesurer
    times = []
    for _ in range(10):
        start = time.time()
        model.generate(...)
        times.append(time.time() - start)

    print(f"{n_threads} threads: {statistics.mean(times):.3f}s")
```

#### 3️⃣ **Établir une formule optimale**

Selon les résultats, on va trouver la meilleure formule. Exemple :

```python
def calculate_optimal_threads(physical_cores, logical_cores):
    if logical_cores >= 16:
        return physical_cores  # Utiliser les cœurs physiques
    elif logical_cores >= 8:
        return logical_cores // 2  # Moitié des threads logiques
    else:
        return logical_cores  # Tout utiliser
```

#### 4️⃣ **Intégrer dans AIConfig**

On va modifier `src/ai/config.py` pour auto-configurer :

```python
class AIConfig:
    def __init__(self):
        # Auto-détection
        cpu_info = detect_optimal_threads()
        self.n_threads = calculate_optimal_threads(
            cpu_info["physical"],
            cpu_info["logical"]
        )
        logger.info(f"🧵 Threads optimaux détectés : {self.n_threads}")
```

**Résultat :** Workly s'adapte automatiquement à **n'importe quel PC** ! 🎯

### 📊 Résultats attendus

| Configuration PC      | Threads actuels (fixe) | Threads optimisés (auto) | Gain estimé       |
| --------------------- | ---------------------- | ------------------------ | ----------------- |
| 4 cœurs / 8 threads   | 6 (over-subscribed)    | 4 (optimal)              | **+10%**          |
| 6 cœurs / 12 threads  | 6 (OK)                 | 6 (optimal)              | **0%** (déjà bon) |
| 8 cœurs / 16 threads  | 6 (sous-utilisé)       | 8 (optimal)              | **+15%**          |
| 12 cœurs / 24 threads | 6 (très sous-utilisé)  | 12 (optimal)             | **+20%**          |

---

## 🎮 Phase 5 : GPU Profiling & Tuning (Optimisation carte graphique)

### 🤔 C'est quoi le problème ?

Ton GPU (RTX 4050, 6 GB VRAM) charge actuellement **100% du modèle** (43 couches sur 43).

**Problèmes potentiels :**

1. **VRAM saturée** : 5.4 GB utilisés / 6 GB disponibles → risque de crash si le système a besoin de VRAM
2. **Pas d'adaptation** : Si quelqu'un a une RTX 3060 (12 GB) ou une GTX 1650 (4 GB), ça ne s'adapte pas
3. **Profil statique** : Mode "performance" toujours actif, même si "balanced" serait mieux dans certains cas

### 🎯 Ce qu'on va faire

#### 1️⃣ **Créer un moniteur VRAM en temps réel**

```python
import pynvml

def get_vram_usage():
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)

    total_gb = info.total / 1024**3
    used_gb = info.used / 1024**3
    free_gb = info.free / 1024**3
    utilization = (used_gb / total_gb) * 100

    return {
        "total": total_gb,
        "used": used_gb,
        "free": free_gb,
        "percent": utilization
    }
```

#### 2️⃣ **Profiler différentes configurations GPU**

On va benchmarker **3 scénarios** :

**A) Tout sur GPU (actuel)**

```python
n_gpu_layers = 43  # Toutes les couches
# VRAM: ~5.4 GB
# Vitesse: Max (22 tok/s)
```

**B) Hybride GPU/CPU**

```python
n_gpu_layers = 35  # 80% sur GPU, 20% sur CPU
# VRAM: ~4.5 GB
# Vitesse: 19-20 tok/s (-10%)
```

**C) CPU uniquement (fallback)**

```python
n_gpu_layers = 0  # Tout sur CPU
# VRAM: ~500 MB
# Vitesse: 5-7 tok/s (-70%, très lent)
```

**On va mesurer pour chaque :**

- Temps de chargement
- Temps de génération
- Tokens/seconde
- VRAM utilisée

#### 3️⃣ **Implémenter la sélection dynamique**

**Logique d'auto-sélection :**

```python
def select_gpu_profile(vram_total_gb, model_size_gb):
    vram_free = vram_total_gb - 2.0  # Garde 2 GB pour le système

    if vram_free >= model_size_gb * 1.2:
        # Assez de VRAM : tout sur GPU
        return {
            "profile": "performance",
            "n_gpu_layers": 43,
            "description": "100% GPU (optimal)"
        }
    elif vram_free >= model_size_gb * 0.8:
        # VRAM juste : hybride GPU/CPU
        return {
            "profile": "balanced",
            "n_gpu_layers": 35,
            "description": "80% GPU + 20% CPU (équilibré)"
        }
    else:
        # Pas assez de VRAM : CPU uniquement
        return {
            "profile": "cpu",
            "n_gpu_layers": 0,
            "description": "CPU uniquement (fallback)"
        }

# Utilisation
vram_info = get_vram_usage()
profile = select_gpu_profile(vram_info["total"], 6.8)
logger.info(f"🎮 Profil GPU auto : {profile['description']}")
```

#### 4️⃣ **Ajouter un système de recommandations**

Si VRAM est limite, afficher un message :

```python
if vram_info["percent"] > 85:
    logger.warning("⚠️ VRAM saturée à 85%+")
    logger.info("💡 Recommandations :")
    logger.info("  - Fermer applications gourmandes (Chrome, jeux)")
    logger.info("  - Utiliser un modèle plus petit (4B au lieu de 7B)")
    logger.info("  - Passer en mode 'balanced' (35 GPU layers)")
```

#### 5️⃣ **Tester l'auto-fallback**

Scénario de test :

1. Lancer Workly en mode "performance"
2. Simuler saturation VRAM (charger autre chose en parallèle)
3. Vérifier que le système passe automatiquement en "balanced"
4. Logger l'événement

**Résultat :** Workly **s'adapte** au GPU de l'utilisateur et **évite les crashes** ! 🛡️

### 📊 Résultats attendus

| Configuration GPU | Profil actuel                | Profil optimisé        | Bénéfice              |
| ----------------- | ---------------------------- | ---------------------- | --------------------- |
| RTX 4090 (24 GB)  | Performance (5.4 GB)         | Performance (5.4 GB)   | **Marge de sécurité** |
| RTX 4050 (6 GB)   | Performance (5.4 GB, 90%)    | Balanced (4.5 GB, 75%) | **Évite crashes**     |
| GTX 1660 (6 GB)   | Performance (crash possible) | Balanced (4.5 GB)      | **Stable**            |
| GTX 1650 (4 GB)   | Performance (crash garanti)  | CPU (500 MB)           | **Fonctionne !**      |

---

## ✅ Phase 6 : Tests & Documentation finale

### 🤔 Pourquoi cette phase ?

Après avoir optimisé IPC, CPU et GPU, il faut :

1. **Vérifier que tout fonctionne ensemble** (tests d'intégration)
2. **Mesurer les gains cumulés** (avant vs après toutes les phases)
3. **Documenter proprement** pour que tu puisses retrouver l'info

### 🎯 Ce qu'on va faire

#### 1️⃣ **Tests d'intégration complets**

On va créer `tests/test_integration_performance.py` qui teste **tout le pipeline** :

```python
def test_full_optimized_pipeline():
    """Test complet : GUI → IPC → Unity + LLM optimisé"""

    # 1. Charger le modèle avec warming cache
    model_manager = ModelManager()
    model_manager.load_model(warm_cache=True)

    # 2. Tester IPC optimisé (batching)
    unity_bridge = UnityBridge()
    unity_bridge.connect()
    batch = [
        {"command": "expression", "name": "happy"},
        {"command": "animation", "name": "wave"}
    ]
    response = unity_bridge.send_batch(batch)
    assert response["status"] == "ok"

    # 3. Générer texte avec LLM optimisé
    start = time.time()
    text = model_manager.generate("Bonjour !")
    latency = time.time() - start
    assert latency < 2.0  # Doit être rapide !

    # 4. Vérifier mémoire stable
    memory_mb = psutil.Process().memory_info().rss / 1024**2
    assert memory_mb < 1000  # Pas de fuite
```

**Tests spécifiques par optimisation :**

```python
def test_warming_cache_active():
    """Vérifier que le warming cache est appliqué"""
    model_manager = ModelManager()

    # Logs doivent contenir "🔥 Warming cache"
    with LogCapture() as logs:
        model_manager.load_model(warm_cache=True)

    assert "Warming cache" in logs.getvalue()
    assert "Cache warmed" in logs.getvalue()

def test_ipc_batching():
    """Vérifier que le batching IPC fonctionne"""
    bridge = UnityBridge()
    bridge.connect()

    # Envoyer batch de 10 messages
    batch = [{"command": "test", "id": i} for i in range(10)]

    start = time.time()
    response = bridge.send_batch(batch)
    latency = time.time() - start

    # Doit être plus rapide que 10 messages séparés
    assert latency < 0.1  # 100ms max pour 10 messages
    assert response["processed"] == 10

def test_cpu_threads_auto_detection():
    """Vérifier que les threads CPU sont auto-détectés"""
    config = AIConfig()

    # n_threads doit être détecté automatiquement
    assert config.n_threads > 0
    assert config.n_threads <= psutil.cpu_count(logical=True)

    # Log doit indiquer détection
    assert "Threads optimaux détectés" in logs

def test_gpu_profile_selection():
    """Vérifier que le profil GPU s'adapte à la VRAM"""
    vram_info = get_vram_usage()
    profile = select_gpu_profile(vram_info["total"], 6.8)

    # Profil doit être cohérent avec VRAM disponible
    if vram_info["free"] < 4.0:
        assert profile["profile"] in ["balanced", "cpu"]
    else:
        assert profile["profile"] == "performance"
```

#### 2️⃣ **Benchmark "Before vs After" (Avant/Après)**

On va créer un tableau comparatif complet :

```markdown
## 📊 Résultats Session 11 : Toutes phases

| Métrique                      | AVANT (baseline) | APRÈS (optimisé)       | Gain             |
| ----------------------------- | ---------------- | ---------------------- | ---------------- |
| **LLM - Première génération** | 2.11s            | 1.75s                  | **-17%** ⚡      |
| **LLM - Tokens/seconde**      | 19.46            | 22.28                  | **+14%** 🚀      |
| **IPC - Latence moyenne**     | 15ms             | 5ms                    | **-67%** ⚡      |
| **IPC - Messages/seconde**    | 60 msg/s         | 180 msg/s              | **+200%** 🚀     |
| **CPU - Threads optimaux**    | 6 (fixe)         | Auto-détecté           | **Adaptable** 🎯 |
| **GPU - VRAM utilisée**       | 5.4 GB (90%)     | 4.5 GB (75%)           | **-17%** 💾      |
| **GPU - Crash risk**          | Élevé (90% VRAM) | Faible (fallback auto) | **Stable** 🛡️    |
| **Mémoire RAM - Fuite**       | 0 MB             | 0 MB                   | **Stable** ✅    |

**Gain cumulé estimé : ~30-40% de performance globale** 🎊
```

**Détail des gains par phase :**

| Phase       | Optimisation        | Gain mesuré                | Impact                          |
| ----------- | ------------------- | -------------------------- | ------------------------------- |
| **Phase 1** | Memory Profiling    | 0% (validation)            | ✅ Aucune fuite détectée        |
| **Phase 2** | Warming Cache       | -17% latence               | ⚡ Première réponse plus rapide |
| **Phase 3** | IPC Batching        | -67% latence               | ⚡ Avatar réactif               |
| **Phase 4** | CPU Auto-threads    | +15% vitesse (PC 8+ cœurs) | 🚀 Adaptabilité                 |
| **Phase 5** | GPU Dynamic Profile | Évite crashes              | 🛡️ Stabilité                    |
| **Phase 6** | Tests & Validation  | -                          | ✅ Qualité assurée              |

#### 3️⃣ **Documenter Session 11 complète**

On va finaliser `docs/sessions/session_11_performance/README.md` avec :

**Sections principales :**

```markdown
# Session 11 - Performance Optimizations

## 📋 Vue d'ensemble

Objectif : Optimiser les performances de Workly sur tous les fronts.

**6 phases :**

1. ✅ Memory Profiling (validation aucune fuite)
2. ✅ LLM Cache Optimization (warming cache -17% latence)
3. ✅ Unity IPC Overhead (batching messages -67% latence)
4. ✅ CPU Optimization (auto-détection threads)
5. ✅ GPU Profiling & Tuning (profil dynamique)
6. ✅ Tests & Documentation (validation complète)

## 🎯 Phase 1 - Memory Profiling

**Objectif :** Vérifier qu'il n'y a pas de fuite mémoire.

**Résultats :**

- ✅ Aucune fuite détectée (test 100 messages)
- ✅ Garbage collector efficace (-509 MB nettoyage)
- 💡 Opportunité identifiée : première génération +433 MB

**Documentation complète :** [MEMORY_PROFILING.md](./MEMORY_PROFILING.md)

## 🔥 Phase 2 - LLM Cache Optimization

**Objectif :** Réduire la latence de la première génération.

**Résultats :**

- ✅ Warming cache implémenté (pré-allocation KV)
- ⚡ -17% latence (2.11s → 1.75s)
- 🚀 +14% vitesse (19.46 → 22.28 tok/s)

**Documentation complète :** [LLM_CACHE_OPTIMIZATION.md](./LLM_CACHE_OPTIMIZATION.md)

## 🔌 Phase 3 - Unity IPC Overhead

**Objectif :** Accélérer la communication Python ↔ Unity.

**Résultats :**

- ✅ Message batching implémenté
- ⚡ -67% latence (15ms → 5ms)
- 🚀 +200% throughput (60 → 180 msg/s)

**Documentation complète :** [IPC_OPTIMIZATION.md](./IPC_OPTIMIZATION.md)

## 🧵 Phase 4 - CPU Optimization

**Objectif :** Auto-détecter le nombre optimal de threads CPU.

**Résultats :**

- ✅ Détection automatique implémentée
- 🎯 Adaptation selon CPU (4, 6, 8, 12+ cœurs)
- 🚀 +15% vitesse sur PC 8+ cœurs

**Documentation complète :** [CPU_OPTIMIZATION.md](./CPU_OPTIMIZATION.md)

## 🎮 Phase 5 - GPU Profiling & Tuning

**Objectif :** Adapter le profil GPU selon VRAM disponible.

**Résultats :**

- ✅ Sélection dynamique implémentée
- 💾 -17% VRAM (5.4 GB → 4.5 GB en mode balanced)
- 🛡️ Évite crashes (auto-fallback CPU si nécessaire)

**Documentation complète :** [GPU_TUNING.md](./GPU_TUNING.md)

## ✅ Phase 6 - Tests & Documentation

**Objectif :** Valider toutes les optimisations et documenter.

**Résultats :**

- ✅ Tests d'intégration créés et passés
- ✅ Benchmark avant/après complet
- ✅ Documentation Session 11 complète

## 🏆 Résultats cumulés

**Performance globale : +30-40% d'amélioration** 🎊

**Gains principaux :**

- ⚡ Réactivité : -17% latence première génération
- ⚡ Avatar : -67% latence IPC (avatar réactif)
- 🎯 Adaptabilité : Auto-détection CPU/GPU
- 🛡️ Stabilité : Aucune fuite mémoire, évite crashes VRAM

## 📚 Scripts créés

Tous les scripts sont archivés dans `scripts/` :

- `profile_memory.py` (Phase 1)
- `benchmark_llm.py` (Phase 2)
- `test_warming.py` (Phase 2)
- `benchmark_ipc.py` (Phase 3)
- `benchmark_cpu_threads.py` (Phase 4)
- `benchmark_gpu_profiles.py` (Phase 5)
- `test_integration_performance.py` (Phase 6)

## 🚀 Prochaines étapes

Session 11 complète ! Prochaine session :

- Session 12 : Audio & Lip-sync (génération vocale + animation bouche)
```

#### 4️⃣ **Mettre à jour tous les README**

Comme d'habitude, on mettra à jour **systématiquement** :

- ✅ `docs/INDEX.md` (ajouter Phase 3-6)
- ✅ `docs/README.md` (Session 11 complète)
- ✅ `README.md` (racine) - **4 sections obligatoires** :
  - Sessions documentées (Session 11 terminée)
  - Guides spécifiques (tous les guides de Phase 1-6)
  - Changelog (Version 0.14.0-alpha finale)
  - Status final (Session 11 COMPLÈTE, Chat 10 terminé)
- ✅ `CURRENT_STATE.md` (dans chat_transitions si transition de chat)

#### 5️⃣ **Créer un guide de référence rapide**

Un fichier `PERFORMANCE_GUIDE.md` pour les utilisateurs :

````markdown
# 🚀 Guide de Performance - Workly

## Configurations recommandées

### GPU faible (< 4 GB VRAM)

- ✅ Mode "cpu" (n_gpu_layers=0)
- ⏱️ Génération : 5-10s par message
- 💡 Conseil : Fermer applications gourmandes
- 📊 Vitesse : ~5-7 tokens/seconde

### GPU moyen (4-8 GB VRAM)

- ✅ Mode "balanced" (n_gpu_layers=35)
- ⏱️ Génération : 2-3s par message
- 💡 Conseil : Surveiller VRAM usage
- 📊 Vitesse : ~19-20 tokens/seconde

### GPU puissant (> 8 GB VRAM)

- ✅ Mode "performance" (n_gpu_layers=43)
- ⏱️ Génération : 1-2s par message
- 💡 Conseil : Tout est optimal !
- 📊 Vitesse : ~22-23 tokens/seconde

## Optimisations automatiques

Workly détecte automatiquement :

- 🧵 **CPU threads** : Adapté au nombre de cœurs
- 🎮 **GPU profile** : Selon VRAM disponible
- 🔥 **Warming cache** : Activé par défaut (réduit latence)
- 🔌 **IPC batching** : Messages regroupés automatiquement

## Troubleshooting

### ⚠️ Problème : VRAM saturée (crash)

**Symptômes :**

- Unity crash au chargement du modèle
- Message "Out of memory" dans les logs
- Écran noir ou freeze

**Solutions :**

1. Passer en mode "balanced" dans `data/config.json`
2. Fermer applications gourmandes (Chrome, jeux)
3. Utiliser un modèle plus petit (4B au lieu de 7B)

**Commande manuelle :**

```json
{
  "ai": {
    "gpu_profile": "balanced"
  }
}
```
````

### ⚠️ Problème : Génération lente (> 5s)

**Symptômes :**

- Réponse IA prend 5+ secondes
- Tokens/seconde < 10
- CPU à 100% d'utilisation

**Solutions :**

1. Vérifier `n_threads` dans les logs (doit être adapté)
2. Vérifier que GPU est bien utilisé (n_gpu_layers > 0)
3. Fermer processus CPU intensifs en arrière-plan

**Vérification :**

```python
# Dans les logs, chercher :
# "🧵 Threads optimaux détectés : X"
# "🎮 Profil GPU auto : Y"
```

### ⚠️ Problème : Avatar réagit avec retard

**Symptômes :**

- Clique sur expression → avatar change 1-2s après
- Mouvements saccadés
- Interface GUI freeze

**Solutions :**

1. IPC optimisé devrait résoudre ça (Phase 3)
2. Vérifier logs Unity pour "Queue overflow"
3. Réduire fréquence d'envoi des messages

**Déjà optimisé dans Session 11 Phase 3 !** ✅

### ⚠️ Problème : Mémoire RAM augmente continuellement

**Symptômes :**

- RAM usage monte de 500 MB → 2 GB après 1h
- Système ralentit
- Windows affiche "Mémoire insuffisante"

**Solutions :**

1. Ce problème a été vérifié en Phase 1 → **aucune fuite détectée** ✅
2. Si ça arrive quand même, redémarrer Workly
3. Vérifier logs Python pour warnings mémoire

**Note :** Pics temporaires normaux (garbage collector nettoie après)

## Commandes de diagnostic

### Vérifier VRAM utilisée

```python
from src.utils.gpu_utils import get_vram_usage

vram = get_vram_usage()
print(f"VRAM : {vram['used']:.2f} GB / {vram['total']:.2f} GB ({vram['percent']:.1f}%)")
```

### Vérifier CPU threads détectés

```python
from src.ai.config import AIConfig

config = AIConfig()
print(f"Threads CPU : {config.n_threads}")
```

### Vérifier profil GPU actif

```python
from src.ai.model_manager import ModelManager

manager = ModelManager()
profile = manager.get_current_profile()
print(f"Profil GPU : {profile['name']} ({profile['n_gpu_layers']} layers)")
```

## Benchmarks de référence

### Configuration test (RTX 4050, 6 GB VRAM)

| Test                | Baseline (avant) | Optimisé (après) | Gain      |
| ------------------- | ---------------- | ---------------- | --------- |
| Chargement modèle   | 5.10s            | 2.57s            | **-49%**  |
| Première génération | 2.11s            | 1.75s            | **-17%**  |
| Génération moyenne  | 1.80s            | 1.75s            | **-3%**   |
| Tokens/seconde      | 19.46            | 22.28            | **+14%**  |
| IPC latence         | 15ms             | 5ms              | **-67%**  |
| Messages IPC/s      | 60               | 180              | **+200%** |

### Comparaison GPU profiles

| Profile                 | VRAM   | Tokens/s | Latence | Stabilité       |
| ----------------------- | ------ | -------- | ------- | --------------- |
| Performance (43 layers) | 5.4 GB | 22 tok/s | 1.75s   | ⚠️ Risque crash |
| Balanced (35 layers)    | 4.5 GB | 20 tok/s | 1.95s   | ✅ Stable       |
| CPU (0 layers)          | 0.5 GB | 6 tok/s  | 6.50s   | ✅ Très stable  |

## Recommandations finales

1. **Laisser l'auto-détection faire son travail** : CPU threads et GPU profile sont optimisés automatiquement
2. **Warming cache activé par défaut** : Ne pas désactiver (améliore première réponse)
3. **IPC batching transparent** : Aucune action requise de ta part
4. **Surveiller VRAM si < 8 GB** : Passer en "balanced" si crashes fréquents
5. **Redémarrer après 2-3h d'utilisation intensive** : Nettoie complètement la mémoire

**Workly est maintenant optimisé à 30-40% de performance en plus !** 🎊

```

### 📊 Récapitulatif des livrables Phase 6

**Fichiers créés/modifiés :**
1. ✅ `tests/test_integration_performance.py` (tests complets)
2. ✅ `docs/sessions/session_11_performance/README.md` (vue d'ensemble finale)
3. ✅ `docs/sessions/session_11_performance/PERFORMANCE_GUIDE.md` (guide utilisateur)
4. ✅ `docs/sessions/session_11_performance/BENCHMARK_RESULTS.md` (tous les benchmarks)
5. ✅ `docs/INDEX.md` (arborescence mise à jour)
6. ✅ `docs/README.md` (Session 11 complète)
7. ✅ `README.md` (racine, 4 sections mises à jour)

**Tests créés :**
- ✅ test_warming_cache_active()
- ✅ test_ipc_batching()
- ✅ test_cpu_threads_auto_detection()
- ✅ test_gpu_profile_selection()
- ✅ test_full_optimized_pipeline()
- ✅ test_memory_stability_long_run()

**Documentation complète :**
- ✅ Toutes les phases documentées (1 à 6)
- ✅ Guides techniques détaillés pour chaque phase
- ✅ Guide utilisateur de référence (troubleshooting)
- ✅ Benchmarks avant/après complets
- ✅ Scripts archivés dans `docs/sessions/session_11_performance/scripts/`

---

## 📊 Récapitulatif global des 4 phases restantes

| Phase | Objectif | Métrique clé | Gain estimé | Complexité |
|-------|----------|--------------|-------------|------------|
| **Phase 3 - IPC** | Accélérer communication Python↔Unity | Latence round-trip | **-50 à -70%** | 🟡 Moyenne |
| **Phase 4 - CPU** | Auto-détecter threads optimaux | Adaptation automatique | **+5 à +15%** (selon CPU) | 🟢 Facile |
| **Phase 5 - GPU** | Profil dynamique selon VRAM | Utilisation VRAM | **Évite crashes** + **stabilité** | 🟡 Moyenne |
| **Phase 6 - Tests** | Valider gains cumulés | Performance globale | **~30-40% total** 🎊 | 🟢 Facile |

### Ordre d'implémentation recommandé

1. **Phase 3 (IPC)** → Priorité haute (impact utilisateur direct : avatar réactif)
2. **Phase 4 (CPU)** → Priorité moyenne (adaptation automatique)
3. **Phase 5 (GPU)** → Priorité haute (évite crashes, stabilité critique)
4. **Phase 6 (Tests)** → Obligatoire (validation finale)

### Effort estimé par phase

| Phase | Temps dev | Temps test | Temps doc | Total |
|-------|-----------|------------|-----------|-------|
| Phase 3 | 2-3h | 1h | 1h | **4-5h** |
| Phase 4 | 1-2h | 1h | 1h | **3-4h** |
| Phase 5 | 2-3h | 1h | 1h | **4-5h** |
| Phase 6 | 1h | 2h | 2h | **5h** |
| **Total** | **6-9h** | **5h** | **5h** | **16-19h** |

### Technologies à maîtriser

**Phase 3 (IPC) :**
- Socket TCP Python (déjà en place)
- JSON serialization (déjà en place)
- C# Queue et threading Unity (déjà en place)
- Nouveau : Message batching, protocole binaire (MessagePack optionnel)

**Phase 4 (CPU) :**
- psutil (déjà installé)
- platform module Python (built-in)
- llama.cpp n_threads parameter (déjà utilisé)

**Phase 5 (GPU) :**
- pynvml (déjà installé)
- llama.cpp n_gpu_layers parameter (déjà utilisé)
- Profils GPU (déjà configurés)

**Phase 6 (Tests) :**
- pytest (déjà installé)
- pytest-benchmark (déjà installé)
- Documentation markdown (déjà maîtrisé)

---

## 🎯 Vision finale après Session 11

### Avant Session 11 (baseline)

```

Workly v0.12.0
├── Chargement modèle : 5.10s
├── Première génération : 2.11s (lente !)
├── Génération suivante : 1.80s
├── IPC latence : 15ms (avatar retard visible)
├── CPU threads : 6 (fixe, pas optimal)
├── GPU profile : performance (risque crash)
├── VRAM usage : 5.4 GB (90% saturé)
└── Mémoire RAM : stable (✅ pas de fuite)

```

### Après Session 11 (optimisé)

```

Workly v0.14.0 🎊
├── Chargement modèle : 2.57s (-49% !) ⚡
├── Première génération : 1.75s (-17% !) ⚡
├── Génération suivante : 1.75s (stable)
├── IPC latence : 5ms (-67% !) ⚡
├── IPC throughput : 180 msg/s (+200% !) 🚀
├── CPU threads : auto-détecté (adaptable) 🎯
├── GPU profile : dynamique (évite crash) 🛡️
├── VRAM usage : 4.5 GB (75%, marge sécurité)
└── Mémoire RAM : stable (✅ validé 100 msgs)

Performance globale : +30-40% 🏆
Stabilité : Crashes VRAM évités 🛡️
Adaptabilité : Fonctionne sur tout PC 🎯

```

---

## 📚 Ressources utiles

### Documentation officielle
- llama.cpp : https://github.com/ggerganov/llama.cpp
- llama-cpp-python : https://github.com/abetlen/llama-cpp-python
- pynvml : https://github.com/gpuopenanalytics/pynvml
- psutil : https://github.com/giampaolo/psutil

### Guides internes (après Session 11)
- `docs/sessions/session_11_performance/MEMORY_PROFILING.md`
- `docs/sessions/session_11_performance/LLM_CACHE_OPTIMIZATION.md`
- `docs/sessions/session_11_performance/IPC_OPTIMIZATION.md`
- `docs/sessions/session_11_performance/CPU_OPTIMIZATION.md`
- `docs/sessions/session_11_performance/GPU_TUNING.md`
- `docs/sessions/session_11_performance/PERFORMANCE_GUIDE.md`

---

**📝 Fin du document de référence - Phases 3 à 6 de Session 11**

*Ce document a été créé exceptionnellement pour servir de référence personnelle détaillée.*
```
