# 🔧 Correction Configuration Git pour Unity

**Date :** 18 octobre 2025  
**Problème :** Fichiers Unity temporaires versionnés par erreur

## ❌ Problème Rencontré

```
error: open("unity/DesktopMateUnity/Temp/FSTimeGet-..."):  Permission denied
error: unable to index file 'unity/DesktopMateUnity/Temp/...'
fatal: adding files failed
```

**Cause :** Les dossiers `Library/`, `Temp/`, et `PackageCache/` de Unity étaient suivis par Git.

## 🎯 Pourquoi c'est un Problème ?

### Dossiers Unity à NE JAMAIS versionner :

1. **`Library/`** (plusieurs GB !) 
   - Cache de compilation Unity
   - Métadonnées des assets
   - Régénéré automatiquement par Unity

2. **`Temp/`**
   - Fichiers temporaires de build
   - Processus Unity en cours
   - Peut causer des erreurs de permission

3. **`PackageCache/`**
   - Packages Unity installés automatiquement
   - Contenu téléchargé depuis le Package Manager
   - Recréé à partir de `Packages/manifest.json`

4. **`Logs/`**
   - Logs de débogage Unity
   - Changent à chaque session

5. **`UserSettings/`**
   - Préférences personnelles de l'éditeur
   - Layout de fenêtres, etc.

## ✅ Solution Appliquée

### 1. Mise à jour `.gitignore`

Ajout des règles Unity :

```gitignore
# ============================================
# UNITY GENERATED FILES - NE PAS VERSIONNER
# ============================================

# Unity dossiers générés automatiquement
unity/**/[Ll]ibrary/
unity/**/[Tt]emp/
unity/**/[Oo]bj/
unity/**/[Bb]uild/
unity/**/[Bb]uilds/
unity/**/[Ll]ogs/
unity/**/[Uu]ser[Ss]ettings/

# Unity PackageCache (packages Unity installés automatiquement)
unity/**/PackageCache/

# Fichiers projet IDE (générés automatiquement)
unity/**/*.csproj
unity/**/*.sln
unity/**/*.suo
unity/**/*.user
```

### 2. Retrait des fichiers déjà trackés

```powershell
git rm -r --cached unity/DesktopMateUnity/Library/
git rm -r --cached unity/DesktopMateUnity/Temp/
```

**Note :** `--cached` retire du tracking Git **sans supprimer** les fichiers locaux.

## 📦 Fichiers Unity à VERSIONNER

### ✅ Obligatoires :
- `Assets/` - Tous les assets du projet
- `ProjectSettings/` - Configuration du projet
- `Packages/manifest.json` - Liste des packages requis
- `Packages/packages-lock.json` - Versions exactes des packages

### ✅ Optionnels (selon projet) :
- `Assets/StreamingAssets/` - Assets chargés au runtime
- `.vsconfig` - Configuration Visual Studio recommandée

## 🎓 Leçons Apprises

### Warnings "LF will be replaced by CRLF"
- **Normal sur Windows** avec Git
- Unity utilise LF (Unix) par défaut
- Git convertit en CRLF (Windows) automatiquement
- Pas un problème, juste informatif

### Fichiers verrouillés
- Unity peut verrouiller des fichiers dans `Temp/`
- **Toujours fermer Unity** avant de faire des opérations Git massives
- Si erreur : fermer Unity, relancer la commande

## 📝 Commandes Git Utiles

### Voir ce qui est tracké :
```powershell
git ls-tree -r main --name-only | Select-String "unity"
```

### Vérifier taille du repo :
```powershell
git count-objects -vH
```

### Nettoyer l'historique Git (ATTENTION!) :
```powershell
# Si Library/ est déjà dans l'historique Git
git filter-branch --tree-filter 'rm -rf unity/DesktopMateUnity/Library' HEAD
```

## 🚀 Bonnes Pratiques

1. **Toujours** utiliser un `.gitignore` Unity dès le début
2. **Vérifier** avec `git status` avant de commit
3. **Fermer Unity** pour les opérations Git importantes
4. **Ne jamais** commit `Library/`, `Temp/`, `Logs/`
5. **Versionner** `ProjectSettings/` et `Packages/manifest.json`

## 📚 Ressources

- [Gitignore officiel Unity](https://github.com/github/gitignore/blob/main/Unity.gitignore)
- [Unity Manual - Version Control](https://docs.unity3d.com/Manual/ExternalVersionControlSystemSupport.html)
- [Git LFS pour gros assets](https://git-lfs.github.com/) (optionnel)

## ✅ Vérification

Après correction, `git status` devrait montrer :
```
M  .gitignore
?? unity/DesktopMateUnity/Assets/
?? unity/DesktopMateUnity/ProjectSettings/
?? unity/DesktopMateUnity/Packages/
```

**PAS** `Library/`, `Temp/`, ou `PackageCache/` ! ✅

---

**Status :** ✅ Corrigé  
**Impact :** Réduit la taille du repo de plusieurs GB  
**Prochaine étape :** Commit normal sans warnings critiques
