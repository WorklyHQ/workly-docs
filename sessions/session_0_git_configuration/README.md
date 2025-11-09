# Session 0 : Configuration Git & Unity

**Date :** 18 octobre 2025  
**Objectif :** Configurer correctement Git pour éviter de versionner les fichiers Unity générés

## 📋 Contenu

- **[GIT_UNITY_FIX.md](GIT_UNITY_FIX.md)** - Correction du `.gitignore` pour Unity

## 🎯 Résumé

Lors du premier commit, Git tentait de versionner les dossiers générés par Unity :
- `Library/` (plusieurs GB de cache)
- `Temp/` (fichiers temporaires)
- `PackageCache/` (packages téléchargés)

Ces dossiers sont **automatiquement régénérés** par Unity et ne doivent **jamais** être versionnés.

## ✅ Solution

1. Ajout des règles Unity dans `.gitignore`
2. Retrait des fichiers déjà trackés avec `git rm --cached`
3. Documentation complète du problème et de la solution

## 📚 Fichiers Créés

- `.gitignore` (mis à jour avec règles Unity complètes)
- `GIT_UNITY_FIX.md` (documentation détaillée)

## 🎓 Points Importants

- Seuls `Assets/`, `ProjectSettings/`, et `Packages/manifest.json` doivent être versionnés
- Unity régénère `Library/` automatiquement à l'ouverture du projet
- Fermer Unity avant les opérations Git massives
- Les warnings "LF → CRLF" sont normaux sur Windows

---

**Prochaine session :** Retour au développement normal ! 🚀
