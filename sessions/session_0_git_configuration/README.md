# Session 0 : Configuration Git & Unity

**Date :** 18 octobre 2025 (Unity) | 10 novembre 2025 (Multi-Repos)  
**Objectif :** Configurer correctement Git pour le projet Workly

## 📋 Contenu

- **[GIT_UNITY_FIX.md](GIT_UNITY_FIX.md)** - Correction du `.gitignore` pour Unity (18 oct. 2025)
- **[GIT_MULTI_REPOS_CONFIG.md](GIT_MULTI_REPOS_CONFIG.md)** - Configuration des 3 repos GitHub (10 nov. 2025) ✨ **NOUVEAU**

## 🎯 Résumé

### 📁 Configuration Unity (18 octobre 2025)

Lors du premier commit, Git tentait de versionner les dossiers générés par Unity :
- `Library/` (plusieurs GB de cache)
- `Temp/` (fichiers temporaires)
- `PackageCache/` (packages téléchargés)

Ces dossiers sont **automatiquement régénérés** par Unity et ne doivent **jamais** être versionnés.

### 🔧 Configuration Multi-Repos (10 novembre 2025) ✨ **NOUVEAU**

Configuration de **3 repos GitHub séparés** avec conventions de commits différentes :

| Repo | URL | Convention |
|------|-----|-----------|
| **workly-desktop** | `https://github.com/WorklyHQ/workly-desktop.git` | **Strict** (Conventional Commits) |
| **workly-website** | `https://github.com/WorklyHQ/workly-website.git` | **Libre** |
| **workly-docs** | `https://github.com/WorklyHQ/workly-docs.git` | **Semi-Strict** |

## ✅ Solutions appliquées

### 🛠️ Fix Unity .gitignore (18 octobre 2025)

1. Ajout des règles Unity dans `.gitignore`
2. Retrait des fichiers déjà trackés avec `git rm --cached`
3. Documentation complète du problème et de la solution

### � Configuration Multi-Repos (10 novembre 2025)

1. ✅ Initialisation du repo `workly-docs` (était absent)
2. ✅ Configuration des remotes GitHub pour les 3 repos
3. ✅ Création des guides de conventions de commits
4. ✅ Premier commit et push de `workly-docs` (151 fichiers)

## �📚 Fichiers créés

### Unity (18 octobre 2025)
- `.gitignore` (mis à jour avec règles Unity complètes)
- `GIT_UNITY_FIX.md` (documentation détaillée)

### Multi-Repos (10 novembre 2025) ✨
- `workly-desktop/GIT_COMMIT_CONVENTIONS.md` (Convention Strict)
- `workly-website/GIT_COMMIT_CONVENTIONS.md` (Convention Libre)
- `workly-docs/GIT_COMMIT_CONVENTIONS.md` (Convention Semi-Strict)
- `workly-docs/sessions/session_0_git_configuration/GIT_MULTI_REPOS_CONFIG.md` (Guide complet)

## 🎓 Points importants

### Unity
- Seuls `Assets/`, `ProjectSettings/`, et `Packages/manifest.json` doivent être versionnés
- Unity régénère `Library/` automatiquement à l'ouverture du projet
- Fermer Unity avant les opérations Git massives
- Les warnings "LF → CRLF" sont normaux sur Windows

### Multi-Repos
- **workly-desktop** : Commits stricts (`feat:`, `fix:`, `docs:`, etc.)
- **workly-website** : Commits libres et descriptifs
- **workly-docs** : `docs:` pour doc technique, libre pour notes
- Chaque repo a son propre cycle de vie et déploiement
- Séparation claire : Code ≠ Site ≠ Documentation

---

**🎊 Session 0 complète ! Configuration Git et Unity terminée ! 🚀**
