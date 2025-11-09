# 🔧 Configuration Git Multi-Repos - Workly Project

**Date :** 10 novembre 2025  
**Chat :** Chat 11 - Configuration Git  
**Objectif :** Configurer 3 repos GitHub séparés avec conventions de commits différentes

---

## 📊 Vue d'ensemble de l'architecture Git

### 🗂️ Structure des repos

Le projet Workly est organisé en **3 repos GitHub séparés** :

```
c:\Dev\workly_project\
├── workly-desktop/        → https://github.com/WorklyHQ/workly-desktop.git
├── workly-website/        → https://github.com/WorklyHQ/workly-website.git
└── workly-docs/           → https://github.com/WorklyHQ/workly-docs.git
```

### 🎯 Conventions de commits par repo

| Repo | Convention | Description |
|------|-----------|-------------|
| **workly-desktop** | **Strict** (Conventional Commits) | `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:` |
| **workly-website** | **Libre** | Commits descriptifs sans format strict |
| **workly-docs** | **Semi-Strict** | `docs:` pour doc technique, libre pour notes |

---

## 🖥️ Repo 1 : workly-desktop

### 📝 Convention : Strict (Conventional Commits)

**URL GitHub :** https://github.com/WorklyHQ/workly-desktop.git

#### Format des commits

```bash
<type>: <description courte>

[corps optionnel]
```

#### Types autorisés

- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation uniquement
- `style:` - Formatage (pas de changement logique)
- `refactor:` - Refactoring
- `test:` - Tests
- `chore:` - Maintenance/configuration
- `perf:` - Optimisation de performance
- `ci:` - Configuration CI/CD
- `build:` - Système de build

#### Exemples

```bash
feat: implement VRM blendshape control
fix: resolve Unity threading issue
docs: update session 11 guide
refactor: simplify IPC message handling
test: add unit tests for ChatEngine
chore: update requirements.txt
```

#### Scopes suggérés (optionnels)

```bash
feat(ai): add emotion detection
fix(unity): resolve VRM loading crash
docs(session-10): add ChatEngine guide
test(ipc): add socket timeout tests
```

**Scopes disponibles :** `ai`, `unity`, `gui`, `ipc`, `discord`, `audio`, `avatar`, `config`, `tests`

#### Règles strictes

- ✅ Impératif présent ("add" pas "added")
- ✅ Pas de majuscule au début
- ✅ Pas de point à la fin
- ✅ Max 72 caractères
- ✅ En anglais

#### Fichier de référence

📄 **[GIT_COMMIT_CONVENTIONS.md](../../workly-desktop/GIT_COMMIT_CONVENTIONS.md)** dans `workly-desktop/`

---

## 🌐 Repo 2 : workly-website

### 📝 Convention : Libre

**URL GitHub :** https://github.com/WorklyHQ/workly-website.git

#### Format des commits

**Aucun format strict !** Tu es libre d'écrire comme tu veux.

#### Suggestions (optionnelles)

Tu **peux** utiliser des préfixes si tu veux, mais ce n'est **pas obligatoire** :

```bash
[ADD] Page about avec équipe
[UPDATE] CSS de la homepage
[FIX] Lien cassé dans navigation
[STYLE] Amélioration responsive mobile
```

#### Exemples valides (tous acceptés)

```bash
# Avec préfixe
[ADD] Page de contact
[UPDATE] CSS homepage

# Sans préfixe (totalement OK !)
Ajout de la page privacy
Mise à jour du design
Correction du footer

# Français ou Anglais (OK !)
Add privacy policy page
Ajout page mentions légales

# Descriptif (OK aussi !)
Refonte complète de la page about avec nouvelles photos

# Court (OK !)
Fix typo
Update CSS
```

#### Règles minimales

- ✅ Description claire et compréhensible
- ✅ Français ou anglais, au choix
- ✅ Commits réguliers plutôt qu'énormes
- ❌ Éviter : commits vides (`update`, `fix`, `.`)

#### Fichier de référence

📄 **[GIT_COMMIT_CONVENTIONS.md](../../workly-website/GIT_COMMIT_CONVENTIONS.md)** dans `workly-website/`

---

## 📚 Repo 3 : workly-docs

### 📝 Convention : Semi-Strict

**URL GitHub :** https://github.com/WorklyHQ/workly-docs.git

#### Format des commits

**Deux formats acceptés :**

1. **Format strict** (pour doc technique) :
```bash
docs: <description>
```

2. **Format libre** (pour notes) :
```bash
Description libre
```

#### Quand utiliser `docs:` ?

| Type de changement | Format |
|-------------------|--------|
| Ajout de session complète | `docs: add session 12 guide` |
| Mise à jour guide technique | `docs: update IPC optimization guide` |
| Création CURRENT_STATE | `docs: update current state for chat 11` |
| Mise à jour INDEX/README | `docs: update index with session 12` |
| Notes rapides/brainstorming | `Notes session 12 - idées` |
| TODO temporaire | `TODO: vérifier Unity version` |

#### Types de commits `docs:`

```bash
docs: add          # Ajout de nouvelle doc
docs: update       # Mise à jour doc existante
docs: fix          # Correction (typos, erreurs)
docs: reorganize   # Réorganisation structure
docs: remove       # Suppression doc obsolète
```

#### Avec scope (recommandé)

```bash
docs(session-12): add website implementation guide
docs(index): update with sessions 10-12
docs(current-state): update for chat 11
docs(transitions): add chat 10 to 11 prompt
```

#### Exemples valides (tous acceptés)

```bash
# Format strict (préféré pour doc technique)
docs: add session 12 website implementation
docs(session-11): add performance guide
docs: update INDEX.md with new sessions

# Format libre (OK pour notes)
Notes de brainstorming pour session 13
TODO - vérifier Unity 2022.3 LTS
Résumé chat 10 - phases 1-3

# Mixte (totalement OK dans le même repo)
docs: add session 12 guide
Notes rapides sur les animations
docs(index): update with session 12
```

#### Langue

**Français privilégié** (projet personnel)

#### Fichier de référence

📄 **[GIT_COMMIT_CONVENTIONS.md](GIT_COMMIT_CONVENTIONS.md)** dans `workly-docs/`

---

## 🚀 Configuration initiale effectuée

### ✅ workly-desktop

```bash
# Déjà configuré
✅ Repo GitHub : https://github.com/WorklyHQ/workly-desktop.git
✅ Branch principale : main
✅ Remote origin configuré
✅ Convention : Strict (Conventional Commits)
✅ Fichier : GIT_COMMIT_CONVENTIONS.md créé
```

### ✅ workly-website

```bash
# Déjà configuré
✅ Repo GitHub : https://github.com/WorklyHQ/workly-website.git
✅ Branch principale : main
✅ Remote origin configuré
✅ Convention : Libre
✅ Fichier : GIT_COMMIT_CONVENTIONS.md créé
```

### ✅ workly-docs

```bash
# Configuration effectuée le 10 novembre 2025
✅ Repo local initialisé : git init
✅ Fichier .gitignore créé
✅ Repo GitHub créé : https://github.com/WorklyHQ/workly-docs.git
✅ Remote origin configuré
✅ Branch principale : main
✅ Premier commit : "docs: initial commit - complete documentation structure"
✅ Push initial effectué : 151 fichiers, 54224 insertions
✅ Convention : Semi-Strict
✅ Fichier : GIT_COMMIT_CONVENTIONS.md créé
```

---

## 📖 Guide d'utilisation rapide

### Vérifier les remotes

```powershell
# workly-desktop
cd c:\Dev\workly_project\workly-desktop
git remote -v

# workly-website
cd c:\Dev\workly_project\workly-website
git remote -v

# workly-docs
cd c:\Dev\workly_project\workly-docs
git remote -v
```

### Workflow typique par repo

#### workly-desktop (Strict)

```bash
cd c:\Dev\workly_project\workly-desktop

# Modifier du code...
git add .
git commit -m "feat: add new feature"
git push
```

#### workly-website (Libre)

```bash
cd c:\Dev\workly_project\workly-website

# Modifier le site...
git add .
git commit -m "Ajout de la page contact"
git push
```

#### workly-docs (Semi-Strict)

```bash
cd c:\Dev\workly_project\workly-docs

# Documentation technique
git add .
git commit -m "docs: add session 13 guide"
git push

# Notes rapides
git add .
git commit -m "Notes brainstorming session 13"
git push
```

---

## 🎯 Avantages de cette configuration

### 🖥️ workly-desktop (Strict)

✅ Historique Git ultra-propre et professionnel  
✅ Génération automatique de changelogs possible  
✅ Facilite la collaboration et la maintenance  
✅ Standard reconnu internationalement  
✅ Versioning sémantique facilité  

### 🌐 workly-website (Libre)

✅ Rapidité des commits (pas de friction)  
✅ Flexibilité totale pour les changements de design  
✅ Naturel et accessible  
✅ Pas de barrière technique  
✅ Focus sur le contenu, pas sur le format  

### 📚 workly-docs (Semi-Strict)

✅ Structure avec `docs:` pour retrouver facilement les guides  
✅ Flexibilité pour les notes rapides  
✅ Pragmatique et adapté au workflow solo + IA  
✅ Historique lisible et organisé  
✅ Pas de blocage pour les brainstorming  

---

## 💡 Pourquoi 3 repos séparés ?

### 🎯 Avantages

1. **Séparation des préoccupations**
   - Code applicatif ≠ Site web ≠ Documentation
   - Chaque repo a son propre cycle de vie

2. **Déploiements indépendants**
   - Le site web peut être mis à jour sans toucher au code
   - La doc peut évoluer sans impacter l'app

3. **Conventions adaptées**
   - Chaque repo a sa convention de commits appropriée
   - Flexibilité vs Structure selon les besoins

4. **Gestion des droits**
   - Possibilité de rendre publique la doc sans exposer le code
   - Collaboration différente selon les repos

5. **Historique clair**
   - Pas de mélange entre commits de code, de site, et de doc
   - Plus facile de retrouver les changements

### ⚠️ Alternative non retenue

**Mono-repo avec tout dedans :**
- ❌ Historique Git mélangé (code + site + doc)
- ❌ Convention de commits difficile à appliquer
- ❌ Déploiements couplés
- ❌ Plus difficile à organiser

---

## 🔍 Recherche dans l'historique

### workly-desktop

```bash
# Trouver toutes les features
git log --grep="^feat:"

# Trouver tous les bugs fix
git log --grep="^fix:"

# Voir les commits d'un scope
git log --grep="feat(ai):"
```

### workly-website

```bash
# Historique complet
git log --oneline

# Recherche par mot-clé
git log --grep="page about"
```

### workly-docs

```bash
# Trouver les commits de doc technique
git log --grep="^docs:"

# Trouver les commits d'une session
git log --grep="session-12"

# Voir tout
git log --oneline
```

---

## 📚 Fichiers de référence créés

| Repo | Fichier | Description |
|------|---------|-------------|
| workly-desktop | `GIT_COMMIT_CONVENTIONS.md` | Guide complet Conventional Commits |
| workly-website | `GIT_COMMIT_CONVENTIONS.md` | Guide convention libre |
| workly-docs | `GIT_COMMIT_CONVENTIONS.md` | Guide convention semi-strict |
| workly-docs | `sessions/session_0_git_configuration/GIT_MULTI_REPOS_CONFIG.md` | Ce document |

---

## 🎓 Points importants à retenir

### ✅ À faire

- **workly-desktop** : Toujours utiliser Conventional Commits
- **workly-website** : Écrire des commits clairs et descriptifs
- **workly-docs** : Utiliser `docs:` pour la doc technique structurée
- Commits réguliers plutôt qu'énormes
- Lire les `GIT_COMMIT_CONVENTIONS.md` de chaque repo en cas de doute

### ❌ À éviter

- Mélanger les conventions entre repos
- Commits vides ou cryptiques (`update`, `fix`, `.`, `qsdfqsdf`)
- Commits énormes avec 100 changements non liés
- Oublier de push après commit (travail non sauvegardé sur GitHub)

---

## 🚀 Prochaines étapes

✅ Configuration Git terminée !

Tu peux maintenant :
1. **Coder** dans `workly-desktop` avec commits stricts
2. **Designer** le site dans `workly-website` avec commits libres
3. **Documenter** dans `workly-docs` avec commits semi-stricts

Chaque repo a son propre workflow Git optimisé pour son usage ! 🎉

---

**🎭 Configuration Multi-Repos Terminée ! 🚀**
