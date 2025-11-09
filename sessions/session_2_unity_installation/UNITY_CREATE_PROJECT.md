# 🎮 Création du Projet Unity - Guide Étape par Étape

## 📋 Instructions Détaillées

### 1️⃣ Ouvrir Unity Hub

1. Lance **Unity Hub**
2. Tu devrais voir Unity 2022.3 LTS dans l'onglet "Installs"

---

### 2️⃣ Créer un Nouveau Projet

1. **Clique sur le bouton "New Project"** (en haut à droite) ou "Nouveau projet"

2. **Sélectionne le bon template** :
   
   ⭐ **CHOIX IMPORTANT** : Cherche et sélectionne :
   
   **"3D (URP)"** ou **"3D Universal Render Pipeline"**
   
   ❌ **NE CHOISIS PAS** :
   - "3D" tout court (Built-in Render Pipeline - ancien)
   - "3D (HDRP)" (trop lourd pour notre usage)
   - "2D"
   
   ✅ **SI "3D (URP)" n'est pas disponible** :
   - Choisis "3D" (on ajoutera URP manuellement après)

---

### 3️⃣ Configurer le Projet

Remplis les champs suivants :

**Project Name (Nom du projet)** :
```
DesktopMateUnity
```

**Location (Emplacement)** :
```
C:\Dev\desktop-mate\unity
```

⚠️ **IMPORTANT** : 
- Clique sur le dossier à côté du champ "Location"
- Navigue jusqu'à `C:\Dev\desktop-mate\unity`
- Le chemin final sera : `C:\Dev\desktop-mate\unity\DesktopMateUnity`

**Organization** (si demandé) :
```
Xyon15
```
(ou laisse vide)

**Version** :
- Sélectionne **Unity 2022.3.XX** (la version que tu viens d'installer)

---

### 4️⃣ Créer le Projet

1. **Vérifie tous les paramètres** :
   - ✅ Template : 3D (URP) ou 3D
   - ✅ Nom : DesktopMateUnity
   - ✅ Emplacement : C:\Dev\desktop-mate\unity
   - ✅ Version : 2022.3.XX

2. **Clique sur "Create Project"** (ou "Créer le projet")

3. **Attends le chargement** ⏳
   - Unity va créer le projet (2-5 minutes)
   - Importer les packages de base
   - Ouvrir l'éditeur Unity
   
   ☕ **C'est le bon moment pour prendre un café !**

---

## ✅ Ce Qui Va se Passer

Unity va créer automatiquement :

```
unity/
└── DesktopMateUnity/
    ├── Assets/              # Tous tes fichiers de jeu (scripts, modèles, etc.)
    ├── Packages/            # Packages Unity installés
    ├── ProjectSettings/     # Configuration du projet
    ├── Library/             # Cache Unity (généré automatiquement)
    └── Logs/               # Logs Unity
```

---

## 🎯 Une Fois Unity Ouvert

Tu devrais voir l'interface Unity avec :

- **Scene** : Vue 3D de ta scène
- **Game** : Aperçu du jeu
- **Hierarchy** : Liste des objets dans la scène
- **Project** : Explorateur de fichiers
- **Inspector** : Propriétés des objets sélectionnés
- **Console** : Messages et erreurs

**Quand tu vois tout ça, reviens me dire "Unity est ouvert" !** 🚀

---

## 🆘 Problèmes Possibles

### Le dossier unity/ n'existe pas encore

Pas de problème ! Crée-le :

```powershell
cd C:\Dev\desktop-mate
mkdir unity
```

Puis recommence la création du projet.

### Unity Hub ne trouve pas le dossier

1. Clique sur le bouton de dossier à côté de "Location"
2. Navigue manuellement jusqu'à `C:\Dev\desktop-mate`
3. Sélectionne le dossier `unity`

### Unity prend beaucoup de temps

**C'est normal !** La première création peut prendre 5-10 minutes selon ton ordinateur.

Unity doit :
- Créer la structure du projet
- Importer tous les packages URP
- Compiler les scripts de base
- Créer le cache

**Sois patient !** ⏳

---

## 💡 Conseil

Pendant le chargement, tu peux :
- Lire le fichier `UNITY_PROJECT_SETUP.md`
- Explorer le script `PythonBridge.cs` que j'ai créé
- Préparer un café ☕

---

**Dis-moi quand Unity est ouvert et prêt !** 😊
