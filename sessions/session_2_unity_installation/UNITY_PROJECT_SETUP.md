# 🎮 Guide de Création du Projet Unity

Maintenant que Unity est installé, créons le projet pour Desktop-Mate !

---

## 📋 Étapes à Suivre

### 1️⃣ Ouvrir Unity Hub

1. Lance **Unity Hub**
2. Assure-toi que Unity 2022.3 LTS est bien installé (visible dans l'onglet "Installs")

### 2️⃣ Créer un Nouveau Projet

1. Dans Unity Hub, clique sur **"New Project"** (ou "Nouveau projet")

2. **Sélectionne le template** :
   - Choisis **"3D (URP)"** ou **"3D Core"**
   - ⚠️ **IMPORTANT** : Si tu as le choix, prends **"3D (URP)"** (Universal Render Pipeline)

3. **Configure le projet** :
   - **Project Name** (Nom) : `DesktopMateUnity`
   - **Location** (Emplacement) : Clique sur le dossier et navigue jusqu'à :
     ```
     C:\Dev\desktop-mate\unity
     ```
   - **Version** : Sélectionne ta version Unity 2022.3 LTS

4. Clique sur **"Create Project"** (ou "Créer")

### 3️⃣ Attendre le Chargement

Unity va :
- Créer le projet (peut prendre 2-5 minutes)
- Importer les packages de base
- Ouvrir l'éditeur Unity

**Note** : C'est normal que ça prenne du temps la première fois !

---

## ✅ Vérifications

Une fois Unity ouvert, vérifie que :

1. **Le projet s'appelle bien "DesktopMateUnity"** (en haut de la fenêtre)

2. **Tu es dans le bon dossier** :
   - Menu **"Edit" > "Preferences" > "External Tools"**
   - Le chemin du projet doit contenir `C:\Dev\desktop-mate\unity`

3. **Tu as bien URP** (si tu l'as choisi) :
   - Dans le dossier **"Assets"**, tu devrais voir des dossiers comme "Settings", "URP", etc.

---

## 🎯 Prochaine Étape

Une fois que Unity est ouvert et prêt :

➡️ **Reviens me dire que c'est bon**, et je t'aiderai à :
1. Installer **UniVRM** (le package pour charger les modèles VRM)
2. Créer la scène principale
3. Créer le script **PythonBridge.cs** pour la communication avec Python

---

## 🆘 Problèmes Courants

### Le dossier unity/ n'existe pas
```powershell
# Dans le terminal PowerShell :
cd C:\Dev\desktop-mate
mkdir unity
```

### Unity ne démarre pas
- Redémarre Unity Hub
- Vérifie que tu as bien installé Unity 2022.3 LTS
- Vérifie que tu as assez d'espace disque (~5 GB minimum)

### Erreur de permissions
- Lance Unity Hub en tant qu'administrateur
- Vérifie que tu as les droits d'écriture dans `C:\Dev\desktop-mate\unity`

---

## 💡 Conseil

Pendant que Unity se charge (ça peut prendre quelques minutes), tu peux :
- Lire la documentation dans `docs/architecture.md`
- Explorer le code Python dans `src/`
- Prendre un café ☕

---

**Une fois Unity ouvert, reviens me voir !** 🚀
