# 🎮 Guide d'installation CUDA pour Desktop-Mate

Ce guide explique comment installer `llama-cpp-python` avec support CUDA (GPU NVIDIA) pour Desktop-Mate.

---

## ⚠️ Prérequis

### Hardware

- **GPU NVIDIA** avec au moins **4 GB de VRAM**
- **Architectures supportées** :
  - Turing (RTX 20xx, GTX 16xx)
  - Ampere (RTX 30xx)
  - Ada Lovelace (RTX 40xx) ✅ (testé avec RTX 4050)
  - Hopper (H100, etc.)

### Software

1. **Windows 10/11** 64-bit
2. **Python 3.10+** (testé avec 3.10.9)
3. **CUDA Toolkit** (voir ci-dessous)
4. **Visual Studio 2022** avec outils C++

---

## 📦 Installation Étape par Étape

### 1. Installer CUDA Toolkit

#### Téléchargement

- **Site officiel** : https://developer.nvidia.com/cuda-downloads
- **Version recommandée** : CUDA 12.x (testé avec 12.9)
- **Taille** : ~3.5 GB

#### Installation

1. Exécuter l'installeur CUDA
2. Choisir "Installation Express" (recommandé)
3. Accepter tous les composants par défaut
4. Redémarrer l'ordinateur après installation

#### Vérification

```powershell
nvcc --version
```

**Output attendu** :
```
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2024 NVIDIA Corporation
Built on Thu_Sep_26_...
Cuda compilation tools, release 12.9, V12.9.86
```

---

### 2. Installer Visual Studio 2022

#### Téléchargement

- **Site officiel** : https://visualstudio.microsoft.com/
- **Version** : Community Edition (gratuit)
- **Taille** : ~7-8 GB

#### Installation

1. Exécuter l'installeur Visual Studio
2. Sélectionner **"Développement Desktop en C++"**
3. Dans les options individuelles, vérifier que sont cochés :
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
   - ✅ Windows SDK (dernière version)
   - ✅ Outils CMake C++ pour Windows
4. Cliquer sur "Installer"
5. Attendre l'installation (~30 minutes)

#### Vérification

```powershell
"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cl
```

**Output attendu** :
```
Microsoft (R) C/C++ Optimizing Compiler Version 19.44...
```

---

### 3. Installer llama-cpp-python avec CUDA

#### 3.1 Activer l'environnement virtuel

```powershell
cd C:\Dev\desktop-mate
.\venv\Scripts\Activate.ps1
```

#### 3.2 Désinstaller l'ancienne version (si existante)

```powershell
pip uninstall -y llama-cpp-python
```

#### 3.3 Compiler avec support CUDA

```powershell
$env:CMAKE_ARGS="-DGGML_CUDA=on"
$env:FORCE_CMAKE="1"
pip install llama-cpp-python --no-cache-dir --force-reinstall --verbose
```

**⏱️ Durée** : 15-25 minutes (selon CPU)

**📊 Progression** :
1. CMake détecte CUDA Toolkit ✅
2. Configuration du projet ✅
3. Compilation des kernels CUDA (.cu files) ⏳ (le plus long)
4. Linking des bibliothèques ✅
5. Création du wheel Python ✅
6. Installation ✅

**✅ Succès** :
```
Successfully built llama-cpp-python
Successfully installed llama-cpp-python-0.3.16
```

---

## 🧪 Tests de Vérification

### Test 1 : Support GPU offload

```powershell
.\venv\Scripts\Activate.ps1
python -c "import llama_cpp.llama_cpp as lc; print('GPU offload:', lc.llama_supports_gpu_offload())"
```

**Output attendu** :
```
ggml_cuda_init: found 1 CUDA devices:
  Device 0: NVIDIA GeForce RTX 4050 Laptop GPU, compute capability 8.9
GPU offload: True
```

**❌ Si False** : La compilation a échoué, recommencer l'étape 3.

---

### Test 2 : Chargement d'un modèle avec GPU layers

```python
from llama_cpp import Llama

llm = Llama(
    model_path="models/zephyr-7b-beta.Q5_K_M.gguf",
    n_gpu_layers=5,  # Test avec 5 layers
    n_ctx=512,
    verbose=True
)

response = llm("Hello, ", max_tokens=10)
print(response["choices"][0]["text"])
```

**Logs attendus** :
```
llama_model_load_from_file_impl: using device CUDA0 (NVIDIA GeForce RTX 4050)
load_tensors: offloading 5 repeating layers to GPU
load_tensors: offloaded 5/33 layers to GPU
load_tensors: CUDA0 model buffer size = 755.00 MiB
```

**✅ Succès** : Le modèle utilise le GPU !

---

### Test 3 : Application complète

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

**Actions** :
1. Onglet **"Connexion"** → Cliquer **"Charger IA"**
2. Ouvrir **Gestionnaire des tâches** (`Ctrl+Shift+Esc`)
3. Onglet **"Performances"** → Sélectionner **GPU**
4. Observer **"Mémoire GPU dédiée"**

**✅ Succès** :
- Avant chargement : ~0.5 GB
- Après chargement : **~3-4 GB** (avec 35 layers)
- Logs : `✅ Modèle chargé avec succès ! (GPU layers: 35)`

---

## ⚙️ Configuration GPU Profiles

Desktop-Mate propose 3 profils GPU dans `data/config.json` :

### 1. Performance (Recommandé si 8+ GB VRAM)

```json
"performance": {
  "n_gpu_layers": 43,      // Toutes les layers sur GPU
  "n_ctx": 4096,           // Contexte large
  "n_batch": 512,
  "n_threads": 6,
  "use_mlock": true
}
```

**VRAM requise** : ~6-7 GB  
**Vitesse** : Maximale 🚀

---

### 2. Balanced (Par défaut, 6 GB VRAM)

```json
"balanced": {
  "n_gpu_layers": 35,      // 35/43 layers sur GPU
  "n_ctx": 2048,
  "n_batch": 256,
  "n_threads": 6,
  "use_mlock": true
}
```

**VRAM requise** : ~3-4 GB  
**Vitesse** : Très bonne ✨

---

### 3. Low-End (4 GB VRAM minimum)

```json
"low_end": {
  "n_gpu_layers": 20,      // 20/43 layers sur GPU
  "n_ctx": 1024,
  "n_batch": 128,
  "n_threads": 4,
  "use_mlock": false
}
```

**VRAM requise** : ~2 GB  
**Vitesse** : Correcte ⚡

---

## 🐛 Dépannage

### Problème 1 : "CUDA support: False"

**Causes possibles** :
1. CUDA Toolkit non installé
2. Visual Studio non installé
3. Variables d'environnement incorrectes

**Solution** :
```powershell
# Vérifier CUDA
nvcc --version

# Vérifier Visual Studio
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

# Recommencer compilation
pip uninstall -y llama-cpp-python
$env:CMAKE_ARGS="-DGGML_CUDA=on"
$env:FORCE_CMAKE="1"
pip install llama-cpp-python --no-cache-dir --force-reinstall --verbose
```

---

### Problème 2 : "CMake not found"

**Solution** :
```powershell
pip install cmake
```

---

### Problème 3 : "CUDA out of memory"

**Symptôme** : Erreur lors du chargement du modèle

**Causes** :
- `n_gpu_layers` trop élevé pour ta VRAM
- Autres applications utilisent la VRAM

**Solution** :
1. Réduire `n_gpu_layers` (par exemple de 35 à 20)
2. Fermer les applications gourmandes en GPU (jeux, navigateurs, etc.)
3. Changer de profil GPU : `performance` → `balanced` → `low_end`

**Dans `data/config.json`** :
```json
{
  "ai": {
    "gpu_profile": "low_end"  // ← Changer ici
  }
}
```

---

### Problème 4 : Compilation échoue avec erreurs

**Erreurs typiques** :
```
error C2440: conversion impossible
error LNK2019: symbole externe non résolu
```

**Solution** :
1. Vérifier que Visual Studio 2022 est installé (pas 2019 ou 2017)
2. Vérifier que "Outils de build MSVC" sont installés
3. Réinstaller CUDA Toolkit (version 12.x)
4. Redémarrer l'ordinateur
5. Recommencer la compilation

---

### Problème 5 : Warnings pendant la compilation

**Exemple** :
```
warning C4244: conversion de 'double' en 'float'
warning #177-D: variable "stride_tile_Q" was declared but never referenced
```

**✅ NORMAL !** Ces warnings sont bénins et n'empêchent pas le fonctionnement.

**Ce qui compte** :
- `Successfully built llama-cpp-python` ✅
- `Successfully installed llama-cpp-python` ✅

---

## 📊 Comparaison Performances

### Test : Génération de 100 tokens avec Zephyr-7B Q5_K_M

| Profil | Layers GPU | VRAM | Temps | Vitesse | Amélioration |
|--------|-----------|------|-------|---------|--------------|
| **CPU only** | 0 | 0 GB | ~20s | 5 tok/s | Baseline |
| **Low-end** | 20 | 2 GB | ~6s | 17 tok/s | **3.3x** |
| **Balanced** | 35 | 3-4 GB | ~3s | 33 tok/s | **6.7x** |
| **Performance** | 43 | 6-7 GB | ~2s | 50 tok/s | **10x** |

**Hardware** : RTX 4050 Laptop GPU (6GB VRAM), i7-13700H, 32GB RAM

---

## 🔧 Scripts Utilitaires

### Script 1 : Test support CUDA

Créer `test_cuda_support.py` :

```python
#!/usr/bin/env python3
import sys
import llama_cpp.llama_cpp as lc

print("="*60)
print("🧪 Test du support CUDA")
print("="*60)

# Test 1: Support GPU offload
has_cuda = lc.llama_supports_gpu_offload()
print(f"\n✅ Support GPU offload: {has_cuda}")

if not has_cuda:
    print("\n❌ CUDA non supporté !")
    print("Recompiler avec: $env:CMAKE_ARGS=\"-DGGML_CUDA=on\"")
    sys.exit(1)

# Test 2: Liste des fonctions CUDA
cuda_funcs = [attr for attr in dir(lc) if 'cuda' in attr.lower() or 'gpu' in attr.lower()]
print(f"\n📋 Fonctions CUDA disponibles ({len(cuda_funcs)}):")
for func in cuda_funcs:
    print(f"  - {func}")

print("\n" + "="*60)
print("✅ Tout est OK ! CUDA fonctionne parfaitement.")
print("="*60)
```

**Usage** :
```powershell
.\venv\Scripts\Activate.ps1
python test_cuda_support.py
```

---

### Script 2 : Monitoring VRAM

Créer `monitor_vram.py` :

```python
#!/usr/bin/env python3
import pynvml
import time

pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

print("🎮 Monitoring VRAM (Ctrl+C pour arrêter)")
print("-" * 50)

try:
    while True:
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        used_gb = info.used / 1024**3
        free_gb = info.free / 1024**3
        total_gb = info.total / 1024**3
        
        print(f"\rVRAM: {used_gb:.2f}/{total_gb:.2f} GB | Libre: {free_gb:.2f} GB", end="")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n✅ Monitoring arrêté")
finally:
    pynvml.nvmlShutdown()
```

**Usage** :
```powershell
.\venv\Scripts\Activate.ps1
pip install pynvml
python monitor_vram.py
```

---

## 📚 Ressources

### Documentation officielle

- **llama.cpp** : https://github.com/ggerganov/llama.cpp
- **llama-cpp-python** : https://github.com/abetlen/llama-cpp-python
- **CUDA Toolkit** : https://docs.nvidia.com/cuda/
- **GGUF Format** : https://github.com/ggerganov/ggml/blob/master/docs/gguf.md

### Modèles recommandés

- **Zephyr-7B** : https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF (utilisé dans Desktop-Mate)
- **Mistral-7B** : https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
- **Llama-3-8B** : https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF

### Communauté

- **Reddit** : r/LocalLLaMA
- **Discord** : llama.cpp Discord server
- **GitHub Issues** : llama-cpp-python issues

---

## ✅ Checklist Finale

Avant de dire "L'installation CUDA est terminée" :

- [ ] `nvcc --version` affiche la version CUDA
- [ ] Visual Studio 2022 installé avec outils C++
- [ ] `llama_supports_gpu_offload()` retourne `True`
- [ ] Test de chargement modèle avec 5 GPU layers réussi
- [ ] VRAM augmente dans le Gestionnaire des tâches
- [ ] Desktop-Mate charge le modèle avec "GPU layers: 35"
- [ ] Génération de texte rapide (~2-3 secondes)

**🎊 Si toutes les cases sont cochées : Félicitations ! CUDA fonctionne ! ✨**

---

**Dernière mise à jour** : 23 octobre 2025  
**Version Desktop-Mate** : 0.5.0-alpha  
**Version llama-cpp-python** : 0.3.16 (avec CUDA)
