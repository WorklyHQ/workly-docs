# 📦 Dépendances Python - Session 14

**Date** : 16 novembre 2025
**Version** : 0.18.0-alpha (cible)

---

## 📊 État Actuel

### Packages Déjà Installés

**Vérification effectuée** : 16 novembre 2025

| Package | Version | Statut | Utilisation |
|---------|---------|--------|-------------|
| `Python` | 3.10.9 | ✅ OK | Runtime principal |
| `PySide6` | (installé) | ✅ OK | Interface Qt GUI |
| `numpy` | (installé) | ✅ OK | Calculs cosine similarity |
| `llama-cpp-python` | (avec CUDA) | ✅ OK | Modèle LLM Zephyr-7B |
| `discord.py` | (installé) | ✅ OK | Bot Discord |
| `pytest` | (installé) | ✅ OK | Tests unitaires |

**Commande vérification** :

```powershell
cd c:\Dev\workly_project\workly-desktop
.\venv\Scripts\Activate.ps1
python -c "import sys; print('Python:', sys.version.split()[0]); import PySide6; print('✅ PySide6'); import numpy; print('✅ numpy')"
```

---

## 📥 Packages à Installer (Phase 1)

### sentence-transformers

**Description** : Modèles embeddings pré-entraînés pour recherche sémantique

**Utilisation** : MemoryManager - Recherche contexte pertinent dans mémoire long-terme

**Taille** :
- Package : ~50 MB
- Modèle `all-MiniLM-L6-v2` : ~80 MB
- Dépendances (torch, transformers, etc.) : ~200 MB
- **Total estimé** : ~330 MB

**Installation** :

```powershell
cd c:\Dev\workly_project\workly-desktop
.\venv\Scripts\Activate.ps1

pip install sentence-transformers

# Vérification
python -c "from sentence_transformers import SentenceTransformer; print('✅ sentence-transformers OK')"
```

**Premier run** (télécharge modèle automatiquement) :

```python
from sentence_transformers import SentenceTransformer

# Télécharge all-MiniLM-L6-v2 (~80 MB) au premier appel
model = SentenceTransformer('all-MiniLM-L6-v2')
```

**Cache modèle** : `C:\Users\<username>\.cache\torch\sentence_transformers\`

---

## 📋 Dépendances Complètes (requirements.txt)

### Fichier Actuel

**Emplacement** : `workly-desktop/requirements.txt`

**Contenu actuel estimé** :

```
PySide6>=6.5.0
llama-cpp-python
discord.py>=2.3.0
python-dotenv
pytest>=7.4.0
```

### Ajouts Session 14

**Ajouter dans requirements.txt** :

```
# === Session 14: Améliorations IA ===
sentence-transformers>=2.2.0  # Embeddings pour recherche sémantique
```

### requirements.txt Complet Suggéré

```txt
# === Core GUI ===
PySide6>=6.5.0

# === IA & LLM ===
llama-cpp-python  # Modèle Zephyr-7B local (CUDA support)
sentence-transformers>=2.2.0  # Embeddings recherche sémantique

# === Discord Bot ===
discord.py>=2.3.0

# === Utilities ===
python-dotenv  # Variables environnement (.env)
numpy>=1.24.0  # Calculs numériques

# === Tests ===
pytest>=7.4.0
pytest-cov>=4.1.0  # Coverage reports
pytest-asyncio>=0.21.0  # Tests async Discord

# === Development (optionnel) ===
# black  # Code formatting
# flake8  # Linting
# mypy  # Type checking
```

---

## 🔧 Installation Complète Nouveau Environnement

### Depuis Zéro

```powershell
# 1. Créer venv
python -m venv venv

# 2. Activer venv
.\venv\Scripts\Activate.ps1

# 3. Mettre à jour pip
python -m pip install --upgrade pip

# 4. Installer llama-cpp-python avec CUDA
$env:CMAKE_ARGS="-DLLAMA_CUDA=on"
$env:FORCE_CMAKE="1"
pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose

# 5. Installer autres packages
pip install -r requirements.txt

# 6. Vérifier installation
pytest tests/ -v
```

**Durée totale** : ~30-40 minutes (compilation CUDA longue)

---

## 📊 Comparaison Tailles

### Avant Session 14

| Composant | Taille |
|-----------|--------|
| venv/ (packages Python) | ~3 GB |
| models/ (Zephyr-7B) | 6.8 GB |
| data/ (config, logs) | <10 MB |
| **TOTAL** | ~9.8 GB |

### Après Session 14

| Composant | Taille |
|-----------|--------|
| venv/ (packages Python) | ~3.3 GB (+300 MB sentence-transformers) |
| models/ (Zephyr-7B) | 6.8 GB |
| data/ (config, logs, **memory**, **personality**, **emotions**) | ~50 MB (+40 MB données IA) |
| **TOTAL** | ~10.15 GB (+350 MB) |

**Impact** : +350 MB (~3.5% augmentation)

---

## 🚨 Prérequis Système

### Hardware Minimum

- **CPU** : Intel i5 ou équivalent (4+ cores)
- **RAM** : 16 GB (8 GB système + 8 GB app)
- **GPU** : NVIDIA GTX 1060 ou supérieur (6 GB VRAM minimum)
- **Disque** : 15 GB espace libre (SSD recommandé)

### Software Prérequis

- **Windows** : 10 ou 11 (64-bit)
- **Python** : 3.10+ (3.10.9 recommandé)
- **CUDA Toolkit** : 11.x ou 12.x (inclus dans drivers NVIDIA)
- **Drivers NVIDIA** : Récents (Game Ready ou Studio)
- **Visual Studio Build Tools** : Pour compilation llama-cpp-python

---

## 🔍 Vérification Installation Complète

### Script Test

**Fichier** : `scripts/verify_dependencies.py`

```python
#!/usr/bin/env python3
"""Vérifie toutes dépendances Session 14."""

import sys
from importlib import import_module

def check_package(name: str, display_name: str = None) -> bool:
    """Vérifie si package importable."""
    display = display_name or name
    try:
        import_module(name)
        print(f"✅ {display}")
        return True
    except ImportError:
        print(f"❌ {display} NOT INSTALLED")
        return False

def main():
    print("=== Vérification Dépendances Workly Session 14 ===\n")

    print(f"Python version: {sys.version.split()[0]}")

    if sys.version_info < (3, 10):
        print("⚠️  WARNING: Python 3.10+ recommandé")

    print("\n--- Packages Core ---")
    results = []
    results.append(check_package("PySide6", "PySide6 (Qt GUI)"))
    results.append(check_package("numpy", "numpy (calculs)"))

    print("\n--- Packages IA ---")
    results.append(check_package("llama_cpp", "llama-cpp-python (LLM)"))
    results.append(check_package("sentence_transformers", "sentence-transformers (embeddings)"))

    print("\n--- Packages Discord ---")
    results.append(check_package("discord", "discord.py (bot)"))

    print("\n--- Packages Tests ---")
    results.append(check_package("pytest", "pytest (tests unitaires)"))

    # Vérifier CUDA
    print("\n--- CUDA Support ---")
    try:
        from llama_cpp import Llama
        cuda_available = hasattr(Llama, '__init__')  # Simplifié
        print(f"✅ CUDA support detected" if cuda_available else "⚠️  CUDA support unknown")
    except:
        print("❌ llama-cpp-python not working")

    # Résumé
    print("\n" + "=" * 50)
    success = sum(results)
    total = len(results)
    print(f"Résultat: {success}/{total} packages OK")

    if success == total:
        print("✅ Toutes dépendances installées !")
        return 0
    else:
        print("❌ Certaines dépendances manquantes")
        print("\nInstaller avec : pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Exécution** :

```powershell
.\venv\Scripts\Activate.ps1
python scripts/verify_dependencies.py
```

---

## 🐛 Troubleshooting

### Problème 1 : sentence-transformers Lent au Premier Run

**Symptôme** : Premier `SentenceTransformer('all-MiniLM-L6-v2')` prend 1-2 minutes

**Cause** : Téléchargement modèle depuis HuggingFace (~80 MB)

**Solution** : Normal, attendre téléchargement. Ensuite en cache.

### Problème 2 : Erreur Import sentence_transformers

**Symptôme** :
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solution** :
```powershell
.\venv\Scripts\Activate.ps1
pip install sentence-transformers
```

### Problème 3 : CUDA Not Available

**Symptôme** :
```python
# Test CUDA
from llama_cpp import Llama
print(hasattr(Llama, 'n_gpu_layers'))  # False
```

**Solution** : Réinstaller llama-cpp-python avec CUDA :

```powershell
$env:CMAKE_ARGS="-DLLAMA_CUDA=on"
$env:FORCE_CMAKE="1"
pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose
```

Voir `docs/chat_transitions/chat_12_gpu_ui_discord/TROUBLESHOOTING.md` pour détails.

---

## 📚 Documentation Packages

### sentence-transformers

**Docs officielles** : https://www.sbert.net/

**Modèles disponibles** : https://www.sbert.net/docs/pretrained_models.html

**Modèle utilisé** : `all-MiniLM-L6-v2`
- Dimension : 384
- Taille : 80 MB
- Performance : Bon équilibre vitesse/qualité
- Langue : Multilingue (inclut français)

**Exemple utilisation** :

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Charger modèle (télécharge au 1er run)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encoder textes
texts = ["Bonjour", "Hello", "Salut"]
embeddings = model.encode(texts)

# embeddings.shape = (3, 384)

# Cosine similarity
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

sim = cosine_similarity(embeddings[0], embeddings[2])
print(f"Similarité 'Bonjour' vs 'Salut': {sim:.3f}")  # ~0.85
```

---

## ✅ Checklist Installation Phase 1

Avant de commencer codage Phase 1 :

- ✅ venv activé (`.\venv\Scripts\Activate.ps1`)
- ✅ `sentence-transformers` installé
- ✅ Import `from sentence_transformers import SentenceTransformer` OK
- ✅ Modèle `all-MiniLM-L6-v2` téléchargé (auto au 1er run)
- ✅ `numpy` disponible
- ✅ Script `verify_dependencies.py` passe

**Commande rapide** :

```powershell
.\venv\Scripts\Activate.ps1
pip install sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); print('✅ OK')"
```

---

**Créé le** : 16 novembre 2025
**Dernière mise à jour** : 16 novembre 2025
